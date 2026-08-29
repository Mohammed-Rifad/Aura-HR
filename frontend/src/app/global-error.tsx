"use client";

/**
 * The last resort — the root layout itself failed.
 *
 * Because the root layout is what crashed, this component has to supply its
 * own <html> and <body>. Nothing else is left to provide them, which also
 * means no fonts, no globals.css, no components. Plain inline styles only.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body
        style={{
          display: "flex",
          minHeight: "100vh",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "1rem",
          fontFamily: "system-ui, sans-serif",
          textAlign: "center",
          padding: "1.5rem",
        }}
      >
        <h1 style={{ fontSize: "1.25rem", fontWeight: 600 }}>
          AURA HR could not start
        </h1>
        <p style={{ color: "#666", fontSize: "0.875rem" }}>
          Something failed before the app could load.
        </p>
        <button
          onClick={reset}
          style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "0.5rem 1rem",
            cursor: "pointer",
          }}
        >
          Reload
        </button>
      </body>
    </html>
  );
}
