"use client";

import { Eye, RefreshCw, Search, Settings2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { PaginationControls } from "@/components/common/PaginationControls";
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
import { useAuth } from "@/hooks/useAuth";
import { useParkingHistory } from "@/hooks/useParking";
import { getApiErrorMessage } from "@/lib/auth";
import { formatCurrency, formatDate, formatDuration } from "@/lib/utils";
import type { ParkingStatus, VehicleType } from "@/types/parking";

export function ParkingHistoryTable() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<Exclude<ParkingStatus, "deleted"> | undefined>();
  const [vehicleType, setVehicleType] = useState<VehicleType | undefined>();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const query = useParkingHistory({
    page,
    limit: 20,
    search: search || undefined,
    status,
    vehicle_type: vehicleType,
    start_date: startDate || undefined,
    end_date: endDate || undefined,
  });

  return (
    <div className="space-y-4">
      <Card className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-6">
        <div className="relative xl:col-span-2">
          <Search className="absolute top-2.5 left-3 size-4 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search plate"
            value={search}
            onChange={(event) => { setSearch(event.target.value); setPage(1); }}
          />
        </div>
        <Select value={status ?? "all"} onValueChange={(value) => { setStatus(value === "all" ? undefined : value as Exclude<ParkingStatus, "deleted">); setPage(1); }}>
          <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={vehicleType ?? "all"} onValueChange={(value) => { setVehicleType(value === "all" ? undefined : value as VehicleType); setPage(1); }}>
          <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All vehicles</SelectItem>
            <SelectItem value="bike">Bike</SelectItem>
            <SelectItem value="car">Car</SelectItem>
          </SelectContent>
        </Select>
        <Input aria-label="Start date" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        <div className="flex gap-2">
          <Input aria-label="End date" type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
          <Button aria-label="Refresh history" onClick={() => query.refetch()} size="icon" variant="outline"><RefreshCw /></Button>
        </div>
      </Card>
      {query.isLoading ? <LoadingState rows={7} /> : null}
      {query.isError ? <ErrorState message={getApiErrorMessage(query.error)} onRetry={() => query.refetch()} /> : null}
      {query.data && query.data.data.length === 0 ? <EmptyState title="No parking history found." description="Adjust filters or create a vehicle entry." /> : null}
      {query.data && query.data.data.length > 0 ? (
        <Card className="overflow-hidden py-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Plate number</TableHead>
                  <TableHead>Vehicle</TableHead>
                  <TableHead>Slot</TableHead>
                  <TableHead>Entry</TableHead>
                  <TableHead>Exit</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Fee</TableHead>
                  <TableHead>Status</TableHead>
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
                    <TableCell>{formatDate(record.exit_time)}</TableCell>
                    <TableCell>{formatDuration(record.duration_minutes)}</TableCell>
                    <TableCell>{formatCurrency(record.fee, record.currency)}</TableCell>
                    <TableCell><ParkingStatusBadge status={record.status} /></TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-2">
                        <Link
                          className={buttonVariants({ size: "sm", variant: "outline" })}
                          href={`/parking/${record.id}`}
                        >
                          <Eye /> View
                        </Link>
                        {user?.role === "admin" ? (
                          <Link
                            className={buttonVariants({ size: "sm", variant: "ghost" })}
                            href={`/parking/${record.id}?edit=1`}
                          >
                            <Settings2 /> Manage
                          </Link>
                        ) : null}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <PaginationControls page={query.data.pagination.page} pages={query.data.pagination.pages} total={query.data.pagination.total} onPageChange={setPage} />
        </Card>
      ) : null}
    </div>
  );
}
