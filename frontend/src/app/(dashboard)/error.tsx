"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // The user gets a sentence; the console gets the stack. In production
    // this is where a Sentry call would go.
    console.error(error);
  }, [error]);

  return (
    <Card className="mx-auto max-w-lg">
      <CardContent className="space-y-4 p-6 text-center">
        <AlertTriangle className="mx-auto size-8 text-amber-600" />

        <div className="space-y-1.5">
          <h2 className="text-lg font-semibold">Something went wrong</h2>
          <p className="text-sm text-muted-foreground">
            This page failed to load. Trying again usually works.
          </p>
        </div>

        {/* In production Next replaces the message with a generic string and
            gives you a digest instead — an id you can match against the
            server logs. Showing the raw message would leak internals. */}
        {error.digest && (
          <p className="font-mono text-xs text-muted-foreground">
            Reference: {error.digest}
          </p>
        )}

        <Button onClick={reset}>Try again</Button>
      </CardContent>
    </Card>
  );
}
