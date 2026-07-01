"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { parkingService } from "@/services/parking.service";
import type {
  ActiveVehiclesQuery,
  ParkingEntryRequest,
  ParkingHistoryQuery,
  ParkingSearchQuery,
  ParkingUpdateRequest,
} from "@/types/parking";

export const parkingKeys = {
  active: (filters: ActiveVehiclesQuery) =>
    ["active-vehicles", filters] as const,
  history: (filters: ParkingHistoryQuery) =>
    ["parking-history", filters] as const,
  record: (id: string) => ["parking-record", id] as const,
  search: (filters: ParkingSearchQuery) =>
    ["parking-search", filters] as const,
};

export function useActiveVehicles(filters: ActiveVehiclesQuery) {
  return useQuery({
    queryKey: parkingKeys.active(filters),
    queryFn: () => parkingService.getActiveVehicles(filters),
  });
}

export function useParkingHistory(filters: ParkingHistoryQuery) {
  return useQuery({
    queryKey: parkingKeys.history(filters),
    queryFn: () => parkingService.getParkingHistory(filters),
  });
}

export function useParkingSearch(filters: ParkingSearchQuery | null) {
  return useQuery({
    queryKey: parkingKeys.search(filters ?? { plate_number: "" }),
    queryFn: () => parkingService.searchParkingRecords(filters!),
    enabled: Boolean(filters?.plate_number),
  });
}

export function useParkingRecord(id: string) {
  return useQuery({
    queryKey: parkingKeys.record(id),
    queryFn: () => parkingService.getParkingRecordById(id),
    enabled: Boolean(id),
  });
}

export function useCreateEntry() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (data: ParkingEntryRequest) =>
      parkingService.createEntry(data),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["active-vehicles"] });
      await client.invalidateQueries({ queryKey: ["parking-history"] });
    },
  });
}

export function useCompleteExit() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      recordId,
      paymentReceived,
    }: {
      recordId: string;
      paymentReceived: boolean;
    }) => parkingService.completeExit(recordId, paymentReceived),
    onSuccess: async (_, variables) => {
      await client.invalidateQueries({ queryKey: ["parking-history"] });
      await client.invalidateQueries({
        queryKey: parkingKeys.record(variables.recordId),
      });
    },
  });
}

export function useUpdateParkingRecord() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({
      recordId,
      data,
    }: {
      recordId: string;
      data: ParkingUpdateRequest;
    }) => parkingService.updateParkingRecord(recordId, data),
    onSuccess: async (_, variables) => {
      await client.invalidateQueries({ queryKey: ["parking-history"] });
      await client.invalidateQueries({ queryKey: ["active-vehicles"] });
      await client.invalidateQueries({
        queryKey: parkingKeys.record(variables.recordId),
      });
    },
  });
}

export function useDeleteParkingRecord() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (recordId: string) =>
      parkingService.deleteParkingRecord(recordId),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["parking-history"] });
      await client.invalidateQueries({ queryKey: ["active-vehicles"] });
    },
  });
}
