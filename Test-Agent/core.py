# core.py
NAME = "Core"

_state = {
    "health": 1.0,
    "state": "idle",
    "tokens": 0
}

def update_from_llm(data: dict):
    _state.update(data)

def status():
    return _state
