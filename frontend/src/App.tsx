import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import VehiclesPage from "./pages/VehiclesPage";
import VehicleDetailPage from "./pages/VehicleDetailPage";
import VehicleFormPage from "./pages/VehicleFormPage";
import DriversPage from "./pages/DriversPage";
import DriverFormPage from "./pages/DriverFormPage";
import DriverDetailPage from "./pages/DriverDetailPage";
import FuelPage from "./pages/FuelPage";
import FuelFormPage from "./pages/FuelFormPage";
import FuelDetailPage from "./pages/FuelDetailPage";
import MaintenancePage from "./pages/MaintenancePage";
import MaintenanceFormPage from "./pages/MaintenanceFormPage";
import MaintenanceDetailPage from "./pages/MaintenanceDetailPage";
import ReportsPage from "./pages/ReportsPage";
import UsersPage from "./pages/UsersPage";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />

        {/* Vehicles */}
        <Route path="vehicles/new" element={
          <ProtectedRoute roles={["admin", "manager"]}><VehicleFormPage /></ProtectedRoute>
        } />
        <Route path="vehicles/:id/edit" element={
          <ProtectedRoute roles={["admin", "manager"]}><VehicleFormPage /></ProtectedRoute>
        } />
        <Route path="vehicles/:id" element={<VehicleDetailPage />} />
        <Route path="vehicles" element={<VehiclesPage />} />

        {/* Drivers */}
        <Route path="drivers/new" element={
          <ProtectedRoute roles={["admin", "manager"]}><DriverFormPage /></ProtectedRoute>
        } />
        <Route path="drivers/:id/edit" element={
          <ProtectedRoute roles={["admin", "manager"]}><DriverFormPage /></ProtectedRoute>
        } />
        <Route path="drivers/:id" element={<DriverDetailPage />} />
        <Route path="drivers" element={<DriversPage />} />

        {/* Fuel */}
        <Route path="fuel/new" element={
          <ProtectedRoute roles={["admin", "manager", "dispatcher"]}><FuelFormPage /></ProtectedRoute>
        } />
        <Route path="fuel/:id" element={<FuelDetailPage />} />
        <Route path="fuel" element={<FuelPage />} />

        {/* Maintenance */}
        <Route path="maintenance/new" element={
          <ProtectedRoute roles={["admin", "manager"]}><MaintenanceFormPage /></ProtectedRoute>
        } />
        <Route path="maintenance/:id/edit" element={
          <ProtectedRoute roles={["admin", "manager"]}><MaintenanceFormPage /></ProtectedRoute>
        } />
        <Route path="maintenance/:id" element={<MaintenanceDetailPage />} />
        <Route path="maintenance" element={<MaintenancePage />} />

        {/* Reports */}
        <Route path="reports" element={
          <ProtectedRoute roles={["admin", "manager"]}><ReportsPage /></ProtectedRoute>
        } />

        {/* Users — admin only */}
        <Route path="users" element={
          <ProtectedRoute roles={["admin"]}><UsersPage /></ProtectedRoute>
        } />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
