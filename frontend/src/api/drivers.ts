import { apiClient } from "./client";
import type { Driver, PaginatedResponse } from "../types";

export async function listDrivers(params?: Record<string, string>): Promise<PaginatedResponse<Driver>> {
  const response = await apiClient.get<PaginatedResponse<Driver>>("/drivers/", { params });
  return response.data;
}

export async function getDriver(id: number): Promise<Driver> {
  const response = await apiClient.get<Driver>(`/drivers/${id}/`);
  return response.data;
}

export async function createDriver(data: Partial<Driver>): Promise<Driver> {
  const response = await apiClient.post<Driver>("/drivers/", data);
  return response.data;
}

export async function updateDriver(id: number, data: Partial<Driver>): Promise<Driver> {
  const response = await apiClient.patch<Driver>(`/drivers/${id}/`, data);
  return response.data;
}

export async function assignVehicle(
  driverId: number,
  vehicleId: number
): Promise<{ id: number; vehicle: number; driver: number; assigned_at: string }> {
  const response = await apiClient.post(`/drivers/${driverId}/assign/`, {
    vehicle_id: vehicleId,
  });
  return response.data;
}
