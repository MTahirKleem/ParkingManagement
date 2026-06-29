import { describe, expect, it } from "vitest";

import {
  clearAccessToken,
  getAccessToken,
  getApiErrorMessage,
  setAccessToken,
} from "@/lib/auth";

describe("auth storage", () => {
  it("stores and clears the MVP access token", () => {
    setAccessToken("abc");
    expect(getAccessToken()).toBe("abc");

    clearAccessToken();
    expect(getAccessToken()).toBeNull();
  });
});

describe("backend error messages", () => {
  it.each([
    ["DUPLICATE_ACTIVE_VEHICLE", "This vehicle is already active in parking."],
    ["VEHICLE_ALREADY_COMPLETED", "This vehicle has already been completed."],
    ["FORBIDDEN", "You do not have permission to perform this action."],
  ])("maps %s to a helpful message", (errorCode, expected) => {
    expect(
      getApiErrorMessage({
        response: {
          data: {
            success: false,
            message: "Backend message",
            error_code: errorCode,
          },
        },
      }),
    ).toBe(expected);
  });

  it("falls back to the backend message", () => {
    expect(
      getApiErrorMessage({
        response: {
          data: {
            success: false,
            message: "Pricing is unavailable",
            error_code: "UNKNOWN_BACKEND_ERROR",
          },
        },
      }),
    ).toBe("Pricing is unavailable");
  });
});
