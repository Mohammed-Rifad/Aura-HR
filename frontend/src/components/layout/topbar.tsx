"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/store/auth";
import { MobileNav } from "@/components/layout/mobile-nav";

function initials(fullName: string, email: string) {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (parts[0]?.[0] ?? email[0] ?? "?").toUpperCase();
}

export function Topbar() {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);

  if (!user) return null;

  async function onLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b bg-card px-5">
      {/* Left: the drawer trigger and the app name, both phone-only. On
          desktop the sidebar already shows the name, so this side is empty
          and justify-between pushes the account menu right. */}
      <div className="flex items-center gap-1">
        <MobileNav />
        <span className="text-lg font-semibold tracking-tight md:hidden">
          AURA HR
        </span>
      </div>

      <div className="flex items-center gap-1">
        <ThemeToggle />

        <DropdownMenu>
          <DropdownMenuTrigger
            render={<Button variant="ghost" className="gap-2 px-2" />}
          >
            <Avatar className="size-7">
              <AvatarFallback className="text-xs">
                {initials(user.full_name, user.email)}
              </AvatarFallback>
            </Avatar>
            <span className="hidden text-sm sm:inline">{user.full_name}</span>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" className="w-56">
            {/* A plain div, not DropdownMenuLabel. Base UI's label maps to a
                GroupLabel, which must sit inside a Menu.Group — and this
                block is not labelling a group of items, it just says who is
                signed in. */}
            <div className="space-y-1 px-2 py-1.5">
              <p className="text-sm font-medium">{user.full_name}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
              <Badge variant="secondary" className="mt-1">
                {user.role}
              </Badge>
            </div>

            <DropdownMenuSeparator />

            <DropdownMenuItem onClick={onLogout}>
              <LogOut className="mr-2 size-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
