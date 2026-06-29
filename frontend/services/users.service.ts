import { api } from "@/lib/api";
import type {
  ApiResponse,
  PaginatedApiResponse,
} from "@/types/api";
import type {
  CreateGuardRequest,
  UpdateUserRequest,
  User,
  UsersQuery,
} from "@/types/user";

export const usersService = {
  async getUsers(
    params: UsersQuery,
  ): Promise<PaginatedApiResponse<User>> {
    const response = await api.get<PaginatedApiResponse<User>>("/users", {
      params,
    });
    return response.data;
  },

  async createGuard(
    data: CreateGuardRequest,
  ): Promise<ApiResponse<User>> {
    const response = await api.post<ApiResponse<User>>("/users", data);
    return response.data;
  },

  async getUserById(userId: string): Promise<ApiResponse<User>> {
    const response = await api.get<ApiResponse<User>>(`/users/${userId}`);
    return response.data;
  },

  async updateUser(
    userId: string,
    data: UpdateUserRequest,
  ): Promise<ApiResponse<User>> {
    const response = await api.put<ApiResponse<User>>(
      `/users/${userId}`,
      data,
    );
    return response.data;
  },

  async deleteUser(
    userId: string,
  ): Promise<ApiResponse<{ id: string; status: "deleted" }>> {
    const response = await api.delete<
      ApiResponse<{ id: string; status: "deleted" }>
    >(`/users/${userId}`);
    return response.data;
  },

  async resetPassword(
    userId: string,
    newPassword: string,
  ): Promise<ApiResponse<{ id: string }>> {
    const response = await api.post<ApiResponse<{ id: string }>>(
      `/users/${userId}/reset-password`,
      { new_password: newPassword },
    );
    return response.data;
  },
};
