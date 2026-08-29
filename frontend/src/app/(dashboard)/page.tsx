"use client";

import {
  AlertTriangle,
  CalendarOff,
  ClipboardCheck,
  Users,
} from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent } from "@/components/ui/card";
import { useDashboard } from "@/hooks/use-dashboard";
import { useAuth } from "@/store/auth";
import { HeadcountChart } from "@/components/dashboard/headcount-chart";
import { AwaitingApprovalList } from "@/components/dashboard/awaiting-approval";
import { ExpiringDocuments } from "@/components/dashboard/expiring-documents";
import Link from "next/link";

export default function DashboardPage() {
  const user = useAuth((s) => s.user);
  const { data, loading, error } = useDashboard();

  if (error) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-destructive">
          {error}
        </CardContent>
      </Card>
    );
  }

  const firstName = user?.first_name || user?.email;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Good to see you, {firstName}
        </h1>
        <p className="text-sm text-muted-foreground">
          Here is what needs your attention today.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="People"
          value={data?.headcount ?? 0}
          hint={data ? `${data.by_department.length} departments` : undefined}
          icon={Users}
          loading={loading}
        />

        <Link
          href="/approvals"
          className="rounded-xl transition-opacity hover:opacity-80"
        >
          <StatCard
            label="Awaiting your approval"
            value={data?.pending_approvals ?? 0}
            hint="Leave requests"
            icon={ClipboardCheck}
            loading={loading}
          />
        </Link>

        {/* Warning tone, but the label and hint carry the meaning too —
            colour alone must never be the signal. */}
        <StatCard
          label="Documents expiring soon"
          value={data?.expiring_documents ?? 0}
          hint="Within 30 days, or already expired"
          icon={AlertTriangle}
          loading={loading}
          tone="warning"
        />

        <StatCard
          label="On leave today"
          value={data?.on_leave_today ?? 0}
          icon={CalendarOff}
          loading={loading}
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <HeadcountChart data={data?.by_department ?? []} loading={loading} />
        <AwaitingApprovalList
          data={data?.awaiting_approval ?? []}
          loading={loading}
        />
      </div>

      <ExpiringDocuments data={data?.expiring_soon ?? []} loading={loading} />
    </div>
  );
}
