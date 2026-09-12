import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { getMaintenance, closeMaintenance } from "../api/maintenance";
import StatusBadge from "../components/StatusBadge/StatusBadge";
import ConfirmModal from "../components/ConfirmModal/ConfirmModal";
import { useAuth } from "../context/AuthContext";
import styles from "./DetailPage.module.css";
import formStyles from "./FormPage.module.css";

const RECORD_TYPE_LABELS: Record<string, string> = {
  planned_to: "Planned Technical Inspection",
  current_repair: "Current Repair",
  major_repair: "Major Repair",
};

export default function MaintenanceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const numericId = Number(id);
  const [showCloseForm, setShowCloseForm] = useState(false);
  const [closeForm, setCloseForm] = useState({
    work_performed: "", parts_cost: "", labor_cost: "", odometer_at_closing: "",
  });
  const [closeError, setCloseError] = useState<string | null>(null);

  const { data: record, isLoading, error } = useQuery({
    queryKey: ["maintenance-record", id],
    queryFn: () => getMaintenance(numericId),
    enabled: !isNaN(numericId),
  });

  const closeMutation = useMutation({
    mutationFn: () => closeMaintenance(numericId, closeForm),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["maintenance-record", id] });
      toast.success("Maintenance record closed!");
      setShowCloseForm(false);
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${v}`).join("; ")
        : (detail ?? "Failed to close record.");
      setCloseError(msg); toast.error(msg);
    },
  });

  const canWrite = user?.role === "admin" || user?.role === "manager";

  if (isNaN(numericId))
    return (
      <div>
        <Link to="/maintenance" className={styles.back}>← Maintenance</Link>
        <p className={styles.error}>Invalid record ID.</p>
      </div>
    );

  if (isLoading) return <p>Loading…</p>;
  if (error || !record)
    return (
      <div>
        <Link to="/maintenance" className={styles.back}>← Maintenance</Link>
        <p className={styles.error}>Record not found.</p>
      </div>
    );

  return (
    <>
      <div>
        <div className={styles.header}>
          <Link to="/maintenance" className={styles.back}>← Maintenance</Link>
          <h1 className={styles.heading}>Maintenance Record #{record.id}</h1>
          <StatusBadge status={record.is_open ? "open" : "closed"} />
        </div>
        <div className={styles.card}>
          <dl className={styles.dl}>
            <dt>Vehicle</dt><dd>{record.vehicle_info}</dd>
            <dt>Type</dt><dd>{RECORD_TYPE_LABELS[record.record_type] ?? record.record_type}</dd>
            <dt>Opened At</dt><dd>{new Date(record.opened_at).toLocaleString()}</dd>
            <dt>Closed At</dt><dd>{record.closed_at ? new Date(record.closed_at).toLocaleString() : "—"}</dd>
            <dt>Status</dt><dd><StatusBadge status={record.is_open ? "open" : "closed"} /></dd>
            <dt>Fault Description</dt><dd style={{ whiteSpace: "pre-wrap" }}>{record.fault_description}</dd>
            {record.work_performed && (
              <><dt>Work Performed</dt><dd style={{ whiteSpace: "pre-wrap" }}>{record.work_performed}</dd></>
            )}
            <dt>Contractor</dt><dd>{record.contractor_name || "—"}</dd>
            <dt>Parts Cost</dt><dd>{record.parts_cost ? `₴${record.parts_cost}` : "—"}</dd>
            <dt>Labor Cost</dt><dd>{record.labor_cost ? `₴${record.labor_cost}` : "—"}</dd>
            <dt>Total Cost</dt><dd>{record.total_cost ? `₴${record.total_cost}` : "—"}</dd>
            {record.odometer_at_closing && (
              <><dt>Odometer at Closing</dt><dd>{Number(record.odometer_at_closing).toLocaleString()} km</dd></>
            )}
          </dl>

          {canWrite && record.is_open && (
            <div className={styles.actions}>
              <Link to={`/maintenance/${id}/edit`} className={styles.editBtn}>
                ✏️ Edit Record
              </Link>
              <button
                className={styles.dangerBtn}
                style={{ background: "#16a34a" }}
                onClick={() => setShowCloseForm((v) => !v)}
              >
                ✓ Close Record
              </button>
            </div>
          )}

          {/* Inline close form */}
          {showCloseForm && (
            <div style={{ marginTop: "1.5rem", borderTop: "1px solid #f1f5f9", paddingTop: "1.5rem" }}>
              <h3 style={{ margin: "0 0 1rem", fontSize: "1rem", fontWeight: 700 }}>Close This Record</h3>
              <div className={formStyles.form}>
                <div className={formStyles.field}>
                  <label>Work Performed *</label>
                  <textarea
                    value={closeForm.work_performed}
                    onChange={(e) => setCloseForm((p) => ({ ...p, work_performed: e.target.value }))}
                    required rows={3} placeholder="Describe all work completed..."
                  />
                </div>
                <div className={formStyles.row}>
                  <div className={formStyles.field}>
                    <label>Parts Cost (₴)</label>
                    <input type="number" step="0.01" min="0" value={closeForm.parts_cost}
                      onChange={(e) => setCloseForm((p) => ({ ...p, parts_cost: e.target.value }))} placeholder="0.00" />
                  </div>
                  <div className={formStyles.field}>
                    <label>Labor Cost (₴)</label>
                    <input type="number" step="0.01" min="0" value={closeForm.labor_cost}
                      onChange={(e) => setCloseForm((p) => ({ ...p, labor_cost: e.target.value }))} placeholder="0.00" />
                  </div>
                </div>
                <div className={formStyles.field}>
                  <label>Odometer at Closing (km)</label>
                  <input type="number" step="0.01" min="0" value={closeForm.odometer_at_closing}
                    onChange={(e) => setCloseForm((p) => ({ ...p, odometer_at_closing: e.target.value }))} placeholder="Current km" />
                </div>
                {closeError && <p className={formStyles.error}>{closeError}</p>}
                <div className={formStyles.actions}>
                  <button
                    type="button"
                    disabled={!closeForm.work_performed || closeMutation.isPending}
                    onClick={() => { setCloseError(null); closeMutation.mutate(); }}
                    className={formStyles.submitBtn}
                    style={{ background: "#16a34a" }}
                  >
                    {closeMutation.isPending ? "Closing…" : "Confirm Close"}
                  </button>
                  <button type="button" onClick={() => setShowCloseForm(false)} className={formStyles.cancelBtn}>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
