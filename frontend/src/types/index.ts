// ============================================================
// Domain type definitions — mirrors the Django model fields
// ============================================================

export type Role = "admin" | "manager" | "dispatcher" | "driver";
export type VehicleStatus = "active" | "maintenance" | "decommissioned";
export type FuelType = "petrol" | "diesel" | "gas" | "electric" | "hybrid";
export type DriverStatus = "active" | "dismissed";
export type MaintenanceType = "planned_to" | "current_repair" | "major_repair";

export interface AuthUser {
  user_id: number;
  username: string;
  role: Role;
}

export interface TokenPair {
  access: string;
  // refresh is set in httpOnly cookie — not in JS
}

export interface Vehicle {
  id: number;
  license_plate: string;
  vin: string;
  make: string;
  model: string;
  year: number;
  fuel_type: FuelType;
  norm_consumption_summer: string;
  norm_consumption_winter: string;
  odometer: string;
  status: VehicleStatus;
  registered_at: string;
}

export interface VehicleWrite {
  license_plate: string;
  vin: string;
  make: string;
  model: string;
  year: number;
  fuel_type: FuelType;
  norm_consumption_summer: string;
  norm_consumption_winter: string;
  odometer?: string;
}

export interface Driver {
  id: number;
  full_name: string;
  personnel_number: string;
  date_of_birth: string;
  phone: string;
  license_category: string;
  license_number: string;
  license_issued_at: string;
  license_expires_at: string;
  status: DriverStatus;
  created_at: string;
}

export interface FuelingRecord {
  id: number;
  vehicle: number;
  vehicle_info: string;
  driver: number;
  driver_info: string;
  fueled_at: string;
  fuel_liters: string;
  price_per_liter: string;
  total_cost: string;
  station_name: string;
  odometer_at_fueling: string;
  actual_consumption: string | null;
  deviation_pct: string | null;
  is_anomalous: boolean | null;
  created_at: string;
}

export interface FuelingRecordWrite {
  vehicle: number;
  driver: number;
  fueled_at: string;
  fuel_liters: string;
  price_per_liter: string;
  station_name: string;
  odometer_at_fueling: string;
}

export interface MaintenanceRecord {
  id: number;
  vehicle: number;
  vehicle_info: string;
  record_type: MaintenanceType;
  opened_at: string;
  closed_at: string | null;
  is_open: boolean;
  fault_description: string;
  work_performed: string;
  contractor_name: string;
  parts_cost: string;
  labor_cost: string;
  total_cost: string;
  odometer_at_closing: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count?: number;  // CursorPagination does not return count
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DashboardStats {
  vehicles: {
    total: number;
    active: number;
    in_maintenance: number;
    decommissioned: number;
  };
  drivers: {
    total: number;
    active: number;
  };
  recent_anomalies_30d: number;
  open_maintenance_count: number;
}

export interface FuelReportSummary {
  total_liters: string | null;
  total_cost: string | null;
  avg_consumption: string | null;
  anomaly_count: number;
  record_count: number;
}

export interface FuelReport {
  summary: FuelReportSummary;
  by_month: Array<{
    month: string;
    liters: string;
    cost: string;
    records: number;
  }>;
  by_vehicle: Array<{
    vehicle_id: number;
    vehicle__license_plate: string;
    vehicle__make: string;
    vehicle__model: string;
    liters: string;
    cost: string;
    avg_consumption: string | null;
    anomaly_count: number;
  }>;
}
