"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, Loader2, PlusCircle } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateEntry } from "@/hooks/useParking";
import { getApiErrorMessage } from "@/lib/auth";

export const vehicleEntrySchema = z.object({
  plate_number: z.string().trim().min(1, "Plate number is required."),
  vehicle_type: z.enum(["bike", "car"]),
  slot: z.string().trim().optional(),
});

type VehicleEntryValues = z.infer<typeof vehicleEntrySchema>;

export function VehicleEntryForm() {
  const mutation = useCreateEntry();
  const [success, setSuccess] = useState<string | null>(null);
  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<VehicleEntryValues>({
    resolver: zodResolver(vehicleEntrySchema),
    defaultValues: { plate_number: "", vehicle_type: "bike", slot: "" },
  });

  const onSubmit = async (values: VehicleEntryValues) => {
    setSuccess(null);
    try {
      const response = await mutation.mutateAsync({
        ...values,
        plate_number: values.plate_number.toUpperCase(),
        slot: values.slot || null,
      });
      setSuccess(`${response.data.plate_number} is now active.`);
      toast.success("Vehicle entry created");
      reset();
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
      {mutation.error ? (
        <Alert variant="destructive">
          <AlertDescription>
            {getApiErrorMessage(mutation.error)}
          </AlertDescription>
        </Alert>
      ) : null}
      {success ? (
        <Alert>
          <AlertDescription className="flex flex-wrap items-center justify-between gap-3">
            <span>{success}</span>
            <Link
              className={buttonVariants({ size: "sm", variant: "outline" })}
              href="/parking/active"
            >
              View active vehicles
              <ArrowRight />
            </Link>
          </AlertDescription>
        </Alert>
      ) : null}
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="plate_number">Plate number</Label>
          <Input
            id="plate_number"
            className="h-12 font-mono text-lg uppercase tracking-wider"
            placeholder="LEA-1234"
            aria-invalid={Boolean(errors.plate_number)}
            {...register("plate_number")}
          />
          {errors.plate_number ? (
            <p className="text-xs text-destructive">
              {errors.plate_number.message}
            </p>
          ) : null}
        </div>
        <div className="space-y-2">
          <Label>Vehicle type</Label>
          <Controller
            name="vehicle_type"
            control={control}
            render={({ field }) => (
              <Select value={field.value} onValueChange={field.onChange}>
                <SelectTrigger className="h-11 w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bike">Bike</SelectItem>
                  <SelectItem value="car">Car</SelectItem>
                </SelectContent>
              </Select>
            )}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="slot">Slot (optional)</Label>
          <Input id="slot" className="h-11" placeholder="A-12" {...register("slot")} />
        </div>
      </div>
      <Button
        className="h-12 w-full text-base sm:w-auto sm:min-w-52"
        disabled={mutation.isPending}
        type="submit"
      >
        {mutation.isPending ? <Loader2 className="animate-spin" /> : <PlusCircle />}
        {mutation.isPending ? "Saving entry…" : "Create vehicle entry"}
      </Button>
    </form>
  );
}
