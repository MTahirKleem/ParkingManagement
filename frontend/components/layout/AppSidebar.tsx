"use client";

import {
  CarFront,
  History,
  LayoutDashboard,
  Search,
  ShieldCheck,
  SquareParking,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import type { UserRole } from "@/types/auth";

export function getNavigation(role: UserRole) {
  const operational = [
    { label: "Vehicle Entry", href: "/parking/entry", icon: CarFront },
    {
      label: "Active Vehicles",
      href: "/parking/active",
      icon: SquareParking,
    },
    { label: "Search Parking", href: "/parking/search", icon: Search },
    { label: "Parking History", href: "/parking/history", icon: History },
  ];
  return role === "admin"
    ? [
        { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        ...operational,
        { label: "Guards", href: "/users", icon: ShieldCheck },
      ]
    : operational;
}

export function AppSidebar({
  role,
  onNavigate,
  className,
}: {
  role: UserRole;
  onNavigate?: () => void;
  className?: string;
}) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col bg-sidebar px-4 py-5 text-sidebar-foreground",
        className,
      )}
    >
      <Link
        href={role === "admin" ? "/dashboard" : "/parking/entry"}
        onClick={onNavigate}
        className="mb-8 flex items-center gap-3 px-2"
      >
        <span className="grid size-10 place-items-center rounded-xl bg-sidebar-primary text-sidebar-primary-foreground shadow-sm">
          <SquareParking className="size-5" />
        </span>
        <div>
          <p className="font-heading text-sm font-semibold">ParkingManagement</p>
          <p className="text-xs text-sidebar-foreground/60">Operations console</p>
        </div>
      </Link>
      <nav className="space-y-1">
        {getNavigation(role).map((item) => {
          const active =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground/75 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
            >
              <item.icon className="size-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto rounded-xl border border-sidebar-border bg-sidebar-accent/50 p-3 text-xs text-sidebar-foreground/65">
        <p className="font-medium text-sidebar-foreground">Cash-first MVP</p>
        <p className="mt-1">Fast, focused parking operations.</p>
      </div>
    </aside>
  );
}
