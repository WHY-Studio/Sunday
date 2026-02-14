"""Compatibility facade over agent.memory_api."""

from agent.memory_api import get_memory_api

NAME = "Memory"
_api = get_memory_api()
_metrics = {"events": 0, "health": 1.0}


def _touch_metric():
    _metrics["events"] += 1
    _metrics["health"] = max(0.3, 1.0 - (_metrics["events"] * 0.005))


def record_birth():
    _api.record_event("birth", "Sunday runtime initialized.", source="system")
    _touch_metric()


def record_event(event_type=None, description="", emotion="neutral", importance=0.5, confidence=None, source="system", **kwargs):
    normalized_type = event_type or kwargs.get("event") or "event"
    normalized_description = description or kwargs.get("content") or kwargs.get("description") or ""
    _api.record_event(
        event_type=normalized_type,
        description=normalized_description,
        emotion=emotion,
        importance=importance,
        source=source,
    )
    _touch_metric()


def record_fact(fact, confidence=1.0, source="system"):
    _api.record_fact(fact=fact, confidence=confidence, source=source)
    _touch_metric()


def recall(query, max_items=5):
    return _api.recall(query=query, max_items=max_items)


def consolidate():
    # SQLite store is already structured; no compaction step required yet.
    return None


def status():
    return {"health": _metrics["health"], "events": _metrics["events"]}
