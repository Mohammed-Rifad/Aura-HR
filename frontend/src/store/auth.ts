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
    const refresh = localStorage.getItem("aura_refresh");
    try {
      // Blacklists the refresh token server-side. If it fails, we still
      // clear locally — a logout that leaves tokens behind is worse.
      await api.post("/auth/logout/", { refresh });
    } catch {
      // ignore
    }
    clearTokens();
    set({ user: null });
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
