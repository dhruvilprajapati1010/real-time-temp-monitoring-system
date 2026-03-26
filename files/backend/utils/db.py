"""
utils/db.py — MongoDB Atlas connection manager.

Uses a module-level singleton so the connection is reused
across requests (important for Flask in production).
"""

import logging
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from backend.config.settings import Config

logger = logging.getLogger(__name__)

# ── Singleton client ───────────────────────────────────────────────────────────
_client: MongoClient | None = None


class MockCollection:
    """Mock MongoDB collection for development when DB is unavailable."""
    
    def __init__(self):
        self.data = []
    
    def find_one(self, query=None, *args, **kwargs):
        if not self.data:
            return None
        # Simple mock: return the first item
        return self.data[0] if self.data else None
    
    def find(self, query=None, projection=None):
        return MockCursor(self.data)
    
    def insert_many(self, docs):
        self.data.extend(docs)
    
    def aggregate(self, pipeline):
        # Simple mock for stats
        if not self.data:
            return []
        values = [doc['value'] for doc in self.data]
        return [{
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }]


class MockCursor:
    """Mock cursor for find operations."""
    
    def __init__(self, data):
        self.data = data
    
    def sort(self, key, direction):
        # Simple sort by timestamp desc
        if key == 'timestamp' and direction == -1:
            self.data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return self
    
    def limit(self, n):
        self.data = self.data[:n]
        return self
    
    def __iter__(self):
        return iter(self.data)


class MockDB:
    """Mock database for development."""
    
    def __init__(self):
        self.temperatures = MockCollection()
        self.alerts = MockCollection()


def get_db():
    """
    Return the MongoDB database object.
    Creates the MongoClient on first call; reuses it afterward.
    Also ensures indexes exist (idempotent).
    """
    global _client

    if _client is None or _client == "mock":
        if _client == "mock":
            return MockDB()
        try:
            _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Force a connection check immediately
            _client.admin.command("ping")
            logger.info("✅  Connected to MongoDB Atlas")
        except Exception as exc:
            logger.warning("❌  Database connection failed: %s", exc)
            logger.info("🔧  Using in-memory mock database for development")
            _client = "mock"  # Mark as mock so we don't retry
            return MockDB()

    db = _client[Config.DB_NAME]
    _ensure_indexes(db)
    return db


def _ensure_indexes(db) -> None:
    """Create indexes once. PyMongo's ensure_index is idempotent."""
    # Only create indexes if it's a real MongoDB db
    if hasattr(db, 'temperatures') and hasattr(db.temperatures, 'create_index'):
        # Fast range queries on timestamp (most common query pattern)
        db.temperatures.create_index([("timestamp", DESCENDING)])
        # Alert queries by type + time
        db.alerts.create_index([("alert_type", 1), ("timestamp", DESCENDING)])
