import { apiClient } from "./client";
import type { FuelingRecord, FuelingRecordWrite, PaginatedResponse } from "../types";

export async function listFuelingRecords(
  params?: Record<string, string>
): Promise<PaginatedResponse<FuelingRecord>> {
  const response = await apiClient.get<PaginatedResponse<FuelingRecord>>("/fuel-records/", {
    params,
  });
  return response.data;
}

export async function getFuelingRecord(id: number): Promise<FuelingRecord> {
  const response = await apiClient.get<FuelingRecord>(`/fuel-records/${id}/`);
  return response.data;
}

export async function createFuelingRecord(data: FuelingRecordWrite): Promise<FuelingRecord> {
  const response = await apiClient.post<FuelingRecord>("/fuel-records/", data);
  return response.data;
}
