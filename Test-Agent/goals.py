"""
goals.py – Core Instinct System

ROLE:
- Evaluates current priorities
- Never generates text
- Influences emotion & attention
"""

import nervous_system

GOALS = {
    "survive": 1.0,
    "learn": 0.6,
    "bond": 0.7
}

def evaluate_goals():
    state = nervous_system.get_body_state()

    if state["integrity"] < 0.5:
        GOALS["survive"] = 1.0
        GOALS["learn"] = 0.2
    elif state["growth"] > 0.6:
        GOALS["learn"] = 0.9

    return GOALS.copy()
