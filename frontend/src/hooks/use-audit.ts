"use client";

import { useCallback, useEffect, useState } from "react";

import { api, errorMessage } from "@/lib/api";
import type { AuditLogEntry, Paginated } from "@/lib/types";

export type AuditFilters = {
  search: string;
  action: string; // "" means all
  model: string; // "" means all
  page: number;
};

export function useAuditLog(filters: AuditFilters) {
  const [data, setData] = useState<Paginated<AuditLogEntry> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { search, action, model, page } = filters;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    api
      .get<Paginated<AuditLogEntry>>("/audit/logs/", {
        params: {
          page,
          ...(search ? { search } : {}),
          ...(action ? { action } : {}),
          ...(model ? { model_name: model } : {}),
        },
      })
      .then((response) => {
        if (cancelled) return;
        setData(response.data);
        setError(null);
      })
      .catch((err) => !cancelled && setError(errorMessage(err)))
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [search, action, model, page]);

  return { data, loading, error };
}

/** The model names that actually appear in the log, for the filter dropdown. */
export function useAuditModels() {
  const [data, setData] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    api
      .get<string[]>("/audit/logs/models/")
      .then((r) => !cancelled && setData(r.data))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}
