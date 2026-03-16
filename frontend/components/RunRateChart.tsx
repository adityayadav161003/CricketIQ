"use client";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import type { RunRatePoint } from "@/lib/api";

interface Props { data: RunRatePoint[]; }

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#111", border: "1px solid #333", borderRadius: 8,
      padding: "0.6rem 0.9rem", fontSize: "0.8rem",
    }}>
      <p style={{ color: "var(--text-muted)", marginBottom: 4 }}>Over {label}</p>
      <p style={{ color: "var(--accent)", fontWeight: 700 }}>
        {payload[0]?.value?.toFixed(2)} avg runs
      </p>
      <p style={{ color: "#888", fontSize: "0.72rem" }}>
        {payload[1]?.value?.toFixed(2)} avg wickets
      </p>
    </div>
  );
};

export default function RunRateChart({ data }: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="card" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: 220 }}>
        <p className="muted-text">No run rate data available.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 style={{ fontWeight: 700, fontSize: "0.85rem", letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "1rem" }}>
        Average Run Rate Per Over
      </h3>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="runsGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00F0FF" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1a1a1a" strokeDasharray="3 3" />
          <XAxis
            dataKey="over_display"
            tick={{ fill: "#666", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "#222" }}
            label={{ value: "Over", position: "insideBottom", offset: -2, fill: "#555", fontSize: 10 }}
          />
          <YAxis tick={{ fill: "#666", fontSize: 11 }} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          {/* Phase boundaries */}
          <ReferenceLine x={6}  stroke="#333" strokeDasharray="4 4" label={{ value: "PP", fill: "#555", fontSize: 10 }} />
          <ReferenceLine x={15} stroke="#333" strokeDasharray="4 4" label={{ value: "Death", fill: "#555", fontSize: 10 }} />
          <Area
            type="monotone" dataKey="avg_runs"
            stroke="#00F0FF" strokeWidth={2}
            fill="url(#runsGrad)" dot={false} activeDot={{ r: 4, fill: "#00F0FF" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
