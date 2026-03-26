"""
services/alert.py — Alert detection & management.

Two alert types
---------------
1. THRESHOLD  : Temperature crosses HIGH or LOW limits
2. RAPID_RISE : Temperature rises more than RAPID_RISE_DELTA °C
                within RAPID_RISE_WINDOW minutes
"""

import logging
from datetime import datetime, timedelta, timezone

from backend.config.settings import Config
from backend.models.temperature import alert_doc
from backend.services.sms import send_sms
from backend.utils.db import get_db

logger = logging.getLogger(__name__)


# ── Public API ─────────────────────────────────────────────────────────────────

def evaluate_temperature(current_temp: float) -> list[dict]:
    """
    Run all alert checks for `current_temp`.
    Persists any triggered alerts and sends SMS (with cooldown).

    Returns a list of alert dicts that were created.
    """
    triggered = []

    # --- Check 1: High threshold ---
    if current_temp >= Config.TEMP_HIGH_THRESHOLD:
        alert = _create_alert(
            alert_type="HIGH",
            temperature=current_temp,
            message=(
                f"🌡️ HIGH TEMP ALERT: {current_temp:.1f}°C — "
                f"exceeds limit of {Config.TEMP_HIGH_THRESHOLD}°C"
            ),
        )
        if alert:
            triggered.append(alert)

    # --- Check 2: Low threshold ---
    elif current_temp <= Config.TEMP_LOW_THRESHOLD:
        alert = _create_alert(
            alert_type="LOW",
            temperature=current_temp,
            message=(
                f"🥶 LOW TEMP ALERT: {current_temp:.1f}°C — "
                f"below limit of {Config.TEMP_LOW_THRESHOLD}°C"
            ),
        )
        if alert:
            triggered.append(alert)

    # --- Check 3: Rapid rise ---
    rapid_alert = _check_rapid_rise(current_temp)
    if rapid_alert:
        triggered.append(rapid_alert)

    return triggered


def get_recent_alerts(limit: int = 50) -> list[dict]:
    """Return the most recent `limit` alerts from MongoDB (newest first)."""
    db = get_db()
    docs = list(
        db.alerts.find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    # Convert datetime → ISO string for JSON serialisation
    for doc in docs:
        doc["timestamp"] = doc["timestamp"].isoformat()
    return docs


# ── Private helpers ────────────────────────────────────────────────────────────

def _create_alert(alert_type: str, temperature: float, message: str) -> dict | None:
    """
    Create, persist, and SMS-notify an alert — if not in cooldown.
    Returns the persisted alert dict or None if suppressed.
    """
    if _in_cooldown(alert_type):
        logger.debug("Alert %s suppressed — cooldown active", alert_type)
        return None

    sms_sent = send_sms(message)

    doc = alert_doc(
        alert_type=alert_type,
        temperature=temperature,
        message=message,
        sms_sent=sms_sent,
    )

    db = get_db()
    db.alerts.insert_one(doc)
    doc.pop("_id", None)
    doc["timestamp"] = doc["timestamp"].isoformat()

    logger.warning("🚨  Alert created: %s", message)
    return doc


def _check_rapid_rise(current_temp: float) -> dict | None:
    """
    Query the last RAPID_RISE_WINDOW minutes of readings.
    If the oldest reading in that window is > RAPID_RISE_DELTA °C below
    current_temp, fire a RAPID_RISE alert.
    """
    db = get_db()
    window_start = datetime.now(timezone.utc) - timedelta(
        minutes=Config.RAPID_RISE_WINDOW
    )

    oldest_in_window = db.temperatures.find_one(
        {"timestamp": {"$gte": window_start}},
        sort=[("timestamp", 1)],          # oldest first
    )

    if not oldest_in_window:
        return None

    delta = current_temp - oldest_in_window["value"]
    if delta >= Config.RAPID_RISE_DELTA:
        return _create_alert(
            alert_type="RAPID_RISE",
            temperature=current_temp,
            message=(
                f"⚡ RAPID RISE ALERT: Temp jumped {delta:.1f}°C in "
                f"{Config.RAPID_RISE_WINDOW} min — now {current_temp:.1f}°C"
            ),
        )
    return None


def _in_cooldown(alert_type: str) -> bool:
    """
    Return True if an alert of `alert_type` was sent within ALERT_COOLDOWN_MINUTES.
    Prevents SMS spam during sustained alert conditions.
    """
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(
        minutes=Config.ALERT_COOLDOWN_MINUTES
    )
    recent = db.alerts.find_one(
        {"alert_type": alert_type, "timestamp": {"$gte": cutoff}},
        sort=[("timestamp", -1)],
    )
    return recent is not None
