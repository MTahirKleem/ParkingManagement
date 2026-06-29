import { beforeEach, describe, expect, it, vi } from "vitest";

const { api } = vi.hoisted(() => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("@/lib/api", () => ({ api }));

import { authService } from "@/services/auth.service";
import { parkingService } from "@/services/parking.service";
import { usersService } from "@/services/users.service";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("auth service", () => {
  it("calls the backend auth endpoints", async () => {
    api.post.mockResolvedValue({ data: "login" });
    api.get.mockResolvedValue({ data: "me" });

    await authService.login("admin@example.com", "Admin@123");
    await authService.getCurrentUser();
    await authService.refreshToken();

    expect(api.post).toHaveBeenNthCalledWith(1, "/auth/login", {
      email: "admin@example.com",
      password: "Admin@123",
    });
    expect(api.get).toHaveBeenCalledWith("/auth/me");
    expect(api.post).toHaveBeenNthCalledWith(2, "/auth/refresh");
  });
});

describe("parking service", () => {
  it("uses every Phase 8 parking endpoint", async () => {
    api.post.mockResolvedValue({ data: {} });
    api.get.mockResolvedValue({ data: {} });
    api.put.mockResolvedValue({ data: {} });
    api.delete.mockResolvedValue({ data: {} });

    await parkingService.createEntry({
      plate_number: "LEA-1",
      vehicle_type: "bike",
    });
    await parkingService.completeExit("record", true);
    await parkingService.getActiveVehicles({ page: 1 });
    await parkingService.getParkingHistory({ status: "completed" });
    await parkingService.searchParkingRecords({ plate_number: "LEA-1" });
    await parkingService.getParkingRecordById("record");
    await parkingService.updateParkingRecord("record", { slot: "A-1" });
    await parkingService.deleteParkingRecord("record");

    expect(api.post).toHaveBeenCalledWith("/parking/entry", {
      plate_number: "LEA-1",
      vehicle_type: "bike",
    });
    expect(api.post).toHaveBeenCalledWith("/parking/record/exit", {
      payment_received: true,
    });
    expect(api.get).toHaveBeenCalledWith("/parking/active", {
      params: { page: 1 },
    });
    expect(api.get).toHaveBeenCalledWith("/parking/history", {
      params: { status: "completed" },
    });
    expect(api.get).toHaveBeenCalledWith("/parking/search", {
      params: { plate_number: "LEA-1" },
    });
    expect(api.put).toHaveBeenCalledWith("/parking/record", { slot: "A-1" });
    expect(api.delete).toHaveBeenCalledWith("/parking/record");
  });
});

describe("users service", () => {
  it("uses every Phase 7 user endpoint", async () => {
    api.post.mockResolvedValue({ data: {} });
    api.get.mockResolvedValue({ data: {} });
    api.put.mockResolvedValue({ data: {} });
    api.delete.mockResolvedValue({ data: {} });

    await usersService.getUsers({ page: 1, role: "guard" });
    await usersService.createGuard({
      name: "Guard",
      email: "guard@example.com",
      password: "Guard@123",
      role: "guard",
    });
    await usersService.getUserById("user");
    await usersService.updateUser("user", { name: "Updated" });
    await usersService.deleteUser("user");
    await usersService.resetPassword("user", "NewGuard@123");

    expect(api.get).toHaveBeenCalledWith("/users", {
      params: { page: 1, role: "guard" },
    });
    expect(api.post).toHaveBeenCalledWith("/users/user/reset-password", {
      new_password: "NewGuard@123",
    });
  });
});
