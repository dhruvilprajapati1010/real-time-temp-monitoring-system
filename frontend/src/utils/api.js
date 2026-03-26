// src/utils/api.js — Centralised API client
// Change BASE_URL in .env to point to your Flask backend.

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

/**
 * Generic fetch wrapper with error handling.
 * Always returns { data, error } — never throws.
 */
async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      return { data: null, error: body.error || `HTTP ${res.status}` };
    }

    const json = await res.json();
    return { data: json.data ?? json, error: null };
  } catch (err) {
    return { data: null, error: err.message || "Network error" };
  }
}

// ── Temperature endpoints ──────────────────────────────────────────────────────

/** Fetch the single latest temperature reading */
export const fetchLatestTemp = () => apiFetch("/api/temperature/latest");

/**
 * Fetch temperature history.
 * @param {number} limit  - max records
 * @param {number} [hours] - only last N hours (optional)
 */
export const fetchTempHistory = (limit = 100, hours) => {
  const params = new URLSearchParams({ limit });
  if (hours) params.set("hours", hours);
  return apiFetch(`/api/temperature/history?${params}`);
};

/**
 * Fetch min/max/avg stats.
 * @param {number} hours - time window
 */
export const fetchTempStats = (hours = 24) =>
  apiFetch(`/api/temperature/stats?hours=${hours}`);

/**
 * Seed test data (dev only).
 * @param {number} count
 */
export const seedTestData = (count = 50) =>
  apiFetch("/api/temperature/seed", {
    method: "POST",
    body: JSON.stringify({ count, base_temp: 25, variance: 8 }),
  });

// ── Alert endpoints ────────────────────────────────────────────────────────────

/**
 * Fetch alert history.
 * @param {number} limit
 * @param {string} [type] - 'HIGH' | 'LOW' | 'RAPID_RISE'
 */
export const fetchAlerts = (limit = 50, type) => {
  const params = new URLSearchParams({ limit });
  if (type) params.set("type", type);
  return apiFetch(`/api/alerts?${params}`);
};

/** Fetch alert counts by type (last 7 days) */
export const fetchAlertStats = () => apiFetch("/api/alerts/stats");

/** Send a test SMS alert */
export const sendTestAlert = () =>
  apiFetch("/api/alerts/test", { method: "POST" });
