"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // The server cannot know the theme — it lives in the browser's
  // localStorage. Rendering a sun or a moon during SSR would be a coin flip,
  // and getting it wrong is a hydration mismatch. So render the button
  // immediately (the layout must not shift) and the icon only after mount.
  useEffect(() => setMounted(true), []);

  const dark = resolvedTheme === "dark";

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(dark ? "light" : "dark")}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {mounted && (dark ? <Sun className="size-4" /> : <Moon className="size-4" />)}
    </Button>
  );
}
