"use client";

import { Banknote, CheckCircle2, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { ParkingStatusBadge } from "@/components/parking/ParkingStatusBadge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { useCompleteExit } from "@/hooks/useParking";
import { getApiErrorMessage } from "@/lib/auth";
import { formatCurrency, formatDuration } from "@/lib/utils";
import type { ParkingRecord } from "@/types/parking";

export function CompleteExitDialog({
  record,
  trigger,
}: {
  record: ParkingRecord;
  trigger?: React.ReactElement;
}) {
  const [open, setOpen] = useState(false);
  const [cashReceived, setCashReceived] = useState(false);
  const [completed, setCompleted] = useState<ParkingRecord | null>(null);
  const mutation = useCompleteExit();

  const complete = async () => {
    if (!cashReceived) return;
    try {
      const response = await mutation.mutateAsync({
        recordId: record.id,
        paymentReceived: true,
      });
      setCompleted(response.data);
      toast.success("Vehicle exit completed");
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) {
          setCashReceived(false);
          setCompleted(null);
          mutation.reset();
        }
      }}
    >
      <DialogTrigger render={trigger ?? <Button size="sm" />}>
        <Banknote />
        Complete exit
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {completed ? "Exit completed" : "Confirm vehicle exit"}
          </DialogTitle>
          <DialogDescription>
            {record.plate_number} · {record.vehicle_type}
          </DialogDescription>
        </DialogHeader>
        {completed ? (
          <div className="grid gap-3 rounded-xl bg-muted p-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Status</span>
              <ParkingStatusBadge status={completed.status} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Duration</span>
              <strong>{formatDuration(completed.duration_minutes)}</strong>
            </div>
            <div className="flex items-center justify-between text-lg">
              <span>Cash received</span>
              <strong>{formatCurrency(completed.fee, completed.currency)}</strong>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Confirm cash has been received before completing this parking session.
            </p>
            <div className="flex items-center gap-3 rounded-xl border p-4">
              <Checkbox
                id={`cash-${record.id}`}
                checked={cashReceived}
                onCheckedChange={(checked) => setCashReceived(checked === true)}
              />
              <Label htmlFor={`cash-${record.id}`}>Cash payment received</Label>
            </div>
            {mutation.error ? (
              <p className="text-sm text-destructive">
                {getApiErrorMessage(mutation.error)}
              </p>
            ) : null}
          </div>
        )}
        <DialogFooter>
          {completed ? (
            <Button onClick={() => setOpen(false)}>
              <CheckCircle2 />
              Done
            </Button>
          ) : (
            <Button disabled={!cashReceived || mutation.isPending} onClick={complete}>
              {mutation.isPending ? <Loader2 className="animate-spin" /> : <Banknote />}
              Complete and record payment
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
