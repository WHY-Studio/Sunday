from agent.identity import NAME, CREATOR
from agent.prompt_builder import build_system_prompt
from agent.relationships import load_relationship_state, verify_creator
from agent.state import SundayState


class SundayRuntime:
    def __init__(self, model_client, memory_api, nervous_system, goals, attachment, sanitizer=None):
        self.model_client = model_client
        self.memory_api = memory_api
        self.nervous_system = nervous_system
        self.goals = goals
        self.attachment = attachment
        self.sanitizer = sanitizer
        self.state = SundayState()

    def _update_state(self):
        body = self.nervous_system.get_body_state()
        self.state.body.update({
            "integrity": float(body.get("integrity", 1.0)),
            "stability": float(body.get("stability", 1.0)),
            "energy": body.get("energy"),
            "error_rate": body.get("error_rate"),
        })
        self.state.affect["stress"] = max(0.0, 1.0 - self.state.body["stability"])
        self.state.affect["tone"] = str(body.get("emotion", "neutral"))
        self.state.goals = self.goals.evaluate_goals()
        self.state.relationship = load_relationship_state(self.memory_api.store)

    def _model_reply(self, prompt):
        completion = self.model_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            messages=[
                {"role": "system", "content": prompt},
            ],
        )
        return completion.choices[0].message.content.strip()

    def handle_user_message(self, text):
        text = (text or "").strip()
        self.state.counters["interaction_count"] += 1

        if text.lower().startswith("/creator "):
            token = text.split(" ", 1)[1].strip()
            ok = verify_creator(token, self.memory_api.store)
            reply = "Creator verification successful." if ok else "Creator verification failed."
            self.memory_api.record_event("creator_verification", reply, source="system")
            return reply

        self._update_state()
        memory_snippets = self.memory_api.recall(text, max_items=5)
        prompt = build_system_prompt(
            user_input=text,
            state=self.state.as_dict(),
            memory_snippets=memory_snippets,
            relationship_state=self.state.relationship.get("state", "unknown"),
        )

        if text.strip().lower() == "who are you?":
            raw = "I am Sunday."
        elif text.strip().lower() == "who created you?":
            raw = "My creator is Vincent Hagen."
        else:
            raw = self._model_reply(prompt)

        reply = self.sanitizer(raw) if self.sanitizer else raw
        self.memory_api.record_event("user_message", text, source="user")
        self.memory_api.record_event("assistant_reply", reply, source=NAME)
        return reply
