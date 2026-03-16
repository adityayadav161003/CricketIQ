"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Leaderboard from "@/components/Leaderboard";
import type { Player, BowlerStat } from "@/lib/api";
import { fetchBattingLeaders, fetchBowlingLeaders } from "@/lib/api";

const HERO_STATS = [
  { label: "IPL Seasons", value: "17+" },
  { label: "Matches Parsed", value: "1,100+" },
  { label: "Deliveries Analyzed", value: "350K+" },
];

export default function HomePage() {
  const [batters, setBatters] = useState<Player[]>([]);
  const [bowlers, setBowlers] = useState<BowlerStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchBattingLeaders(10), fetchBowlingLeaders(10)])
      .then(([bat, bowl]) => {
        setBatters(bat.leaders);
        setBowlers(bowl.leaders);
      })
      .catch(() => setError("Could not connect to CricketIQ API. Start the backend server."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ textAlign: "center", padding: "4rem 0 3rem" }}
      >
        <div className="badge" style={{ marginBottom: "1.25rem", fontSize: "0.75rem" }}>
          AI-Powered Cricket Analytics
        </div>
        <h1 style={{ fontSize: "clamp(2.2rem, 5vw, 3.5rem)", fontWeight: 800, letterSpacing: "-1.5px", lineHeight: 1.1, marginBottom: "1rem" }}>
          Decode Cricket{" "}
          <span className="gradient-text">Through Data.</span>
        </h1>
        <p style={{ color: "var(--text-muted)", maxWidth: 520, margin: "0 auto 2.5rem", fontSize: "1rem", lineHeight: 1.7 }}>
          Ball-by-ball analytics from IPL and International T20 matches. Uncover player performance, phase insights, and match turning points.
        </p>

        {/* Hero stats */}
        <div style={{ display: "flex", justifyContent: "center", gap: "2.5rem", flexWrap: "wrap" }}>
          {HERO_STATS.map((s) => (
            <div key={s.label}>
              <div className="stat-value" style={{ fontSize: "1.8rem" }}>{s.value}</div>
              <div className="muted-text" style={{ fontSize: "0.78rem", marginTop: "0.2rem" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </motion.section>

      {/* ── API error banner ─────────────────────────────────────────────── */}
      {error && (
        <div style={{
          background: "rgba(255,80,80,0.1)", border: "1px solid rgba(255,80,80,0.3)",
          borderRadius: 10, padding: "0.85rem 1.25rem", marginBottom: "2rem",
          fontSize: "0.85rem", color: "#ff8080",
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── Loading skeleton ─────────────────────────────────────────────── */}
      {loading && !error && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
          {[0, 1].map((i) => (
            <div key={i} className="card" style={{ minHeight: 350, animation: "pulse 1.5s ease-in-out infinite", opacity: 0.4 }} />
          ))}
        </div>
      )}

      {/* ── Leaderboards ─────────────────────────────────────────────────── */}
      {!loading && !error && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
          <Leaderboard
            title="🏏 Batting Leaders"
            items={batters.map((b) => ({
              name: b.batter,
              primary: b.total_runs,
              primaryLabel: "runs",
              secondary: b.strike_rate?.toFixed(1),
              secondaryLabel: "SR",
              tertiary: b.innings,
              tertiaryLabel: "inn",
            }))}
          />
          <Leaderboard
            title="🎯 Bowling Leaders"
            accent="#a78bfa"
            items={bowlers.map((b) => ({
              name: b.bowler,
              primary: b.wickets,
              primaryLabel: "wkts",
              secondary: b.economy?.toFixed(2),
              secondaryLabel: "eco",
              tertiary: b.overs?.toFixed(1),
              tertiaryLabel: "overs",
            }))}
          />
        </div>
      )}
    </div>
  );
}
