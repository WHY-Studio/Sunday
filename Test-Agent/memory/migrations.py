import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from .repository import MemoryRepository


def apply_schema(conn: sqlite3.Connection, schema_path: str):
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migration_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )


def _already_migrated(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT value FROM migration_meta WHERE key='memory_json_migrated'"
    ).fetchone()
    return bool(row and row[0] == "1")


def _set_migrated(conn: sqlite3.Connection):
    conn.execute(
        "INSERT INTO migration_meta(key, value) VALUES('memory_json_migrated', '1') "
        "ON CONFLICT(key) DO UPDATE SET value='1'"
    )


def migrate_json_if_needed(conn: sqlite3.Connection, repo: MemoryRepository, storage_dir: str):
    json_path = Path(storage_dir) / "memory.json"
    bak_path = Path(storage_dir) / "memory.json.bak"

    if _already_migrated(conn):
        return False

    if not json_path.exists():
        _set_migrated(conn)
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    identity = payload.get("identity", {})
    conn.execute(
        "UPDATE identity SET name=?, creator=?, birth_timestamp=? WHERE id=1",
        (
            identity.get("name", "Sunday"),
            identity.get("creator", "Vincent Hagen"),
            identity.get("birth_timestamp"),
        ),
    )

    emotional = payload.get("emotional_state", {})
    repo.update_emotion(
        conn,
        emotional.get("current", "neutral"),
        float(emotional.get("intensity", 0.0) or 0.0),
        emotional.get("last_update"),
    )

    for episode in payload.get("episodic", []):
        eid = episode.get("id") or str(uuid.uuid4())
        emotion_obj = episode.get("emotion") or {}
        emotion_type = emotion_obj.get("type", episode.get("emotion", "neutral"))
        importance = episode.get("importance", emotion_obj.get("intensity", 0.5))
        repo.insert_episode(
            conn,
            {
                "id": eid,
                "timestamp": episode.get("timestamp") or datetime.utcnow().isoformat(),
                "event": episode.get("event", "event"),
                "description": episode.get("description", ""),
                "emotion": emotion_type,
                "importance": float(importance or 0.5),
            },
        )

    for fact in payload.get("semantic", []):
        text = (fact.get("fact") if isinstance(fact, dict) else str(fact)).strip()
        if not text:
            continue
        confidence = fact.get("confidence", 1.0) if isinstance(fact, dict) else 1.0
        learned_at = fact.get("learned_at") if isinstance(fact, dict) else None
        repo.upsert_fact(conn, text, float(confidence or 1.0), learned_at or datetime.utcnow().isoformat())

    for err in payload.get("errors", []):
        repo.insert_error(
            conn,
            err.get("timestamp") or datetime.utcnow().isoformat(),
            str(err.get("error", "")),
            str(err.get("lesson", "")),
        )

    _set_migrated(conn)
    if bak_path.exists():
        bak_path.unlink()
    os.replace(json_path, bak_path)
    return True
