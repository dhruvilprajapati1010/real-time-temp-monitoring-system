// src/components/TemperatureChart.jsx
// Line chart showing temperature history using Chart.js + react-chartjs-2.

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { useMemo } from "react";

ChartJS.register(
  CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler
);

/**
 * Format a UTC ISO timestamp to a short HH:MM label.
 */
function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function TemperatureChart({ readings, loading }) {
  const { labels, values } = useMemo(() => {
    const sorted = [...readings].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    return {
      labels: sorted.map((r) => fmtTime(r.timestamp)),
      values: sorted.map((r) => r.value),
    };
  }, [readings]);

  const data = {
    labels,
    datasets: [
      {
        label: "Temperature (°C)",
        data: values,
        borderColor: "#34d399",           // emerald-400
        backgroundColor: "rgba(52,211,153,0.08)",
        pointBackgroundColor: values.map((v) =>
          v >= 40 ? "#f87171" : v <= 0 ? "#60a5fa" : "#34d399"
        ),
        pointRadius: 3,
        pointHoverRadius: 6,
        fill: true,
        tension: 0.35,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 600 },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#111827",
        borderColor: "#374151",
        borderWidth: 1,
        titleColor: "#9ca3af",
        bodyColor: "#f9fafb",
        callbacks: {
          label: (ctx) => ` ${ctx.parsed.y.toFixed(1)} °C`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: "#1f2937" },
        ticks: {
          color: "#6b7280",
          maxTicksLimit: 10,
          font: { family: "monospace", size: 11 },
        },
      },
      y: {
        grid: { color: "#1f2937" },
        ticks: {
          color: "#6b7280",
          font: { family: "monospace", size: 11 },
          callback: (v) => `${v}°C`,
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-600 animate-pulse">
        Loading chart…
      </div>
    );
  }

  if (!readings.length) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-600">
        No data yet — seed some test data or connect your ESP8266.
      </div>
    );
  }

  return (
    <div className="h-64">
      <Line data={data} options={options} />
    </div>
  );
}
