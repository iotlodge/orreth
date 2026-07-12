# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-11 — 0027, the Fingertip
# 0030 §3 (2026-07-12): the plan gate — origin plans wait for their human; and the
# ladder's word is INTENTION (Objective · Intention · Observation · Thought).
"""The Fingertip (0027 · 0030): thought.graph made concrete — the universe IS the
node graph, and the ladder is Objective · Intention · Observation · Thought.

An objective arrives at a tier; the orchestration incarnation AT that tier curates
it into a PLAN — and the plan is HITL-approved before any intention fans (0030 §3:
origin plans always wait for their human). Intentions ride down (one intent, a
budget slice, citation refs — never the whole); the chassis executes observations
at the bottom; the dispatching seat grades what returns with critic markers (0024);
and the human's request is the top — no orchestrator ever confirms its own
completion (JB lock 2026-07-11). Templates are versioned artifacts in memory,
factory-maintained; standing jobs are the same incarnations with no completion
condition (R8). Scratch evaporates by design (R7): what lands is RunRecords,
outcomes, and what the floors' KeepRules pin.
"""
from __future__ import annotations

from . import crypto, factory, markers
from .chassis import Chassis
from .identity import is_within
from .node import make_memory

VERSION = "0.1.0"


class WorkflowError(Exception):
    """Refused at save — never at incident review (0008's law, kept)."""


def _content(spec: dict) -> dict:
    return {k: spec[k] for k in
            ("version", "scope", "title", "standing", "nodes", "edges", "narrative")}


def workflow_template(scope: str, *, name: str, intentions: list[dict],
                      standing: bool = False) -> dict:
    """A universe-level workflow as a GraphSpec-shaped artifact (R8): nodes are
    SEATS with altitude, edges carry dispatch DOWN and review UP, the narrative
    keeps the 0008 §3 bijection. Non-standing templates END AT THE HUMAN — the
    objective's request is the top node (JB lock 2026-07-11). Standing templates
    loop review→objective on the beat instead: no completion condition — an organ.

    intentions: [{"id", "intent", "seat": scope | "home", "ask_human": optional}]
    """
    finger_nodes = [{"id": s["id"], "kind": "seat", "role": "fingertip",
                     "altitude": s.get("seat", "home"), "intent": s["intent"],
                     **({"ask_human": s["ask_human"]} if s.get("ask_human") else {})}
                    for s in intentions]
    nodes = [{"id": "objective", "kind": "seat", "role": "orchestrator", "altitude": "home"},
             *finger_nodes,
             {"id": "review", "kind": "seat", "role": "review", "altitude": "home"}]
    dispatch = [{"from": "objective", "to": n["id"]} for n in finger_nodes]
    report = [{"from": n["id"], "to": "review"} for n in finger_nodes]
    if standing:
        close = [{"from": "review", "to": "objective", "when": "beat"}]
        top_sentence = {"text": "REVIEW folds each beat's findings back into the "
                                "objective — no completion condition; the job beats "
                                "like an organ (R8).",
                        "nodes": ["review"], "edges": ["review→objective"]}
    else:
        nodes.append({"id": "human", "kind": "seat", "role": "human", "altitude": "top"})
        close = [{"from": "review", "to": "human", "when": "assembled"}]
        top_sentence = {"text": "REVIEW assembles what returned and hands it UP: the "
                                "human's request is the top node, and its resolution "
                                "is the only completion confirmation.",
                        "nodes": ["review", "human"], "edges": ["review→human"]}
    ref = lambda e: f"{e['from']}→{e['to']}"  # noqa: E731 — narrative edge naming
    narrative = [
        {"text": f"The objective lands at {scope}; its orchestration incarnation "
                 f"plans high and dispatches {len(finger_nodes)} intention(s) down.",
         "nodes": ["objective"], "edges": [ref(e) for e in dispatch]},
        *[{"text": f"Intention {n['id']} rides to {n['altitude']} carrying one intent, "
                   "a budget slice, and citation refs — never the whole.",
           "nodes": [n["id"]], "edges": [f"{n['id']}→review"]} for n in finger_nodes],
        top_sentence,
    ]
    content = {"version": VERSION, "scope": scope, "title": name, "standing": standing,
               "nodes": nodes, "edges": dispatch + report + close,
               "narrative": narrative}
    return {"id": crypto.content_hash(content), **content}


