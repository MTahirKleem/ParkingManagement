import { describe, expect, it } from "vitest";

import { vehicleEntrySchema } from "@/components/parking/VehicleEntryForm";
import {
  displayUserName,
  parkingUpdateSchema,
} from "@/components/parking/ParkingRecordDetails";

describe("parking forms", () => {
  it("requires a plate and supported vehicle type", () => {
    expect(
      vehicleEntrySchema.safeParse({
        plate_number: "",
        vehicle_type: "bike",
        slot: "",
      }).success,
    ).toBe(false);
    expect(
      vehicleEntrySchema.safeParse({
        plate_number: "LEA-1234",
        vehicle_type: "car",
        slot: "",
      }).success,
    ).toBe(true);
  });

  it("allows only editable parking fields", () => {
    expect(
      parkingUpdateSchema.safeParse({
        plate_number: "LEA-9999",
        vehicle_type: "car",
        slot: "B-5",
        notes: "Corrected",
      }).success,
    ).toBe(true);
    expect(
      parkingUpdateSchema.safeParse({
        plate_number: "",
        vehicle_type: "truck",
      }).success,
    ).toBe(false);
  });

  it("prefers a resolved user name and falls back to the audit ID", () => {
    expect(displayUserName("Entry Guard", "507f1f77bcf86cd799439011")).toBe(
      "Entry Guard",
    );
    expect(displayUserName(null, "507f1f77bcf86cd799439011")).toBe(
      "507f1f77bcf86cd799439011",
    );
    expect(displayUserName(null, null)).toBe("—");
  });
});
