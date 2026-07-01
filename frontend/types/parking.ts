export type VehicleType = "bike" | "car";
export type ParkingStatus = "active" | "completed" | "cancelled" | "deleted";

export type Payment = {
  method: "cash";
  received: boolean;
  received_by: string;
  received_by_name?: string | null;
  received_at: string;
};

export type PricingSnapshot = {
  pricing_rule_id: string;
  pricing_type: "fixed" | "hourly";
  fixed_rate: number | null;
  base_hours: number | null;
  base_fee: number | null;
  extra_hour_fee: number | null;
  grace_minutes: number;
};

export type ParkingRecord = {
  id: string;
  plate_number: string;
  normalized_plate_number: string;
  vehicle_type: VehicleType;
  slot: string | null;
  entry_time: string;
  exit_time: string | null;
  status: ParkingStatus;
  duration_minutes: number | null;
  fee: number | null;
  currency: "PKR";
  payment: Payment | null;
  pricing_snapshot: PricingSnapshot | null;
  ocr?: Record<string, unknown> | null;
  notes: string | null;
  created_by: string;
  created_by_name?: string | null;
  completed_by: string | null;
  completed_by_name?: string | null;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
};

export type ParkingEntryRequest = {
  plate_number: string;
  vehicle_type: VehicleType;
  slot?: string | null;
};

export type ParkingExitRequest = {
  payment_received: true;
};

export type ParkingUpdateRequest = {
  plate_number?: string;
  vehicle_type?: VehicleType;
  slot?: string | null;
  notes?: string | null;
};

export type ActiveVehiclesQuery = {
  page?: number;
  limit?: number;
  search?: string;
  vehicle_type?: VehicleType;
};

export type ParkingHistoryQuery = ActiveVehiclesQuery & {
  status?: Exclude<ParkingStatus, "deleted">;
  start_date?: string;
  end_date?: string;
};

export type ParkingSearchQuery = {
  plate_number: string;
  status?: Exclude<ParkingStatus, "deleted">;
};
