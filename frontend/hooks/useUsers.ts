"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { usersService } from "@/services/users.service";
import type {
  CreateGuardRequest,
  UpdateUserRequest,
  UsersQuery,
} from "@/types/user";

export const usersKey = (filters: UsersQuery) => ["users", filters] as const;

export function useUsers(filters: UsersQuery) {
  return useQuery({
    queryKey: usersKey(filters),
    queryFn: () => usersService.getUsers(filters),
  });
}

export function useCreateGuard() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateGuardRequest) =>
      usersService.createGuard(data),
    onSuccess: () => client.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateUser() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: string;
      data: UpdateUserRequest;
    }) => usersService.updateUser(userId, data),
    onSuccess: () => client.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useDeleteUser() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => usersService.deleteUser(userId),
    onSuccess: () => client.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({
      userId,
      newPassword,
    }: {
      userId: string;
      newPassword: string;
    }) => usersService.resetPassword(userId, newPassword),
  });
}
