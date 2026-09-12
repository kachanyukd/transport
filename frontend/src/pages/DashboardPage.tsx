import { useQuery } from "@tanstack/react-query";
import { getDashboardStats } from "../api/reports";
import styles from "./DashboardPage.module.css";

function StatCard({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className={styles.statCard} style={{ borderTop: `4px solid ${color ?? "#2563eb"}` }}>
      <div className={styles.statValue}>{value}</div>
      <div className={styles.statLabel}>{label}</div>
    </div>
  );
}

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboardStats,
    refetchInterval: 60_000,
  });

  if (isLoading) return <p>Loading dashboard...</p>;
  if (error) return <p className={styles.error}>Failed to load dashboard data.</p>;
  if (!data) return null;

  return (
    <div>
      <h1 className={styles.heading}>Dashboard</h1>
      <div className={styles.grid}>
        <StatCard label="Total Vehicles" value={data.vehicles.total} color="#2563eb" />
        <StatCard label="Active Vehicles" value={data.vehicles.active} color="#16a34a" />
        <StatCard label="In Maintenance" value={data.vehicles.in_maintenance} color="#ea580c" />
        <StatCard label="Decommissioned" value={data.vehicles.decommissioned} color="#6b7280" />
      </div>
      <div className={styles.grid} style={{ marginTop: "1.5rem" }}>
        <StatCard label="Total Drivers" value={data.drivers.total} color="#7c3aed" />
        <StatCard label="Active Drivers" value={data.drivers.active} color="#16a34a" />
        <StatCard label="Anomalies (30d)" value={data.recent_anomalies_30d} color="#dc2626" />
        <StatCard label="Open Maintenance" value={data.open_maintenance_count} color="#ea580c" />
      </div>
    </div>
  );
}
