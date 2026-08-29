import { Skeleton } from "@/components/ui/skeleton";

/**
 * What the app looks like before we know who you are.
 *
 * Deliberately the same shape as the real shell — same sidebar width, same
 * topbar height, same padding. A centred "Loading…" throws the layout away,
 * so everything jumps into place a moment later. This just fills in.
 */
export function AppShellSkeleton() {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 border-r bg-card md:block">
        {/* The name is known before any request. Showing it costs nothing
            and tells the user they are in the right place. */}
        <div className="flex h-14 items-center border-b px-5">
          <span className="text-lg font-semibold tracking-tight">AURA HR</span>
        </div>

        <nav className="space-y-1 p-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-9 w-full" />
          ))}
        </nav>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-between border-b bg-card px-5">
          <span className="text-lg font-semibold tracking-tight md:hidden">
            AURA HR
          </span>
          <div className="hidden md:block" />

          <div className="flex items-center gap-2">
            <Skeleton className="size-7 rounded-full" />
            <Skeleton className="hidden h-4 w-24 sm:block" />
          </div>
        </header>

        <main className="flex-1 space-y-6 bg-muted/30 p-6">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-72" />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-28 w-full" />
            ))}
          </div>

          <Skeleton className="h-64 w-full" />
        </main>
      </div>
    </div>
  );
}
