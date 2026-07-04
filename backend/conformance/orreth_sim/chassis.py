"""Orreth.agent — the Chassis (0015): one fixed loop forever; behavior arrives as data.

prepare → plan → the NUCLEUS (holds the plan, executes observations in PARALLEL — each
either a deterministic skill or a governed model call: the becky-shaped duality) →
reflect/critic → replan → repeat until objective or breaker. The breaker doesn't fail:
it PARKS — the unsolved intent becomes a knowledge-acquisition assignment (0014).
Failure is fuel.

Cognition is injected (`think(klass, prompt) -> str`): the same chassis runs on a stub
in tests and the governed model plane in production. Persona is a costume; the loop is
the law; every cycle is on the record.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from . import crypto, resolver
from .identity import NOW
from .node import make_memory

_PLAN = """{persona}
Objective: {intent}
{feedback}Available skills (deterministic, instant): {skills}.
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


class Chassis:
    """The architecture never changes; Policy, Prompts, Skills, Persona are the profile."""

    def __init__(self, surface, think, *, persona: str = "", skills: dict | None = None,
                 max_cycles: int = 3, max_obs: int = 3, klass: str = "low"):
        self.surface, self.think = surface, think
        self.persona, self.skills = persona, skills or {}
        self.max_cycles, self.max_obs, self.klass = max_cycles, max_obs, klass
        self.trace: list[dict] = []               # the loop, on the record
        self._ctx = None                          # ResolvedContext id — the law, pinned

    # ---- the fixed loop ---------------------------------------------------------------
    def run(self, intent: str) -> dict:
        feedback = ""
        for cycle in range(1, self.max_cycles + 1):
            budget_before = self.surface.budget_left
            observations = self._plan(intent, feedback)
            results = self._nucleus(observations)             # parallel, least-privilege
            verdict = self.think(self.klass, _CRITIC.format(
                persona=self.persona, intent=intent,
                results="\n".join(f"- [{k}] {q} → {r}" for k, q, r in results)))
            done = verdict.strip().upper().startswith("DONE")
            self.trace.append({"cycle": cycle, "observations": len(results),
                               "verdict": verdict[:60]})
            self._record(intent, cycle, done, budget_before - self.surface.budget_left)
            if done:
                return {"status": "done", "answer": verdict.split(":", 1)[1].strip(),
                        "cycles": cycle}
            feedback = f"Prior attempt lacked: {verdict.split(':', 1)[-1].strip()}\n"
        return self._park(intent, feedback)                   # the breaker doesn't fail

    def _plan(self, intent: str, feedback: str) -> list[tuple[str, str]]:
        raw = self.think(self.klass, _PLAN.format(
            persona=self.persona, intent=intent, feedback=feedback,
            skills=", ".join(self.skills) or "none", max_obs=self.max_obs))
        obs = []
        for line in raw.splitlines():
            line = line.strip()
            if line.upper().startswith("OBSERVE") and ":" in line:
                head, question = line.split(":", 1)
                skill = head.split()[-1].strip().lower()
                obs.append((skill, question.strip()))
        return obs[: self.max_obs] or [("reason", intent)]    # never wander, never stall

    def _nucleus(self, observations: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
        """Holds the plan; executes ONLY what the planner asked — in parallel. Deterministic
        skills answer instantly and free; 'reason' goes through the governed door."""
        def one(skill: str, question: str) -> tuple[str, str, str]:
            if skill in self.skills:
                return (skill, question, str(self.skills[skill](question)))
            return ("reason", question,
                    self.think(self.klass, f"{self.persona}\nAnswer concisely: {question}"))
        with ThreadPoolExecutor(max_workers=len(observations)) as pool:
            return list(pool.map(lambda o: one(*o), observations))

    def _record(self, intent: str, cycle: int, done: bool, tokens: int) -> None:
        """Every cycle of thought is a signed RunRecord, pinned to the law it ran under —
        the roll-up's raw material, and the presence layer's heartbeat."""
        node = self.surface.node
        if self._ctx is None:
            self._ctx = resolver.resolve(node)["id"]
        run = {
            "id": crypto.content_hash({"i": intent, "c": cycle, "at": NOW(),
                                       "a": self.surface.identity["did"]}),
            "agent": self.surface.identity["did"], "scope": node.scope,
            "goal_hash": crypto.content_hash({"intent": intent}),
            "occurred_at": NOW(), "outcome": "success" if done else "partial",
            "scores": [{"objective": "objective-met", "score": 1.0 if done else 0.0}],
            "cost": {"tokens": max(tokens, 0), "model_calls": 1},
            "context_hash": self._ctx,
            "author": node.steward["did"],
        }
        run["sig"] = node.steward_kp.sign(node.steward["did"], {k: run[k] for k in
                     ("id", "agent", "scope", "goal_hash", "occurred_at")})
        node.record_run(run)

    def _park(self, intent: str, feedback: str) -> dict:
        """Breaker: the unsolved objective becomes a knowledge-acquisition assignment (0014)."""
        node = self.surface.node
        rid = node.write(make_memory(
            node.steward, node.steward_kp, node.scope,
            {"parked_intent": intent, "missing": feedback.strip(),
             "handoff": "knowledge-acquisition"},
            kind="semantic", tags=["parked", "knowledge-intent"]))
        return {"status": "parked", "record": rid, "cycles": self.max_cycles}
