/**
 * Reports page — fuel cost report with Recharts chart.
 * Filters stored in URL search params (sharable links).
 */

import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getFuelReport } from "../api/reports";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import styles from "./ReportsPage.module.css";

export default function ReportsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const from = searchParams.get("from") ?? "";
  const to = searchParams.get("to") ?? "";

  const params: Record<string, string> = {};
  if (from) params.from = from;
  if (to) params.to = to;

  const { data, isLoading, error } = useQuery({
    queryKey: ["report-fuel", params],
    queryFn: () => getFuelReport(params),
  });

  function handleFilterChange(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    setSearchParams(next);
  }

  const chartData = data?.by_month.map((row) => ({
    month: new Date(row.month).toLocaleDateString("uk", { month: "short", year: "numeric" }),
    cost: Number(row.cost),
    liters: Number(row.liters),
  })) ?? [];

  return (
    <div>
      <h1 className={styles.heading}>Fuel Report</h1>
      <div className={styles.filters}>
        <label>
          From:
          <input
            type="date"
            value={from}
            onChange={(e) => handleFilterChange("from", e.target.value)}
          />
        </label>
        <label>
          To:
          <input
            type="date"
            value={to}
            onChange={(e) => handleFilterChange("to", e.target.value)}
          />
        </label>
      </div>

      {isLoading && <p>Loading report...</p>}
      {error && <p className={styles.error}>Failed to load report.</p>}

      {data && (
        <>
          <div className={styles.summaryGrid}>
            <div className={styles.summaryCard}>
              <div className={styles.summaryValue}>
                {data.summary.total_liters ? Number(data.summary.total_liters).toFixed(1) : "—"} L
              </div>
              <div className={styles.summaryLabel}>Total Liters</div>
            </div>
            <div className={styles.summaryCard}>
              <div className={styles.summaryValue}>
                {data.summary.total_cost
                  ? Number(data.summary.total_cost).toLocaleString("uk", {
                      style: "currency",
                      currency: "UAH",
                    })
                  : "—"}
              </div>
              <div className={styles.summaryLabel}>Total Cost</div>
            </div>
            <div className={styles.summaryCard}>
              <div className={styles.summaryValue}>
                {data.summary.avg_consumption
                  ? `${Number(data.summary.avg_consumption).toFixed(2)} L/100km`
                  : "—"}
              </div>
              <div className={styles.summaryLabel}>Avg Consumption</div>
            </div>
            <div className={styles.summaryCard}>
              <div className={styles.summaryValue}>{data.summary.anomaly_count}</div>
              <div className={styles.summaryLabel}>Anomalies</div>
            </div>
          </div>

          {chartData.length > 0 && (
            <div className={styles.chartCard}>
              <h2 className={styles.chartTitle}>Cost by Month</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cost" fill="#2563eb" name="Cost (₴)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className={styles.tableCard}>
            <h2 className={styles.chartTitle}>By Vehicle</h2>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>License Plate</th>
                  <th>Make / Model</th>
                  <th>Total Liters</th>
                  <th>Total Cost</th>
                  <th>Avg Consumption</th>
                  <th>Anomalies</th>
                </tr>
              </thead>
              <tbody>
                {data.by_vehicle.map((row) => (
                  <tr key={row.vehicle_id}>
                    <td>{row["vehicle__license_plate"]}</td>
                    <td>{row["vehicle__make"]} {row["vehicle__model"]}</td>
                    <td>{Number(row.liters).toFixed(1)}</td>
                    <td>{Number(row.cost).toLocaleString()}</td>
                    <td>{row.avg_consumption ? Number(row.avg_consumption).toFixed(2) : "—"}</td>
                    <td>{row.anomaly_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
