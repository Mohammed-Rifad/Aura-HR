"use client";

import { useEffect, useState } from "react";

import { api, errorMessage } from "@/lib/api";
import type { DashboardSummary } from "@/lib/types";

export function useDashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // React runs effects twice in development. Without this flag, the second
    // run's response can land after unmount and warn.
    let cancelled = false;

    api
      .get<DashboardSummary>("/dashboard/")
      .then((response) => {
        if (!cancelled) setData(response.data);
      })
      .catch((err) => {
        if (!cancelled) setError(errorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}
