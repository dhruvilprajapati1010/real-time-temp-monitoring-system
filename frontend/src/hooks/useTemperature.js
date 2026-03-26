// src/hooks/useTemperature.js — Reactive data hooks with auto-refresh

import { useState, useEffect, useCallback, useRef } from "react";
import {
  fetchLatestTemp,
  fetchTempHistory,
  fetchTempStats,
  fetchAlerts,
  fetchAlertStats,
} from "../utils/api";

const DEFAULT_REFRESH_MS = 30_000; // 30 seconds

/**
 * useLatestTemp — Polls the latest temperature reading.
 *
 * Returns: { temp, timestamp, loading, error, refresh }
 */
export function useLatestTemp(intervalMs = DEFAULT_REFRESH_MS) {
  const [state, setState] = useState({ temp: null, timestamp: null, loading: true, error: null });
  const timerRef = useRef(null);

  const refresh = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    const { data, error } = await fetchLatestTemp();
    setState({
      temp: data?.value ?? null,
      timestamp: data?.timestamp ?? null,
      loading: false,
      error,
    });
  }, []);

  useEffect(() => {
    refresh();
    timerRef.current = setInterval(refresh, intervalMs);
    return () => clearInterval(timerRef.current);
  }, [refresh, intervalMs]);

  return { ...state, refresh };
}

/**
 * useTempHistory — Fetches temperature history with configurable window.
 *
 * Returns: { readings, loading, error, refresh }
 */
export function useTempHistory(limit = 100, hours = 24, intervalMs = DEFAULT_REFRESH_MS) {
  const [state, setState] = useState({ readings: [], loading: true, error: null });

  const refresh = useCallback(async () => {
    setState((s) => ({ ...s, loading: true }));
    const { data, error } = await fetchTempHistory(limit, hours);
    setState({
      readings: Array.isArray(data) ? [...data].reverse() : [], // oldest-first for chart
      loading: false,
      error,
    });
  }, [limit, hours]);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, intervalMs);
    return () => clearInterval(timer);
  }, [refresh, intervalMs]);

  return { ...state, refresh };
}

/**
 * useTempStats — Fetches min/max/avg statistics.
 *
 * Returns: { stats, loading, error, setHours }
 */
export function useTempStats() {
  const [hours, setHours] = useState(24);
  const [state, setState] = useState({ stats: null, loading: true, error: null });

  useEffect(() => {
    let active = true;
    setState((s) => ({ ...s, loading: true }));
    fetchTempStats(hours).then(({ data, error }) => {
      if (active) setState({ stats: data, loading: false, error });
    });
    return () => { active = false; };
  }, [hours]);

  return { ...state, hours, setHours };
}

/**
 * useAlerts — Fetches alert history.
 *
 * Returns: { alerts, loading, error, refresh }
 */
export function useAlerts(limit = 50, intervalMs = DEFAULT_REFRESH_MS) {
  const [state, setState] = useState({ alerts: [], loading: true, error: null });

  const refresh = useCallback(async () => {
    const { data, error } = await fetchAlerts(limit);
    setState({ alerts: Array.isArray(data) ? data : [], loading: false, error });
  }, [limit]);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, intervalMs);
    return () => clearInterval(timer);
  }, [refresh, intervalMs]);

  return { ...state, refresh };
}

/**
 * useAlertStats — Fetches alert counts by type.
 */
export function useAlertStats() {
  const [state, setState] = useState({ stats: null, loading: true, error: null });

  useEffect(() => {
    fetchAlertStats().then(({ data, error }) => {
      setState({ stats: data, loading: false, error });
    });
  }, []);

  return state;
}
