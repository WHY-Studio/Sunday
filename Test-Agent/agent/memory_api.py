from memory.memory_manager import get_memory_manager


class MemoryAPI:
    def __init__(self):
        self.manager = get_memory_manager()

    def record_event(self, event_type, description, emotion="neutral", importance=0.5, source="system"):
        _ = source
        self.manager.record_event(event_type, description, emotion=emotion, importance=importance)

    def record_fact(self, fact, confidence=1.0, source="system"):
        _ = source
        self.manager.record_fact(fact=fact, confidence=confidence)

    def recall(self, query, max_items=5):
        return self.manager.recall(query=query, max_items=max_items)


_default_api = MemoryAPI()


def get_memory_api():
    return _default_api
