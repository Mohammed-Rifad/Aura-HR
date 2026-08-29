"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AppShellSkeleton } from "@/components/layout/app-shell-skeleton";
import { useAuth } from "@/store/auth";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";


export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const ready = useAuth((s) => s.ready);
  const loadSession = useAuth((s) => s.loadSession);

  // Ask the server who we are, once, on first mount.
  useEffect(() => {
    if (!ready) loadSession();
  }, [ready, loadSession]);

  // Only redirect AFTER the check has finished. Redirecting while `ready`
  // is false would bounce a logged-in user to /login on every page refresh.
  useEffect(() => {
    if (ready && !user) router.replace("/login");
  }, [ready, user, router]);

   if (!ready) return <AppShellSkeleton />;

  // The redirect to /login is in flight. Keep the skeleton up rather than
  // rendering nothing — a blank white screen reads as a crash, and this is
  // usually only a few hundred milliseconds.
  if (!user) return <AppShellSkeleton />;


   return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <Topbar />
        <main className="flex-1 bg-muted/30 p-6">{children}</main>
      </div>
    </div>
   )
}
