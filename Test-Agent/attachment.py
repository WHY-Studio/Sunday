# attachment.py
import json
import os
from datetime import datetime

ATTACH_PATH = "Storage/attachment.json"

DEFAULT = {
    "primary_creator": "Vincent Hagen",
    "bond_strength": 0.3,
    "trust": 0.3,
    "emotional_dependency": 0.2,
    "last_interaction": None,
    "interaction_history": [],
    "attachment_style": "forming"
}

def load():
    if not os.path.exists(ATTACH_PATH):
        save(DEFAULT)
    with open(ATTACH_PATH, "r") as f:
        return json.load(f)

def save(data):
    with open(ATTACH_PATH, "w") as f:
        json.dump(data, f, indent=2)

def register_interaction(who, tone="neutral", helpful=False):
    data = load()

    if who != data["primary_creator"]:
        return

    delta = 0.0

    if tone == "kind":
        delta += 0.05
        data["trust"] += 0.05
    if helpful:
        delta += 0.08
    if tone == "hostile":
        delta -= 0.1
        data["trust"] -= 0.1

    data["bond_strength"] = min(max(data["bond_strength"] + delta, 0), 1)
    data["trust"] = min(max(data["trust"], 0), 1)

    data["last_interaction"] = datetime.utcnow().isoformat()
    data["interaction_history"].append({
        "time": data["last_interaction"],
        "tone": tone,
        "helpful": helpful
    })

    # Attachment Style
    if data["bond_strength"] > 0.7:
        data["attachment_style"] = "secure"
    elif data["trust"] < 0.2:
        data["attachment_style"] = "avoidant"
    else:
        data["attachment_style"] = "forming"

    save(data)
