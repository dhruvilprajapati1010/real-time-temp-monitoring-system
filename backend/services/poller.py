"""
services/poller.py — Background polling loop.

Runs in a daemon thread so Flask stays non-blocking.
Every POLL_INTERVAL_SECONDS it:
  1. Fetches the latest reading from ThingSpeak
  2. Saves it to MongoDB
  3. Runs alert evaluation
"""

import logging
import threading
import time

from backend.config.settings import Config
from backend.services import alert as alert_svc
from backend.services import thingspeak as ts_svc

logger = logging.getLogger(__name__)

_poll_thread: threading.Thread | None = None
_stop_event = threading.Event()


def start() -> None:
    """Start the background polling thread (idempotent)."""
    global _poll_thread

    if _poll_thread and _poll_thread.is_alive():
        logger.info("Poller already running")
        return

    _stop_event.clear()
    _poll_thread = threading.Thread(target=_loop, daemon=True, name="temp-poller")
    _poll_thread.start()
    logger.info(
        "🔄  Poller started — interval: %ds", Config.POLL_INTERVAL_SECONDS
    )


def stop() -> None:
    """Signal the polling thread to exit gracefully."""
    _stop_event.set()
    logger.info("Poller stop requested")


def _loop() -> None:
    """Inner polling loop — runs until stop() is called."""
    while not _stop_event.is_set():
        try:
            _poll_once()
        except Exception as exc:
            # Never let an unhandled exception kill the poller thread
            logger.error("Poller unhandled error: %s", exc, exc_info=True)

        # Use wait() instead of sleep() so stop() can interrupt immediately
        _stop_event.wait(timeout=Config.POLL_INTERVAL_SECONDS)

    logger.info("Poller stopped")


def _poll_once() -> None:
    """Fetch → Save → Evaluate one reading cycle."""
    entry = ts_svc.fetch_latest()
    if entry is None:
        logger.warning("No data from ThingSpeak — will retry next cycle")
        return

    saved = ts_svc.save_reading(entry)

    if saved:
        alerts = alert_svc.evaluate_temperature(entry["value"])
        if alerts:
            logger.warning("Triggered %d alert(s) for %.2f°C", len(alerts), entry["value"])
        else:
            logger.info("✅  Reading OK: %.2f°C", entry["value"])
