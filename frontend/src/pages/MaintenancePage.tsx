import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { listMaintenance, createMaintenance } from "../api/maintenance";
import { listVehicles } from "../api/vehicles";
import StatusBadge from "../components/StatusBadge/StatusBadge";
import MockFillButton from "../components/MockFillButton/MockFillButton";
import { useAuth } from "../context/AuthContext";
import styles from "./TablePage.module.css";

function extractCursor(url: string | null): string | null {
  if (!url) return null;
  try { const u = new URL(url, window.location.origin); return u.searchParams.get("cursor"); }
  catch { return null; }
}

function randomItem<T>(arr: T[]): T { return arr[Math.floor(Math.random() * arr.length)]; }

const RECORD_TYPES  = ["planned_to", "current_repair", "major_repair"] as const;
const FAULT_DESCS   = [
  "Планове ТО згідно регламенту технічного обслуговування.",
  "Несправність гальмівної системи, скрип при гальмуванні.",
  "Витік моторного масла, необхідна заміна прокладок.",
  "Заміна зношених шин на всіх осях.",
  "Несправність кондиціонера, не охолоджує.",
  "Поломка стартера, двигун не заводиться.",
  "Замінити акумуляторну батарею.",
  "Несправність рульового управління.",
];
const CONTRACTORS = ["СТО Авторемонт", "ТОВ Автосервіс Плюс", "Mercedes-Benz Service", "DAF Trucks Ukraine", "Офіційний дилер Toyota", "Renault Trucks Service"];

export default function MaintenancePage() {
  const [cursor, setCursor] = useState<string | null>(null);
  const [isOpenFilter, setIsOpenFilter] = useState("");
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const canCreate = user?.role === "admin" || user?.role === "manager";

  const params: Record<string, string> = {};
  if (isOpenFilter) params.is_open = isOpenFilter;
  if (cursor) params.cursor = cursor;

  const { data, isLoading, error } = useQuery({
    queryKey: ["maintenance", params],
    queryFn: () => listMaintenance(params),
  });

  const { data: vehiclesData } = useQuery({
    queryKey: ["vehicles-all"],
    queryFn: () => listVehicles(),
    enabled: canCreate,
  });

  const mockMutation = useMutation({
    mutationFn: createMaintenance,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      toast.success("Demo maintenance record opened!");
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error?.detail ?? "Demo maintenance failed.";
      toast.error(typeof msg === "string" ? msg : JSON.stringify(msg));
    },
  });

  function handleDemoMaintenance() {
    const vehicles = vehiclesData?.results ?? [];
    const active = vehicles.filter((v) => v.status === "active");
    const pool = active.length ? active : vehicles;
    if (!pool.length) {
      toast.error("Add at least one vehicle first (use ⚡ Demo on Vehicles page).");
      return;
    }
    const v = randomItem(pool);
    mockMutation.mutate({
      vehicle: v.id,
      record_type: randomItem(RECORD_TYPES),
      opened_at: new Date().toISOString(),
      fault_description: randomItem(FAULT_DESCS),
      contractor_name: randomItem(CONTRACTORS),
      parts_cost: "0",
      labor_cost: "0",
    } as any);
  }

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.heading}>Maintenance Records</h1>
        {canCreate && (
          <div className={styles.headerActions}>
            <MockFillButton onClick={handleDemoMaintenance} loading={mockMutation.isPending} />
            <Link to="/maintenance/new" className={styles.addBtn}>+ Open Request</Link>
          </div>
        )}
      </div>
      <div className={styles.filters}>
        <select value={isOpenFilter} onChange={(e) => { setIsOpenFilter(e.target.value); setCursor(null); }}>
          <option value="">All</option>
          <option value="true">Open only</option>
          <option value="false">Closed only</option>
        </select>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p className={styles.error}>Failed to load maintenance records.</p>}
      {data && (
        <>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Vehicle</th><th>Type</th><th>Opened</th><th>Closed</th>
                  <th>Status</th><th>Total Cost</th><th>Contractor</th><th>Description</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={9} style={{ textAlign: "center", color: "#64748b", padding: "2rem" }}>
                    No records yet. Click "⚡ Demo" to add one instantly.
                  </td></tr>
                ) : (
                  data.results.map((r) => (
                    <tr key={r.id}>
                      <td>{r.vehicle_info}</td>
                      <td><StatusBadge status={r.record_type} /></td>
                      <td>{new Date(r.opened_at).toLocaleDateString()}</td>
                      <td>{r.closed_at ? new Date(r.closed_at).toLocaleDateString() : "—"}</td>
                      <td><StatusBadge status={r.is_open ? "open" : "closed"} /></td>
                      <td>{r.total_cost}</td>
                      <td>{r.contractor_name || "—"}</td>
                      <td style={{ maxWidth: 180, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {r.fault_description}
                      </td>
                      <td style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                        <Link to={`/maintenance/${r.id}`} className={styles.viewLink}>View</Link>
                        {canCreate && r.is_open && (
                          <Link to={`/maintenance/${r.id}/edit`} className={styles.viewLink} style={{ color: "#7c3aed" }}>Edit</Link>
                        )}
                        {canCreate && r.is_open && (
                          <Link to={`/maintenance/new?close=${r.id}`} className={styles.viewLink} style={{ color: "#16a34a" }}>Close</Link>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          <div className={styles.pagination}>
            <button disabled={!data.previous} onClick={() => { const c = extractCursor(data.previous); if (c !== null) setCursor(c); }}>Previous</button>
            <button disabled={!data.next}     onClick={() => { const c = extractCursor(data.next);     if (c !== null) setCursor(c); }}>Next</button>
          </div>
        </>
      )}
    </div>
  );
}
