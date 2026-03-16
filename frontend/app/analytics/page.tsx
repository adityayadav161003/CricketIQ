"use client";
import { useEffect, useState } from "react";
import RunRateChart from "@/components/RunRateChart";
import Leaderboard from "@/components/Leaderboard";
import type { RunRatePoint, PhaseLeader, BowlerStat } from "@/lib/api";
import { fetchRunRateProgression, fetchPhaseBatting, fetchBowlingLeaders } from "@/lib/api";

type Phase = "powerplay" | "middle" | "death";

export default function AnalyticsPage() {
  const [runRate, setRunRate] = useState<RunRatePoint[]>([]);
  const [phaseLeaders, setPhaseLeaders] = useState<PhaseLeader[]>([]);
  const [bowlers, setBowlers] = useState<BowlerStat[]>([]);
  const [activePhase, setActivePhase] = useState<Phase>("powerplay");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch run rate + bowling leaders once
  useEffect(() => {
    Promise.all([fetchRunRateProgression(1), fetchBowlingLeaders(10, 10)])
      .then(([rr, bowl]) => { setRunRate(rr.progression); setBowlers(bowl.leaders); })
      .catch(() => setError("Could not load analytics. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  // Fetch phase-batting when tab changes
  useEffect(() => {
    fetchPhaseBatting(activePhase, 10)
      .then((d) => setPhaseLeaders(d.leaders))
      .catch(() => {});
  }, [activePhase]);

  const PHASES: Phase[] = ["powerplay", "middle", "death"];
  const PHASE_LABELS: Record<Phase, string> = { powerplay: "⚡ Powerplay", middle: "🎯 Middle", death: "💀 Death" };

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.8rem", fontWeight: 800, letterSpacing: "-0.5px", marginBottom: "0.35rem" }}>Analytics</h1>
        <p className="muted-text" style={{ fontSize: "0.9rem" }}>Run rate progression · Phase leaders · Bowling rankings</p>
      </div>

      {error && (
        <div style={{ background: "rgba(255,80,80,0.1)", border: "1px solid rgba(255,80,80,0.3)", borderRadius: 10, padding: "0.85rem 1.25rem", marginBottom: "1.5rem", fontSize: "0.85rem", color: "#ff8080" }}>
          ⚠️ {error}
        </div>
      )}

      {/* Run rate chart */}
      <div style={{ marginBottom: "2rem" }}>
        {loading
          ? <div className="card" style={{ minHeight: 290, opacity: 0.3 }} />
          : <RunRateChart data={runRate} />
        }
      </div>

      {/* Phase tabs + leaderboard */}
      <div style={{ marginBottom: "2rem" }}>
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
          {PHASES.map((p) => (
            <button key={p}
              onClick={() => setActivePhase(p)}
              style={{
                background: activePhase === p ? "var(--accent-dim)" : "#111",
                border: `1px solid ${activePhase === p ? "var(--accent)" : "#222"}`,
                color: activePhase === p ? "var(--accent)" : "var(--text-muted)",
                borderRadius: 8, padding: "0.45rem 1rem",
                fontSize: "0.82rem", fontWeight: 600, cursor: "pointer",
              }}
            >{PHASE_LABELS[p]}</button>
          ))}
        </div>

        <Leaderboard
          title={`${PHASE_LABELS[activePhase]} Batting Leaders`}
          items={phaseLeaders.map((l) => ({
            name: l.batter,
            primary: l.total_runs,
            primaryLabel: "runs",
            secondary: l.strike_rate?.toFixed(1),
            secondaryLabel: "SR",
            tertiary: l.boundary_pct?.toFixed(1) + "%",
            tertiaryLabel: "bdry",
          }))}
        />
      </div>

      {/* Bowling leaders */}
      <Leaderboard
        title="🎯 Bowling Leaders"
        accent="#a78bfa"
        items={bowlers.map((b) => ({
          name: b.bowler,
          primary: b.wickets,
          primaryLabel: "wkts",
          secondary: b.economy?.toFixed(2),
          secondaryLabel: "eco",
          tertiary: b.dot_pct?.toFixed(1) + "%",
          tertiaryLabel: "dot%",
        }))}
      />
    </div>
  );
}
