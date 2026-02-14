import os
import sys
import threading

from openai import OpenAI

import attachment
import goals
import nervous_system
from agent.logger import emit_chat, emit_log, emit_status
from agent.memory_api import get_memory_api
from agent.relationships import ensure_creator_token
from agent.runtime import SundayRuntime
import Memory
import sleep


def sanitize(text: str) -> str:
    text = (text or "").replace("\r", "").strip()
    lines = [line for line in text.splitlines() if line.strip()]
    cleaned = []
    for line in lines:
        if cleaned and cleaned[-1].strip() == line.strip():
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def final_sanitize(text: str) -> str:
    return sanitize(text)


def build_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        emit_log("[ERROR] GROQ_API_KEY is missing. Set environment variable GROQ_API_KEY.")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def main():
    nervous_system.start()
    threading.Thread(target=sleep.start, daemon=True).start()

    memory_api = get_memory_api()
    ensure_creator_token(emit_log=emit_log)

    emit_log("[ANALYZE] Flow: Terminal.py starts llm.py as subprocess and exchanges newline-delimited JSON messages.")
    emit_log("[ANALYZE] UI transport: llm.py prints JSON lines with type=chat/status/log and Terminal parses them.")
    emit_log("[ANALYZE] Previous issues addressed: JSON memory file lock conflicts and incompatible record_event kwargs.")

    client = build_client()
    if client is None:
        return

    runtime = SundayRuntime(
        model_client=client,
        memory_api=memory_api,
        nervous_system=nervous_system,
        goals=goals,
        attachment=attachment,
        sanitizer=final_sanitize,
    )

    Memory.record_birth()
    emit_status({"state": "ready", "health": 1.0, "tokens": 0})

    for raw in sys.stdin:
        text = (raw or "").strip()
        if not text:
            continue
        try:
            reply = runtime.handle_user_message(text)
            emit_chat(reply)
            emit_status(runtime.state.as_dict())
        except Exception as exc:
            emit_log(f"[ERROR] runtime failure: {exc}")


if __name__ == "__main__":
    main()
