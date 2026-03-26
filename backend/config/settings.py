"""
settings.py — Centralised configuration loader.
Reads all secrets from environment variables (or .env via python-dotenv).
Never hard-code credentials here; always use .env.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file from project root


class Config:
    # ── MongoDB ────────────────────────────────────────────────────────────────
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "iot_temp_monitor")

    # ── ThingSpeak ─────────────────────────────────────────────────────────────
    THINGSPEAK_READ_API_KEY: str = os.getenv("THINGSPEAK_READ_API_KEY", "")
    THINGSPEAK_CHANNEL_ID: str = os.getenv("THINGSPEAK_CHANNEL_ID", "")
    THINGSPEAK_BASE_URL: str = "https://api.thingspeak.com"

    # ── Twilio ─────────────────────────────────────────────────────────────────
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")   # e.g. +14155552671
    ALERT_TO_NUMBER: str = os.getenv("ALERT_TO_NUMBER", "")         # your phone number

    # ── Alert Thresholds ───────────────────────────────────────────────────────
    TEMP_HIGH_THRESHOLD: float = float(os.getenv("TEMP_HIGH_THRESHOLD", "40.0"))   # °C
    TEMP_LOW_THRESHOLD: float = float(os.getenv("TEMP_LOW_THRESHOLD", "0.0"))      # °C
    RAPID_RISE_DELTA: float = float(os.getenv("RAPID_RISE_DELTA", "5.0"))          # °C
    RAPID_RISE_WINDOW: int = int(os.getenv("RAPID_RISE_WINDOW", "5"))              # minutes

    # ── Flask ──────────────────────────────────────────────────────────────────
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    PORT: int = int(os.getenv("PORT", "5000"))

    # ── Polling ────────────────────────────────────────────────────────────────
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))

    # Cooldown between SMS alerts for the same alert type (minutes)
    ALERT_COOLDOWN_MINUTES: int = int(os.getenv("ALERT_COOLDOWN_MINUTES", "15"))
