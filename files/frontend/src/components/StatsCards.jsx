// src/components/StatsCards.jsx
// Displays min / max / avg / count for the selected time window.

export default function StatsCards({ stats, loading, hours, setHours }) {
  const windows = [1, 6, 24, 72];

  const cards = [
    { label: "MIN",   key: "min",   unit: "°C", color: "text-blue-400"   },
    { label: "MAX",   key: "max",   unit: "°C", color: "text-red-400"    },
    { label: "AVG",   key: "avg",   unit: "°C", color: "text-emerald-400"},
    { label: "READS", key: "count", unit: "",   color: "text-gray-300"   },
  ];

  return (
    <div>
      {/* Time window selector */}
      <div className="flex gap-2 mb-4">
        {windows.map((h) => (
          <button
            key={h}
            onClick={() => setHours(h)}
            className={`px-3 py-1 rounded text-xs font-mono transition-all ${
              hours === h
                ? "bg-emerald-500 text-black font-bold"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            {h}h
          </button>
        ))}
      </div>

      {/* Cards grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {cards.map(({ label, key, unit, color }) => (
          <div
            key={key}
            className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center"
          >
            <p className="text-gray-500 text-xs tracking-widest mb-1">{label}</p>
            <p className={`text-2xl font-bold font-mono ${color}`}>
              {loading || !stats
                ? "—"
                : stats[key] !== undefined
                ? `${stats[key]}${unit}`
                : "—"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
