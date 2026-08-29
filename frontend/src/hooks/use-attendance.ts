"use client";

import { useCallback, useEffect, useState } from "react";
import type { AxiosError } from "axios";

import { api } from "@/lib/api";
import type {
  Attendance,
  AttendanceSummary,
  Paginated,
} from "@/lib/types";

/** Today's record, or null if you have not checked in yet. */
export function useAttendanceToday() {
  const [data, setData] = useState<Attendance | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    api
      .get<Attendance>("/attendance/today/")
      .then((r) => setData(r.data))
      .catch((error) => {
        // A 404 here is not a failure. It means "no record today", which is
        // exactly what you see before your first check-in.
        if ((error as AxiosError).response?.status === 404) setData(null);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, refresh };
}

/** Every record in one month, newest first. */
export function useAttendanceMonth(year: number, month: number) {
  const [data, setData] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);

    // First and last day of the month. Month 0 of the next month is the
    // last day of this one — a standard JavaScript date trick.
    const first = new Date(year, month - 1, 1);
    const last = new Date(year, month, 0);
    const iso = (d: Date) => d.toLocaleDateString("en-CA"); // YYYY-MM-DD

    api
      .get<Paginated<Attendance>>("/attendance/", {
        params: {
          date__gte: iso(first),
          date__lte: iso(last),
          page_size: 40,
        },
      })
      .then((r) => setData(r.data.results))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [year, month]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, refresh };
}

/** The counted version of the same month. */
export function useAttendanceSummary(year: number, month: number) {
  const [data, setData] = useState<AttendanceSummary | null>(null);

  const refresh = useCallback(() => {
    api
      .get<AttendanceSummary>("/attendance/summary/", {
        params: { year, month },
      })
      .then((r) => setData(r.data))
      .catch(() => {});
  }, [year, month]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, refresh };
}
