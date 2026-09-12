import { FormEvent, useState, useEffect } from "react";
import { useNavigate, Link, useSearchParams, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { createMaintenance, closeMaintenance, updateMaintenance, getMaintenance } from "../api/maintenance";
import { listVehicles } from "../api/vehicles";
import styles from "./FormPage.module.css";

const RECORD_TYPES = [
  { value: "planned_to",     label: "Planned Technical Inspection" },
  { value: "current_repair", label: "Current Repair" },
  { value: "major_repair",   label: "Major Repair" },
];

export default function MaintenanceFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = !!id;
  const numericId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const closeId = searchParams.get("close");
  const [error, setError] = useState<string | null>(null);

  const now = new Date();
  const localISO = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);

  const [openForm, setOpenForm] = useState({
    vehicle: 0, record_type: "current_repair", opened_at: localISO,
    fault_description: "", contractor_name: "", parts_cost: "", labor_cost: "",
  });
  const [closeForm, setCloseForm] = useState({
    work_performed: "", parts_cost: "", labor_cost: "", odometer_at_closing: "",
  });

  const { data: vehicles } = useQuery({ queryKey: ["vehicles-all"], queryFn: () => listVehicles() });

  // Fetch existing record in edit mode
  const { data: existing, isLoading: loadingExisting } = useQuery({
    queryKey: ["maintenance-record", id],
    queryFn: () => getMaintenance(numericId),
    enabled: isEdit && !isNaN(numericId),
  });

  useEffect(() => {
    if (existing) {
      const dt = new Date(existing.opened_at);
      const local = new Date(dt.getTime() - dt.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
      setOpenForm({
        vehicle: existing.vehicle,
        record_type: existing.record_type,
        opened_at: local,
        fault_description: existing.fault_description ?? "",
        contractor_name: existing.contractor_name ?? "",
        parts_cost: existing.parts_cost ?? "",
        labor_cost: existing.labor_cost ?? "",
      });
    }
  }, [existing]);

  const openMutation = useMutation({
    mutationFn: (data: typeof openForm) =>
      isEdit
        ? updateMaintenance(numericId, { ...data, opened_at: new Date(data.opened_at).toISOString() } as any)
        : createMaintenance({ ...data, opened_at: new Date(data.opened_at).toISOString() } as any),
    onSuccess: (record) => {
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["maintenance-record", id] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      toast.success(isEdit ? "Maintenance record updated!" : "Maintenance request opened successfully!");
      navigate(isEdit ? `/maintenance/${record.id}` : "/maintenance");
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${v}`).join("; ")
        : (detail ?? "Failed to save maintenance record.");
      setError(msg); toast.error(msg);
    },
  });

  const closeMutation = useMutation({
    mutationFn: (data: typeof closeForm) => closeMaintenance(Number(closeId), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      toast.success("Maintenance record closed successfully!");
      navigate("/maintenance");
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${v}`).join("; ")
        : (detail ?? "Failed to close maintenance record.");
      setError(msg); toast.error(msg);
    },
  });

  function handleOpenChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
    const { name, value } = e.target;
    setOpenForm((prev) => ({ ...prev, [name]: name === "vehicle" ? Number(value) : value }));
  }
  function handleCloseChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const { name, value } = e.target;
    setCloseForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleOpenSubmit(e: FormEvent) {
    e.preventDefault(); setError(null);
    if (!openForm.vehicle) { setError("Please select a vehicle."); return; }
    openMutation.mutate(openForm);
  }
  function handleCloseSubmit(e: FormEvent) {
    e.preventDefault(); setError(null);
    closeMutation.mutate(closeForm);
  }

  // ── Close mode ──
  if (closeId) {
    return (
      <div>
        <div className={styles.header}>
          <Link to="/maintenance" className={styles.back}>← Maintenance</Link>
          <h1 className={styles.heading}>Close Maintenance Record #{closeId}</h1>
        </div>
        <div className={styles.card}>
          <form onSubmit={handleCloseSubmit} className={styles.form}>
            <div className={styles.field}>
              <label>Work Performed *</label>
              <textarea name="work_performed" value={closeForm.work_performed} onChange={handleCloseChange}
                required placeholder="Describe all work completed..." rows={4} />
            </div>
            <div className={styles.row}>
              <div className={styles.field}>
                <label>Parts Cost (₴)</label>
                <input name="parts_cost" type="number" step="0.01" min="0" value={closeForm.parts_cost} onChange={handleCloseChange} placeholder="0.00" />
              </div>
              <div className={styles.field}>
                <label>Labor Cost (₴)</label>
                <input name="labor_cost" type="number" step="0.01" min="0" value={closeForm.labor_cost} onChange={handleCloseChange} placeholder="0.00" />
              </div>
            </div>
            <div className={styles.field}>
              <label>Odometer at Closing (km)</label>
              <input name="odometer_at_closing" type="number" step="0.01" min="0" value={closeForm.odometer_at_closing} onChange={handleCloseChange} placeholder="Current odometer reading" />
            </div>
            {error && <p className={styles.error}>{error}</p>}
            <div className={styles.actions}>
              <button type="submit" disabled={closeMutation.isPending} className={styles.submitBtn}>
                {closeMutation.isPending ? "Closing…" : "Close Record"}
              </button>
              <Link to="/maintenance" className={styles.cancelBtn}>Cancel</Link>
            </div>
          </form>
        </div>
      </div>
    );
  }

  if (isEdit && loadingExisting) return <p>Loading maintenance record…</p>;

  // ── Open / Edit mode ──
  return (
    <div>
      <div className={styles.header}>
        <Link to={isEdit ? `/maintenance/${id}` : "/maintenance"} className={styles.back}>
          ← {isEdit ? "Back to Record" : "Maintenance"}
        </Link>
        <h1 className={styles.heading}>
          {isEdit ? "Edit Maintenance Record" : "Open Maintenance Request"}
        </h1>
      </div>
      <div className={styles.card}>
        <form onSubmit={handleOpenSubmit} className={styles.form}>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Vehicle *</label>
              <select name="vehicle" value={openForm.vehicle} onChange={handleOpenChange} required>
                <option value={0}>— Select vehicle —</option>
                {vehicles?.results.map((v) => (
                  <option key={v.id} value={v.id}>{v.license_plate} — {v.make} {v.model}</option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label>Record Type *</label>
              <select name="record_type" value={openForm.record_type} onChange={handleOpenChange} required>
                {RECORD_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Opened At *</label>
              <input name="opened_at" type="datetime-local" value={openForm.opened_at} onChange={handleOpenChange} required />
            </div>
            <div className={styles.field}>
              <label>Contractor Name</label>
              <input name="contractor_name" value={openForm.contractor_name} onChange={handleOpenChange} placeholder="ServiceCo Ltd" />
            </div>
          </div>
          <div className={styles.field}>
            <label>Fault Description *</label>
            <textarea name="fault_description" value={openForm.fault_description} onChange={handleOpenChange}
              required placeholder="Describe the fault or reason for maintenance..." rows={3} />
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Parts Cost (₴)</label>
              <input name="parts_cost" type="number" step="0.01" min="0" value={openForm.parts_cost} onChange={handleOpenChange} placeholder="0.00" />
            </div>
            <div className={styles.field}>
              <label>Labor Cost (₴)</label>
              <input name="labor_cost" type="number" step="0.01" min="0" value={openForm.labor_cost} onChange={handleOpenChange} placeholder="0.00" />
            </div>
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <div className={styles.actions}>
            <button type="submit" disabled={openMutation.isPending} className={styles.submitBtn}>
              {openMutation.isPending ? "Saving…" : isEdit ? "Save Changes" : "Open Request"}
            </button>
            <Link to={isEdit ? `/maintenance/${id}` : "/maintenance"} className={styles.cancelBtn}>Cancel</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
