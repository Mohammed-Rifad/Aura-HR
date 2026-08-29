import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "next-themes";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
   title: {
    default: "AURA HR",
    template: "%s · AURA HR",
  },
  description:
    "HR platform with an AI assistant that can only see what you can see.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // suppressHydrationWarning is required, not optional. next-themes runs a
    // blocking script that sets class="dark" on <html> BEFORE React hydrates.
    // React then sees markup that does not match what it rendered on the
    // server and warns. This tells it that difference is expected — here,
    // and only here.
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <ThemeProvider
          // Matches your CSS: @custom-variant dark (&:is(.dark *))
          attribute="class"
          defaultTheme="system"
          enableSystem
          // Without this, switching theme animates every colour on the page
          // at once, which looks like a glitch rather than a transition.
          disableTransitionOnChange
        >
          {children}
          <Toaster richColors position="top-right" />
        </ThemeProvider>
      </body>
    </html>
  );
}

