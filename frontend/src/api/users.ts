import { apiClient } from "./client";

export interface AppUser {
  id: number;
  username: string;
  email: string;
  role: "admin" | "manager" | "dispatcher" | "driver";
  is_active: boolean;
  created_at: string;
  driver: number | null;
}

export interface UserWrite {
  username: string;
  email: string;
  role: "admin" | "manager" | "dispatcher" | "driver";
  password: string;
  is_active?: boolean;
}

export async function listUsers(): Promise<AppUser[]> {
  // UserViewSet is not paginated (no pagination_class set), returns plain array
  const res = await apiClient.get<AppUser[]>("/users/");
  return res.data;
}

export async function createUser(data: UserWrite): Promise<AppUser> {
  const res = await apiClient.post<AppUser>("/users/", data);
  return res.data;
}

export async function updateUser(id: number, data: Partial<UserWrite>): Promise<AppUser> {
  const res = await apiClient.patch<AppUser>(`/users/${id}/`, data);
  return res.data;
}

export async function deactivateUser(id: number): Promise<void> {
  await apiClient.delete(`/users/${id}/`);
}
