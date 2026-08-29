import Link from "next/link";
import type { Metadata } from "next";
import { Compass } from "lucide-react";

import { Button } from "@/components/ui/button";

export const metadata: Metadata = { title: "Page not found" };

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 p-6 text-center">
      <Compass className="size-10 text-muted-foreground" />

      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">
          Page not found
        </h1>
        <p className="max-w-sm text-sm text-muted-foreground">
          That link doesn&apos;t lead anywhere. It may have moved, or it may
          never have existed.
        </p>
      </div>

      <Button nativeButton={false} render={<Link href="/" />}>
        Back to the dashboard
      </Button>
    </div>
  );
}
