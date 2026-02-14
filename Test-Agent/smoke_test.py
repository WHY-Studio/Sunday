from agent.memory_api import MemoryAPI
from agent.memory_store import MemoryStore
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


def main():
    store = MemoryStore("Storage/smoke_sunday.db")
    api = MemoryAPI(store)
    api.record_event("smoke", "smoke event", source="test")
    snippets = api.recall("smoke", max_items=3)
    assert snippets, "recall should return at least one snippet"

    runtime = SundayRuntime(
        model_client=StubClient(),
        memory_api=api,
        nervous_system=StubNervous(),
        goals=StubGoals(),
        attachment=StubAttachment(),
    )
    reply = runtime.handle_user_message("Hello")
    assert isinstance(reply, str) and reply, "runtime should return a non-empty reply"
    print("smoke_test passed")


if __name__ == "__main__":
    main()
