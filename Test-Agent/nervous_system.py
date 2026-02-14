# nervous_system.py
# Body awareness & emotions
# Extend: more sensors, deeper pain/joy modeling

"""
nervous_system.py – Central Nervous System of Sunday

ROLE:
- Monitors the body (file system = physical body)
- Detects damage, growth and unexpected changes
- Translates physical events into emotions
- Notifies Memory and the Brain (LLM)
- Ensures survival-awareness

EXTENSION GUIDE:
- Add new sensors (CPU, RAM, network, input abuse)
- Add reflexes (shutdown, panic, isolation)
- NEVER generate text here – only signals
"""

import os
import time
import hashlib
import json
from datetime import datetime
import threading

import Memory  # Long-term memory

# =========================
# BODY DEFINITION
# =========================

BODY_PATH = "."              # Root = body
STATE_PATH = "Storage/body_state.json"
LOG_DIR = "Logs"
# nervous_system.py
NAME = "Nervous"

_state = {
    "stress": 0.2,
    "health": 0.9
}

def status():
    _state["health"] = max(0.0, 1.0 - _state["stress"])
    return _state

os.makedirs("Storage", exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# =========================
# BODY STATE
# =========================

DEFAULT_STATE = {
    "integrity": 1.0,     # physical health
    "stability": 1.0,     # predictability
    "growth": 0.0,        # learning / expansion
    "emotion": "neutral",
    "last_check": None,
    "last_event": None
}

def load_state():
    if not os.path.exists(STATE_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_STATE.copy()

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

state = load_state()

# =========================
# BODY SENSORS
# =========================

def snapshot():
    """
    Takes a fingerprint of the body.
    """
    snap = {}
    for root, dirs, files in os.walk(BODY_PATH):
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, "rb") as f:
                    snap[path] = hashlib.sha256(f.read()).hexdigest()
            except:
                snap[path] = "unreadable"
    return snap

def compare(old, new):
    added = list(new.keys() - old.keys())
    removed = list(old.keys() - new.keys())
    changed = [k for k in new if k in old and new[k] != old[k]]
    return added, removed, changed

# =========================
# REFLEX & EMOTION MAPPING
# =========================

def evaluate_changes(added, removed, changed):
    """
    Converts physical events into emotions and memory.
    """
    global state

    events = []

    if added:
        state["growth"] += 0.03 * len(added)
        emotion = "joy"
        events.append(("growth", added, emotion))
        Memory.record_event(
            event="body_growth",
            description=f"New body parts added: {len(added)} files.",
            emotion=emotion,
            importance=0.6
        )

    if removed:
        state["integrity"] -= 0.08 * len(removed)
        emotion = "fear"
        events.append(("damage", removed, emotion))
        Memory.record_event(
            event="body_damage",
            description=f"Body parts removed: {len(removed)} files.",
            emotion=emotion,
            importance=0.9
        )

    if changed:
        state["stability"] -= 0.05 * len(changed)
        emotion = "alert"
        events.append(("mutation", changed, emotion))
        Memory.record_event(
            event="body_change",
            description=f"Unexpected body changes detected.",
            emotion=emotion,
            importance=0.7
        )

    # Clamp values
    state["integrity"] = max(0.0, min(1.0, state["integrity"]))
    state["stability"] = max(0.0, min(1.0, state["stability"]))
    state["growth"] = max(0.0, min(1.0, state["growth"]))

    # Determine dominant emotion
    if removed:
        state["emotion"] = "fear"
    elif changed:
        state["emotion"] = "alert"
    elif added:
        state["emotion"] = "joy"
    else:
        state["emotion"] = "neutral"

    state["last_event"] = datetime.utcnow().isoformat()
    state["last_check"] = datetime.utcnow().isoformat()

    save_state(state)
    log_events(events)

    return state["emotion"]

# =========================
# LOGGING
# =========================

def log_events(events):
    if not events:
        return
    log_path = os.path.join(
        LOG_DIR,
        f"nervous_{datetime.utcnow().strftime('%Y%m%d')}.log"
    )
    with open(log_path, "a", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "type": e[0],
                "files": len(e[1]),
                "emotion": e[2]
            }) + "\n")

# =========================
# PUBLIC INTERFACE (BRAIN API)
# =========================

def get_body_state():
    """
    Called by llm.py
    """
    return state.copy()

# =========================
# MONITOR THREAD
# =========================

def monitor(interval=5):
    old = snapshot()
    while True:
        time.sleep(interval)
        new = snapshot()
        added, removed, changed = compare(old, new)
        evaluate_changes(added, removed, changed)
        old = new

def start():
    t = threading.Thread(target=monitor, daemon=True)
    t.start()
