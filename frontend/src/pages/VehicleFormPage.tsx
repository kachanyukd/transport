import { FormEvent, useState, useCallback, useEffect } from "react";
import { useNavigate, Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { createVehicle, updateVehicle, getVehicle } from "../api/vehicles";
import type { VehicleWrite } from "../types";
import styles from "./FormPage.module.css";
import vinStyles from "./VinDecoder.module.css";

const FUEL_TYPES = ["petrol", "diesel", "gas", "electric", "hybrid"];

async function decodeVin(vin: string): Promise<{
  make?: string; model?: string; year?: number; fuelType?: string;
} | null> {
  if (vin.length !== 17) return null;
  try {
    const res = await fetch(
      `https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/${vin}?format=json`
    );
    if (!res.ok) return null;
    const data = await res.json();
    const r = data?.Results?.[0];
    if (!r || r.ErrorCode !== "0") return null;
    const rawFuel = (r.FuelTypePrimary ?? "").toLowerCase();
    let fuelType: string | undefined;
    if (rawFuel.includes("gasoline")) fuelType = "petrol";
    else if (rawFuel.includes("diesel")) fuelType = "diesel";
    else if (rawFuel.includes("electric") && !rawFuel.includes("hybrid")) fuelType = "electric";
    else if (rawFuel.includes("hybrid")) fuelType = "hybrid";
    else if (rawFuel.includes("gas") || rawFuel.includes("natural")) fuelType = "gas";
    return {
      make: r.Make || undefined,
      model: r.Model || undefined,
      year: r.ModelYear ? parseInt(r.ModelYear) : undefined,
      fuelType,
    };
  } catch { return null; }
}

const EMPTY_FORM: VehicleWrite = {
  license_plate: "", vin: "", make: "", model: "",
  year: new Date().getFullYear(), fuel_type: "petrol",
  norm_consumption_summer: "", norm_consumption_winter: "", odometer: "0",
};

export default function VehicleFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = !!id;
  const numericId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [vinDecoding, setVinDecoding] = useState(false);
  const [vinStatus, setVinStatus] = useState<"idle" | "found" | "not_found">("idle");
  const [form, setForm] = useState<VehicleWrite>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);

  const { data: existing, isLoading: loadingExisting } = useQuery({
    queryKey: ["vehicle", id],
    queryFn: () => getVehicle(numericId),
    enabled: isEdit && !isNaN(numericId),
  });

  useEffect(() => {
    if (existing) {
      setForm({
        license_plate: existing.license_plate,
        vin: existing.vin,
        make: existing.make,
        model: existing.model,
        year: existing.year,
        fuel_type: existing.fuel_type,
        norm_consumption_summer: existing.norm_consumption_summer,
        norm_consumption_winter: existing.norm_consumption_winter,
        odometer: existing.odometer,
      });
    }
  }, [existing]);

  const mutation = useMutation({
    mutationFn: (data: VehicleWrite) =>
      isEdit ? updateVehicle(numericId, data) : createVehicle(data),
    onSuccess: (vehicle) => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      queryClient.invalidateQueries({ queryKey: ["vehicle", id] });
      toast.success(isEdit
        ? `Vehicle ${vehicle.license_plate} updated successfully!`
        : `Vehicle ${vehicle.license_plate} created successfully!`
      );
      navigate(`/vehicles/${vehicle.id}`);
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${v}`).join("; ")
        : (detail ?? (isEdit ? "Failed to update vehicle." : "Failed to create vehicle."));
      setError(msg);
      toast.error(msg);
    },
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: name === "year" ? Number(value) : value }));
    if (name === "vin") setVinStatus("idle");
  }

  const handleVinDecode = useCallback(async () => {
    if (form.vin.length !== 17) { setError("VIN must be exactly 17 characters."); return; }
    setVinDecoding(true); setError(null);
    const toastId = toast.loading("Decoding VIN…");
    const result = await decodeVin(form.vin);
    toast.dismiss(toastId);
    setVinDecoding(false);
    if (!result) {
      setVinStatus("not_found");
      toast.error("VIN not recognised — fill fields manually.");
      return;
    }
    setVinStatus("found");
    setForm((prev) => ({
      ...prev,
      make: result.make ?? prev.make,
      model: result.model ?? prev.model,
      year: result.year ?? prev.year,
      fuel_type: (result.fuelType as any) ?? prev.fuel_type,
    }));
    toast.success("Make, model and year filled from VIN!");
  }, [form.vin]);

  function handleSubmit(e: FormEvent) { e.preventDefault(); setError(null); mutation.mutate(form); }

  if (isEdit && loadingExisting) return <p>Loading vehicle…</p>;

  return (
    <div>
      <div className={styles.header}>
        <Link to={isEdit ? `/vehicles/${id}` : "/vehicles"} className={styles.back}>
          ← {isEdit ? "Back to Vehicle" : "Vehicles"}
        </Link>
        <h1 className={styles.heading}>{isEdit ? "Edit Vehicle" : "Add New Vehicle"}</h1>
      </div>
      <div className={styles.card}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label>VIN *</label>
            <div className={vinStyles.vinRow}>
              <input name="vin" value={form.vin} onChange={handleChange} required
                placeholder="17-character VIN" maxLength={17} style={{ textTransform: "uppercase" }} />
              <button type="button" className={vinStyles.decodeBtn} onClick={handleVinDecode}
                disabled={vinDecoding || form.vin.length !== 17} title="Decode VIN to auto-fill make, model, year">
                {vinDecoding ? "Decoding…" : "🔍 Decode VIN"}
              </button>
            </div>
            {vinStatus === "found" && <span className={vinStyles.vinSuccess}>✓ Filled from VIN</span>}
            {vinStatus === "not_found" && <span className={vinStyles.vinWarn}>⚠ VIN not recognised — fill manually</span>}
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>License Plate *</label>
              <input name="license_plate" value={form.license_plate} onChange={handleChange} required
                placeholder="AA1234BB" style={{ textTransform: "uppercase" }} />
            </div>
            <div className={styles.field}>
              <label>Year *</label>
              <input name="year" type="number" value={form.year} onChange={handleChange} required min={1900} max={2030} />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Make *</label>
              <input name="make" value={form.make} onChange={handleChange} required placeholder="Toyota" />
            </div>
            <div className={styles.field}>
              <label>Model *</label>
              <input name="model" value={form.model} onChange={handleChange} required placeholder="Corolla" />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Fuel Type *</label>
              <select name="fuel_type" value={form.fuel_type} onChange={handleChange} required>
                {FUEL_TYPES.map((t) => (
                  <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label>Odometer (km)</label>
              <input name="odometer" value={form.odometer} onChange={handleChange} type="number" step="0.01" min="0" placeholder="0" />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Norm Consumption Summer (L/100km) *</label>
              <input name="norm_consumption_summer" value={form.norm_consumption_summer} onChange={handleChange}
                required type="number" step="0.01" min="0.1" placeholder="8.50" />
            </div>
            <div className={styles.field}>
              <label>Norm Consumption Winter (L/100km) *</label>
              <input name="norm_consumption_winter" value={form.norm_consumption_winter} onChange={handleChange}
                required type="number" step="0.01" min="0.1" placeholder="10.00" />
            </div>
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <div className={styles.actions}>
            <button type="submit" disabled={mutation.isPending} className={styles.submitBtn}>
              {mutation.isPending ? "Saving…" : isEdit ? "Save Changes" : "Create Vehicle"}
            </button>
            <Link to={isEdit ? `/vehicles/${id}` : "/vehicles"} className={styles.cancelBtn}>Cancel</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
