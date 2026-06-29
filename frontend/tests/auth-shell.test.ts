import { describe, expect, it } from "vitest";

import { getNavigation } from "@/components/layout/AppSidebar";
import { loginSchema } from "@/components/auth/LoginForm";

describe("login form validation", () => {
  it("requires a valid email and password", () => {
    expect(
      loginSchema.safeParse({ email: "bad", password: "" }).success,
    ).toBe(false);
    expect(
      loginSchema.safeParse({
        email: "admin@example.com",
        password: "Admin@123",
      }).success,
    ).toBe(true);
  });
});

describe("role navigation", () => {
  it("shows Guards only to administrators", () => {
    expect(getNavigation("admin").map((item) => item.label)).toContain(
      "Guards",
    );
    expect(getNavigation("guard").map((item) => item.label)).not.toContain(
      "Guards",
    );
  });

  it("keeps operational parking links for both roles", () => {
    for (const role of ["admin", "guard"] as const) {
      const labels = getNavigation(role).map((item) => item.label);
      expect(labels).toEqual(
        expect.arrayContaining([
          "Vehicle Entry",
          "Active Vehicles",
          "Search Parking",
          "Parking History",
        ]),
      );
    }
  });
});
