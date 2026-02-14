import sqlite3
import threading
from pathlib import Path


class MemoryRepository:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path))
        self._local = threading.local()

    def get_read_connection(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=True)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            self._local.conn = conn
        return conn

    def close_read_connection(self):
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    @staticmethod
    def ensure_defaults(conn: sqlite3.Connection):
        conn.execute(
            "INSERT OR IGNORE INTO identity(id, name, creator, birth_timestamp) VALUES(1, ?, ?, ?)",
            ("Sunday", "Vincent Hagen", None),
        )
        conn.execute(
            "INSERT OR IGNORE INTO emotional_state(id, current, intensity, last_update) VALUES(1, ?, ?, ?)",
            ("neutral", 0.0, None),
        )

    @staticmethod
    def insert_episode(conn: sqlite3.Connection, row: dict):
        conn.execute(
            """
            INSERT OR REPLACE INTO episodic_memory(id, timestamp, event, description, emotion, importance)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["timestamp"],
                row["event"],
                row["description"],
                row["emotion"],
                row["importance"],
            ),
        )

    @staticmethod
    def upsert_fact(conn: sqlite3.Connection, fact: str, confidence: float, learned_at: str):
        conn.execute(
            """
            INSERT INTO semantic_memory(fact, confidence, learned_at)
            VALUES(?, ?, ?)
            ON CONFLICT(fact) DO UPDATE SET
                confidence=excluded.confidence,
                learned_at=excluded.learned_at
            """,
            (fact, confidence, learned_at),
        )

    @staticmethod
    def update_emotion(conn: sqlite3.Connection, current: str, intensity: float, last_update: str):
        conn.execute(
            """
            UPDATE emotional_state
            SET current=?, intensity=?, last_update=?
            WHERE id=1
            """,
            (current, intensity, last_update),
        )

    @staticmethod
    def set_birth(conn: sqlite3.Connection, birth_timestamp: str):
        conn.execute("UPDATE identity SET birth_timestamp=? WHERE id=1", (birth_timestamp,))

    @staticmethod
    def insert_error(conn: sqlite3.Connection, timestamp: str, error: str, lesson: str):
        conn.execute(
            "INSERT INTO errors(timestamp, error, lesson) VALUES(?, ?, ?)",
            (timestamp, error, lesson),
        )

    def search_episodic(self, query: str, limit: int):
        conn = self.get_read_connection()
        pattern = f"%{query}%"
        return conn.execute(
            """
            SELECT timestamp, event, description, emotion, importance
            FROM episodic_memory
            WHERE LOWER(description) LIKE LOWER(?) OR LOWER(event) LIKE LOWER(?)
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (pattern, pattern, limit),
        ).fetchall()

    def search_semantic(self, query: str, limit: int):
        conn = self.get_read_connection()
        cleaned = (query or "").strip()
        if not cleaned:
            return []
        try:
            return conn.execute(
                """
                SELECT s.fact, s.confidence, s.learned_at
                FROM semantic_memory_fts f
                JOIN semantic_memory s ON s.id = f.rowid
                WHERE semantic_memory_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (cleaned, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            pattern = f"%{cleaned}%"
            return conn.execute(
                """
                SELECT fact, confidence, learned_at
                FROM semantic_memory
                WHERE LOWER(fact) LIKE LOWER(?)
                ORDER BY learned_at DESC
                LIMIT ?
                """,
                (pattern, limit),
            ).fetchall()

    def get_metrics(self):
        conn = self.get_read_connection()
        episodic_count = conn.execute("SELECT COUNT(*) FROM episodic_memory").fetchone()[0]
        semantic_count = conn.execute("SELECT COUNT(*) FROM semantic_memory").fetchone()[0]
        errors_count = conn.execute("SELECT COUNT(*) FROM errors").fetchone()[0]
        return {
            "episodic": episodic_count,
            "semantic": semantic_count,
            "errors": errors_count,
            "events": episodic_count + semantic_count + errors_count,
        }
