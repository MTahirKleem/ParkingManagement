"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { LoadingState } from "@/components/common/LoadingState";
import { AppHeader } from "@/components/layout/AppHeader";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { useAuth } from "@/hooks/useAuth";

export function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading || !user) {
    return (
      <main className="mx-auto w-full max-w-5xl p-6">
        <LoadingState rows={6} />
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-muted/35">
      <AppSidebar
        className="fixed inset-y-0 left-0 hidden md:flex"
        role={user.role}
      />
      <div className="md:pl-64">
        <AppHeader />
        <main className="mx-auto w-full max-w-[1500px] p-4 md:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