def check_workflow(spec: dict) -> None:
    """The save gate (0008 §2's discipline, kept): refused at save, never at
    incident review."""
    if spec["id"] != crypto.content_hash(_content(spec)):
        raise WorkflowError("the artifact moved under its id — refused at save")
    ids = {n["id"] for n in spec["nodes"]}
    for e in spec["edges"]:
        if e["from"] not in ids or e["to"] not in ids:
            raise WorkflowError(f"edge {e['from']}→{e['to']} names a node that "
                                "does not exist — refused at save")
    for n in spec["nodes"]:
        if n.get("role") == "fingertip" and not n.get("intent"):
            raise WorkflowError(f"fingertip seat {n['id']} carries no intent — "
                                "refused at save")
    roles = [n.get("role") for n in spec["nodes"]]
    pairs = {(e["from"], e["to"]) for e in spec["edges"]}
    if roles.count("orchestrator") != 1 or roles.count("review") != 1:
        raise WorkflowError("a workflow has exactly one orchestrator and one review "
                            "seat — refused at save")
    if spec["standing"]:
        if "human" in roles or ("review", "objective") not in pairs:
            raise WorkflowError("a standing job never completes: no human top, and "
                                "review loops back on the beat — refused at save")
    elif "human" not in roles or ("review", "human") not in pairs:
        raise WorkflowError("the human's request IS the top node (JB lock "
                            "2026-07-11) — a workflow without it is refused at save")
    named_n = [n for s in spec["narrative"] for n in s.get("nodes", [])]
    named_e = [e for s in spec["narrative"] for e in s.get("edges", [])]
    if sorted(named_n) != sorted(ids) or \
            sorted(named_e) != sorted(f"{a}→{b}" for a, b in pairs):
        raise WorkflowError("narrative and graph disagree — the bijection broke; "
                            "refused at save")


def save_template(node, spec: dict) -> str:
    """A versioned artifact in memory — config IS memory (R8). The factory
    maintains these like any behavioral asset; a new version is a new record,
    lineage intact, and the old one is never rewritten."""
    check_workflow(spec)
    rec = make_memory(node.steward, node.steward_kp, node.scope,
                      {"workflow": {"id": spec["id"], **_content(spec)}},
                      kind="semantic", tags=["workflow-template", spec["title"]])
    return node.write(rec)


def make_intention(objective_hash: str, intent: str, budget_tokens: int,
                refs: list | None = None) -> dict:
    """What rides down — and ALL that rides down (0027 §3 · 0030): one intent, a
    budget slice, citation refs. Never the plan, never the siblings, never the why."""
    return {"of": objective_hash, "intent": intent,
            "budget": {"tokens": int(budget_tokens)}, "refs": list(refs or [])}


def dispatch_allowed(audience: str, target_scope: str) -> bool:
    """Entitlement is the token (0027 §7): dispatch rides only where the
    orchestration's becky-chained authority already reaches."""
    return is_within(target_scope, audience)


def review_severity(status: str, cycles: int | None) -> str:
    """The reviewing seat's grade (0024 lanes): clean first-cycle DONE is a low;
    a DONE that needed correction is a medium; an unfinished intention is a high —
    the human's lane, because unfinished work is where the risk lives."""
    if status == "done":
        return "low" if (cycles or 1) <= 1 else "medium"
    return "high"


