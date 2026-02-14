import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_safe(path):
    candidate = (PROJECT_ROOT / path).resolve() if not os.path.isabs(path) else Path(path).resolve()
    if PROJECT_ROOT not in candidate.parents and candidate != PROJECT_ROOT:
        raise ValueError("Path outside project root is not allowed.")
    return candidate


def read_file(path):
    safe_path = _resolve_safe(path)
    if not safe_path.exists() or not safe_path.is_file():
        return ""
    return safe_path.read_text(encoding="utf-8", errors="replace")


def list_dir(path="."):
    safe_path = _resolve_safe(path)
    if not safe_path.exists() or not safe_path.is_dir():
        return []
    return sorted([p.name for p in safe_path.iterdir()])


def search_logs(pattern):
    logs_dir = PROJECT_ROOT / "Logs"
    if not logs_dir.exists():
        return []
    matches = []
    for log_file in logs_dir.glob("*.log"):
        text = log_file.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if pattern in line:
                matches.append(f"{log_file.name}: {line}")
    return matches
