// src/pages/Dashboard.jsx
// Main dashboard: live gauge + chart + stats + recent alerts.

import { useState } from "react";
import ThermometerGauge from "../components/ThermometerGauge";
import TemperatureChart from "../components/TemperatureChart";
import StatsCards from "../components/StatsCards";
import AlertBadge from "../components/AlertBadge";
import {
  useLatestTemp,
  useTempHistory,
  useTempStats,
  useAlerts,
} from "../hooks/useTemperature";
import { seedTestData, sendTestAlert } from "../utils/api";

export default function Dashboard() {
  const { temp, timestamp, loading: latestLoading, error: latestError, refresh: refreshLatest } =
    useLatestTemp(30_000);

  const { readings, loading: histLoading } = useTempHistory(100, 24, 30_000);

  const { stats, loading: statsLoading, hours, setHours } = useTempStats();

  const { alerts, loading: alertsLoading } = useAlerts(5, 30_000);

  const [seeding, setSeeding] = useState(false);
  const [seedMsg, setSeedMsg] = useState("");
  const [testSmsMsg, setTestSmsMsg] = useState("");

  async function handleSeed() {
    setSeeding(true);
    setSeedMsg("");
    const { error } = await seedTestData(60);
    setSeedMsg(error ? `Error: ${error}` : "✅ 60 test readings inserted!");
    setSeeding(false);
    setTimeout(() => setSeedMsg(""), 4000);
  }

  async function handleTestSms() {
    setTestSmsMsg("Sending…");
    const { data, error } = await sendTestAlert();
    setTestSmsMsg(
      error ? `Error: ${error}` : data?.sms_sent ? "📱 SMS sent!" : "⚠️ SMS skipped (Twilio not configured)"
    );
    setTimeout(() => setTestSmsMsg(""), 5000);
  }

  return (
    <div className="space-y-8">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Live Dashboard
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1">
            Last updated:{" "}
            {timestamp
              ? new Date(timestamp).toLocaleTimeString()
              : latestLoading
              ? "Loading…"
              : "N/A"}
          </p>
        </div>

        {/* Dev tools */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={handleSeed}
            disabled={seeding}
            className="px-3 py-1.5 text-xs font-mono rounded bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition-all disabled:opacity-50"
          >
            {seeding ? "Seeding…" : "🌱 Seed Data"}
          </button>
          <button
            onClick={handleTestSms}
            className="px-3 py-1.5 text-xs font-mono rounded bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition-all"
          >
            📱 Test SMS
          </button>
        </div>
      </div>

      {/* Feedback messages */}
      {seedMsg && (
        <p className="text-xs font-mono text-emerald-400 -mt-4">{seedMsg}</p>
      )}
      {testSmsMsg && (
        <p className="text-xs font-mono text-amber-400 -mt-4">{testSmsMsg}</p>
      )}

      {/* Error banner */}
      {latestError && (
        <div className="bg-red-950 border border-red-800 text-red-400 rounded-lg px-4 py-3 text-sm font-mono">
          ⚠️ API error: {latestError}. Make sure your Flask backend is running on port 5000.
        </div>
      )}

      {/* ── Top row: Gauge + current stats ──────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Gauge card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col items-center justify-center gap-4">
          <ThermometerGauge temperature={temp} loading={latestLoading} />
          <button
            onClick={refreshLatest}
            className="text-xs font-mono text-gray-600 hover:text-emerald-400 transition-colors"
          >
            ↻ Refresh
          </button>
        </div>

        {/* Stats cards — spans 2 columns */}
        <div className="md:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-xs font-bold text-gray-500 tracking-widest uppercase mb-4">
            Statistics
          </h2>
          <StatsCards
            stats={stats}
            loading={statsLoading}
            hours={hours}
            setHours={setHours}
          />
        </div>
      </div>

      {/* ── Chart ───────────────────────────────────────────────────────── */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-bold text-gray-500 tracking-widest uppercase">
            Temperature History (last 24h)
          </h2>
          <span className="text-xs font-mono text-gray-600">
            {readings.length} readings
          </span>
        </div>
        <TemperatureChart readings={readings} loading={histLoading} />
      </div>

      {/* ── Recent alerts ────────────────────────────────────────────────── */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xs font-bold text-gray-500 tracking-widest uppercase mb-4">
          Recent Alerts
        </h2>
        {alertsLoading ? (
          <p className="text-gray-600 text-sm font-mono animate-pulse">Loading alerts…</p>
        ) : alerts.length === 0 ? (
          <p className="text-gray-600 text-sm font-mono">
            ✅ No alerts yet — system is operating within thresholds.
          </p>
        ) : (
          <div className="space-y-3">
            {alerts.map((a, i) => (
              <AlertBadge key={i} alert={a} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
