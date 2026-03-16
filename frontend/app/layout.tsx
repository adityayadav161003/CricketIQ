import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "CricketIQ — Decode Cricket Through Data",
  description: "AI-powered IPL and T20I cricket analytics dashboard.",
};

const NAV = [
  { href: "/", label: "Home" },
  { href: "/players", label: "Players" },
  { href: "/matches", label: "Matches" },
  { href: "/analytics", label: "Analytics" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body>
        {/* ── Navigation ─────────────────────────────────────────────────── */}
        <header style={{
          position: "sticky", top: 0, zIndex: 50,
          background: "rgba(11,11,11,0.85)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid #1a1a1a",
          padding: "0 2rem",
        }}>
          <nav style={{
            maxWidth: 1200, margin: "0 auto",
            display: "flex", alignItems: "center",
            justifyContent: "space-between", height: 56,
          }}>
            <Link href="/" style={{ textDecoration: "none" }}>
              <span style={{ fontWeight: 800, fontSize: "1.15rem", letterSpacing: "-0.5px" }}>
                <span className="gradient-text">CricketIQ</span>
              </span>
            </Link>
            <div style={{ display: "flex", gap: "1.75rem", alignItems: "center" }}>
              {NAV.map((n) => (
                <Link key={n.href} href={n.href} className="nav-link">{n.label}</Link>
              ))}
            </div>
          </nav>
        </header>

        {/* ── Main ────────────────────────────────────────────────────────── */}
        <main style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem" }}>
          {children}
        </main>

        {/* ── Footer ──────────────────────────────────────────────────────── */}
        <footer style={{
          borderTop: "1px solid #1a1a1a",
          padding: "1.5rem 2rem",
          textAlign: "center",
          color: "var(--text-muted)",
          fontSize: "0.8rem",
          marginTop: "4rem",
        }}>
          CricketIQ &mdash; Decode Cricket Through Data · Data from{" "}
          <a href="https://cricsheet.org" target="_blank" rel="noopener noreferrer" className="accent-text">Cricsheet</a>
        </footer>
      </body>
    </html>
  );
}
