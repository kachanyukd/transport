import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getDriver } from "../api/drivers";
import StatusBadge from "../components/StatusBadge/StatusBadge";
import { useAuth } from "../context/AuthContext";
import styles from "./DetailPage.module.css";

export default function DriverDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const numericId = Number(id);

  const { data: driver, isLoading, error } = useQuery({
    queryKey: ["driver", id],
    queryFn: () => getDriver(numericId),
    enabled: !isNaN(numericId),
  });

  const canWrite = user?.role === "admin" || user?.role === "manager";

  if (isNaN(numericId))
    return (
      <div>
        <Link to="/drivers" className={styles.back}>← Drivers</Link>
        <p className={styles.error}>Invalid driver ID.</p>
      </div>
    );

  if (isLoading) return <p>Loading…</p>;
  if (error || !driver)
    return (
      <div>
        <Link to="/drivers" className={styles.back}>← Drivers</Link>
        <p className={styles.error}>Driver not found.</p>
      </div>
    );

  return (
    <div>
      <div className={styles.header}>
        <Link to="/drivers" className={styles.back}>← Drivers</Link>
        <h1 className={styles.heading}>{driver.full_name}</h1>
        <StatusBadge status={driver.status} />
      </div>
      <div className={styles.card}>
        <dl className={styles.dl}>
          <dt>Personnel #</dt><dd>{driver.personnel_number}</dd>
          <dt>Date of Birth</dt><dd>{new Date(driver.date_of_birth).toLocaleDateString()}</dd>
          <dt>Phone</dt><dd>{driver.phone}</dd>
          <dt>License Category</dt><dd>{driver.license_category}</dd>
          <dt>License Number</dt><dd>{driver.license_number}</dd>
          <dt>License Issued</dt><dd>{new Date(driver.license_issued_at).toLocaleDateString()}</dd>
          <dt>License Expires</dt><dd>{new Date(driver.license_expires_at).toLocaleDateString()}</dd>
          <dt>Status</dt><dd><StatusBadge status={driver.status} /></dd>
          <dt>Added</dt><dd>{new Date(driver.created_at).toLocaleDateString()}</dd>
        </dl>
        {canWrite && (
          <div className={styles.actions}>
            <Link to={`/drivers/${id}/edit`} className={styles.editBtn}>
              ✏️ Edit Driver
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
