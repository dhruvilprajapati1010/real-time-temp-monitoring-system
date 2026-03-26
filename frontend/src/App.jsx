// src/App.jsx — Root component with routing and global layout

import { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import AlertHistory from "./pages/AlertHistory";

export default function App() {
  const [page, setPage] = useState("dashboard");

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-mono">
      {/* ── Nav ─────────────────────────────────────────────────────────── */}
      <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Animated pulse dot */}
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="text-emerald-400 font-bold text-lg tracking-widest uppercase">
              ThermoWatch
            </span>
            <span className="text-gray-600 text-xs hidden sm:inline">
              IoT Temperature Monitor
            </span>
          </div>

          <div className="flex gap-1">
            {[
              { id: "dashboard", label: "Dashboard" },
              { id: "alerts",    label: "Alerts" },
            ].map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setPage(id)}
                className={`px-4 py-1.5 rounded text-sm transition-all ${
                  page === id
                    ? "bg-emerald-500 text-black font-bold"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* ── Page ────────────────────────────────────────────────────────── */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {page === "dashboard" && <Dashboard />}
        {page === "alerts"    && <AlertHistory />}
      </main>
    </div>
  );
}
