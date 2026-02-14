"""Compatibility wrapper for the SQLite-backed memory manager."""

from memory.memory_manager import get_memory_manager

NAME = "Memory"


def record_birth():
    return get_memory_manager().record_birth()


def record_event(event=None, description="", emotion="neutral", importance=0.5, **kwargs):
    # Backward compatibility aliases
    normalized_event = event or kwargs.get("event_type") or kwargs.get("type") or "event"
    normalized_description = (
        description
        or kwargs.get("content")
        or kwargs.get("message")
        or kwargs.get("description")
        or ""
    )
    return get_memory_manager().record_event(
        normalized_event,
        normalized_description,
        emotion=emotion,
        importance=importance,
    )


def record_fact(fact, confidence=1.0, **kwargs):
    _ = kwargs
    return get_memory_manager().record_fact(fact, confidence=confidence)


def update_emotion(emotion, intensity):
    return get_memory_manager().update_emotion(emotion, intensity)


def record_error(error, lesson):
    return get_memory_manager().record_error(error, lesson)


def recall(query, max_items=5):
    return get_memory_manager().recall(query, max_items=max_items)


def status():
    return get_memory_manager().status()


def consolidate():
    # Kept for compatibility with sleep module.
    return None
