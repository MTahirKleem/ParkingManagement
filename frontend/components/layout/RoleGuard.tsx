"use client";

import { ShieldX } from "lucide-react";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import type { UserRole } from "@/types/auth";

export function RoleGuard({
  allowed,
  children,
}: {
  allowed: UserRole[];
  children: React.ReactNode;
}) {
  const { user } = useAuth();
  if (!user || !allowed.includes(user.role)) {
    return (
      <Card>
        <CardContent className="flex min-h-80 flex-col items-center justify-center gap-4 text-center">
          <ShieldX className="size-10 text-destructive" />
          <div>
            <h1 className="text-xl font-semibold">Access restricted</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              You do not have permission to perform this action.
            </p>
          </div>
          <Link className={buttonVariants()} href="/parking/entry">
            Return to vehicle entry
          </Link>
        </CardContent>
      </Card>
    );
  }
  return children;
}
