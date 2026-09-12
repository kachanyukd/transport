import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { listFuelingRecords, createFuelingRecord } from "../api/fueling";
import { listVehicles } from "../api/vehicles";
import { listDrivers } from "../api/drivers";
import MockFillButton from "../components/MockFillButton/MockFillButton";
import { useAuth } from "../context/AuthContext";
import styles from "./TablePage.module.css";

function extractCursor(url: string | null): string | null {
  if (!url) return null;
  try { const u = new URL(url, window.location.origin); return u.searchParams.get("cursor"); }
  catch { return null; }
}

const STATIONS = ["WOG", "OKKO", "SOCAR", "ANP", "KLO", "БРСМ", "Shell"];

function randomItem<T>(arr: T[]): T { return arr[Math.floor(Math.random() * arr.length)]; }
function randomBetween(a: number, b: number) { return +(a + Math.random() * (b - a)).toFixed(2); }

export default function FuelPage() {
  const [cursor, setCursor] = useState<string | null>(null);
  const [anomalousFilter, setAnomalousFilter] = useState("");
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const canCreate = user?.role === "admin" || user?.role === "manager" || user?.role === "dispatcher";

  const params: Record<string, string> = {};
  if (anomalousFilter) params.is_anomalous = anomalousFilter;
  if (cursor) params.cursor = cursor;

  const { data, isLoading, error } = useQuery({
    queryKey: ["fuel-records", params],
    queryFn: () => listFuelingRecords(params),
  });

  // For demo: fetch first vehicle and first driver
  const { data: vehiclesData } = useQuery({
    queryKey: ["vehicles-all"],
    queryFn: () => listVehicles(),
    enabled: canCreate,
  });
  const { data: driversData } = useQuery({
    queryKey: ["drivers-all"],
    queryFn: () => listDrivers(),
    enabled: canCreate,
  });

  const mockMutation = useMutation({
    mutationFn: createFuelingRecord,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fuel-records"] });
      toast.success("Demo fuel record added!");
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error?.detail ?? "Demo fuel record failed.";
      toast.error(typeof msg === "string" ? msg : JSON.stringify(msg));
    },
  });

  function handleDemoFuel() {
    const vehicles = vehiclesData?.results ?? [];
    const drivers  = driversData?.results  ?? [];
    if (!vehicles.length || !drivers.length) {
      toast.error("Add at least one vehicle and one driver first (use ⚡ Demo there).");
      return;
    }
    const v = randomItem(vehicles);
    const d = randomItem(drivers);
    // Random date in last 30 days
    const daysAgo = Math.floor(Math.random() * 30);
    const fueled_at = new Date(Date.now() - daysAgo * 86400000).toISOString();
    const liters  = randomBetween(30, 200);
    const price   = randomBetween(52, 59);
    const odo     = +(parseFloat(v.odometer) + randomBetween(100, 1500)).toFixed(2);

    mockMutation.mutate({
      vehicle: v.id,
      driver:  d.id,
      fueled_at,
      fuel_liters:        String(liters),
      price_per_liter:    String(price),
      station_name:       randomItem(STATIONS),
      odometer_at_fueling: String(odo),
    });
  }

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.heading}>Fuel Records</h1>
        {canCreate && (
          <div className={styles.headerActions}>
            <MockFillButton onClick={handleDemoFuel} loading={mockMutation.isPending} />
            <Link to="/fuel/new" className={styles.addBtn}>+ Register Fueling</Link>
          </div>
        )}
      </div>
      <div className={styles.filters}>
        <select value={anomalousFilter} onChange={(e) => { setAnomalousFilter(e.target.value); setCursor(null); }}>
          <option value="">All records</option>
          <option value="true">Anomalous only</option>
          <option value="false">Normal only</option>
        </select>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p className={styles.error}>Failed to load fuel records.</p>}
      {data && (
        <>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Date</th><th>Vehicle</th><th>Driver</th><th>Liters</th>
                  <th>Price/L</th><th>Total</th><th>Odometer</th>
                  <th>Consumption</th><th>Deviation</th><th>Anomalous</th><th>Station</th><th></th>
                </tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={12} style={{ textAlign: "center", color: "#64748b", padding: "2rem" }}>
                    No records yet. Click "⚡ Demo" for instant entry.
                  </td></tr>
                ) : (
                  data.results.map((r) => (
                    <tr key={r.id}>
                      <td>{new Date(r.fueled_at).toLocaleDateString()}</td>
                      <td>{r.vehicle_info}</td>
                      <td>{r.driver_info}</td>
                      <td>{r.fuel_liters}</td>
                      <td>{r.price_per_liter}</td>
                      <td>{r.total_cost}</td>
                      <td>{Number(r.odometer_at_fueling).toLocaleString()}</td>
                      <td>{r.actual_consumption ?? "—"}</td>
                      <td>{r.deviation_pct ? `${Number(r.deviation_pct).toFixed(1)}%` : "—"}</td>
                      <td>
                        {r.is_anomalous === null ? "—"
                          : r.is_anomalous ? <span className={styles.anomalousBadge}>YES</span>
                          : "No"}
                      </td>
                      <td>{r.station_name}</td>
                      <td><Link to={`/fuel/${r.id}`} className={styles.viewLink}>View</Link></td>
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
