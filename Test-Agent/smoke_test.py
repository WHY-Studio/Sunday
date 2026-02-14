import os
import tempfile
from pathlib import Path


def run_test():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "Storage" / "memory.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        os.environ["SUNDAY_MEMORY_DB"] = str(db_path)

        import Memory
        from agent.runtime import SundayRuntime

        class StubNervous:
            @staticmethod
            def get_body_state():
                return {"integrity": 1.0, "stability": 1.0, "emotion": "neutral"}

        class StubGoals:
            @staticmethod
            def evaluate_goals():
                return {"survive": 1.0, "learn": 0.6, "bond": 0.7}

        class StubAttachment:
            pass

        class StubCompletions:
            @staticmethod
            def create(model, temperature, messages):
                class Msg:
                    content = "Smoke test response"

                class Choice:
                    message = Msg()

                class Resp:
                    choices = [Choice()]

                return Resp()

        class StubChat:
            completions = StubCompletions()

        class StubClient:
            chat = StubChat()

        class SimpleMemoryAPI:
            def record_event(self, event_type, description, emotion="neutral", importance=0.5, source="system"):
                _ = source
                Memory.record_event(event=event_type, description=description, emotion=emotion, importance=importance)

            def record_fact(self, fact, confidence=1.0, source="system"):
                _ = source
                Memory.record_fact(fact, confidence=confidence)

            def recall(self, query, max_items=5):
                return Memory.recall(query, max_items=max_items)

        Memory.record_birth()
        Memory.record_event("smoke", "smoke event", emotion="neutral", importance=0.4)
        snippets = Memory.recall("smoke", max_items=3)
        assert snippets, "recall should return at least one snippet"

        runtime = SundayRuntime(
            model_client=StubClient(),
            memory_api=SimpleMemoryAPI(),
            nervous_system=StubNervous(),
            goals=StubGoals(),
            attachment=StubAttachment(),
        )
        reply = runtime.handle_user_message("Hello")
        assert isinstance(reply, str) and reply, "runtime should return a non-empty reply"

        info = Memory.status()
        assert "events" in info and info["events"] >= 1


def main():
    run_test()
    print("smoke_test passed")


if __name__ == "__main__":
    main()
