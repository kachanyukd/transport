import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { Role } from "../types";
import styles from "./Layout.module.css";

interface NavItem {
  to: string;
  label: string;
  roles?: Role[];
}

const NAV_ITEMS: NavItem[] = [
  { to: "/dashboard",   label: "🏠 Dashboard" },
  { to: "/vehicles",    label: "🚛 Vehicles" },
  { to: "/drivers",     label: "👤 Drivers",     roles: ["admin", "manager", "dispatcher"] },
  { to: "/fuel",        label: "⛽ Fuel Records" },
  { to: "/maintenance", label: "🔧 Maintenance", roles: ["admin", "manager", "dispatcher"] },
  { to: "/reports",     label: "📊 Reports",     roles: ["admin", "manager"] },
  { to: "/users",       label: "🔑 Users",       roles: ["admin"] },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role))
  );

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>Fleet Manager</div>
        <nav>
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.active : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className={styles.userInfo}>
          <span>{user?.username}</span>
          <span className={styles.role}>{user?.role}</span>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            Logout
          </button>
        </div>
      </aside>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
