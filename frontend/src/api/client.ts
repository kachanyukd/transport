import axios from "axios";

// Access token is kept only in memory — never in localStorage/sessionStorage.
let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: true, // send/receive the httpOnly refresh-token cookie
});

// Attach the access token to every outgoing request
apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// On 401, try a silent refresh once, then retry the original request
let isRefreshing = false;
let pendingQueue: Array<() => void> = [];

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        // Wait for the ongoing refresh to finish, then retry
        await new Promise<void>((resolve) => pendingQueue.push(resolve));
        return apiClient(originalRequest);
      }

      isRefreshing = true;
      try {
        // Dynamic import avoids a circular import with ./auth
        const { refreshToken } = await import("./auth");
        const newAccess = await refreshToken();
        setAccessToken(newAccess);
        pendingQueue.forEach((resolve) => resolve());
        pendingQueue = [];
        return apiClient(originalRequest);
      } catch (refreshError) {
        setAccessToken(null);
        pendingQueue = [];
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
