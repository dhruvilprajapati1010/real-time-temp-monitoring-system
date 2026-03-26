"""
models/temperature.py — MongoDB document schemas using PyMongo.

We use plain dicts (not an ORM) to stay lightweight.
Each helper returns a dict ready to be inserted into MongoDB.
"""

from datetime import datetime, timezone


def temperature_doc(value: float, source: str = "thingspeak") -> dict:
    """
    Schema for a single temperature reading.

    Fields
    ------
    value    : Temperature in °C
    source   : Where the reading came from (e.g. 'thingspeak', 'manual')
    timestamp: UTC datetime of the reading
    """
    return {
        "value": round(float(value), 2),
        "source": source,
        "timestamp": datetime.now(timezone.utc),
    }


def alert_doc(
    alert_type: str,
    temperature: float,
    message: str,
    sms_sent: bool = False,
) -> dict:
    """
    Schema for an alert event.

    Fields
    ------
    alert_type  : 'HIGH' | 'LOW' | 'RAPID_RISE'
    temperature : Temperature that triggered the alert (°C)
    message     : Human-readable description
    sms_sent    : Whether an SMS was successfully delivered
    timestamp   : UTC datetime of the alert
    """
    return {
        "alert_type": alert_type,
        "temperature": round(float(temperature), 2),
        "message": message,
        "sms_sent": sms_sent,
        "timestamp": datetime.now(timezone.utc),
    }
