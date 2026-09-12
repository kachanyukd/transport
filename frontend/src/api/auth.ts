import { apiClient } from "./client";
import type { AuthUser } from "../types";

interface LoginResponse {
  access: string;
}

interface JwtPayload {
  user_id: number;
  username: string;
  role: string;
  exp: number;
}

function parseJwt(token: string): JwtPayload {
  const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  const json = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );
  return JSON.parse(json) as JwtPayload;
}

export async function login(username: string, password: string): Promise<{ access: string; user: AuthUser }> {
  const response = await apiClient.post<LoginResponse>("/auth/token/", {
    username,
    password,
  });
  const { access } = response.data;
  const payload = parseJwt(access);
  const user: AuthUser = {
    user_id: payload.user_id,
    username: payload.username,
    role: payload.role as AuthUser["role"],
  };
  return { access, user };
}

export async function logout(): Promise<void> {
  // Blacklist the refresh token (sends the httpOnly cookie automatically)
  await apiClient.post("/auth/token/blacklist/", {});
}

export async function refreshToken(): Promise<string> {
  const response = await apiClient.post<LoginResponse>("/auth/token/refresh/", {});
  return response.data.access;
}
