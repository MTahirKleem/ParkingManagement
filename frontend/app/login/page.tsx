"use client";

import { SquareParking } from "lucide-react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { LoginForm } from "@/components/auth/LoginForm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated && user) {
      router.replace(user.role === "admin" ? "/dashboard" : "/parking/entry");
    }
  }, [isAuthenticated, isLoading, router, user]);

  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-muted/40 px-4 py-12">
      <div className="absolute inset-x-0 top-0 h-52 bg-sidebar" />
      <div className="absolute top-20 left-1/2 size-72 -translate-x-1/2 rounded-full bg-primary/20 blur-3xl" />
      <Card className="relative w-full max-w-md border-border/70 shadow-2xl">
        <CardHeader className="items-center pb-2 text-center">
          <span className="mb-3 grid size-12 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-lg">
            <SquareParking />
          </span>
          <CardTitle className="font-heading text-2xl">
            ParkingManagement
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Sign in to manage daily parking operations.
          </p>
        </CardHeader>
        <CardContent className="pt-4">
          <LoginForm />
        </CardContent>
      </Card>
    </main>
  );
}
