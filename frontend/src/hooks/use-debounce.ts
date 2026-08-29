"use client";

import { useEffect, useState } from "react";

export function useDebounced<T>(value: T, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    // Typing again cancels the pending timer, so only the last keystroke
    // in a 300ms window actually fires a request.
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
