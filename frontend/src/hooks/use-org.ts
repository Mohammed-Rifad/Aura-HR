"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { Department, Designation, Paginated } from "@/lib/types";

export function useDepartments() {
  const [data, setData] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .get<Paginated<Department>>("/org/departments/")
      .then((r) => !cancelled && setData(r.data.results))
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading };
}


export function useDesignations() {
  const [data, setData] = useState<Designation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .get<Paginated<Designation>>("/org/designations/")
      .then((r) => !cancelled && setData(r.data.results))
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading };
}
