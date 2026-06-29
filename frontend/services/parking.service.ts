import { api } from "@/lib/api";
import type {
  ApiResponse,
  PaginatedApiResponse,
} from "@/types/api";
import type {
  ActiveVehiclesQuery,
  ParkingEntryRequest,
  ParkingHistoryQuery,
  ParkingRecord,
  ParkingSearchQuery,
  ParkingUpdateRequest,
} from "@/types/parking";

export const parkingService = {
  async createEntry(
    data: ParkingEntryRequest,
  ): Promise<ApiResponse<ParkingRecord>> {
    const response = await api.post<ApiResponse<ParkingRecord>>(
      "/parking/entry",
      data,
    );
    return response.data;
  },

  async completeExit(
    recordId: string,
    paymentReceived: boolean,
  ): Promise<ApiResponse<ParkingRecord>> {
    const response = await api.post<ApiResponse<ParkingRecord>>(
      `/parking/${recordId}/exit`,
      { payment_received: paymentReceived },
    );
    return response.data;
  },

  async getActiveVehicles(
    params: ActiveVehiclesQuery,
  ): Promise<PaginatedApiResponse<ParkingRecord>> {
    const response = await api.get<PaginatedApiResponse<ParkingRecord>>(
      "/parking/active",
      { params },
    );
    return response.data;
  },

  async getParkingHistory(
    params: ParkingHistoryQuery,
  ): Promise<PaginatedApiResponse<ParkingRecord>> {
    const response = await api.get<PaginatedApiResponse<ParkingRecord>>(
      "/parking/history",
      { params },
    );
    return response.data;
  },

  async searchParkingRecords(
    params: ParkingSearchQuery,
  ): Promise<ApiResponse<ParkingRecord[]>> {
    const response = await api.get<ApiResponse<ParkingRecord[]>>(
      "/parking/search",
      { params },
    );
    return response.data;
  },

  async getParkingRecordById(
    recordId: string,
  ): Promise<ApiResponse<ParkingRecord>> {
    const response = await api.get<ApiResponse<ParkingRecord>>(
      `/parking/${recordId}`,
    );
    return response.data;
  },

  async updateParkingRecord(
    recordId: string,
    data: ParkingUpdateRequest,
  ): Promise<ApiResponse<ParkingRecord>> {
    const response = await api.put<ApiResponse<ParkingRecord>>(
      `/parking/${recordId}`,
      data,
    );
    return response.data;
  },

  async deleteParkingRecord(
    recordId: string,
  ): Promise<ApiResponse<{ id: string; status: "deleted" }>> {
    const response = await api.delete<
      ApiResponse<{ id: string; status: "deleted" }>
    >(`/parking/${recordId}`);
    return response.data;
  },
};
