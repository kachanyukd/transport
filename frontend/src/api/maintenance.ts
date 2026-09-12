import { apiClient } from "./client";
import type { MaintenanceRecord, PaginatedResponse } from "../types";

export async function listMaintenance(
  params?: Record<string, string>
): Promise<PaginatedResponse<MaintenanceRecord>> {
  const response = await apiClient.get<PaginatedResponse<MaintenanceRecord>>("/maintenance/", {
    params,
  });
  return response.data;
}

export async function getMaintenance(id: number): Promise<MaintenanceRecord> {
  const response = await apiClient.get<MaintenanceRecord>(`/maintenance/${id}/`);
  return response.data;
}

export async function createMaintenance(
  data: Partial<MaintenanceRecord>
): Promise<MaintenanceRecord> {
  const response = await apiClient.post<MaintenanceRecord>("/maintenance/", data);
  return response.data;
}

export async function updateMaintenance(
  id: number,
  data: Partial<MaintenanceRecord>
): Promise<MaintenanceRecord> {
  const response = await apiClient.patch<MaintenanceRecord>(`/maintenance/${id}/`, data);
  return response.data;
}

export async function closeMaintenance(
  id: number,
  data: { work_performed: string; parts_cost?: string; labor_cost?: string; odometer_at_closing?: string }
): Promise<MaintenanceRecord> {
  const response = await apiClient.post<MaintenanceRecord>(`/maintenance/${id}/close/`, data);
  return response.data;
}
