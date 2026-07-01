import { api } from "@/lib/api";
import type { ApiResponse } from "@/types/api";
import type {
  AuthUser,
  LoginData,
  RefreshTokenData,
} from "@/types/auth";

export const authService = {
  async login(email: string, password: string): Promise<ApiResponse<LoginData>> {
    const response = await api.post<ApiResponse<LoginData>>("/auth/login", {
      email,
      password,
    });
    return response.data;
  },

  async getCurrentUser(): Promise<ApiResponse<AuthUser>> {
    const response = await api.get<ApiResponse<AuthUser>>("/auth/me");
    return response.data;
  },

  async refreshToken(): Promise<ApiResponse<RefreshTokenData>> {
    const response =
      await api.post<ApiResponse<RefreshTokenData>>("/auth/refresh");
    return response.data;
  },

  logout(): void {
    // Token and state cleanup is coordinated by AuthProvider.
  },
};
