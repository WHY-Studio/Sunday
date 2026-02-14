import os
import secrets


TOKEN_PATH = "Storage/creator_token.txt"


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


def load_relationship_state(store):
    return {"state": store.get_relationship("relationship_state", "unknown")}


def verify_creator(token, store):
    expected = _read_token()
    if not expected:
        return False
    if str(token).strip() == expected:
        store.set_relationship("relationship_state", "creator_verified")
        return True
    return False


def is_creator_verified(store):
    return store.get_relationship("relationship_state", "unknown") == "creator_verified"
