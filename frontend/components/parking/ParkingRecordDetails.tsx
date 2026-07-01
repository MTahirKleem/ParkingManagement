"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Pencil, Trash2 } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { ParkingStatusBadge } from "@/components/parking/ParkingStatusBadge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/hooks/useAuth";
import {
  useDeleteParkingRecord,
  useParkingRecord,
  useUpdateParkingRecord,
} from "@/hooks/useParking";
import { getApiErrorMessage } from "@/lib/auth";
import { formatCurrency, formatDate, formatDuration } from "@/lib/utils";
import type { ParkingRecord } from "@/types/parking";

export const parkingUpdateSchema = z.object({
  plate_number: z.string().trim().min(1, "Plate number is required."),
  vehicle_type: z.enum(["bike", "car"]),
  slot: z.string().optional(),
  notes: z.string().optional(),
});

type UpdateValues = z.infer<typeof parkingUpdateSchema>;

function Detail({ label, value, mono = false }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{label}</p>
      <div className={mono ? "font-mono text-sm" : "text-sm font-medium"}>{value || "—"}</div>
    </div>
  );
}

function EditDialog({ record, defaultOpen }: { record: ParkingRecord; defaultOpen: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const mutation = useUpdateParkingRecord();
  const { register, control, handleSubmit } = useForm<UpdateValues>({
    resolver: zodResolver(parkingUpdateSchema),
    defaultValues: {
      plate_number: record.plate_number,
      vehicle_type: record.vehicle_type,
      slot: record.slot ?? "",
      notes: record.notes ?? "",
    },
  });
  const submit = async (values: UpdateValues) => {
    try {
      await mutation.mutateAsync({
        recordId: record.id,
        data: { ...values, slot: values.slot || null, notes: values.notes || null },
      });
      toast.success("Parking record updated");
      setOpen(false);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="outline" />}><Pencil /> Edit record</DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit parking record</DialogTitle>
          <DialogDescription>Only correction fields are available in the MVP.</DialogDescription>
        </DialogHeader>
        <form className="space-y-4" onSubmit={handleSubmit(submit)}>
          <div className="space-y-2"><Label htmlFor="edit-plate-number">Plate number</Label><Input id="edit-plate-number" {...register("plate_number")} /></div>
          <div className="space-y-2">
            <Label htmlFor="edit-vehicle-type">Vehicle type</Label>
            <Controller name="vehicle_type" control={control} render={({ field }) => (
              <Select value={field.value} onValueChange={field.onChange}>
                <SelectTrigger className="w-full" id="edit-vehicle-type"><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="bike">Bike</SelectItem><SelectItem value="car">Car</SelectItem></SelectContent>
              </Select>
            )} />
          </div>
          <div className="space-y-2"><Label htmlFor="edit-slot">Slot</Label><Input id="edit-slot" {...register("slot")} /></div>
          <div className="space-y-2"><Label htmlFor="edit-notes">Notes</Label><Textarea id="edit-notes" {...register("notes")} /></div>
          {mutation.error ? <p className="text-sm text-destructive">{getApiErrorMessage(mutation.error)}</p> : null}
          <DialogFooter>
            <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? <Loader2 className="animate-spin" /> : <Pencil />} Save changes</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function ParkingRecordDetails({ id }: { id: string }) {
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = useParkingRecord(id);
  const deletion = useDeleteParkingRecord();

  useEffect(() => {
    if (query.isError) toast.error(getApiErrorMessage(query.error));
  }, [query.error, query.isError]);

  if (query.isLoading) return <LoadingState rows={8} />;
  if (query.isError || !query.data) return <ErrorState message={getApiErrorMessage(query.error)} onRetry={() => query.refetch()} />;
  const record = query.data.data;

  const remove = async () => {
    try {
      await deletion.mutateAsync(record.id);
      toast.success("Parking record deleted");
      router.replace("/parking/history");
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="font-mono text-2xl font-semibold">{record.plate_number}</h1>
          <ParkingStatusBadge status={record.status} />
        </div>
        {user?.role === "admin" ? (
          <div className="flex gap-2">
            <EditDialog record={record} defaultOpen={searchParams.get("edit") === "1"} />
            <AlertDialog>
              <AlertDialogTrigger render={<Button variant="destructive" />}><Trash2 /> Delete</AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader><AlertDialogTitle>Delete this parking record?</AlertDialogTitle><AlertDialogDescription>This is a soft delete. The record will disappear from normal parking views.</AlertDialogDescription></AlertDialogHeader>
                <AlertDialogFooter><AlertDialogCancel>Cancel</AlertDialogCancel><AlertDialogAction variant="destructive" onClick={remove}>Delete record</AlertDialogAction></AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        ) : null}
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardHeader><CardTitle>Parking details</CardTitle></CardHeader>
          <CardContent className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Detail label="Normalized plate" value={record.normalized_plate_number} mono />
            <Detail label="Vehicle type" value={record.vehicle_type} />
            <Detail label="Slot" value={record.slot} />
            <Detail label="Entry time" value={formatDate(record.entry_time)} />
            <Detail label="Exit time" value={formatDate(record.exit_time)} />
            <Detail label="Duration" value={formatDuration(record.duration_minutes)} />
            <Detail label="Fee" value={formatCurrency(record.fee, record.currency)} />
            <Detail label="Currency" value={record.currency} />
            <Detail label="Created by" value={record.created_by} mono />
            <Detail label="Completed by" value={record.completed_by} mono />
            <Detail label="Created at" value={formatDate(record.created_at)} />
            <Detail label="Updated at" value={formatDate(record.updated_at)} />
            <div className="sm:col-span-2 lg:col-span-3"><Detail label="Notes" value={record.notes} /></div>
          </CardContent>
        </Card>
        <div className="space-y-5">
          <Card>
            <CardHeader><CardTitle>Payment</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {record.payment ? <>
                <Detail label="Method" value={record.payment.method} />
                <Detail label="Received" value={record.payment.received ? "Yes" : "No"} />
                <Detail label="Received by" value={record.payment.received_by} mono />
                <Detail label="Received at" value={formatDate(record.payment.received_at)} />
              </> : <p className="text-sm text-muted-foreground">Payment is recorded when the vehicle exits.</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Pricing snapshot</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {record.pricing_snapshot ? <>
                <Detail label="Pricing type" value={record.pricing_snapshot.pricing_type} />
                <Detail label="Pricing rule" value={record.pricing_snapshot.pricing_rule_id} mono />
                <Separator />
                <Detail label="Fixed rate" value={formatCurrency(record.pricing_snapshot.fixed_rate)} />
                <Detail label="Base hours / fee" value={`${record.pricing_snapshot.base_hours ?? "—"} / ${formatCurrency(record.pricing_snapshot.base_fee)}`} />
                <Detail label="Extra hour fee" value={formatCurrency(record.pricing_snapshot.extra_hour_fee)} />
                <Detail label="Grace minutes" value={record.pricing_snapshot.grace_minutes} />
              </> : <p className="text-sm text-muted-foreground">Pricing is captured when the vehicle exits.</p>}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
