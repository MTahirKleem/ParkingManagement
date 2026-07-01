"use client";

import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/lib/auth";
import { authService } from "@/services/auth.service";
import type { AuthUser } from "@/types/auth";

export type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  logout: () => void;
  refreshCurrentUser: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    clearAccessToken();
    authService.logout();
    setToken(null);
    setUser(null);
  }, []);

  const refreshCurrentUser = useCallback(async () => {
    const storedToken = getAccessToken();
    if (!storedToken) {
      logout();
      return;
    }
    try {
      const response = await authService.getCurrentUser();
      setToken(storedToken);
      setUser(response.data);
    } catch {
      logout();
      throw new Error("Unable to load the current user.");
    }
  }, [logout]);

  useEffect(() => {
    const hydrate = async () => {
      try {
        await refreshCurrentUser();
      } catch {
        // The interceptor and logout path already clear invalid sessions.
      } finally {
        setIsLoading(false);
      }
    };
    void hydrate();
  }, [refreshCurrentUser]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authService.login(email, password);
    setAccessToken(response.data.access_token);
    setToken(response.data.access_token);
    setUser(response.data.user);
    return response.data.user;
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      logout,
      refreshCurrentUser,
    }),
    [isLoading, login, logout, refreshCurrentUser, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
