"use client";

import {
  ArrowRight,
  CarFront,
  History,
  Search,
  ShieldCheck,
  SquareParking,
} from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";

export default function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;

  const actions =
    user.role === "admin"
      ? [
          ["Vehicle Entry", "/parking/entry", CarFront],
          ["Active Vehicles", "/parking/active", SquareParking],
          ["Parking History", "/parking/history", History],
          ["Manage Guards", "/users", ShieldCheck],
        ]
      : [
          ["Vehicle Entry", "/parking/entry", CarFront],
          ["Active Vehicles", "/parking/active", SquareParking],
          ["Search Parking", "/parking/search", Search],
          ["Parking History", "/parking/history", History],
        ];

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Operations"
        title={`Welcome, ${user.name}`}
        description="Choose an available module. Dashboard analytics will appear only when supported by backend APIs."
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {actions.map(([label, href, Icon]) => (
          <Link href={href as string} key={href as string}>
            <Card className="group h-full transition hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-md">
              <CardContent className="flex h-full min-h-40 flex-col justify-between">
                <span className="grid size-10 place-items-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="size-5" />
                </span>
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium">{label as string}</span>
                  <ArrowRight className="size-4 text-muted-foreground transition group-hover:translate-x-1 group-hover:text-primary" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
