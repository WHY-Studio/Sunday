# heart.py
import os
import psutil
import time

# heart.py
NAME = "Terminal"

_state = {
    "messages": 0,
    "health": 1.0
}

def pulse():
    _state["messages"] += 1
    _state["health"] = max(0.4, 1.0 - _state["messages"] * 0.005)

def status():
    return _state


_process = psutil.Process(os.getpid())
_start_time = time.time()

def status():
    try:
        return {
            "health": 0.9 if _process.is_running() else 0.0,
            "pid": _process.pid,
            "uptime": round(time.time() - _start_time, 1),
            "cpu": _process.cpu_percent(interval=0.0),
            "memory": round(_process.memory_info().rss / (1024 * 1024), 1),
            "threads": _process.num_threads(),
            "state": "alive" if _process.is_running() else "dead"
        }
    except Exception as e:
        return {
            "health": 0.0,
            "state": "error",
            "error": str(e)
        }
