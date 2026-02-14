import json
import os
import secrets


TOKEN_PATH = "Storage/creator_token.txt"
REL_PATH = "Storage/relationship_state.json"


def ensure_creator_token(emit_log=None):
    os.makedirs("Storage", exist_ok=True)
    if os.path.exists(TOKEN_PATH):
        return
    token = secrets.token_urlsafe(24)
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        f.write(token)
    if emit_log:
        emit_log("[SETUP] creator token created. Use /creator <token>")


def _read_token():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _save_rel(state: str):
    with open(REL_PATH, "w", encoding="utf-8") as f:
        json.dump({"state": state}, f)


def load_relationship_state(store=None):
    _ = store
    if not os.path.exists(REL_PATH):
        return {"state": "unknown"}
    with open(REL_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"state": data.get("state", "unknown")}


def verify_creator(token, store=None):
    _ = store
    expected = _read_token()
    if not expected:
        return False
    if str(token).strip() == expected:
        _save_rel("creator_verified")
        return True
    return False


def is_creator_verified(store=None):
    return load_relationship_state(store).get("state") == "creator_verified"
