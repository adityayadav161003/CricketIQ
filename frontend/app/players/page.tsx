"use client";
import { useEffect, useState } from "react";
import PlayerCard from "@/components/PlayerCard";
import type { Player } from "@/lib/api";
import { fetchPlayers } from "@/lib/api";

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const PAGE_SIZE = 24;

  useEffect(() => {
    setLoading(true);
    fetchPlayers(PAGE_SIZE, offset)
      .then((res) => { setPlayers(res.players); setTotal(res.total); })
      .catch(() => setError("Could not load players. Is the backend running?"))
      .finally(() => setLoading(false));
  }, [offset]);

  const displayed = players.filter((p) =>
    p.batter.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.8rem", fontWeight: 800, letterSpacing: "-0.5px", marginBottom: "0.35rem" }}>
          Player Statistics
        </h1>
        <p className="muted-text" style={{ fontSize: "0.9rem" }}>
          {total.toLocaleString()} players · Career batting analytics
        </p>
      </div>

      {/* Search */}
      <div style={{ marginBottom: "1.5rem" }}>
        <input
          type="text"
          placeholder="Search player..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            background: "#111", border: "1px solid #222", borderRadius: 8,
            padding: "0.6rem 1rem", color: "var(--text)", fontSize: "0.875rem",
            width: 280, outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "var(--accent)")}
          onBlur={(e) => (e.target.style.borderColor = "#222")}
        />
      </div>

      {/* Error */}
      {error && (
        <div style={{ background: "rgba(255,80,80,0.1)", border: "1px solid rgba(255,80,80,0.3)", borderRadius: 10, padding: "0.85rem 1.25rem", marginBottom: "1.5rem", fontSize: "0.85rem", color: "#ff8080" }}>
          ⚠️ {error}
        </div>
      )}

      {/* Grid */}
      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="card" style={{ minHeight: 140, opacity: 0.3 }} />
          ))}
        </div>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
            {displayed.map((player, i) => (
              <PlayerCard key={player.batter} player={player} rank={offset + i + 1} />
            ))}
          </div>
          {displayed.length === 0 && <p className="muted-text" style={{ marginTop: "2rem", textAlign: "center" }}>No players found.</p>}

          {/* Pagination */}
          {!search && (
            <div style={{ display: "flex", justifyContent: "center", gap: "1rem", marginTop: "2rem" }}>
              <button className="btn-glow" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                style={{ opacity: offset === 0 ? 0.35 : 1 }}>← Prev</button>
              <span className="muted-text" style={{ alignSelf: "center", fontSize: "0.8rem" }}>
                {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
              </span>
              <button className="btn-glow" disabled={offset + PAGE_SIZE >= total} onClick={() => setOffset(offset + PAGE_SIZE)}
                style={{ opacity: offset + PAGE_SIZE >= total ? 0.35 : 1 }}>Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
