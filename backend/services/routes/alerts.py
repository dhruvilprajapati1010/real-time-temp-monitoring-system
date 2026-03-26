"""
routes/alerts.py — REST endpoints for alert management.

Endpoints
---------
GET  /api/alerts               → Recent alert history
GET  /api/alerts/stats         → Count by type
POST /api/alerts/test          → Trigger a manual test alert (dev only)
"""

import logging

from flask import Blueprint, jsonify, request

from backend.config.settings import Config
from backend.services import alert as alert_svc
from backend.services.sms import send_sms

logger = logging.getLogger(__name__)
bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


# ── GET /api/alerts ───────────────────────────────────────────────────────────
@bp.route("", methods=["GET"])
def list_alerts():
    """
    Query params
    ------------
    limit : int  — max records to return (default 50)
    type  : str  — filter by alert_type ('HIGH' | 'LOW' | 'RAPID_RISE')
    """
    limit = min(int(request.args.get("limit", 50)), 500)
    alert_type = request.args.get("type")

    from backend.utils.db import get_db
    from datetime import datetime, timezone

    db = get_db()
    query = {}
    if alert_type:
        query["alert_type"] = alert_type.upper()

    docs = list(
        db.alerts.find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )

    for doc in docs:
        if isinstance(doc.get("timestamp"), datetime):
            doc["timestamp"] = doc["timestamp"].isoformat()

    return jsonify({"status": "ok", "count": len(docs), "data": docs})


# ── GET /api/alerts/stats ─────────────────────────────────────────────────────
@bp.route("/stats", methods=["GET"])
def alert_stats():
    """Return count of each alert type over the last 7 days."""
    from backend.utils.db import get_db
    from datetime import datetime, timedelta, timezone

    db = get_db()
    since = datetime.now(timezone.utc) - timedelta(days=7)

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {"_id": "$alert_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    raw = list(db.alerts.aggregate(pipeline))
    stats = {row["_id"]: row["count"] for row in raw}
    total = sum(stats.values())

    return jsonify({
        "status": "ok",
        "data": {
            "HIGH": stats.get("HIGH", 0),
            "LOW": stats.get("LOW", 0),
            "RAPID_RISE": stats.get("RAPID_RISE", 0),
            "total": total,
            "window_days": 7,
        }
    })


# ── POST /api/alerts/test ─────────────────────────────────────────────────────
@bp.route("/test", methods=["POST"])
def test_alert():
    """
    Send a test SMS and optionally create a test alert document.
    Body: { "message": "custom text" }  (optional)
    """
    if Config.FLASK_ENV == "production":
        return jsonify({"error": "Test endpoint disabled in production"}), 403

    body = request.get_json(silent=True) or {}
    message = body.get("message", "🧪 TEST ALERT from IoT Temp Monitor — system OK")

    sms_sent = send_sms(message)
    return jsonify({
        "status": "ok",
        "sms_sent": sms_sent,
        "message": message,
    })
