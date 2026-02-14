import json


def emit_status(state):
    print(json.dumps({"type": "status", "payload": state}), flush=True)


def emit_chat(text):
    print(json.dumps({"type": "chat", "payload": text}), flush=True)


def emit_log(text):
    print(json.dumps({"type": "log", "payload": text}), flush=True)
