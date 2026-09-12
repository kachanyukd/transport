import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getFuelingRecord } from "../api/fueling";
import styles from "./DetailPage.module.css";

export default function FuelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = Number(id);

  const { data: record, isLoading, error } = useQuery({
    queryKey: ["fuel-record", id],
    queryFn: () => getFuelingRecord(numericId),
    enabled: !isNaN(numericId),
  });

  if (isNaN(numericId))
    return (
      <div>
        <Link to="/fuel" className={styles.back}>← Fuel Records</Link>
        <p className={styles.error}>Invalid record ID.</p>
      </div>
    );

  if (isLoading) return <p>Loading…</p>;
  if (error || !record)
    return (
      <div>
        <Link to="/fuel" className={styles.back}>← Fuel Records</Link>
        <p className={styles.error}>Record not found.</p>
      </div>
    );

  return (
    <div>
      <div className={styles.header}>
        <Link to="/fuel" className={styles.back}>← Fuel Records</Link>
        <h1 className={styles.heading}>Fuel Record #{record.id}</h1>
      </div>
      <div className={styles.card}>
        <dl className={styles.dl}>
          <dt>Date</dt><dd>{new Date(record.fueled_at).toLocaleString()}</dd>
          <dt>Vehicle</dt><dd>{record.vehicle_info}</dd>
          <dt>Driver</dt><dd>{record.driver_info}</dd>
          <dt>Station</dt><dd>{record.station_name}</dd>
          <dt>Fuel Liters</dt><dd>{record.fuel_liters} L</dd>
          <dt>Price / Liter</dt><dd>₴{record.price_per_liter}</dd>
          <dt>Total Cost</dt><dd>₴{record.total_cost}</dd>
          <dt>Odometer</dt><dd>{Number(record.odometer_at_fueling).toLocaleString()} km</dd>
          <dt>Actual Consumption</dt><dd>{record.actual_consumption ?? "—"} L/100km</dd>
          <dt>Deviation</dt><dd>{record.deviation_pct ? `${Number(record.deviation_pct).toFixed(1)}%` : "—"}</dd>
          <dt>Anomalous</dt>
          <dd>
            {record.is_anomalous === null ? "—"
              : record.is_anomalous
                ? <span style={{ color: "#dc2626", fontWeight: 700 }}>⚠ YES</span>
                : <span style={{ color: "#16a34a" }}>No</span>}
          </dd>
          <dt>Created</dt><dd>{new Date(record.created_at).toLocaleDateString()}</dd>
        </dl>
        <p style={{ marginTop: "1rem", color: "#64748b", fontSize: "0.85rem" }}>
          ℹ️ Fuel records are immutable — they cannot be edited after creation.
        </p>
      </div>
    </div>
  );
}
