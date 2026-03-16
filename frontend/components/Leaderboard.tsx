"use client";
import { motion } from "framer-motion";

interface LeaderItem {
  name: string;
  primary: string | number;
  primaryLabel: string;
  secondary?: string | number;
  secondaryLabel?: string;
  tertiary?: string | number;
  tertiaryLabel?: string;
}

interface Props {
  title: string;
  accent?: string;
  items: LeaderItem[];
}

export default function Leaderboard({ title, items, accent = "var(--accent)" }: Props) {
  return (
    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid #1a1a1a" }}>
        <h2 style={{ fontWeight: 700, fontSize: "0.9rem", letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--text-muted)" }}>
          {title}
        </h2>
      </div>

      <div>
        {items.map((item, i) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.25, delay: i * 0.035 }}
            style={{
              display: "flex",
              alignItems: "center",
              padding: "0.65rem 1.25rem",
              borderBottom: i < items.length - 1 ? "1px solid #161616" : "none",
              transition: "background 0.15s",
            }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.background = "#161616")}
            onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.background = "transparent")}
          >
            {/* Rank */}
            <div style={{
              width: 24, minWidth: 24, fontWeight: 700, fontSize: "0.75rem",
              color: i < 3 ? accent : "var(--text-muted)",
            }}>
              {i + 1}
            </div>

            {/* Name */}
            <div style={{ flex: 1, fontWeight: 600, fontSize: "0.88rem", paddingLeft: "0.5rem" }}>
              {item.name}
            </div>

            {/* Stats */}
            <div style={{ display: "flex", gap: "1.25rem", alignItems: "center" }}>
              {item.tertiary != null && (
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600 }}>{item.tertiary}</div>
                  <div style={{ fontSize: "0.6rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{item.tertiaryLabel}</div>
                </div>
              )}
              {item.secondary != null && (
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600 }}>{item.secondary}</div>
                  <div style={{ fontSize: "0.6rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{item.secondaryLabel}</div>
                </div>
              )}
              <div style={{ textAlign: "right", minWidth: 48 }}>
                <div style={{ fontSize: "1rem", fontWeight: 700, color: accent }}>{item.primary}</div>
                <div style={{ fontSize: "0.6rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{item.primaryLabel}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
