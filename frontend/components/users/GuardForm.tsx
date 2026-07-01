"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Pencil, UserPlus } from "lucide-react";
import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateGuard, useUpdateUser } from "@/hooks/useUsers";
import { getApiErrorMessage } from "@/lib/auth";
import type { User } from "@/types/user";

export const createGuardSchema = z.object({
  name: z.string().trim().min(2, "Name must be at least 2 characters."),
  email: z.email("Enter a valid email address."),
  phone: z.string().trim().optional(),
  password: z.string().min(8, "Password must be at least 8 characters."),
});

export const updateGuardSchema = z.object({
  name: z.string().trim().min(2, "Name must be at least 2 characters."),
  phone: z.string().trim().optional(),
  status: z.enum(["active", "inactive"]),
});

type CreateGuardValues = z.infer<typeof createGuardSchema>;
type UpdateGuardValues = z.infer<typeof updateGuardSchema>;
type GuardFormValues = {
  name: string;
  email: string;
  phone: string;
  password: string;
  status: "active" | "inactive";
};

const guardFormSchema = (isEditing: boolean) =>
  z.object({
    name: z.string().trim().min(2, "Name must be at least 2 characters."),
    email: isEditing
      ? z.string()
      : z.email("Enter a valid email address."),
    phone: z.string().trim(),
    password: isEditing
      ? z.string()
      : z.string().min(8, "Password must be at least 8 characters."),
    status: z.enum(["active", "inactive"]),
  });

export function GuardForm({ user }: { user?: User }) {
  const [open, setOpen] = useState(false);
  const createMutation = useCreateGuard();
  const updateMutation = useUpdateUser();
  const isEditing = Boolean(user);
  const mutation = isEditing ? updateMutation : createMutation;
  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<GuardFormValues>({
    resolver: zodResolver(guardFormSchema(isEditing)),
    defaultValues: {
      name: user?.name ?? "",
      email: user?.email ?? "",
      phone: user?.phone ?? "",
      password: "",
      status: user?.status === "inactive" ? "inactive" : "active",
    },
  });

  useEffect(() => {
    if (!open) return;
    reset({
      name: user?.name ?? "",
      email: user?.email ?? "",
      phone: user?.phone ?? "",
      password: "",
      status: user?.status === "inactive" ? "inactive" : "active",
    });
  }, [isEditing, open, reset, user]);

  const onSubmit = async (values: GuardFormValues) => {
    try {
      if (isEditing && user) {
        const update: UpdateGuardValues = values;
        await updateMutation.mutateAsync({
          userId: user.id,
          data: {
            name: update.name,
            phone: update.phone || null,
            status: update.status,
          },
        });
        toast.success("Guard updated");
      } else {
        const create: CreateGuardValues = values;
        await createMutation.mutateAsync({
          name: create.name,
          email: create.email,
          phone: create.phone || null,
          password: create.password,
          role: "guard",
        });
        toast.success("Guard account created");
      }
      setOpen(false);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button size={isEditing ? "sm" : "default"} variant={isEditing ? "outline" : "default"} />
        }
      >
        {isEditing ? <Pencil /> : <UserPlus />}
        {isEditing ? "Edit" : "Add guard"}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit guard" : "Create guard account"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Update this guard's profile and account status."
              : "Create login credentials for a parking guard."}
          </DialogDescription>
        </DialogHeader>
        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-2">
            <Label htmlFor={`guard-name-${user?.id ?? "new"}`}>Name</Label>
            <Input id={`guard-name-${user?.id ?? "new"}`} {...register("name")} />
            {errors.name ? <p className="text-sm text-destructive">{errors.name.message}</p> : null}
          </div>
          {!isEditing ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="guard-email">Email</Label>
                <Input id="guard-email" type="email" {...register("email")} />
                {errors.email ? (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                ) : null}
              </div>
              <div className="space-y-2">
                <Label htmlFor="guard-password">Password</Label>
                <Input id="guard-password" type="password" {...register("password")} />
                {errors.password ? (
                  <p className="text-sm text-destructive">{errors.password.message}</p>
                ) : null}
              </div>
            </>
          ) : null}
          <div className="space-y-2">
            <Label htmlFor={`guard-phone-${user?.id ?? "new"}`}>Phone</Label>
            <Input id={`guard-phone-${user?.id ?? "new"}`} {...register("phone")} />
          </div>
          {isEditing ? (
            <div className="space-y-2">
              <Label>Account status</Label>
              <Controller
                control={control}
                name="status"
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>
          ) : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button disabled={mutation.isPending} type="submit">
              {mutation.isPending ? <Loader2 className="animate-spin" /> : null}
              {isEditing ? "Save changes" : "Create guard"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
