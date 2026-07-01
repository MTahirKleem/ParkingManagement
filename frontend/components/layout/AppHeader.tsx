"use client";

import { LogOut, Menu } from "lucide-react";

import { AppSidebar } from "@/components/layout/AppSidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";

export function AppHeader() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background/90 px-4 backdrop-blur md:px-8">
      <div className="flex items-center gap-3">
        <Sheet>
          <SheetTrigger
            render={
              <Button
                aria-label="Open navigation"
                className="md:hidden"
                size="icon"
                variant="outline"
              />
            }
          >
            <Menu />
          </SheetTrigger>
          <SheetContent className="w-72 p-0" side="left">
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <AppSidebar role={user.role} />
          </SheetContent>
        </Sheet>
        <div>
          <p className="text-sm font-medium">{user.name}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
        <Badge className="capitalize" variant="secondary">
          {user.role}
        </Badge>
      </div>
      <Button onClick={logout} size="sm" variant="outline">
        <LogOut />
        <span className="hidden sm:inline">Logout</span>
      </Button>
    </header>
  );
}
