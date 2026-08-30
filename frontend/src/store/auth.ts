import { create } from "zustand";

import { api, clearTokens, getAccessToken, setTokens } from "@/lib/api";
import type { LoginResponse, Role, User } from "@/lib/types";

type AuthState = {
  user: User | null;
  /** false until we have checked localStorage. Guards against redirecting
   *  a logged-in user to /login during the first render. */
  ready: boolean;

  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  loadSession: () => Promise<void>;
  hasRole: (...roles: Role[]) => boolean;
};

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  ready: false,

  login: async (email, password) => {
    const { data } = await api.post<LoginResponse>("/auth/login/", {
      email,
      password,
    });
    setTokens(data.access, data.refresh);
    set({ user: data.user, ready: true });
    return data.user;
  },

  logout: async () => {
    // Captured before clearing. The axios interceptor reads the token out of
    // localStorage, so a request fired after clearTokens() would go out
    // unauthenticated and be rejected.
    const access = getAccessToken();
    const refresh = localStorage.getItem("aura_refresh");

    // Clear locally FIRST. Nothing the server replies changes the outcome,
    // so waiting for it only delays the redirect — and on a sleeping free
    // tier that is a frozen-looking screen for nearly a minute.
    clearTokens();
    set({ user: null });

    // Fire and forget. Blacklisting the refresh token still matters — it is
    // what stops a stolen one being reused — but the UI does not depend on
    // the answer.
    if (access && refresh) {
      api
        .post(
          "/auth/logout/",
          { refresh },
          { headers: { Authorization: `Bearer ${access}` } },
        )
        .catch(() => {});
    }
  },


  /** Runs once on app start. A token in localStorage is not proof of a
   *  valid session, so we ask the server who we are. */
  loadSession: async () => {
    if (!getAccessToken()) {
      set({ user: null, ready: true });
      return;
    }
    try {
      const { data } = await api.get<User>("/auth/me/");
      set({ user: data, ready: true });
    } catch {
      clearTokens();
      set({ user: null, ready: true });
    }
  },

  hasRole: (...roles) => {
    const role = get().user?.role;
    return role ? roles.includes(role) : false;
  },
}));
