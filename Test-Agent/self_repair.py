"""
self_repair.py – Autonomous Self-Healing System (Windows-like)

ROLE:
- Observes body integrity
- Performs safe integrity checks
- Restores only known-critical files
- Creates backups before touching anything
- Reports detailed health & repair status
"""

import os
import sys
import shutil
import time
from datetime import datetime
import json

# =========================
# 🔧 CONFIG
# =========================

NAME = "SelfRepair"

CRITICAL_FILES = [
    "llm.py",
    "Memory.py",
    "nervous_system.py"
]

BACKUP_DIR = "Storage/backups"
LOG_PREFIX = "[SELF_REPAIR]"

os.makedirs(BACKUP_DIR, exist_ok=True)

# =========================
# 🧠 INTERNAL STATE
# =========================

_state = {
    "health": 1.0,
    "repairs_total": 0,
    "last_run": None,
    "last_result": "idle",
    "errors": []
}

# =========================
# 🖨 LOGGING
# =========================

def log(msg):
    print(f"{LOG_PREFIX} {msg}", flush=True)

# =========================
# 🧬 STATUS API (for BodyTab)
# =========================

def status():
    return {
        "health": _state["health"],
        "repairs": _state["repairs_total"],
        "last_run": _state["last_run"],
        "result": _state["last_result"],
        "errors": list(_state["errors"])
    }

# =========================
# 💾 BACKUP SYSTEM
# =========================

def backup_critical_files():
    log("Creating backups of critical files...")
    for file in CRITICAL_FILES:
        if os.path.exists(file):
            dest = os.path.join(BACKUP_DIR, file)
            shutil.copy(file, dest)
            log(f"Backup created: {file}")

def restore_from_backup(filename):
    backup = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup):
        shutil.copy(backup, filename)
        log(f"Restored {filename} from backup")
        return True
    return False

# =========================
# 🔍 INTEGRITY CHECKS
# =========================

def check_integrity():
    """
    Returns integrity score [0..1]
    """
    missing = []
    for file in CRITICAL_FILES:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        log(f"Integrity violation: missing files -> {missing}")
        _state["errors"].extend(missing)
        return 0.2

    return 1.0

# =========================
# 🛠 REPAIR ENGINE
# =========================

def attempt_repair():
    log("Attempting system repair...")

    repaired_any = False

    for file in CRITICAL_FILES:
        if not os.path.exists(file):
            log(f"Critical file missing: {file}")
            if restore_from_backup(file):
                repaired_any = True
            else:
                log(f"No backup available for {file}")

    return repaired_any

# =========================
# 🚑 MAIN REPAIR ROUTINE
# =========================

def main():
    log("Self-repair started")
    _state["last_run"] = datetime.utcnow().isoformat()
    _state["errors"].clear()

    time.sleep(0.5)

    # Step 1: Backup first (Windows rule)
    backup_critical_files()

    # Step 2: Integrity check
    integrity = check_integrity()
    _state["health"] = integrity

    if integrity >= 0.8:
        log("System integrity OK – no repair needed")
        _state["last_result"] = "healthy"
        return

    # Step 3: Repair
    success = attempt_repair()
    _state["repairs_total"] += 1

    time.sleep(0.5)

    # Step 4: Re-check
    integrity = check_integrity()
    _state["health"] = integrity

    if success and integrity >= 0.8:
        log("Repair successful")
        _state["last_result"] = "repaired"
    else:
        log("Repair incomplete – manual intervention recommended")
        _state["last_result"] = "degraded"

    log("Self-repair finished")

# =========================
# ▶ ENTRY POINT
# =========================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"CRITICAL FAILURE: {e}")
        _state["health"] = 0.0
        _state["last_result"] = "failed"
