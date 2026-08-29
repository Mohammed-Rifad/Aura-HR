"use client";

import { useEffect, useState } from "react";
import type {
  EmployeeDetail,
  LeaveRequestListItem,
  Paginated,
  EmployeeListItem
} from "@/lib/types";
import { api, errorMessage } from "@/lib/api";
// import type { , Paginated } from "@/lib/types";

export type EmployeeFilters = {
  search: string;
  department: string; // "" means all
  status: string;     // "" means all
  page: number;
};

export function useEmployees(filters: EmployeeFilters) {
  const [data, setData] = useState<Paginated<EmployeeListItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { search, department, status, page } = filters;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    api
      .get<Paginated<EmployeeListItem>>("/employees/", {
        // Empty values are left out entirely. Sending `status=` would make
        // the backend filter for an empty status and return nothing.
        params: {
          page,
          ...(search ? { search } : {}),
          ...(department ? { department } : {}),
          ...(status ? { status } : {}),
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
  }, [search, department, status, page]);

  return { data, loading, error };
}

export function useEmployee(id: string) {
  const [data, setData] = useState<EmployeeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    api
      .get<EmployeeDetail>(`/employees/${id}/`)
      .then((r) => !cancelled && setData(r.data))
      // A 404 here means the row isn't in this user's scope. That's the
      // backend refusing to confirm the person exists — not a broken page.
      .catch((e) => !cancelled && setError(errorMessage(e)))
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [id]);

  return { data, loading, error };
}

export function useEmployeeLeave(id: string) {
  const [data, setData] = useState<LeaveRequestListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    api
      .get<Paginated<LeaveRequestListItem>>("/leave/requests/", {
        params: { employee: id, ordering: "-start_date" },
      })
      .then((r) => !cancelled && setData(r.data.results))
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [id]);

  return { data, loading };
}


export function useEmployeeOptions() {
  const [data, setData] = useState<EmployeeListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .get<Paginated<EmployeeListItem>>("/employees/", {
        params: { page_size: 100, status: "ACTIVE" },
      })
      .then((r) => !cancelled && setData(r.data.results))
      .catch(() => {})
      // finally, not then — a failed request must still stop loading, or a
      // network blip leaves the skeleton on screen for good.
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading };
}
