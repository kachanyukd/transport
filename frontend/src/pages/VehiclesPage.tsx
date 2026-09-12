import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { listVehicles, createVehicle } from "../api/vehicles";
import StatusBadge from "../components/StatusBadge/StatusBadge";
import MockFillButton from "../components/MockFillButton/MockFillButton";
import { useAuth } from "../context/AuthContext";
import styles from "./TablePage.module.css";

function extractCursor(url: string | null): string | null {
  if (!url) return null;
  try {
    const u = new URL(url, window.location.origin);
    return u.searchParams.get("cursor");
  } catch { return null; }
}

const MOCK_VEHICLES = [
  { license_plate: "ПО0001АА", vin: "JT2BF22K100185834", make: "Toyota",      model: "Camry",       year: 2021, fuel_type: "petrol" as const, norm_consumption_summer: "8.20", norm_consumption_winter: "10.00", odometer: "45000" },
  { license_plate: "ПО0002ВВ", vin: "WDB9062031R197343", make: "Mercedes",    model: "Actros 1845", year: 2020, fuel_type: "diesel" as const, norm_consumption_summer: "29.00", norm_consumption_winter: "34.00", odometer: "320000" },
  { license_plate: "ПО0003СС", vin: "VF1JG000050954012", make: "Renault",     model: "Kangoo",      year: 2022, fuel_type: "diesel" as const, norm_consumption_summer: "6.80",  norm_consumption_winter: "8.50",  odometer: "18000" },
  { license_plate: "ПО0004ДД", vin: "YV2RT8XAXKA749571", make: "Volvo",       model: "FH16 750",    year: 2019, fuel_type: "diesel" as const, norm_consumption_summer: "32.00", norm_consumption_winter: "38.00", odometer: "680000" },
  { license_plate: "ПО0005ЕЕ", vin: "TMBCE41Z0E6065743", make: "Skoda",       model: "Octavia",     year: 2023, fuel_type: "petrol" as const, norm_consumption_summer: "6.50",  norm_consumption_winter: "8.00",  odometer: "5500" },
];

export default function VehiclesPage() {
  const [cursor, setCursor] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [mockIdx, setMockIdx] = useState(0);

  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (cursor) params.cursor = cursor;

  const { data, isLoading, error } = useQuery({
    queryKey: ["vehicles", params],
    queryFn: () => listVehicles(params),
  });

  const mockMutation = useMutation({
    mutationFn: createVehicle,
    onSuccess: (v) => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      toast.success(`Demo vehicle ${v.license_plate} added!`);
      setMockIdx((i) => (i + 1) % MOCK_VEHICLES.length);
    },
    onError: () => toast.error("Demo vehicle already exists — try another."),
  });

  const canWrite = user?.role === "admin" || user?.role === "manager";

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.heading}>Vehicles</h1>
        {canWrite && (
          <div className={styles.headerActions}>
            <MockFillButton
              onClick={() => mockMutation.mutate(MOCK_VEHICLES[mockIdx])}
              loading={mockMutation.isPending}
            />
            <Link to="/vehicles/new" className={styles.addBtn}>+ Add Vehicle</Link>
          </div>
        )}
      </div>
      <div className={styles.filters}>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setCursor(null); }}>
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="maintenance">Maintenance</option>
          <option value="decommissioned">Decommissioned</option>
        </select>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p className={styles.error}>Failed to load vehicles.</p>}
      {data && (
        <>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>License Plate</th><th>Make / Model</th><th>Year</th>
                  <th>Fuel Type</th><th>Odometer (km)</th><th>Status</th><th></th>
                </tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={7} style={{ textAlign: "center", color: "#64748b", padding: "2rem" }}>
                    No vehicles found. Click "+ Add Vehicle" or "⚡ Demo" to add one.
                  </td></tr>
                ) : (
                  data.results.map((v) => (
                    <tr key={v.id}>
                      <td><strong>{v.license_plate}</strong></td>
                      <td>{v.make} {v.model}</td>
                      <td>{v.year}</td>
                      <td>{v.fuel_type}</td>
                      <td>{Number(v.odometer).toLocaleString()}</td>
                      <td><StatusBadge status={v.status} /></td>
                      <td><Link to={`/vehicles/${v.id}`} className={styles.viewLink}>View</Link></td>
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
