import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import type { ApiError } from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const ACCESS_KEY = "aura_access";
const REFRESH_KEY = "aura_refresh";

// ---------------------------------------------------------------------------
// Token storage
//
// Every read is guarded: Next renders on the server first, where there is no
// localStorage. Without the guard the app crashes before it reaches the browser.
// ---------------------------------------------------------------------------

export function getAccessToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(access: string, refresh: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

// ---------------------------------------------------------------------------
// The client
// ---------------------------------------------------------------------------

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ---------------------------------------------------------------------------
// Refresh
// ---------------------------------------------------------------------------

let refreshPromise: Promise<string> | null = null;

async function doRefresh(): Promise<string> {
  const refresh = getRefreshToken();
  if (!refresh) throw new Error("No refresh token");

  // Plain axios, not `api`. Using the instance here would send a failing
  // refresh back through the interceptor below, which would refresh again,
  // forever.
  const { data } = await axios.post<{ access: string; refresh?: string }>(
    `${BASE_URL}/auth/refresh/`,
    { refresh },
  );

  // The backend rotates refresh tokens and blacklists the old one, so the
  // new one MUST be saved. Keep the old and the next refresh fails.
  setTokens(data.access, data.refresh ?? refresh);
  return data.access;
}

function refreshAccessToken(): Promise<string> {
  // Single flight. A dashboard fires five requests, all five get 401. Without
  // this they become five refresh calls — the first succeeds and blacklists
  // the token, the other four fail, and the user is logged out for no reason.
  if (!refreshPromise) {
    refreshPromise = doRefresh().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

type Retriable = InternalAxiosRequestConfig & { _retried?: boolean };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as Retriable | undefined;

    if (error.response?.status !== 401 || !original) {
      return Promise.reject(error);
    }

    // A wrong password is a genuine 401. So is a dead refresh token.
    // Neither should trigger a refresh.
    const url = original.url ?? "";
    if (url.includes("/auth/login/") || url.includes("/auth/refresh/")) {
      return Promise.reject(error);
    }

    // Retry once, never twice. Otherwise a request that is genuinely
    // unauthorised loops until the browser gives up.
    if (original._retried) return Promise.reject(error);
    original._retried = true;

    try {
      const token = await refreshAccessToken();
      original.headers.Authorization = `Bearer ${token}`;
      return api(original);
    } catch {
      clearTokens();
      if (typeof window !== "undefined") window.location.href = "/login";
      return Promise.reject(error);
    }
  },
);

/**
 * fetch() with the access token attached and one refresh retry.
 *
 * The streaming endpoint cannot go through axios — axios buffers the entire
 * body before returning, which defeats streaming. This keeps that one call
 * on the same token and the same single-flight refresh as everything else.
 */
export async function authedFetch(path: string, init: RequestInit = {}) {
  const send = (token: string | null) =>
    fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

  let response = await send(getAccessToken());

  if (response.status === 401) {
    try {
      response = await send(await refreshAccessToken());
    } catch {
      clearTokens();
      if (typeof window !== "undefined") window.location.href = "/login";
    }
  }

  return response;
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export function errorMessage(error: unknown): string {
  // Your backend normalises every error to { message, errors, code }.
  const data = (error as AxiosError<ApiError>)?.response?.data;
  return data?.message ?? "Something went wrong. Please try again.";
}

