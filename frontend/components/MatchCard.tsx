"use client";
import { motion } from "framer-motion";
import type { Match } from "@/lib/api";

interface Props { match: Match; index?: number; }

export default function MatchCard({ match, index = 0 }: Props) {
  const date = match.match_date
    ? new Date(match.match_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })
    : "Date TBD";

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04 }}
    >
      {/* Header: season / type */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
        <span className="badge">{match.match_type ?? "T20"}</span>
        <span className="muted-text" style={{ fontSize: "0.72rem" }}>{date}</span>
      </div>

      {/* Teams */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.6rem" }}>
        <span style={{ fontWeight: 700, fontSize: "0.95rem", flex: 1 }}>{match.team1 ?? "TBD"}</span>
        <span className="muted-text" style={{ fontSize: "0.65rem", letterSpacing: "0.1em", fontWeight: 600 }}>VS</span>
        <span style={{ fontWeight: 700, fontSize: "0.95rem", flex: 1, textAlign: "right" }}>{match.team2 ?? "TBD"}</span>
      </div>

      {/* Result */}
      {match.winner && (
        <div style={{
          background: "rgba(0,240,255,0.07)",
          border: "1px solid rgba(0,240,255,0.15)",
          borderRadius: 8,
          padding: "0.4rem 0.75rem",
          fontSize: "0.75rem",
          fontWeight: 500,
          marginBottom: "0.5rem",
        }}>
          🏆 <span className="accent-text">{match.winner}</span> won
        </div>
      )}

      {/* Venue + POTM */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.25rem" }}>
        <span className="muted-text" style={{ fontSize: "0.7rem" }}>📍 {match.city ?? match.venue ?? "—"}</span>
        {match.player_of_match && (
          <span className="muted-text" style={{ fontSize: "0.7rem" }}>⭐ {match.player_of_match}</span>
        )}
      </div>
    </motion.div>
  );
}
