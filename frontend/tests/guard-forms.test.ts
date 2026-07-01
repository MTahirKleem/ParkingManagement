import { describe, expect, it } from "vitest";

import {
  createGuardSchema,
  updateGuardSchema,
} from "@/components/users/GuardForm";
import { resetPasswordSchema } from "@/components/users/ResetPasswordDialog";

describe("guard form schemas", () => {
  it("requires a valid guard account", () => {
    expect(
      createGuardSchema.safeParse({
        name: "",
        email: "invalid",
        phone: "",
        password: "short",
      }).success,
    ).toBe(false);

    expect(
      createGuardSchema.safeParse({
        name: "Gate Guard",
        email: "guard@example.com",
        phone: "+92 300 1234567",
        password: "Secure@123",
      }).success,
    ).toBe(true);
  });

  it("validates editable guard fields", () => {
    expect(
      updateGuardSchema.safeParse({
        name: "Gate Guard",
        phone: "",
        status: "active",
      }).success,
    ).toBe(true);

    expect(
      updateGuardSchema.safeParse({
        name: "",
        phone: "",
        status: "active",
      }).success,
    ).toBe(false);
  });

  it("requires an eight-character reset password", () => {
    expect(resetPasswordSchema.safeParse({ password: "short" }).success).toBe(
      false,
    );
    expect(
      resetPasswordSchema.safeParse({ password: "NewPass@123" }).success,
    ).toBe(true);
  });
});
