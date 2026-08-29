import {
  Activity,
  CalendarCheck,
  ClipboardCheck,
  Clock,
  LayoutDashboard,
  ScrollText,
  Sparkles,
  Users,
  UsersRound,
  type LucideIcon,
} from "lucide-react";

import type { Role } from "./types";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  /** undefined means everyone */
  roles?: Role[];
};

export const NAV: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Employees", href: "/employees", icon: Users },
  { label: "Leave", href: "/leave", icon: CalendarCheck },
  {
    label: "Approvals",
    href: "/approvals",
    icon: ClipboardCheck,
    roles: ["ADMIN", "HR", "MANAGER"],
  },
  { label: "Attendance", href: "/attendance", icon: Clock },
  { label: "Assistant", href: "/assistant", icon: Sparkles },
  { label: "Accounts", href: "/accounts", icon: UsersRound, roles: ["ADMIN"] },
    { label: "AI activity", href: "/ai-activity", icon: Activity, roles: ["ADMIN"] },

  { label: "Audit log", href: "/audit", icon: ScrollText, roles: ["ADMIN"] },
];

export function navFor(role: Role | undefined): NavItem[] {
  if (!role) return [];
  return NAV.filter((item) => !item.roles || item.roles.includes(role));
}


/** Is this nav item the page you are on? */
export function isActive(pathname: string, href: string) {
  // "/" would match every route with startsWith, so it needs an exact test.
  // Everything else highlights on its sub-pages too.
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}
