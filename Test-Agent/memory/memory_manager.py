import atexit
import os
import queue
import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path

from .migrations import apply_schema, migrate_json_if_needed
from .repository import MemoryRepository


class MemoryWriter(threading.Thread):
    def __init__(self, db_path: str, write_queue: queue.Queue):
        super().__init__(daemon=True, name="MemoryWriter")
        self.db_path = db_path
        self.write_queue = write_queue
        self._stop_event = threading.Event()
        self.conn = None

    def run(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=True)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.row_factory = sqlite3.Row
        while not self._stop_event.is_set():
            task = self.write_queue.get()
            if task is None:
                self.write_queue.task_done()
                break
            func, args, kwargs, done_event, result_holder = task
            try:
                result_holder["result"] = func(self.conn, *args, **kwargs)
                self.conn.commit()
            except Exception as exc:
                self.conn.rollback()
                result_holder["error"] = exc
            finally:
                done_event.set()
                self.write_queue.task_done()

        self.conn.close()

    def stop(self):
        self._stop_event.set()
        self.write_queue.put(None)


class MemoryManager:
    def __init__(self, db_path="Storage/memory.db"):
        self.db_path = db_path
        self.storage_dir = str(Path(db_path).parent)
        os.makedirs(self.storage_dir, exist_ok=True)

        self._repo = MemoryRepository(db_path)
        self._queue = queue.Queue()
        self._writer = MemoryWriter(db_path=db_path, write_queue=self._queue)

        setup_conn = sqlite3.connect(self.db_path, check_same_thread=True)
        setup_conn.row_factory = sqlite3.Row
        apply_schema(setup_conn, self._schema_path())
        MemoryRepository.ensure_defaults(setup_conn)
        migrate_json_if_needed(setup_conn, self._repo, self.storage_dir)
        setup_conn.commit()
        setup_conn.close()

        self._writer.start()
        atexit.register(self.close)

    def _schema_path(self):
        return str(Path(__file__).with_name("schema.sql"))

    def _enqueue_write(self, func, *args, **kwargs):
        done_event = threading.Event()
        result_holder = {}
        self._queue.put((func, args, kwargs, done_event, result_holder))
        done_event.wait()
        if "error" in result_holder:
            raise result_holder["error"]
        return result_holder.get("result")

    def record_birth(self):
        def _write(conn):
            row = conn.execute("SELECT birth_timestamp FROM identity WHERE id=1").fetchone()
            if row and row[0]:
                return row[0]
            ts = datetime.utcnow().isoformat()
            MemoryRepository.set_birth(conn, ts)
            return ts

        return self._enqueue_write(_write)

    def record_event(self, event, description, emotion="neutral", importance=0.5):
        def _write(conn):
            eid = str(uuid.uuid4())
            MemoryRepository.insert_episode(
                conn,
                {
                    "id": eid,
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": str(event),
                    "description": str(description),
                    "emotion": str(emotion),
                    "importance": float(importance),
                },
            )
            return eid

        return self._enqueue_write(_write)

    def record_fact(self, fact, confidence=1.0):
        fact_text = str(fact).strip()
        if not fact_text:
            return None

        def _write(conn):
            MemoryRepository.upsert_fact(
                conn,
                fact_text,
                float(confidence),
                datetime.utcnow().isoformat(),
            )
            return fact_text

        return self._enqueue_write(_write)

    def update_emotion(self, emotion, intensity):
        def _write(conn):
            MemoryRepository.update_emotion(
                conn,
                str(emotion),
                float(intensity),
                datetime.utcnow().isoformat(),
            )

        self._enqueue_write(_write)

    def record_error(self, error, lesson):
        def _write(conn):
            MemoryRepository.insert_error(
                conn,
                datetime.utcnow().isoformat(),
                str(error),
                str(lesson),
            )

        self._enqueue_write(_write)
        self.update_emotion("fear", 0.7)

    def recall(self, query, max_items=5):
        query = (query or "").strip()
        if not query:
            return []

        episodic = self._repo.search_episodic(query, max_items)
        semantic = self._repo.search_semantic(query, max_items)

        results = []
        for row in episodic:
            results.append(
                f"I remember {row['description']} and felt {row['emotion']} (intensity {float(row['importance']):.2f})."
            )
            if len(results) >= max_items:
                return results

        for row in semantic:
            results.append(
                f"I know: {row['fact']} (confidence {float(row['confidence']):.2f})."
            )
            if len(results) >= max_items:
                break

        return results

    def status(self):
        metrics = self._repo.get_metrics()
        health = max(0.3, 1.0 - (metrics["events"] * 0.003))
        return {
            "health": round(health, 3),
            "events": metrics["events"],
            "episodic": metrics["episodic"],
            "semantic": metrics["semantic"],
            "errors": metrics["errors"],
        }

    def close(self):
        if getattr(self, "_writer", None) and self._writer.is_alive():
            self._writer.stop()
            self._writer.join(timeout=2.0)
        self._repo.close_read_connection()


_manager = None
_manager_lock = threading.Lock()


def get_memory_manager() -> MemoryManager:
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                db_path = os.getenv("SUNDAY_MEMORY_DB", "Storage/memory.db")
                _manager = MemoryManager(db_path=db_path)
    return _manager
