"""
services/thingspeak.py — ThingSpeak API integration.

Responsibilities
----------------
1. Fetch the latest temperature reading from ThingSpeak
2. Fetch historical readings (last N entries)
3. Persist new readings to MongoDB (de-duplicated by entry_id)
"""

import logging
from datetime import datetime, timezone

import requests

from backend.config.settings import Config
from backend.models.temperature import temperature_doc
from backend.utils.db import get_db

logger = logging.getLogger(__name__)


# ── Public API ─────────────────────────────────────────────────────────────────

def fetch_latest() -> dict | None:
    """
    Fetch the single most-recent entry from ThingSpeak.

    Returns a normalised dict:
        {
            "entry_id": int,
            "value": float,       # °C
            "timestamp": datetime
        }
    or None on failure.
    """
    url = (
        f"{Config.THINGSPEAK_BASE_URL}/channels/"
        f"{Config.THINGSPEAK_CHANNEL_ID}/feeds/last.json"
        f"?api_key={Config.THINGSPEAK_READ_API_KEY}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return _parse_entry(data)
    except requests.RequestException as exc:
        logger.error("ThingSpeak fetch_latest failed: %s", exc)
        return None
    except (KeyError, ValueError) as exc:
        logger.error("ThingSpeak parse error: %s", exc)
        return None


def fetch_history(results: int = 100) -> list[dict]:
    """
    Fetch the last `results` entries from ThingSpeak.

    Returns a list of normalised dicts (newest-first).
    """
    url = (
        f"{Config.THINGSPEAK_BASE_URL}/channels/"
        f"{Config.THINGSPEAK_CHANNEL_ID}/feeds.json"
        f"?api_key={Config.THINGSPEAK_READ_API_KEY}"
        f"&results={results}"
    )

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        feeds = resp.json().get("feeds", [])
        parsed = [_parse_entry(f) for f in feeds]
        return [p for p in parsed if p is not None]  # filter failed parses
    except requests.RequestException as exc:
        logger.error("ThingSpeak fetch_history failed: %s", exc)
        return []


def save_reading(entry: dict) -> bool:
    """
    Persist a ThingSpeak entry to MongoDB.
    De-duplicates by entry_id to avoid double-inserts during polling.

    Returns True if inserted, False if already exists or on error.
    """
    db = get_db()
    entry_id = entry.get("entry_id")

    # De-duplication check
    if entry_id and db.temperatures.find_one({"entry_id": entry_id}):
        logger.debug("Duplicate entry_id %s — skipping", entry_id)
        return False

    doc = temperature_doc(entry["value"])
    doc["entry_id"] = entry_id
    doc["timestamp"] = entry["timestamp"]   # use ThingSpeak's timestamp

    try:
        db.temperatures.insert_one(doc)
        logger.info("💾  Saved reading %.2f°C (entry_id=%s)", entry["value"], entry_id)
        return True
    except Exception as exc:
        logger.error("MongoDB insert failed: %s", exc)
        return False


# ── Private helpers ────────────────────────────────────────────────────────────

def _parse_entry(raw: dict) -> dict | None:
    """Convert a raw ThingSpeak feed entry to a clean internal dict."""
    try:
        # ThingSpeak stores field1 as a string; convert to float
        value = float(raw["field1"])
        # ThingSpeak timestamps are ISO-8601 UTC
        ts = datetime.fromisoformat(raw["created_at"].replace("Z", "+00:00"))
        return {
            "entry_id": raw.get("entry_id"),
            "value": value,
            "timestamp": ts,
        }
    except (KeyError, TypeError, ValueError):
        return None
