import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { Role } from "../types";

interface Props {
  children: React.ReactNode;
  roles?: Role[];
}

/**
 * ProtectedRoute — guards routes by authentication and optional role check.
 * Unauthenticated → redirect to /login.
 * Wrong role → redirect to /dashboard.
 *
 * Note: frontend guards complement (not replace) server-side RBAC.
 */
export default function ProtectedRoute({ children, roles }: Props) {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
