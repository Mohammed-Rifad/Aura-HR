"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Dialog } from "@base-ui/react/dialog";
import { Menu, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { isActive, navFor } from "@/lib/nav";
import { cn } from "@/lib/utils";
import { useAuth } from "@/store/auth";

/**
 * The sidebar, for phones.
 *
 * Built on Base UI's Dialog primitives rather than our DialogContent, which
 * is hard-centred with top-1/2 / -translate-1/2. Fighting those classes to
 * make a left-edge drawer is more fragile than composing the primitives.
 * We still get the focus trap, Escape handling and scroll lock for free.
 */
export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const role = useAuth((s) => s.user?.role);
  const items = navFor(role);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger
        render={<Button variant="ghost" size="icon" className="md:hidden" />}
      >
        <Menu className="size-5" />
        <span className="sr-only">Open menu</span>
      </Dialog.Trigger>

      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-50 bg-black/40 data-open:animate-in data-open:fade-in-0 data-closed:animate-out data-closed:fade-out-0" />

        <Dialog.Popup className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-card outline-none data-open:animate-in data-open:slide-in-from-left data-closed:animate-out data-closed:slide-out-to-left">
          <div className="flex h-14 shrink-0 items-center justify-between border-b px-5">
            {/* Base UI expects a Title for screen readers. It is also the
                obvious place for the app name. */}
            <Dialog.Title className="text-lg font-semibold tracking-tight">
              AURA HR
            </Dialog.Title>

            <Dialog.Close render={<Button variant="ghost" size="icon-sm" />}>
              <X className="size-4" />
              <span className="sr-only">Close menu</span>
            </Dialog.Close>
          </div>

          <nav className="space-y-1 overflow-y-auto p-3">
            {items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                // Close on navigate. Without this the drawer sits open on
                // top of the page you just asked for.
                onClick={() => setOpen(false)}
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
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
