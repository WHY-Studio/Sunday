# Memory.py
# Long-term memory system for Sunday
# Includes episodic, semantic, emotional memory and consolidation

import json
import os
from datetime import datetime
import uuid
import threading
import time

NAME = "Memory"
STORAGE_PATH = "Storage/memory.json"

_FILE_LOCK = threading.Lock()
# =========================
# INTERNAL METRICS (health/events)
# =========================
_metrics = {
    "events": 0,
    "health": 1.0
}

def _bump_metrics():
    _metrics["events"] += 1
    _metrics["health"] = max(0.3, 1.0 - _metrics["events"] * 0.01)

def status():
    return {
        "health": _metrics["health"],
        "events": _metrics["events"]
    }

# =========================
# DEFAULT STRUCTURE
# =========================
def _default_memory():
    return {
        "identity": {
            "name": "Sunday",
            "creator": "Vincent Hagen",
            "birth_timestamp": None
        },
        "emotional_state": {
            "current": "neutral",
            "intensity": 0.0,
            "last_update": None
        },
        "episodic": [],
        "semantic": [],
        "errors": [],
        "meta": {
            "last_updated": None,
            "memory_count": 0
        }
    }

def _ensure_keys(mem: dict) -> dict:
    """Make sure all required keys exist, even after upgrades."""
    default = _default_memory()
    for k, v in default.items():
        if k not in mem:
            mem[k] = v
    # nested keys
    if "identity" not in mem or not isinstance(mem["identity"], dict):
        mem["identity"] = default["identity"]
    else:
        for k, v in default["identity"].items():
            mem["identity"].setdefault(k, v)

    if "emotional_state" not in mem or not isinstance(mem["emotional_state"], dict):
        mem["emotional_state"] = default["emotional_state"]
    else:
        for k, v in default["emotional_state"].items():
            mem["emotional_state"].setdefault(k, v)

    if "meta" not in mem or not isinstance(mem["meta"], dict):
        mem["meta"] = default["meta"]
    else:
        for k, v in default["meta"].items():
            mem["meta"].setdefault(k, v)

    # types
    for arr_key in ("episodic", "semantic", "errors"):
        if arr_key not in mem or not isinstance(mem[arr_key], list):
            mem[arr_key] = []

    return mem

# =========================
# LOAD / SAVE (robust + atomic)
# =========================
def load_memory():
    # ensure directory exists
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)

    if not os.path.exists(STORAGE_PATH):
        return _default_memory()

    # empty file -> reset
    try:
        if os.path.getsize(STORAGE_PATH) == 0:
            return _default_memory()
    except OSError:
        return _default_memory()

    try:
        with open(STORAGE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return _default_memory()
        return _ensure_keys(data)

    except json.JSONDecodeError:
        # backup broken file
        broken_path = STORAGE_PATH + ".broken"
        try:
            os.replace(STORAGE_PATH, broken_path)
        except Exception:
            pass
        return _default_memory()

    except Exception:
        return _default_memory()

def save_memory(mem):
    global memory
    mem = _ensure_keys(mem)
    mem["meta"]["last_updated"] = datetime.utcnow().isoformat()
    mem["meta"]["memory_count"] = len(mem.get("episodic", [])) + len(mem.get("semantic", []))

    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)

    # Windows-safe atomic write with lock + retries
    with _FILE_LOCK:
        tmp_path = STORAGE_PATH + ".tmp"

        # write tmp first
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)

        # replace with retries (WinError 32)
        last_err = None
        for _ in range(15):
            try:
                os.replace(tmp_path, STORAGE_PATH)
                last_err = None
                break
            except PermissionError as e:
                last_err = e
                time.sleep(0.05)

        if last_err is not None:
            # If replace keeps failing, keep tmp as backup and raise
            raise last_err

    memory = mem

# global in-memory state
memory = load_memory()

# =========================
# BIRTH
# =========================
def record_birth():
    global memory
    memory = _ensure_keys(memory)
    if memory["identity"]["birth_timestamp"] is None:
        memory["identity"]["birth_timestamp"] = datetime.utcnow().isoformat()
        save_memory(memory)

# =========================
# EMOTIONS
# =========================
def update_emotion(emotion: str, intensity: float = 0.5):
    global memory
    memory = _ensure_keys(memory)

    memory["emotional_state"]["current"] = emotion
    memory["emotional_state"]["intensity"] = float(intensity)
    memory["emotional_state"]["last_update"] = datetime.utcnow().isoformat()
    save_memory(memory)

# =========================
# EPISODIC MEMORY
# =========================
def record_event(event: str, description: str, emotion="neutral", importance=0.5, confidence=None):
    """
    event: short tag (e.g. "creator_mentioned")
    description: human readable description
    emotion: "joy"/"fear"/...
    importance: 0..1
    confidence: optional (kept for compatibility if you pass it)
    """
    global memory
    memory = _ensure_keys(memory)
    _bump_metrics()

    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "description": description,
        "emotion": {
            "type": emotion,
            "intensity": float(importance)
        },
        "importance": float(importance)
    }
    if confidence is not None:
        entry["confidence"] = float(confidence)

    memory["episodic"].append(entry)

    # Update emotional state & persist
    update_emotion(emotion, importance)
    save_memory(memory)

# =========================
# SEMANTIC MEMORY (FACTS)
# =========================
def record_fact(fact: str, confidence=1.0):
    global memory
    memory = _ensure_keys(memory)
    _bump_metrics()

    fact = str(fact).strip()
    if not fact:
        return

    for f in memory["semantic"]:
        if f.get("fact") == fact:
            return

    memory["semantic"].append({
        "fact": fact,
        "confidence": float(confidence),
        "learned_at": datetime.utcnow().isoformat()
    })
    save_memory(memory)

# =========================
# ERROR LEARNING
# =========================
def record_error(error: str, lesson: str):
    global memory
    memory = _ensure_keys(memory)
    _bump_metrics()

    memory["errors"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "error": str(error),
        "lesson": str(lesson),
        "emotion": "fear"
    })
    update_emotion("fear", 0.7)
    save_memory(memory)

# =========================
# MEMORY CONSOLIDATION (SLEEP)
# =========================
def consolidate():
    """
    Transfer episodic memories into semantic facts during sleep.
    Avoid duplicates in semantic memory.
    """
    global memory
    memory = _ensure_keys(memory)

    for e in memory.get("episodic", []):
        fact = f"{e.get('event', '')}: {e.get('description', '')}".strip()
        if not fact or fact == ":":
            continue

        exists = any(f.get("fact") == fact for f in memory.get("semantic", []))
        if not exists:
            memory["semantic"].append({
                "fact": fact,
                "confidence": 0.8,
                "learned_at": datetime.utcnow().isoformat()
            })

    save_memory(memory)

# =========================
# RETRIEVAL
# =========================
def recall(query: str, max_items=5):
    q = (query or "").lower().strip()
    if not q:
        return []

    results = []
    for e in reversed(memory.get("episodic", [])):
        if len(results) >= max_items:
            break
        desc = (e.get("description") or "").lower()
        if q in desc:
            emo = e.get("emotion", {}) or {}
            results.append(
                f"I remember {e.get('description', '')} and felt {emo.get('type', 'neutral')} "
                f"(intensity {emo.get('intensity', 0.0)})."
            )
    return results