"""
routes/temperature.py — REST endpoints for temperature data.

All responses use JSON.  Timestamps are ISO-8601 UTC strings.

Endpoints
---------
GET  /api/temperature/latest          → Most recent reading
GET  /api/temperature/history?limit=N → Last N readings (newest first)
GET  /api/temperature/stats           → Min / Max / Avg for a time range
POST /api/temperature/seed            → Insert test data (dev only)
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from backend.config.settings import Config
from backend.models.temperature import temperature_doc
from backend.services import thingspeak as ts_svc
from backend.utils.db import get_db

logger = logging.getLogger(__name__)
bp = Blueprint("temperature", __name__, url_prefix="/api/temperature")


# ── GET /api/temperature/latest ───────────────────────────────────────────────
@bp.route("/latest", methods=["GET"])
def get_latest():
    """
    Returns the most recent temperature reading stored in MongoDB.
    Falls back to a live ThingSpeak fetch if the DB is empty.
    """
    db = get_db()
    doc = db.temperatures.find_one({}, sort=[("timestamp", -1)], projection={"_id": 0})

    if doc is None:
        # Try a live fetch as a fallback
        entry = ts_svc.fetch_latest()
        if entry is None:
            return jsonify({"error": "No data available"}), 404
        doc = {
            "value": entry["value"],
            "timestamp": entry["timestamp"].isoformat(),
            "source": "thingspeak-live",
        }
    else:
        doc["timestamp"] = doc["timestamp"].isoformat()

    return jsonify({"status": "ok", "data": doc})


# ── GET /api/temperature/history ──────────────────────────────────────────────
@bp.route("/history", methods=["GET"])
def get_history():
    """
    Query params
    ------------
    limit  : int  — max readings to return (default 100, max 1000)
    hours  : int  — only return readings from the last N hours (optional)
    """
    limit = min(int(request.args.get("limit", 100)), 1000)
    hours = request.args.get("hours", type=int)

    db = get_db()
    query: dict = {}

    if hours:
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query["timestamp"] = {"$gte": since}

    docs = list(
        db.temperatures
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )

    # Serialise datetimes
    for doc in docs:
        doc["timestamp"] = doc["timestamp"].isoformat()

    return jsonify({"status": "ok", "count": len(docs), "data": docs})


# ── GET /api/temperature/stats ────────────────────────────────────────────────
@bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Query params
    ------------
    hours : int — time window in hours (default 24)

    Returns min, max, average, and reading count.
    """
    hours = int(request.args.get("hours", 24))
    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    db = get_db()
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {
            "$group": {
                "_id": None,
                "min": {"$min": "$value"},
                "max": {"$max": "$value"},
                "avg": {"$avg": "$value"},
                "count": {"$sum": 1},
            }
        },
    ]

    result = list(db.temperatures.aggregate(pipeline))
    if not result:
        return jsonify({"status": "ok", "data": None, "message": "No data in window"})

    stats = result[0]
    stats.pop("_id", None)
    stats["avg"] = round(stats["avg"], 2)
    stats["window_hours"] = hours

    return jsonify({"status": "ok", "data": stats})


# ── POST /api/temperature/seed ────────────────────────────────────────────────
@bp.route("/seed", methods=["POST"])
def seed_test_data():
    """
    Insert synthetic test readings (useful for dev/demo without a real device).
    Body (JSON): { "count": 20, "base_temp": 25.0, "variance": 5.0 }
    """
    if Config.FLASK_ENV == "production":
        return jsonify({"error": "Seed endpoint disabled in production"}), 403

    import random
    from datetime import timedelta

    body = request.get_json(silent=True) or {}
    count = min(int(body.get("count", 20)), 200)
    base = float(body.get("base_temp", 25.0))
    variance = float(body.get("variance", 5.0))

    db = get_db()
    docs = []
    now = datetime.now(timezone.utc)

    for i in range(count):
        doc = temperature_doc(base + random.uniform(-variance, variance))
        # Spread readings evenly over the last 24 hours
        doc["timestamp"] = now - timedelta(minutes=(count - i) * (1440 / count))
        doc["source"] = "seed"
        docs.append(doc)

    db.temperatures.insert_many(docs)
    logger.info("🌱  Seeded %d test readings", count)
    return jsonify({"status": "ok", "inserted": count})
