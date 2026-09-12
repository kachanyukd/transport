import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { listUsers, createUser, updateUser, deactivateUser } from "../api/users";
import type { AppUser, UserWrite } from "../api/users";
import ConfirmModal from "../components/ConfirmModal/ConfirmModal";
import MockFillButton from "../components/MockFillButton/MockFillButton";
import styles from "./TablePage.module.css";
import modalStyles from "./UsersPage.module.css";

const ROLES = ["admin", "manager", "dispatcher", "driver"] as const;

const MOCK_USERS = [
  { username: "manager_demo",    email: "manager@fleet.demo",    role: "manager"    as const, password: "Demo1234!" },
  { username: "dispatcher_demo", email: "dispatcher@fleet.demo", role: "dispatcher" as const, password: "Demo1234!" },
  { username: "driver_demo",     email: "driver@fleet.demo",     role: "driver"     as const, password: "Demo1234!" },
  { username: "manager2_demo",   email: "manager2@fleet.demo",   role: "manager"    as const, password: "Demo1234!" },
];
const ROLE_COLORS: Record<string, string> = {
  admin: "#7c3aed", manager: "#2563eb", dispatcher: "#0891b2", driver: "#16a34a",
};

// ─── Small inline modal for create / edit user ───────────────────────
interface UserModalProps {
  initial?: AppUser | null;
  onClose: () => void;
  onSaved: () => void;
}

