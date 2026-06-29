export type UserRole = "admin" | "guard";
export type UserStatus = "active" | "inactive" | "deleted";

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  role: UserRole;
  status: UserStatus;
  last_login_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type LoginData = {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
};

export type RefreshTokenData = {
  access_token: string;
  token_type: "bearer";
};
