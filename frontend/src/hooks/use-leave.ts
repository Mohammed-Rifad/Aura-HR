"use client";

import { useCallback, useEffect, useState } from "react";

import { api, errorMessage } from "@/lib/api";
import type {
  LeaveBalance,
  LeaveRequestListItem,
  LeaveType,
  Paginated,
} from "@/lib/types";

export function useLeaveBalances(employeeId?: string) {
  const [data, setData] = useState<LeaveBalance[]>([]);
  const [loading, setLoading] = useState(true);

  // useCallback so the page can call refresh() after applying for leave,
  // without this function being rebuilt on every render.
  const refresh = useCallback(() => {
    if (!employeeId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .get<Paginated<LeaveBalance>>("/leave/balances/", {
        params: { employee: employeeId },
      })
      .then((r) => setData(r.data.results))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [employeeId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, refresh };
}

export function useMyLeaveRequests(employeeId?: string) {
  const [data, setData] = useState<LeaveRequestListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    if (!employeeId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .get<Paginated<LeaveRequestListItem>>("/leave/requests/", {
        params: { employee: employeeId, ordering: "-start_date" },
      })
      .then((r) => {
        setData(r.data.results);
        setError(null);
      })
      .catch((e) => setError(errorMessage(e)))
      .finally(() => setLoading(false));
  }, [employeeId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh };
}

export function useLeaveTypes() {
  const [data, setData] = useState<LeaveType[]>([]);

  useEffect(() => {
    let cancelled = false;
    api
      .get<Paginated<LeaveType>>("/leave/types/")
      .then((r) => !cancelled && setData(r.data.results))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}

export function usePendingApprovals() {
  const [data, setData] = useState<LeaveRequestListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setLoading(true);
    api
      .get<Paginated<LeaveRequestListItem>>("/leave/requests/", {
        params: { status: "PENDING", ordering: "start_date" },
      })
      .then((r) => {
        setData(r.data.results);
        setError(null);
      })
      .catch((e) => setError(errorMessage(e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh };
}
