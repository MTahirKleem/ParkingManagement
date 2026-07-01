"use client";

import { Eye, RefreshCw, Search } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { PaginationControls } from "@/components/common/PaginationControls";
import { CompleteExitDialog } from "@/components/parking/CompleteExitDialog";
import { ParkingStatusBadge } from "@/components/parking/ParkingStatusBadge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useActiveVehicles } from "@/hooks/useParking";
import { getApiErrorMessage } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import type { VehicleType } from "@/types/parking";

export function ActiveVehiclesTable() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [vehicleType, setVehicleType] = useState<VehicleType | undefined>();
  const query = useActiveVehicles({
    page,
    limit: 20,
    search: search || undefined,
    vehicle_type: vehicleType,
  });

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-3 p-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute top-2.5 left-3 size-4 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search plate number"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
          />
        </div>
        <Select
          value={vehicleType ?? "all"}
          onValueChange={(value) => {
            setVehicleType(value === "all" ? undefined : (value as VehicleType));
            setPage(1);
          }}
        >
          <SelectTrigger className="w-full sm:w-44">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All vehicle types</SelectItem>
            <SelectItem value="bike">Bike</SelectItem>
            <SelectItem value="car">Car</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={() => query.refetch()} variant="outline">
          <RefreshCw />
          Refresh
        </Button>
      </Card>
      {query.isLoading ? <LoadingState rows={6} /> : null}
      {query.isError ? (
        <ErrorState message={getApiErrorMessage(query.error)} onRetry={() => query.refetch()} />
      ) : null}
      {query.data && query.data.data.length === 0 ? (
        <EmptyState title="No active vehicles found." description="Create a vehicle entry or adjust your filters." />
      ) : null}
      {query.data && query.data.data.length > 0 ? (
        <Card className="overflow-hidden py-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Plate number</TableHead>
                  <TableHead>Vehicle type</TableHead>
                  <TableHead>Slot</TableHead>
                  <TableHead>Entry time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created by</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {query.data.data.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell className="font-mono font-semibold">{record.plate_number}</TableCell>
                    <TableCell className="capitalize">{record.vehicle_type}</TableCell>
                    <TableCell>{record.slot || "—"}</TableCell>
                    <TableCell>{formatDate(record.entry_time)}</TableCell>
                    <TableCell><ParkingStatusBadge status={record.status} /></TableCell>
                    <TableCell className="font-mono text-xs">{record.created_by.slice(-8)}</TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-2">
                        <Link
                          className={buttonVariants({ size: "sm", variant: "outline" })}
                          href={`/parking/${record.id}`}
                        >
                          <Eye />
                          Details
                        </Link>
                        <CompleteExitDialog record={record} />
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <PaginationControls
            page={query.data.pagination.page}
            pages={query.data.pagination.pages}
            total={query.data.pagination.total}
            onPageChange={setPage}
          />
        </Card>
      ) : null}
    </div>
  );
}
