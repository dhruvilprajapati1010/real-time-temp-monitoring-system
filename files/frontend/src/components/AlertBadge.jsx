// src/components/AlertBadge.jsx
// A styled badge that colours itself based on alert type.

const CONFIG = {
  HIGH:       { label: "HIGH TEMP",   bg: "bg-red-950",    border: "border-red-700",    text: "text-red-400",    icon: "🌡️" },
  LOW:        { label: "LOW TEMP",    bg: "bg-blue-950",   border: "border-blue-700",   text: "text-blue-400",   icon: "🥶" },
  RAPID_RISE: { label: "RAPID RISE",  bg: "bg-amber-950",  border: "border-amber-700",  text: "text-amber-400",  icon: "⚡" },
  DEFAULT:    { label: "ALERT",       bg: "bg-gray-900",   border: "border-gray-700",   text: "text-gray-400",   icon: "🔔" },
};

/**
 * Format an ISO UTC timestamp to a human-readable local time.
 */
function fmtDateTime(iso) {
  return new Date(iso).toLocaleString([], {
    month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export default function AlertBadge({ alert }) {
  const cfg = CONFIG[alert.alert_type] ?? CONFIG.DEFAULT;

  return (
    <div className={`rounded-lg border ${cfg.bg} ${cfg.border} p-4 flex items-start gap-3`}>
      {/* Icon */}
      <span className="text-xl mt-0.5">{cfg.icon}</span>

      {/* Body */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 flex-wrap">
          {/* Type pill */}
          <span className={`text-xs font-bold tracking-widest ${cfg.text} font-mono`}>
            {cfg.label}
          </span>
          {/* SMS sent indicator */}
          {alert.sms_sent && (
            <span className="text-xs text-gray-500 font-mono">📱 SMS sent</span>
          )}
        </div>

        {/* Message */}
        <p className="text-gray-300 text-sm mt-1 font-mono">{alert.message}</p>

        {/* Footer: temperature + timestamp */}
        <div className="flex gap-4 mt-2 text-xs text-gray-500 font-mono">
          <span>{alert.temperature?.toFixed(1)}°C</span>
          <span>{fmtDateTime(alert.timestamp)}</span>
        </div>
      </div>
    </div>
  );
}
