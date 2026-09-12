import { FormEvent, useState, useEffect } from "react";
import { useNavigate, Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { createDriver, updateDriver, getDriver } from "../api/drivers";
import styles from "./FormPage.module.css";

const LICENSE_CATEGORIES = ["B", "C", "D", "BC", "CD", "BCE", "CDE"];

const today = new Date().toISOString().slice(0, 10);
const eighteenYearsAgo = new Date(new Date().setFullYear(new Date().getFullYear() - 18))
  .toISOString().slice(0, 10);

const EMPTY_FORM = {
  full_name: "", personnel_number: "", date_of_birth: eighteenYearsAgo,
  phone: "", license_category: "C", license_number: "",
  license_issued_at: today, license_expires_at: "", status: "active" as const,
};

export default function DriverFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = !!id;
  const numericId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  const { data: existing, isLoading: loadingExisting } = useQuery({
    queryKey: ["driver", id],
    queryFn: () => getDriver(numericId),
    enabled: isEdit && !isNaN(numericId),
  });

  useEffect(() => {
    if (existing) {
      setForm({
        full_name: existing.full_name,
        personnel_number: existing.personnel_number,
        date_of_birth: existing.date_of_birth,
        phone: existing.phone,
        license_category: existing.license_category,
        license_number: existing.license_number,
        license_issued_at: existing.license_issued_at,
        license_expires_at: existing.license_expires_at,
        status: existing.status as "active",
      });
    }
  }, [existing]);

  const mutation = useMutation({
    mutationFn: (data: typeof form) =>
      isEdit ? updateDriver(numericId, data as any) : createDriver(data as any),
    onSuccess: (driver) => {
      queryClient.invalidateQueries({ queryKey: ["drivers"] });
      queryClient.invalidateQueries({ queryKey: ["driver", id] });
      toast.success(isEdit
        ? `Driver "${driver.full_name}" updated successfully!`
        : `Driver "${driver.full_name}" added successfully!`
      );
      navigate(isEdit ? `/drivers/${numericId}` : "/drivers");
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join("; ")
        : (detail ?? (isEdit ? "Failed to update driver." : "Failed to create driver."));
      setError(msg);
      toast.error(msg);
    },
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e: FormEvent) { e.preventDefault(); setError(null); mutation.mutate(form); }

  if (isEdit && loadingExisting) return <p>Loading driver…</p>;

  return (
    <div>
      <div className={styles.header}>
        <Link to={isEdit ? `/drivers/${id}` : "/drivers"} className={styles.back}>
          ← {isEdit ? "Back to Driver" : "Drivers"}
        </Link>
        <h1 className={styles.heading}>{isEdit ? "Edit Driver" : "Add New Driver"}</h1>
      </div>
      <div className={styles.card}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Full Name *</label>
              <input name="full_name" value={form.full_name} onChange={handleChange} required placeholder="Іванов Іван Іванович" />
            </div>
            <div className={styles.field}>
              <label>Personnel Number *</label>
              <input name="personnel_number" value={form.personnel_number} onChange={handleChange} required placeholder="DRV-009" />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>Date of Birth *</label>
              <input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} required />
            </div>
            <div className={styles.field}>
              <label>Phone *</label>
              <input name="phone" value={form.phone} onChange={handleChange} required placeholder="+380671234567" />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>License Category *</label>
              <select name="license_category" value={form.license_category} onChange={handleChange} required>
                {LICENSE_CATEGORIES.map((cat) => <option key={cat} value={cat}>{cat}</option>)}
              </select>
            </div>
            <div className={styles.field}>
              <label>License Number *</label>
              <input name="license_number" value={form.license_number} onChange={handleChange} required placeholder="АВС123456" />
            </div>
          </div>
          <div className={styles.row}>
            <div className={styles.field}>
              <label>License Issued At *</label>
              <input name="license_issued_at" type="date" value={form.license_issued_at} onChange={handleChange} required />
            </div>
            <div className={styles.field}>
              <label>License Expires At *</label>
              <input name="license_expires_at" type="date" value={form.license_expires_at} onChange={handleChange} required />
            </div>
          </div>
          {isEdit && (
            <div className={styles.field}>
              <label>Status</label>
              <select name="status" value={form.status} onChange={handleChange}>
                <option value="active">Active</option>
                <option value="dismissed">Dismissed</option>
              </select>
            </div>
          )}
          {error && <p className={styles.error}>{error}</p>}
          <div className={styles.actions}>
            <button type="submit" disabled={mutation.isPending} className={styles.submitBtn}>
              {mutation.isPending ? "Saving…" : isEdit ? "Save Changes" : "Create Driver"}
            </button>
            <Link to={isEdit ? `/drivers/${id}` : "/drivers"} className={styles.cancelBtn}>Cancel</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
