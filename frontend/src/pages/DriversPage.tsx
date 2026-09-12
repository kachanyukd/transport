import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { listDrivers, createDriver } from "../api/drivers";
import StatusBadge from "../components/StatusBadge/StatusBadge";
import MockFillButton from "../components/MockFillButton/MockFillButton";
import { useAuth } from "../context/AuthContext";
import styles from "./TablePage.module.css";

function extractCursor(url: string | null): string | null {
  if (!url) return null;
  try { const u = new URL(url, window.location.origin); return u.searchParams.get("cursor"); }
  catch { return null; }
}

const MOCK_DRIVERS = [
  { full_name: "Гончаренко Олег Вікторович",   personnel_number: "DRV-D01", date_of_birth: "1987-06-14", phone: "+380501110001", license_category: "CE", license_number: "ДЕМ000001", license_issued_at: "2016-03-01", license_expires_at: "2028-03-01" },
  { full_name: "Захаренко Сергій Михайлович",  personnel_number: "DRV-D02", date_of_birth: "1991-11-22", phone: "+380501110002", license_category: "C",  license_number: "ДЕМ000002", license_issued_at: "2018-07-15", license_expires_at: "2029-07-15" },
  { full_name: "Лисенко Андрій Павлович",      personnel_number: "DRV-D03", date_of_birth: "1984-03-07", phone: "+380501110003", license_category: "D",  license_number: "ДЕМ000003", license_issued_at: "2014-09-20", license_expires_at: "2027-09-20" },
  { full_name: "Остапенко Ігор Юрійович",      personnel_number: "DRV-D04", date_of_birth: "1993-08-30", phone: "+380501110004", license_category: "B",  license_number: "ДЕМ000004", license_issued_at: "2020-01-10", license_expires_at: "2030-01-10" },
  { full_name: "Шевченко Максим Олексійович",  personnel_number: "DRV-D05", date_of_birth: "1989-12-05", phone: "+380501110005", license_category: "CE", license_number: "ДЕМ000006", license_issued_at: "2017-05-25", license_expires_at: "2028-05-25" },
];

export default function DriversPage() {
  const [cursor, setCursor] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [mockIdx, setMockIdx] = useState(0);

  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (cursor) params.cursor = cursor;

  const { data, isLoading, error } = useQuery({
    queryKey: ["drivers", params],
    queryFn: () => listDrivers(params),
  });

  const mockMutation = useMutation({
    mutationFn: createDriver,
    onSuccess: (d: any) => {
      queryClient.invalidateQueries({ queryKey: ["drivers"] });
      toast.success(`Demo driver "${d.full_name}" added!`);
      setMockIdx((i) => (i + 1) % MOCK_DRIVERS.length);
    },
    onError: () => toast.error("Demo driver already exists — try another."),
  });

  const canWrite = user?.role === "admin" || user?.role === "manager";

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.heading}>Drivers</h1>
        {canWrite && (
          <div className={styles.headerActions}>
            <MockFillButton
              onClick={() => mockMutation.mutate(MOCK_DRIVERS[mockIdx] as any)}
              loading={mockMutation.isPending}
            />
            <Link to="/drivers/new" className={styles.addBtn}>+ Add Driver</Link>
          </div>
        )}
      </div>
      <div className={styles.filters}>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setCursor(null); }}>
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>
      {isLoading && <p>Loading...</p>}
      {error && <p className={styles.error}>Failed to load drivers.</p>}
      {data && (
        <>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Full Name</th><th>Personnel #</th><th>Phone</th>
                  <th>License Category</th><th>License #</th><th>License Expires</th><th>Status</th><th></th>
                </tr>
              </thead>
              <tbody>
                {data.results.length === 0 ? (
                  <tr><td colSpan={8} style={{ textAlign: "center", color: "#64748b", padding: "2rem" }}>
                    No drivers found. Click "⚡ Demo" or "+ Add Driver".
                  </td></tr>
                ) : (
                  data.results.map((d) => (
                    <tr key={d.id}>
                      <td><strong>{d.full_name}</strong></td>
                      <td>{d.personnel_number}</td>
                      <td>{d.phone}</td>
                      <td>{d.license_category}</td>
                      <td>{d.license_number}</td>
                      <td>{new Date(d.license_expires_at).toLocaleDateString()}</td>
                      <td><StatusBadge status={d.status} /></td>
                      <td><Link to={`/drivers/${d.id}`} className={styles.viewLink}>View</Link></td>
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
