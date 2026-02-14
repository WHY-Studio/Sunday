from agent.memory_store import MemoryStore


class MemoryAPI:
    def __init__(self, store=None):
        self.store = store or MemoryStore("Storage/sunday.db")

    def record_event(self, event_type, description, emotion="neutral", importance=0.5, source="system"):
        self.store.add_event(event_type, description, emotion=emotion, importance=importance, source=source)

    def record_fact(self, fact, confidence=1.0, source="system"):
        fact = str(fact).strip()
        if not fact:
            return
        self.store.add_fact(fact=fact, confidence=confidence, source=source)

    def recall(self, query, max_items=5):
        rows = self.store.search_events(query=query, limit=max_items)
        snippets = []
        for ts, event_type, description, emotion, importance, source in rows:
            snippets.append(f"[{event_type}] {description} ({emotion}, importance {importance:.2f})")
        return snippets


_default_api = MemoryAPI()


def get_memory_api():
    return _default_api
