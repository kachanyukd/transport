import { apiClient } from "./client";
import type { Vehicle, VehicleWrite, PaginatedResponse } from "../types";

export async function listVehicles(params?: Record<string, string>): Promise<PaginatedResponse<Vehicle>> {
  const response = await apiClient.get<PaginatedResponse<Vehicle>>("/vehicles/", { params });
  return response.data;
}

export async function getVehicle(id: number): Promise<Vehicle> {
  const response = await apiClient.get<Vehicle>(`/vehicles/${id}/`);
  return response.data;
}

export async function createVehicle(data: VehicleWrite): Promise<Vehicle> {
  const response = await apiClient.post<Vehicle>("/vehicles/", data);
  return response.data;
}

export async function updateVehicle(id: number, data: Partial<VehicleWrite>): Promise<Vehicle> {
  const response = await apiClient.patch<Vehicle>(`/vehicles/${id}/`, data);
  return response.data;
}

export async function decommissionVehicle(id: number): Promise<Vehicle> {
  const response = await apiClient.post<Vehicle>(`/vehicles/${id}/decommission/`);
  return response.data;
}
