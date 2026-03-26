// src/components/ThermometerGauge.jsx
// An animated circular gauge that visualises current temperature.

import { useMemo } from "react";

const MIN_TEMP = -10;
const MAX_TEMP = 60;

/**
 * Maps a temperature value to a colour string.
 * Cold → blue, normal → emerald, warm → amber, hot → red.
 */
function tempColor(t) {
  if (t === null) return "#6b7280"; // gray
  if (t < 10)  return "#60a5fa"; // blue-400
  if (t < 25)  return "#34d399"; // emerald-400
  if (t < 35)  return "#fbbf24"; // amber-400
  return "#f87171";               // red-400
}

function tempLabel(t) {
  if (t === null) return "—";
  if (t < 10)  return "COLD";
  if (t < 25)  return "NORMAL";
  if (t < 35)  return "WARM";
  return "HOT";
}

export default function ThermometerGauge({ temperature, loading }) {
  const color = tempColor(temperature);
  const label = tempLabel(temperature);

  // Arc parameters (SVG circle)
  const radius = 80;
  const cx = 100;
  const cy = 100;
  const circumference = 2 * Math.PI * radius;

  // Map temperature to 0–1 progress (clamped)
  const progress = useMemo(() => {
    if (temperature === null) return 0;
    const clamped = Math.max(MIN_TEMP, Math.min(MAX_TEMP, temperature));
    return (clamped - MIN_TEMP) / (MAX_TEMP - MIN_TEMP);
  }, [temperature]);

  const dashOffset = circumference * (1 - progress);

  return (
    <div className="flex flex-col items-center gap-2">
      <svg
        viewBox="0 0 200 200"
        className="w-48 h-48 drop-shadow-lg"
        style={{ filter: `drop-shadow(0 0 16px ${color}44)` }}
      >
        {/* Background track */}
        <circle
          cx={cx} cy={cy} r={radius}
          fill="none"
          stroke="#1f2937"
          strokeWidth={14}
        />

        {/* Progress arc — rotate so it starts at bottom-left */}
        <circle
          cx={cx} cy={cy} r={radius}
          fill="none"
          stroke={color}
          strokeWidth={14}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={loading ? circumference : dashOffset}
          transform="rotate(-90 100 100)"
          style={{ transition: "stroke-dashoffset 1s ease, stroke 0.5s ease" }}
        />

        {/* Temperature text */}
        <text
          x={cx} y={cy - 8}
          textAnchor="middle"
          fontSize="32"
          fontWeight="bold"
          fill={color}
          fontFamily="monospace"
          style={{ transition: "fill 0.5s ease" }}
        >
          {loading ? "..." : temperature !== null ? `${temperature.toFixed(1)}` : "N/A"}
        </text>

        {/* °C unit */}
        <text x={cx} y={cy + 18} textAnchor="middle" fontSize="14" fill="#9ca3af" fontFamily="monospace">
          °C
        </text>

        {/* Status label */}
        <text
          x={cx} y={cy + 40}
          textAnchor="middle"
          fontSize="10"
          fill={color}
          fontFamily="monospace"
          letterSpacing="3"
        >
          {loading ? "LOADING" : label}
        </text>
      </svg>
    </div>
  );
}
