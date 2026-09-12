/**
 * AuthContext — manages authentication state.
 *
 * Access token is stored ONLY in React Context memory.
 * It is never written to localStorage or sessionStorage.
 * The refresh token is in an httpOnly cookie (set by the backend).
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { login as apiLogin, logout as apiLogout, refreshToken } from "../api/auth";
import { setAccessToken } from "../api/client";
import type { AuthUser } from "../types";

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount: attempt silent refresh using httpOnly cookie
  useEffect(() => {
    (async () => {
      try {
        const access = await refreshToken();
        setAccessToken(access);
        // Decode user from token payload
        const payload = parseJwt(access);
        setUser({
          user_id: payload.user_id,
          username: payload.username,
          role: payload.role as AuthUser["role"],
        });
      } catch {
        // No valid refresh token — user is not authenticated
        setUser(null);
        setAccessToken(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const { access, user: authUser } = await apiLogin(username, password);
    setAccessToken(access);
    setUser(authUser);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      // Ignore errors on logout
    } finally {
      setAccessToken(null);
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

// Minimal JWT decoder — does not verify signature (server does that)
interface JwtPayload {
  user_id: number;
  username: string;
  role: string;
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
