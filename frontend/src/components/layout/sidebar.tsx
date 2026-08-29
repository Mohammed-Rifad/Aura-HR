"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/store/auth";
import { isActive, navFor } from "@/lib/nav";

export function Sidebar() {
  const pathname = usePathname();
  const role = useAuth((s) => s.user?.role);
  const items = navFor(role);

  return (
    <aside className="hidden w-60 shrink-0 border-r bg-card md:block">
      <div className="flex h-14 items-center border-b px-5">
        <span className="text-lg font-semibold tracking-tight">AURA HR</span>
      </div>

      <nav className="space-y-1 p-3">
         
               {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
              isActive(pathname, item.href)
                ? "bg-primary/10 font-medium text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            <item.icon className="size-4" />
            {item.label}
          </Link>
        ))}

      </nav>
    </aside>
  );
}
