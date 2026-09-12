import { FormEvent, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { createFuelingRecord } from "../api/fueling";
import { listVehicles } from "../api/vehicles";
import { listDrivers } from "../api/drivers";
import type { FuelingRecordWrite } from "../types";
import styles from "./FormPage.module.css";

export default function FuelFormPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const now = new Date();
  const localISO = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);

  const [form, setForm] = useState<FuelingRecordWrite>({
    vehicle: 0, driver: 0, fueled_at: localISO,
    fuel_liters: "", price_per_liter: "", station_name: "", odometer_at_fueling: "",
  });

  const { data: vehicles } = useQuery({ queryKey: ["vehicles-all"], queryFn: () => listVehicles() });
  const { data: drivers } = useQuery({ queryKey: ["drivers-all"], queryFn: () => listDrivers() });

  const mutation = useMutation({
    mutationFn: createFuelingRecord,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fuel-records"] });
      toast.success("Fueling record registered successfully!");
      navigate("/fuel");
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${v}`).join("; ")
        : (detail ?? "Failed to save fueling record.");
      setError(msg);
      toast.error(msg);
    },
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: ["vehicle", "driver"].includes(name) ? Number(value) : value }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault(); setError(null);
    if (!form.vehicle || !form.driver) { setError("Please select both vehicle and driver."); return; }
    mutation.mutate({ ...form, fueled_at: new Date(form.fueled_at).toISOString() });
  }

  return (
    <div>
      <div className={styles.header}>
        <Link to="/fuel" className={styles.back}>← Fuel Records</Link>
        <h1 className={styles.heading}>Register Fueling</h1>
      </div>
      <div className={styles.card}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Vehicle *</label>
              <select name="vehicle" value={form.vehicle} onChange={handleChange} required>
                <option value={0}>— Select vehicle —</option>
                {vehicles?.results.map((v) => (
                  <option key={v.id} value={v.id}>{v.license_plate} — {v.make} {v.model}</option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label>Driver *</label>
              <select name="driver" value={form.driver} onChange={handleChange} required>
                <option value={0}>— Select driver —</option>
                {drivers?.results.map((d) => (
                  <option key={d.id} value={d.id}>{d.full_name} ({d.personnel_number})</option>
                ))}
              </select>
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Date & Time *</label>
              <input name="fueled_at" type="datetime-local" value={form.fueled_at} onChange={handleChange} required />
            </div>
            <div className={styles.field}>
              <label>Station Name *</label>
              <input name="station_name" value={form.station_name} onChange={handleChange} required placeholder="WOG, OKKO, SOCAR..." />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Fuel Liters *</label>
              <input name="fuel_liters" type="number" step="0.01" min="0.01" value={form.fuel_liters} onChange={handleChange} required placeholder="45.00" />
            </div>
            <div className={styles.field}>
              <label>Price per Liter *</label>
              <input name="price_per_liter" type="number" step="0.01" min="0.01" value={form.price_per_liter} onChange={handleChange} required placeholder="58.50" />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Odometer at Fueling (km) *</label>
              <input name="odometer_at_fueling" type="number" step="0.01" min="0" value={form.odometer_at_fueling} onChange={handleChange} required placeholder="15000.00" />
            </div>
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <div className={styles.actions}>
            <button type="submit" disabled={mutation.isPending} className={styles.submitBtn}>
              {mutation.isPending ? "Saving..." : "Register Fueling"}
            </button>
            <Link to="/fuel" className={styles.cancelBtn}>Cancel</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
