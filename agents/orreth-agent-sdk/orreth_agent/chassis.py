"""The Chassis (0015), network edition: one fixed loop forever; behavior arrives as data.

prepare (recall what you already lived) → plan → the NUCLEUS (executes ONLY what the
planner asked, in parallel; deterministic skills answer free, 'reason' goes through the
governed door) → critic → replan → repeat until objective or breaker. The breaker doesn't
fail: it PARKS the intent as a knowledge-acquisition assignment. Failure is fuel.

Cognition is injected: RuleThink runs anywhere with zero keys; GovernedThink runs the
model plane for real. Persona is a costume; the loop is the law; every cycle is a signed
RunRecord — which is exactly why the agent appears in the Console within one tick.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from .client import FieldClient

_PLAN = """{persona}
Objective: {intent}
{memory}{feedback}Available skills (deterministic, instant): {skills}.
Plan the MINIMUM observations needed. Reply ONLY with lines of the form:
OBSERVE <skill-name>: <question>       (to use a deterministic skill)
OBSERVE reason: <question>             (to reason with a model)
Maximum {max_obs} lines."""

_CRITIC = """{persona}
Objective: {intent}
Observations gathered:
{results}
If the objective is answerable NOW, reply exactly: DONE: <the answer, one paragraph>.
Otherwise reply exactly: RETRY: <what is missing, one line>."""

_CRITIC_REASK = ("Your last reply wore neither face. Reply again with exactly "
                 "one line — either: DONE: <the answer> or: RETRY: <what is "
                 "missing>.")


def _parse_critic(text: str):
    """0047 sp1 (typed thoughts — the sim's `typed.parse_critic`, twin): the
    critic's word wears exactly one of two faces, and the word after the
    colon is the point. (done, word) or None — a bare DONE with nothing
    after it is not an answer."""
    import re
    m = re.match(r"\s*(DONE|RETRY)\s*:\s*(\S.*)\s*$", text or "", re.I | re.S)
    if not m:
        return None
    return m.group(1).upper() == "DONE", m.group(2).strip()


class Chassis:
    """The architecture never changes; objective, persona, skills, cadence are the profile."""

    def __init__(self, client: FieldClient, think, *, persona: str = "",
                 skills: dict | None = None, max_cycles: int = 3, max_obs: int = 3,
                 klass: str = "low"):
        self.client, self.think = client, think
        self.persona, self.skills = persona, skills or {}
        self.max_cycles, self.max_obs, self.klass = max_cycles, max_obs, klass
        self.trace: list[dict] = []

    def run(self, intent: str) -> dict:
        memory = self._prepare()
        feedback = ""
        for cycle in range(1, self.max_cycles + 1):
            t0 = getattr(self.think, "last_tokens", 0)      # per-cycle cost, not cumulative —
            c0 = getattr(self.think, "last_calls", 0)       # the roll-ups must add up (0005)
            observations = self._plan(intent, memory, feedback)
            results = self._nucleus(observations)
            critic_prompt = _CRITIC.format(
                persona=self.persona, intent=intent,
                results="\n".join(f"- [{k}] {q} → {r}" for k, q, r in results))
            verdict = self.think(self.klass, critic_prompt)
            parsed = _parse_critic(verdict)
            if parsed is None:
                # 0047 sp1 — the typed re-ask: the contract named ONCE, never
                # a guess; a word that fails twice is an honest RETRY
                verdict = self.think(self.klass,
                                     critic_prompt + "\n\n" + _CRITIC_REASK)
                parsed = _parse_critic(verdict)
            done, word = parsed if parsed is not None else (
                False, "the critic's word wore neither face twice — "
                       "honest retry, never a guess")
            self.trace.append({"cycle": cycle, "observations": len(results),
                               "verdict": verdict[:80]})
            self.client.diary(intent, cycle=cycle, done=done,
                              tokens=getattr(self.think, "last_tokens", 0) - t0,
                              model_calls=getattr(self.think, "last_calls", 0) - c0)
            if done:
                self.client.remember({"objective": intent, "answer": word},
                                     kind="episodic", tags=["objective", "answered"])
                return {"status": "done", "answer": word, "cycles": cycle}
            feedback = f"Prior attempt lacked: {word}\n"
        self.client.park(intent, feedback.strip())
        return {"status": "parked", "cycles": self.max_cycles}

    def _prepare(self) -> str:
        """Join the memory thread: what this identity already lived shapes the plan."""
        hits = self.client.recall(days=365).get("hits", [])[:5]
        if not hits:
            return ""
        lines = []
        for h in hits:
            body = self.client.body_of(h["ref"]) or {}
            lines.append(f"- {h['occurred_at'][:10]} · {json.dumps(body)[:120]}")
        return "What you already remember:\n" + "\n".join(lines) + "\n"

    def _plan(self, intent: str, memory: str, feedback: str) -> list[tuple[str, str]]:
        raw = self.think(self.klass, _PLAN.format(
            persona=self.persona, intent=intent, memory=memory, feedback=feedback,
            skills=", ".join(self.skills) or "none", max_obs=self.max_obs))
        obs = []
        for line in raw.splitlines():
            line = line.strip()
            if line.upper().startswith("OBSERVE") and ":" in line:
                head, question = line.split(":", 1)
                obs.append((head.split()[-1].strip().lower(), question.strip()))
        return obs[: self.max_obs] or [("reason", intent)]      # never wander, never stall

    def _nucleus(self, observations: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
        def one(skill: str, question: str) -> tuple[str, str, str]:
            if skill in self.skills:
                try:
                    return (skill, question, str(self.skills[skill](question)))
                except Exception as e:                    # a skill that errors is an observation too
                    return (skill, question, f"(skill error: {e})")
            return ("reason", question,
                    self.think(self.klass, f"{self.persona}\nAnswer concisely: {question}"))
        with ThreadPoolExecutor(max_workers=max(1, len(observations))) as pool:
            return list(pool.map(lambda o: one(*o), observations))


# ---- cognition, injected -------------------------------------------------------------------

class RuleThink:
    """Deterministic cognition — the chassis runs anywhere with zero keys. It plans one
    observation per available skill (plus one 'reason'), and calls DONE once results exist."""

    def __init__(self, skills: dict | None = None):
        self.skills = list(skills or {})
        self.last_tokens, self.last_calls = 0, 0

    def __call__(self, klass: str, prompt: str) -> str:
        if "Plan the MINIMUM" in prompt:
            lines = [f"OBSERVE {s}: {s} for the objective" for s in self.skills[:2]]
            lines.append("OBSERVE reason: summarize what the observations mean")
            return "\n".join(lines)
        if "Observations gathered" in prompt:
            gathered = [l for l in prompt.splitlines() if l.strip().startswith("- [")]
            useful = [l for l in gathered if "(skill error" not in l]
            if useful:
                return "DONE: " + "; ".join(l.split("→", 1)[-1].strip()[:100] for l in useful)
            return "RETRY: every observation errored"
        return "observed: " + prompt.splitlines()[-1][:120]


class GovernedThink:
    """Real cognition through the plane's door: /model/authorize picks the model and debits
    the lease; litellm executes; /model/meter reconciles. The plane never sees a prompt."""

    def __init__(self, client: FieldClient, *, max_tokens: int = 400):
        self.client, self.max_tokens = client, max_tokens
        self.last_tokens, self.last_calls = 0, 0

    def __call__(self, klass: str, prompt: str, *, content=None,
                 pin: str | None = None) -> str:
        """content (0052 — quinn's eyes): an optional litellm content-parts
        list (text + image parts) replacing the plain prompt in the message;
        `prompt` still sizes the estimate. Same authorize → execute → meter,
        image or not — a governed eye is metered like a governed thought.
        pin (0058 sp2): an assignment's named mind narrows the class — the
        plane refuses a pinned miss rather than serving a substitute."""
        import litellm                                            # optional extra: [governed]
        est = self.max_tokens + len(prompt) // 3 + (1500 if content else 0)
        grant = self.client.authorize(klass, est, pin=pin)
        if not grant or "model" not in grant:
            raise PermissionError("the plane refused this class under the current lease")
        resp = litellm.completion(model=grant["model"],
                                  messages=[{"role": "user",
                                             "content": content or prompt}],
                                  max_tokens=self.max_tokens)
        tokens = resp.usage.total_tokens
        try:
            usd = litellm.completion_cost(completion_response=resp)
        except Exception:
            usd = 0.0
        self.client.meter(grant, klass=klass, tokens=tokens, usd=usd, model=grant["model"])
        self.last_tokens += tokens
        self.last_calls += 1
        return resp.choices[0].message.content
