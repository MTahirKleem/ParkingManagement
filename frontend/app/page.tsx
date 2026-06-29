"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { LoadingState } from "@/components/common/LoadingState";
import { useAuth } from "@/hooks/useAuth";

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    router.replace(
      !user ? "/login" : user.role === "admin" ? "/dashboard" : "/parking/entry",
    );
  }, [isLoading, router, user]);

  return (
    <main className="mx-auto mt-20 w-full max-w-3xl p-6">
      <LoadingState rows={4} />
    </main>
  );
}
