import type { ApiError } from "@/types/api";

export const ACCESS_TOKEN_KEY = "parkingmanagement_access_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
}

const friendlyErrors: Record<string, string> = {
  INVALID_CREDENTIALS: "The email or password you entered is incorrect.",
  USER_INACTIVE: "This account is inactive. Contact an administrator.",
  UNAUTHORIZED: "Your session has expired. Please sign in again.",
  FORBIDDEN: "You do not have permission to perform this action.",
  DUPLICATE_ACTIVE_VEHICLE: "This vehicle is already active in parking.",
  PARKING_RECORD_NOT_FOUND: "This parking record could not be found.",
  VEHICLE_ALREADY_COMPLETED: "This vehicle has already been completed.",
  PRICING_RULE_NOT_FOUND: "No active pricing rule is available.",
  VALIDATION_ERROR: "Please review the highlighted information.",
};

type ErrorWithResponse = {
  response?: { data?: Partial<ApiError> };
  message?: string;
};

export function getApiErrorMessage(error: unknown): string {
  const candidate =
    typeof error === "object" && error !== null
      ? (error as ErrorWithResponse)
      : undefined;
  const apiError = candidate?.response?.data;

  if (apiError?.error_code && friendlyErrors[apiError.error_code]) {
    return friendlyErrors[apiError.error_code];
  }
  if (apiError?.message) return apiError.message;
  if (candidate?.message) return candidate.message;
  return "Something went wrong. Please try again.";
}
