"""
sleep.py – Passive Memory Consolidation

ROLE:
- Runs silently in background
- Compresses memories
- Forms long-term opinions
"""

import time
import Memory
import nervous_system

SLEEP_INTERVAL = 60  # Sekunden

def sleep_cycle():
    state = nervous_system.get_body_state()

    if state["stability"] > 0.7 and state["integrity"] > 0.7:
        Memory.consolidate()

def start():
    while True:
        time.sleep(SLEEP_INTERVAL)
        sleep_cycle()
