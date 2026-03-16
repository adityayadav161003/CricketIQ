"use client";
import { useEffect, useState } from "react";
import MatchCard from "@/components/MatchCard";
import type { Match } from "@/lib/api";
import { fetchMatches } from "@/lib/api";

export default function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [season, setSeason] = useState("");
  const [offset, setOffset] = useState(0);
  const PAGE_SIZE = 30;

  useEffect(() => {
    setLoading(true);
    fetchMatches(PAGE_SIZE, offset, season || undefined)
      .then((res) => { setMatches(res.matches); setTotal(res.total); })
      .catch(() => setError("Could not load matches. Is the backend running?"))
      .finally(() => setLoading(false));
  }, [offset, season]);

  const SEASONS = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016"];

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.8rem", fontWeight: 800, letterSpacing: "-0.5px", marginBottom: "0.35rem" }}>Match Library</h1>
        <p className="muted-text" style={{ fontSize: "0.9rem" }}>{total.toLocaleString()} matches indexed</p>
      </div>

      {/* Season filter */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <button
          onClick={() => { setSeason(""); setOffset(0); }}
          style={{
            background: !season ? "var(--accent)" : "#161616",
            color: !season ? "#000" : "var(--text-muted)",
            border: "1px solid #222", borderRadius: 8,
            padding: "0.4rem 0.85rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600,
          }}
        >All</button>
        {SEASONS.map((s) => (
          <button key={s}
            onClick={() => { setSeason(s); setOffset(0); }}
            style={{
              background: season === s ? "var(--accent)" : "#161616",
              color: season === s ? "#000" : "var(--text-muted)",
              border: "1px solid #222", borderRadius: 8,
              padding: "0.4rem 0.85rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600,
            }}
          >{s}</button>
        ))}
      </div>

      {error && (
        <div style={{ background: "rgba(255,80,80,0.1)", border: "1px solid rgba(255,80,80,0.3)", borderRadius: 10, padding: "0.85rem 1.25rem", marginBottom: "1.5rem", fontSize: "0.85rem", color: "#ff8080" }}>
          ⚠️ {error}
        </div>
      )}

      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
          {Array.from({ length: 12 }).map((_, i) => <div key={i} className="card" style={{ minHeight: 140, opacity: 0.3 }} />)}
        </div>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
            {matches.map((m, i) => <MatchCard key={m.cricsheet_id} match={m} index={i} />)}
          </div>
          {matches.length === 0 && <p className="muted-text" style={{ marginTop: "2rem", textAlign: "center" }}>No matches found.</p>}

          <div style={{ display: "flex", justifyContent: "center", gap: "1rem", marginTop: "2rem" }}>
            <button className="btn-glow" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
              style={{ opacity: offset === 0 ? 0.35 : 1 }}>← Prev</button>
            <span className="muted-text" style={{ alignSelf: "center", fontSize: "0.8rem" }}>
              {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
            </span>
            <button className="btn-glow" disabled={offset + PAGE_SIZE >= total} onClick={() => setOffset(offset + PAGE_SIZE)}
              style={{ opacity: offset + PAGE_SIZE >= total ? 0.35 : 1 }}>Next →</button>
          </div>
        </>
      )}
    </div>
  );
}