class Orchestration:
    """One objective, living as a factory-stamped incarnation (R8): birth
    certificate, budget from the intent, the objective's life. run() dispatches,
    reviews, assembles — and RETURNS; the caller's request is the confirmation,
    never this class (JB lock 2026-07-11)."""

    def __init__(self, home, becky, template: dict, objective: str, *,
                 archetype: dict | None = None, budget_tokens: int = 2400):
        check_workflow(template)
        self.home, self.template, self.objective = home, template, objective
        arch = archetype or becky.issue_identity("archetype", home.scope)[0]
        gen = "standing-" + template["title"] if template["standing"] else \
            "objective-" + crypto.content_hash({"o": objective})[:23]
        [self.surface] = factory.stamp(home, becky, arch, 1, generation=gen,
                                       budget_tokens=budget_tokens)
        self.goal = crypto.content_hash({"objective": objective})
        self.answers: dict[str, str] = {}   # HITL: intention id -> the human's word
        self.branches: dict[str, dict] = {} # intention id -> terminal branch state

    # ---- the plan gate (0030 §3) ----------------------------------------------------
    def plan(self) -> dict:
        """The curated plan, readable: what would fan, where, and what it will ask
        the human mid-flow. This is what STAGES — origin plans always wait for
        their human (JB canon 2026-07-12)."""
        fingers = [n for n in self.template["nodes"] if n.get("role") == "fingertip"]
        share = max(self.surface.budget_left // max(len(fingers), 1), 60)
        return {"objective": self.objective, "goal_hash": self.goal,
                "intentions": [{"id": n["id"], "seat": n["altitude"],
                                "intent": n["intent"],
                                **({"asks_you": n["ask_human"]}
                                   if n.get("ask_human") else {}),
                                "budget": {"tokens": share}} for n in fingers]}

    # ---- HITL inside the flow (0027 §8) --------------------------------------------
    def questions(self) -> list[dict]:
        """What waits for the human right now — consequence waits (0012)."""
        return [{"intention": n["id"], "question": n["ask_human"]}
                for n in self.template["nodes"]
                if n.get("ask_human") and n["id"] not in self.answers]

    def answer_human(self, intention_id: str, text: str) -> None:
        """The human's word arrives; the parked branch may dispatch on the next run."""
        self.answers[intention_id] = text

    # ---- the flow ------------------------------------------------------------------
    def run(self, seats: dict, beckys: dict, think, skills: dict | None = None,
            *, plan_approved: bool = False) -> dict:
        """seats: scope -> node — the universe construct IS the node graph. Each
        intention becomes a fingertip chassis at its seat; results ride up; the
        dispatching seat grades every return on the record. Re-runnable: finished
        branches stay finished (the resume shape, like the self-dialog's).

        THE GATE COMES FIRST (0030 §3): without the human's approval of the plan,
        nothing fans — the staged plan is returned instead. Consequence waits."""
        if not plan_approved:
            return {"status": "staged", "plan": self.plan(),
                    "held": "the plan waits for its human (0030 §3) — origin "
                            "plans always wait"}
        fingers = [n for n in self.template["nodes"] if n.get("role") == "fingertip"]
        share = max(self.surface.budget_left // max(len(fingers), 1), 60)
        me = {"did": self.surface.identity["did"], "scope": self.home.scope}
        for n in fingers:
            if n["id"] in self.branches and \
                    self.branches[n["id"]].get("status") not in ("waiting-human", "dark"):
                continue                                   # finished stays finished
            branch: dict = {"intention": n["id"], "seat": n["altitude"]}
            if n.get("ask_human") and n["id"] not in self.answers:
                branch["status"] = "waiting-human"          # consequence waits (0012)
                branch["question"] = n["ask_human"]
                self.branches[n["id"]] = branch
                continue
            target = self.home if n["altitude"] == "home" else seats.get(n["altitude"])
            if target is None or not dispatch_allowed(
                    self.surface.lease["audience"], target.scope):
                # refuse AND ask (JB lock 2026-07-11): the branch goes dark, and a
                # human-visible entitlement ask lands on the record at home
                branch["status"] = "dark"
                branch["entitlement_ask"] = self.home.write(make_memory(
                    me, self.surface.kp, self.home.scope,
                    {"entitlement_ask": {"of": self.goal, "target": n["altitude"],
                                         "intention": n["id"]}},
                    kind="semantic", tags=["entitlement-ask"]))
                self.branches[n["id"]] = branch
                continue
            intent = n["intent"] if n["id"] not in self.answers else \
                f"{n['intent']} — the human answered: {self.answers[n['id']]}"
            work = make_intention(self.goal, intent, share, refs=n.get("refs"))
            branch.update(self._fingertip(target, beckys[target.scope], work, n,
                                          think, skills or {}))
            # review rides altitude (0027 §6): the DISPATCHING seat grades the
            # return — author ≠ agent, on the record, lanes route what follows
            severity = review_severity(branch["status"], branch.get("cycles"))
            mk = markers.make_marker(me, self.surface.kp, self.home.scope,
                                     [branch["outcome"]],
                                     reason=f"review of intention {n['id']}: "
                                            f"{branch['status']}",
                                     change_severity=severity)
            branch["severity"], branch["marker"] = severity, self.home.write(mk)
            self.branches[n["id"]] = branch
        return self._assemble(me)

    def _fingertip(self, target, becky, work: dict, n: dict, think,
                   skills: dict) -> dict:
        """The bottom of the graph: a stamped fingertip runs the chassis on its
        intention — the observations happen here (0030's third rung). Scratch
        evaporates (R7); RunRecords land per cycle; the outcome rides up."""
        [fsurf] = factory.stamp(target, becky, self.surface.identity, 1,
                                generation=f"finger-{n['id']}",
                                budget_tokens=work["budget"]["tokens"])
        res = Chassis(fsurf, think, skills=skills, max_cycles=2).run(work["intent"])
        outcome = make_memory({"did": fsurf.identity["did"], "scope": target.scope},
                              fsurf.kp, target.scope,
                              {"outcome": {"intention": n["id"], "of": work["of"],
                                           "status": res["status"],
                                           "answer": res.get("answer", ""),
                                           "cycles": res.get("cycles")}},
                              kind="semantic", tags=["intention-outcome"])
        rid = target.write(outcome)
        factory.retire(target, fsurf.identity)          # the intention was the life
        return {"status": res["status"], "answer": res.get("answer", ""),
                "cycles": res.get("cycles"), "outcome": rid}

    def _assemble(self, me: dict) -> dict:
        """The assembly rides UP as a record; the RETURN is a report, never a
        confirmation — the human's request resolution is the top (JB lock)."""
        branches = list(self.branches.values())
        waiting = [b for b in branches if b["status"] == "waiting-human"]
        dark = [b for b in branches if b["status"] == "dark"]
        done = all(b["status"] == "done" for b in branches) and bool(branches)
        assembly = {"objective": self.objective, "goal_hash": self.goal,
                    "branches": branches,
                    "verification": "complete" if done else "partial",
                    **({"waiting_on_human": [b["intention"] for b in waiting]}
                       if waiting else {}),
                    **({"dark": [b["intention"] for b in dark]} if dark else {})}
        rec = make_memory(me, self.surface.kp, self.home.scope,
                          {"objective_outcome": assembly}, kind="semantic",
                          tags=["objective-outcome"])
        assembly["record"] = self.home.write(rec)
        return assembly


class PortfolioMonitor:
    """The first standing incarnation (JB lock 2026-07-11): an immortal job,
    beating like an organ (R8). Each beat reviews the floors' pulse — aggregates
    only, the sibling-benchmark law (0005) — and writes one observation memory.
    There is no completion condition to reach; retirement is a governed act, not
    an outcome. Its factory-RL duty arrives with spoonful 7 (0011)."""

    def __init__(self, home, becky, *, archetype: dict | None = None,
                 budget_tokens: int = 1200):
        arch = archetype or becky.issue_identity("archetype", home.scope)[0]
        [self.surface] = factory.stamp(home, becky, arch, 1,
                                       generation="standing-portfolio-monitor",
                                       budget_tokens=budget_tokens)
        self.home, self.beats = home, 0

    def beat(self) -> str:
        self.beats += 1
        obs = {"portfolio": {"beat": self.beats,
                             "cohort": self.home.benchmark(),
                             "rollups": len(self.home.child_rollups)}}
        rec = make_memory({"did": self.surface.identity["did"],
                           "scope": self.home.scope},
                          self.surface.kp, self.home.scope, obs,
                          kind="episodic", tags=["portfolio-observation", "standing"])
        return self.home.write(rec)
