"use client";
import { motion } from "framer-motion";
import type { Player, BowlerStat } from "@/lib/api";

interface Props {
  player: Player;
  bowling?: BowlerStat | null;
  rank?: number;
}

export default function PlayerCard({ player, bowling, rank }: Props) {
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: (rank ?? 0) * 0.04 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          {rank != null && (
            <span className="badge" style={{ marginBottom: "0.4rem", display: "block", width: "fit-content" }}>
              #{rank}
            </span>
          )}
          <h3 style={{ fontWeight: 700, fontSize: "1rem", letterSpacing: "-0.3px" }}>{player.batter}</h3>
          <p className="muted-text" style={{ fontSize: "0.75rem", marginTop: "0.15rem" }}>
            {player.matches} matches · {player.innings} innings
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="stat-value">{player.total_runs}</div>
          <div className="muted-text" style={{ fontSize: "0.7rem" }}>Total Runs</div>
        </div>
      </div>

      {/* Batting stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "0.5rem", marginBottom: bowling ? "1rem" : 0 }}>
        {[
          { label: "SR", value: player.strike_rate?.toFixed(1) },
          { label: "AVG", value: player.average?.toFixed(1) ?? "—" },
          { label: "4s", value: player.fours },
          { label: "6s", value: player.sixes },
        ].map(({ label, value }) => (
          <div key={label} style={{ background: "#161616", borderRadius: 8, padding: "0.4rem 0.5rem", textAlign: "center" }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 600 }}>{value}</div>
            <div className="muted-text" style={{ fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Bowling summary (if available) */}
      {bowling && (
        <div style={{ borderTop: "1px solid #1a1a1a", paddingTop: "0.75rem", display: "flex", gap: "1rem" }}>
          <div>
            <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--accent)" }}>{bowling.wickets}</span>
            <span className="muted-text" style={{ fontSize: "0.65rem", marginLeft: "0.3rem" }}>wkts</span>
          </div>
          <div>
            <span style={{ fontSize: "0.75rem", fontWeight: 600 }}>{bowling.economy?.toFixed(2)}</span>
            <span className="muted-text" style={{ fontSize: "0.65rem", marginLeft: "0.3rem" }}>econ</span>
          </div>
        </div>
      )}
    </motion.div>
  );
}
