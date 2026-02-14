from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SundayState:
    body: dict = field(default_factory=lambda: {
        "integrity": 1.0,
        "stability": 1.0,
        "energy": None,
        "error_rate": None,
    })
    affect: dict = field(default_factory=lambda: {
        "tone": "neutral",
        "stress": 0.0,
        "confidence": 0.8,
    })
    goals: dict = field(default_factory=lambda: {
        "survive": 1.0,
        "learn": 0.6,
        "bond": 0.7,
    })
    relationship: dict = field(default_factory=lambda: {"state": "unknown"})
    counters: dict = field(default_factory=lambda: {
        "tokens": 0,
        "interaction_count": 0,
        "last_error": None,
    })

    def as_dict(self):
        return {
            "body": self.body,
            "affect": self.affect,
            "goals": self.goals,
            "relationship": self.relationship,
            "counters": self.counters,
        }
