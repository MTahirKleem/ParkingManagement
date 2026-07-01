import type { UserRole, UserStatus } from "@/types/auth";

export type User = {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  role: UserRole;
  status: UserStatus;
  last_login_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type CreateGuardRequest = {
  name: string;
  email: string;
  phone?: string | null;
  password: string;
  role: "guard";
};

export type UpdateUserRequest = {
  name?: string;
  phone?: string | null;
  status?: UserStatus;
};

export type UsersQuery = {
  page?: number;
  limit?: number;
  role?: UserRole;
  status?: UserStatus;
  search?: string;
};
