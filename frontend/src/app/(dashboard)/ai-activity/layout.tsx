import type { Metadata } from "next";

export const metadata: Metadata = { title: "AI Activity" };

// A layout exists here only to carry that title. It is a server component,
// which is the whole point — "use client" pages cannot export metadata.
export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
