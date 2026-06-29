"use client";

import { Eye, Search } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { ParkingStatusBadge } from "@/components/parking/ParkingStatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { useParkingSearch } from "@/hooks/useParking";
import { getApiErrorMessage } from "@/lib/auth";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { ParkingSearchQuery, ParkingStatus } from "@/types/parking";

export function ParkingSearchForm() {
  const [plate, setPlate] = useState("");
  const [status, setStatus] = useState<
    Exclude<ParkingStatus, "deleted"> | undefined
  >();
  const [filters, setFilters] = useState<ParkingSearchQuery | null>(null);
  const query = useParkingSearch(filters);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!plate.trim()) return;
    setFilters({ plate_number: plate.trim(), status });
  };

  return (
    <div className="space-y-5">
      <Card>
        <CardContent>
          <form className="grid gap-4 sm:grid-cols-[1fr_220px_auto]" onSubmit={submit}>
            <div className="space-y-2">
              <Label htmlFor="search-plate">Plate number</Label>
              <Input
                id="search-plate"
                className="font-mono uppercase"
                placeholder="LEA-1234, LEA 1234, or LEA1234"
                value={plate}
                onChange={(event) => setPlate(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Status (optional)</Label>
              <Select
                value={status ?? "all"}
                onValueChange={(value) =>
                  setStatus(
                    value === "all"
                      ? undefined
                      : (value as Exclude<ParkingStatus, "deleted">),
                  )
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Any visible status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button className="self-end" disabled={!plate.trim()}>
              <Search />
              Search
            </Button>
          </form>
        </CardContent>
      </Card>
      {query.isLoading ? <LoadingState rows={4} /> : null}
      {query.isError ? (
        <ErrorState message={getApiErrorMessage(query.error)} onRetry={() => query.refetch()} />
      ) : null}
      {filters && query.data?.data.length === 0 ? (
        <EmptyState title="No search results found." description="Try another plate format or status." />
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
                  <TableHead>Exit time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Fee</TableHead>
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
                    <TableCell><ParkingStatusBadge status={record.status} /></TableCell>
                    <TableCell>{formatCurrency(record.fee, record.currency)}</TableCell>
                    <TableCell className="text-right">
                      <Button nativeButton={false} size="sm" variant="outline" render={<Link href={`/parking/${record.id}`} />}>
                        <Eye />
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      ) : null}
    </div>
  );
}
