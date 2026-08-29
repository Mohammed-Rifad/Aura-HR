"use client";

import { useCallback, useEffect, useState } from "react";

import { api, errorMessage } from "@/lib/api";
import type { Paginated, User } from "@/lib/types";

export type AccountFilters = {
  search: string;
  role: string; // "" means all
  verified: string; // "" means all, otherwise "true" or "false"
};

export function useAccounts(filters: AccountFilters) {
  const [data, setData] = useState<Paginated<User> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { search, role, verified } = filters;

  // useCallback so the page can call refresh() after verifying someone,
  // without rebuilding this function on every render.
  const refresh = useCallback(() => {
    setLoading(true);
    api
      .get<Paginated<User>>("/auth/users/", {
        // Empty values are left out entirely. Sending `role=` would make the
        // backend filter for an empty role and return nothing.
        params: {
          ...(search ? { search } : {}),
          ...(role ? { role } : {}),
          ...(verified ? { is_verified: verified } : {}),
        },
      })
      .then((response) => {
        setData(response.data);
        setError(null);
      })
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [search, role, verified]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh };
}
