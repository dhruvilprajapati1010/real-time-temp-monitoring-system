// src/pages/AlertHistory.jsx
// Full alert log with filter by type and alert statistics.

import { useState } from "react";
import AlertBadge from "../components/AlertBadge";
import { useAlerts, useAlertStats } from "../hooks/useTemperature";

const TYPES = ["ALL", "HIGH", "LOW", "RAPID_RISE"];

export default function AlertHistory() {
  const [filter, setFilter] = useState("ALL");
  const { alerts, loading, error, refresh } = useAlerts(100, 30_000);
  const { stats, loading: statsLoading } = useAlertStats();

  // Client-side filter (data already fetched)
  const filtered =
    filter === "ALL" ? alerts : alerts.filter((a) => a.alert_type === filter);

  return (
    <div className="space-y-8">
      {/* ── Header ───────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Alert History
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Last 100 alerts — auto-refreshes every 30s
          </p>
        </div>
        <button
          onClick={refresh}
          className="px-3 py-1.5 text-xs font-mono rounded bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition-all self-start"
        >
          ↻ Refresh
        </button>
      </div>

      {/* ── Stats row ────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "HIGH",       key: "HIGH",       color: "text-red-400",    icon: "🌡️" },
          { label: "LOW",        key: "LOW",        color: "text-blue-400",   icon: "🥶" },
          { label: "RAPID RISE", key: "RAPID_RISE", color: "text-amber-400",  icon: "⚡" },
          { label: "TOTAL",      key: "total",      color: "text-gray-300",   icon: "🔔" },
        ].map(({ label, key, color, icon }) => (
          <div
            key={key}
            className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center"
          >
            <p className="text-gray-500 text-xs tracking-widest mb-1 font-mono">
              {icon} {label}
            </p>
            <p className={`text-3xl font-bold font-mono ${color}`}>
              {statsLoading || !stats ? "—" : stats[key] ?? 0}
            </p>
            <p className="text-gray-600 text-xs mt-1 font-mono">last 7 days</p>
          </div>
        ))}
      </div>

      {/* ── Filter tabs ───────────────────────────────────────────────────── */}
      <div className="flex gap-2 flex-wrap">
        {TYPES.map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`px-4 py-1.5 rounded text-xs font-mono font-bold transition-all ${
              filter === t
                ? "bg-emerald-500 text-black"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            {t}
          </button>
        ))}
        <span className="ml-auto text-xs font-mono text-gray-600 self-center">
          {filtered.length} records
        </span>
      </div>

      {/* ── Error banner ──────────────────────────────────────────────────── */}
      {error && (
        <div className="bg-red-950 border border-red-800 text-red-400 rounded-lg px-4 py-3 text-sm font-mono">
          ⚠️ {error}
        </div>
      )}

      {/* ── List ─────────────────────────────────────────────────────────── */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-20 bg-gray-900 border border-gray-800 rounded-lg animate-pulse"
            />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <p className="text-gray-600 font-mono text-sm">
            {filter === "ALL"
              ? "✅ No alerts on record. System is healthy!"
              : `No ${filter} alerts found.`}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((a, i) => (
            <AlertBadge key={i} alert={a} />
          ))}
        </div>
      )}
    </div>
  );
}