function UserModal({ initial, onClose, onSaved }: UserModalProps) {
  const queryClient = useQueryClient();
  const isEdit = !!initial;

  const [form, setForm] = useState<UserWrite>({
    username: initial?.username ?? "",
    email: initial?.email ?? "",
    role: initial?.role ?? "driver",
    password: "",
    is_active: initial?.is_active ?? true,
  });
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (data: UserWrite) =>
      isEdit ? updateUser(initial!.id, data) : createUser(data),
    onSuccess: (user) => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(isEdit ? `User "${user.username}" updated!` : `User "${user.username}" created!`);
      onSaved();
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.error?.detail ?? err?.response?.data;
      const msg = typeof detail === "object"
        ? Object.entries(detail).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join("; ")
        : (String(detail) || "Save failed.");
      setError(msg);
      toast.error(msg);
    },
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const payload = { ...form };
    // don't send empty password on edit
    if (isEdit && !payload.password) delete (payload as any).password;
    mutation.mutate(payload);
  }

  return (
    <div className={modalStyles.overlay} onClick={onClose}>
      <div className={modalStyles.modal} onClick={(e) => e.stopPropagation()} role="dialog">
        <h2 className={modalStyles.title}>{isEdit ? "Edit User" : "Create User"}</h2>
        <form onSubmit={handleSubmit} className={modalStyles.form}>
          <div className={modalStyles.field}>
            <label>Username *</label>
            <input name="username" value={form.username} onChange={handleChange} required placeholder="john_doe" />
          </div>
          <div className={modalStyles.field}>
            <label>Email</label>
            <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="john@company.ua" />
          </div>
          <div className={modalStyles.field}>
            <label>Role *</label>
            <select name="role" value={form.role} onChange={handleChange} required>
              {ROLES.map((r) => <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>)}
            </select>
          </div>
          <div className={modalStyles.field}>
            <label>{isEdit ? "New Password (leave blank to keep)" : "Password *"}</label>
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              required={!isEdit}
              placeholder={isEdit ? "••••••••" : "min 8 characters"}
              minLength={isEdit ? undefined : 8}
            />
          </div>
          {isEdit && (
            <label className={modalStyles.checkboxRow}>
              <input name="is_active" type="checkbox" checked={form.is_active} onChange={handleChange} />
              <span>Active account</span>
            </label>
          )}
          {error && <p className={modalStyles.error}>{error}</p>}
          <div className={modalStyles.actions}>
            <button type="button" onClick={onClose} className={modalStyles.cancelBtn}>Cancel</button>
            <button type="submit" disabled={mutation.isPending} className={modalStyles.submitBtn}>
              {mutation.isPending ? "Saving…" : isEdit ? "Save Changes" : "Create User"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Main UsersPage ───────────────────────────────────────────────────
export default function UsersPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editUser, setEditUser] = useState<AppUser | null>(null);
  const [deactivateTarget, setDeactivateTarget] = useState<AppUser | null>(null);
  const [mockIdx, setMockIdx] = useState(0);

  const { data: users = [], isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: listUsers,
  });

  const mockMutation = useMutation({
    mutationFn: createUser,
    onSuccess: (u) => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(`Demo user "${u.username}" created! Password: Demo1234!`);
      setMockIdx((i) => (i + 1) % MOCK_USERS.length);
    },
    onError: () => toast.error("Demo user already exists — try another."),
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: number) => deactivateUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(`User "${deactivateTarget?.username}" deactivated.`);
      setDeactivateTarget(null);
    },
    onError: () => { toast.error("Failed to deactivate user."); setDeactivateTarget(null); },
  });

  function openCreate() { setEditUser(null); setShowModal(true); }
  function openEdit(u: AppUser) { setEditUser(u); setShowModal(true); }
  function closeModal() { setShowModal(false); setEditUser(null); }

  return (
    <>
      {showModal && (
        <UserModal initial={editUser} onClose={closeModal} onSaved={closeModal} />
      )}
      <ConfirmModal
        isOpen={!!deactivateTarget}
        title="Deactivate User"
        message={`Deactivate "${deactivateTarget?.username}"? They will no longer be able to log in.`}
        confirmLabel="Deactivate"
        danger
        onConfirm={() => deactivateMutation.mutate(deactivateTarget!.id)}
        onCancel={() => setDeactivateTarget(null)}
      />

      <div>
        <div className={styles.header}>
          <h1 className={styles.heading}>Users</h1>
          <div className={styles.headerActions}>
            <MockFillButton
              onClick={() => mockMutation.mutate(MOCK_USERS[mockIdx])}
              loading={mockMutation.isPending}
            />
            <button onClick={openCreate} className={styles.addBtn}>+ Add User</button>
          </div>
        </div>

        {isLoading && <p>Loading…</p>}
        {error && <p className={styles.error}>Failed to load users.</p>}

        {!isLoading && (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: "center", color: "#64748b", padding: "2rem" }}>
                      No users found.
                    </td>
                  </tr>
                ) : (
                  users.map((u) => (
                    <tr key={u.id} style={{ opacity: u.is_active ? 1 : 0.5 }}>
                      <td><strong>{u.username}</strong></td>
                      <td>{u.email || "—"}</td>
                      <td>
                        <span style={{
                          background: ROLE_COLORS[u.role] + "18",
                          color: ROLE_COLORS[u.role],
                          padding: "0.2rem 0.6rem",
                          borderRadius: "99px",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                        }}>
                          {u.role}
                        </span>
                      </td>
                      <td>
                        <span style={{
                          color: u.is_active ? "#16a34a" : "#94a3b8",
                          fontWeight: 600,
                          fontSize: "0.85rem",
                        }}>
                          {u.is_active ? "● Active" : "○ Inactive"}
                        </span>
                      </td>
                      <td>{new Date(u.created_at).toLocaleDateString()}</td>
                      <td style={{ display: "flex", gap: "0.5rem" }}>
                        <button
                          onClick={() => openEdit(u)}
                          className={styles.viewLink}
                          style={{ background: "none", border: "none", cursor: "pointer", padding: 0 }}
                        >
                          Edit
                        </button>
                        {u.is_active && (
                          <button
                            onClick={() => setDeactivateTarget(u)}
                            style={{
                              background: "none", border: "none", cursor: "pointer",
                              color: "#dc2626", fontSize: "0.85rem", fontWeight: 500, padding: 0,
                            }}
                          >
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
