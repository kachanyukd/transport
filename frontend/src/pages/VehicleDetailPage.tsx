import { useState } from "react";
import { useParams, Link, useNavigate, Navigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { getVehicle, decommissionVehicle } from "../api/vehicles";
import StatusBadge from "../components/StatusBadge/StatusBadge";
import ConfirmModal from "../components/ConfirmModal/ConfirmModal";
import { useAuth } from "../context/AuthContext";
import styles from "./DetailPage.module.css";

export default function VehicleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [showConfirm, setShowConfirm] = useState(false);

  const numericId = Number(id);
  const isNew = id === "new";

  const { data: vehicle, isLoading, error } = useQuery({
    queryKey: ["vehicle", id],
    queryFn: () => getVehicle(numericId),
    enabled: !isNew && !isNaN(numericId),
  });

  const decommission = useMutation({
    mutationFn: () => decommissionVehicle(numericId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      queryClient.invalidateQueries({ queryKey: ["vehicle", id] });
      toast.success(`${vehicle?.license_plate} successfully decommissioned`);
      navigate("/vehicles");
    },
    onError: () => {
      toast.error("Cannot decommission — close all open maintenance records first.");
    },
  });

  if (isNew) return <Navigate to="/vehicles" replace />;

  if (isNaN(numericId))
    return (
      <div>
        <Link to="/vehicles" className={styles.back}>← Vehicles</Link>
        <p className={styles.error}>Invalid vehicle ID.</p>
      </div>
    );

  if (isLoading) return <p>Loading...</p>;
  if (error)
    return (
      <div>
        <Link to="/vehicles" className={styles.back}>← Vehicles</Link>
        <p className={styles.error}>Vehicle not found.</p>
      </div>
    );
  if (!vehicle) return null;

  const canWrite = user?.role === "admin" || user?.role === "manager";

  return (
    <>
      <ConfirmModal
        isOpen={showConfirm}
        title="Decommission Vehicle"
        message={`Are you sure you want to decommission ${vehicle.license_plate}? This action cannot be undone.`}
        confirmLabel="Decommission"
        danger
        onConfirm={() => {
          setShowConfirm(false);
          decommission.mutate();
        }}
        onCancel={() => setShowConfirm(false)}
      />

      <div>
        <div className={styles.header}>
          <Link to="/vehicles" className={styles.back}>← Vehicles</Link>
          <h1 className={styles.heading}>{vehicle.license_plate}</h1>
          <StatusBadge status={vehicle.status} />
        </div>
        <div className={styles.card}>
          <dl className={styles.dl}>
            <dt>VIN</dt><dd>{vehicle.vin}</dd>
            <dt>Make / Model</dt><dd>{vehicle.make} {vehicle.model}</dd>
            <dt>Year</dt><dd>{vehicle.year}</dd>
            <dt>Fuel Type</dt><dd>{vehicle.fuel_type}</dd>
            <dt>Odometer</dt><dd>{Number(vehicle.odometer).toLocaleString()} km</dd>
            <dt>Norm (summer)</dt><dd>{vehicle.norm_consumption_summer} L/100km</dd>
            <dt>Norm (winter)</dt><dd>{vehicle.norm_consumption_winter} L/100km</dd>
            <dt>Registered</dt><dd>{new Date(vehicle.registered_at).toLocaleDateString()}</dd>
          </dl>
          {canWrite && (
            <div className={styles.actions}>
              {vehicle.status !== "decommissioned" && (
                <Link to={`/vehicles/${id}/edit`} className={styles.editBtn}>
                  ✏️ Edit Vehicle
                </Link>
              )}
              {vehicle.status !== "decommissioned" && (
                <button
                  className={styles.dangerBtn}
                  onClick={() => setShowConfirm(true)}
                  disabled={decommission.isPending}
                >
                  {decommission.isPending ? "Processing..." : "Decommission Vehicle"}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
