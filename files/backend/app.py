"""
app.py — Flask application factory.

Usage
-----
Development : python app.py
Production  : gunicorn "app:create_app()" --workers 2 --bind 0.0.0.0:5000
"""

import logging
import sys

from flask import Flask, jsonify
from flask_cors import CORS

from backend.config.settings import Config
from backend.routes import alerts, temperature
from backend.services import poller


def create_app() -> Flask:
    """
    Application factory pattern.
    Allows easy testing by calling create_app() with a test config.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Allow the React dev server (port 3000) and the same-origin in production
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Logging ────────────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # ── Blueprints ─────────────────────────────────────────────────────────────
    app.register_blueprint(temperature.bp)
    app.register_blueprint(alerts.bp)

    # ── Health check ───────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "IoT Temp Monitor API"})

    # ── Global error handlers ──────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(exc):
        logging.getLogger(__name__).error("Unhandled 500: %s", exc)
        return jsonify({"error": "Internal server error"}), 500

    # ── Start background poller ────────────────────────────────────────────────
    # Only start in the main process (not Flask's reloader subprocess)
    import os
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true" or Config.FLASK_ENV == "production":
        poller.start()

    return app


# ── Dev entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=(Config.FLASK_ENV == "development"),
        use_reloader=False,   # Disable reloader to avoid double-starting the poller
    )
