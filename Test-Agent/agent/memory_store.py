import os
import sqlite3
import threading
import uuid
from datetime import datetime


class MemoryStore:
    def __init__(self, db_path="Storage/sunday.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.init_db()

    def init_db(self):
        with self._lock:
            cur = self.conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS events(
                    id TEXT PRIMARY KEY,
                    ts TEXT,
                    type TEXT,
                    description TEXT,
                    emotion TEXT,
                    importance REAL,
                    source TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS facts(
                    id TEXT PRIMARY KEY,
                    ts TEXT,
                    fact TEXT UNIQUE,
                    confidence REAL,
                    source TEXT
                )
                """
            )
            cur.execute("CREATE TABLE IF NOT EXISTS relationships(key TEXT PRIMARY KEY, value TEXT)")
            self.conn.commit()

    def set_meta(self, key, value):
        with self._lock:
            self.conn.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(key), str(value)),
            )
            self.conn.commit()

    def get_meta(self, key, default=None):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key=?", (str(key),))
        row = cur.fetchone()
        return row[0] if row else default

    def add_event(self, event_type, description, emotion="neutral", importance=0.5, source="system"):
        with self._lock:
            self.conn.execute(
                "INSERT INTO events(id, ts, type, description, emotion, importance, source) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    datetime.utcnow().isoformat(),
                    str(event_type),
                    str(description),
                    str(emotion),
                    float(importance),
                    str(source),
                ),
            )
            self.conn.commit()

    def add_fact(self, fact, confidence=1.0, source="system"):
        with self._lock:
            self.conn.execute(
                "INSERT OR IGNORE INTO facts(id, ts, fact, confidence, source) VALUES(?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    datetime.utcnow().isoformat(),
                    str(fact).strip(),
                    float(confidence),
                    str(source),
                ),
            )
            self.conn.commit()

    def search_events(self, query, limit=5):
        q = f"%{(query or '').strip()}%"
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT ts, type, description, emotion, importance, source
            FROM events
            WHERE description LIKE ? OR type LIKE ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (q, q, int(limit)),
        )
        return cur.fetchall()

    def set_relationship(self, key, value):
        with self._lock:
            self.conn.execute(
                "INSERT INTO relationships(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(key), str(value)),
            )
            self.conn.commit()

    def get_relationship(self, key, default=None):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM relationships WHERE key=?", (str(key),))
        row = cur.fetchone()
        return row[0] if row else default

    def close(self):
        with self._lock:
            self.conn.close()
