import { apiClient } from "./client";
import type { DashboardStats, FuelReport } from "../types";

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>("/dashboard/");
  return response.data;
}

export async function getFuelReport(params?: Record<string, string>): Promise<FuelReport> {
  const response = await apiClient.get<FuelReport>("/reports/fuel/", { params });
  return response.data;
}

export async function getMaintenanceReport(
  params?: Record<string, string>
): Promise<Record<string, unknown>> {
  const response = await apiClient.get<Record<string, unknown>>("/reports/maintenance/", {
    params,
  });
  return response.data;
}

export async function getMileageReport(
  params?: Record<string, string>
): Promise<Record<string, unknown>> {
  const response = await apiClient.get<Record<string, unknown>>("/reports/mileage/", { params });
  return response.data;
}

export async function getSummaryReport(
  params?: Record<string, string>
): Promise<Record<string, unknown>> {
  const response = await apiClient.get<Record<string, unknown>>("/reports/summary/", { params });
  return response.data;
}
