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

from . import crypto, factory, improver, markers, resolver
from .chassis import Chassis
from .identity import NOW, is_within
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


def author_plan(scope: str, *, req_id: str, objective: str,
                proposals: list, floors: list[str], budget: int = 2400,
                allowed=None, min_share: int = 60) -> dict:
    """0047 sp4 — the mind proposes, the law disposes. Semantic decomposition
    belongs to the studio; pricing, entitlement, and the save gate stay
    deterministic — money is never the mind's to invent. proposals:
    [{"seat": scope, "intent": sentence}] from the studio's typed plan;
    floors: the real seats on the wire. Refuses loudly (WorkflowError) on an
    empty plan, a malformed proposal, an unknown or duplicated seat, the
    orchestrator's own floor, or a template that fails check_workflow —
    refused at save, never at incident review. The returned plan is
    wire-shaped (curate_plan's exact keys) and additionally carries "spec" —
    the workflow template's content hash the walk of the work will name."""
    allowed = allowed or dispatch_allowed
    if not isinstance(proposals, list) or not proposals:
        raise WorkflowError("the mind proposed no intentions — an empty plan "
                            "is refused at save")
    entries, seen = [], set()
    for i, p in enumerate(proposals):
        seat = str((p or {}).get("seat") or "").strip() if isinstance(p, dict) else ""
        intent = str((p or {}).get("intent") or "").strip() if isinstance(p, dict) else ""
        if not seat or not intent:
            raise WorkflowError(f"proposal {i + 1} is not seat+intent shaped — "
                                "refused at save")
        if seat == scope:
            raise WorkflowError("the orchestrator's own floor is the assembly "
                                "seat, never a leg — refused at save")
        if seat in seen:
            raise WorkflowError(f"seat {seat} proposed twice — one leg per "
                                "seat; refused at save")
        if seat not in floors:
            raise WorkflowError(f"no floor named {seat} stands on this wire — "
                                "refused at save")
        seen.add(seat)
        entries.append({"seat": seat, "intent": intent})
    share = max(int(budget) // (len(entries) + 1), min_share)
    intentions = []
    for e in entries:
        entry = {"seat": e["seat"], "budget": {"tokens": share},
                 "intent": e["intent"]}
        if not allowed(scope, e["seat"]):
            entry["beyond_token"] = True     # honest in the plan: it will ask leave
        intentions.append(entry)
    spec = workflow_template(
        scope, name=f"objective-{req_id[:24]}",
        intentions=[{"id": f"i{n + 1}", "intent": e["intent"], "seat": e["seat"]}
                    for n, e in enumerate(entries)])
    check_workflow(spec)                     # the mind's plan survives the law or dies here
    goal = crypto.content_hash({"objective": objective, "req": req_id})
    return {"objective": objective, "goal": goal, "intentions": intentions,
            "dark": [], "spec": spec["id"],
            "question": f"the flow asks (0027 §8): where shall "
                        f"“{objective[:48]}” deploy? resolve me with your "
                        "answer — silence is denial",
            "share": share}


def gap_offer(reading: dict) -> dict | None:
    """0047 sp5 (law 7 — the gap is fuel, mechanically): when the studio's
    reading names gaps, the plan card carries the offer to GROW the missing
    craft — plainly worded, unchecked by default (0032 §4's one-approval-
    moment precedent, kept: the human's single word approves the plan AND,
    only if checked, commissions the lack). None when the reading names
    nothing — the offer is never pressed on a plan it doesn't fit."""
    gaps = [str(g).strip() for g in (reading or {}).get("gaps") or []
            if str(g).strip()]
    if not gaps:
        return None
    return {"gaps": gaps[:3],
            "terms": "one commission per gap — the librarian gathers, the "
                     "factory drafts, and the newborn craft WAITS at your "
                     "gate (0045 law 6)"}


def choreography(plan: dict, branches: list | None = None, *,
                 question_answer: str | None = None) -> dict:
    """The visible mind (0031 §6): the flow's choreography as DATA — nodes, edges,
    and a narrative in bijection (0008 §3's discipline), composed by the seat that
    owns the flow and rendered BLIND by the glass. Before approval it is the plan
    made visible; after assembly the same picture, lit by what actually ran —
    one world, one picture (rule 7): every branch shows, the mid-flow legs too."""
    remaining = list(branches or [])

    def claim(seat: str) -> dict:
        for i, b in enumerate(remaining):
            if b.get("seat") == seat:
                return remaining.pop(i)
        return {}

    fingers = []
    for n, entry in enumerate(plan.get("intentions") or [], 1):
        b = claim(entry.get("seat", "?"))
        fingers.append({"id": f"i{n}", "kind": "seat", "role": "fingertip",
                        "altitude": entry.get("seat", "?"),
                        "intent": entry.get("intent", ""),
                        "budget": (entry.get("budget") or {}).get("tokens"),
                        **({"beyond_token": True} if entry.get("beyond_token") else {}),
                        **({"status": b["status"]} if b.get("status") else {}),
                        **({"severity": b["severity"]} if b.get("severity") else {}),
                        **({"cycles": b["cycles"]} if b.get("cycles") is not None else {}),
                        **({"marker": b["marker"]} if b.get("marker") else {}),
                        **({"outcome": b["outcome"]} if b.get("outcome") else {}),
                        **({"answer": b["answer"]} if b.get("answer") else {}),
                        **({"span": b["span"]} if b.get("span") else {})})
    for b in remaining:                       # mid-flow legs (the iac after an answer)
        n = len(fingers) + 1
        fingers.append({"id": f"i{n}", "kind": "seat", "role": "fingertip",
                        "altitude": b.get("seat", "?"),
                        "intent": "dispatched mid-flow, on the human's answer",
                        **({"status": b["status"]} if b.get("status") else {}),
                        **({"severity": b["severity"]} if b.get("severity") else {}),
                        **({"cycles": b["cycles"]} if b.get("cycles") is not None else {}),
                        **({"marker": b["marker"]} if b.get("marker") else {}),
                        **({"outcome": b["outcome"]} if b.get("outcome") else {}),
                        **({"answer": b["answer"]} if b.get("answer") else {}),
                        **({"span": b["span"]} if b.get("span") else {})})
    nodes = [{"id": "objective", "kind": "seat", "role": "orchestrator"},
             *fingers,
             {"id": "review", "kind": "seat", "role": "review"},
             {"id": "human", "kind": "seat", "role": "human"}]
    dispatch = [{"from": "objective", "to": f["id"]} for f in fingers]
    report = [{"from": f["id"], "to": "review"} for f in fingers]
    close = [{"from": "review", "to": "human", "when": "assembled"}]
    ref = lambda e: f"{e['from']}→{e['to']}"  # noqa: E731 — narrative edge naming
    narrative = [
        {"text": f"The objective lands; its orchestration seat plans high and "
                 f"dispatches {len(fingers)} intention(s) down.",
         "nodes": ["objective"], "edges": [ref(e) for e in dispatch]},
        *[{"text": f"Intention {f['id']} rides to {f['altitude']} carrying one "
                   "intent and a budget slice — never the plan, never the siblings"
                   + (". It will ask leave — beyond this token."
                      if f.get("beyond_token") else ".")
                   + (f" It returned {f['status']}"
                      + (f", graded {f['severity']} by the dispatching seat"
                         if f.get("severity") else "") + "."
                      if f.get("status") else ""),
           "nodes": [f["id"]], "edges": [f"{f['id']}→review"]} for f in fingers],
        {"text": "REVIEW assembles what returned and hands it UP: the human's "
                 "request is the top node, and its resolution is the only "
                 "completion confirmation."
                 + (f" You answered: “{question_answer}”." if question_answer else ""),
         "nodes": ["review", "human"], "edges": ["review→human"]},
    ]
    return {"kind": "graph", "title": str(plan.get("objective", ""))[:80],
            "nodes": nodes, "edges": dispatch + report + close,
            "narrative": narrative}


def make_intention(objective_hash: str, intent: str, budget_tokens: int,
                refs: list | None = None) -> dict:
    """What rides down — and ALL that rides down (0027 §3 · 0030): one intent, a
    budget slice, citation refs. Never the plan, never the siblings, never the why.
    0033 §4 (the coordinate, soft): the intention is content-addressed — the
    ladder's second rung gains the identity every record below it will cite."""
    msg = {"of": objective_hash, "intent": intent,
           "budget": {"tokens": int(budget_tokens)}, "refs": list(refs or [])}
    return {"id": crypto.content_hash(msg), **msg}


def coordinate_tags(of: str | None = None, via: str | None = None) -> list[str]:
    """The ladder's axes as tags (0033 §4, the soft landing): `of:<objective>` ·
    `via:<intention>` — index lookups; kept valid beside the hard field below.
    Records cite only hashes they already hold at write time; nothing is
    invented after the fact."""
    tags = []
    if of:
        tags.append(f"of:{of}")
    if via:
        tags.append(f"via:{via}")
    return tags


def coordinate(objective: str | None = None, intention: str | None = None,
               observation: str | None = None, thought: str | None = None) -> dict:
    """The coordinate, HARD (0033 §4 — the Phase D gate, JB approval
    2026-07-15): the record's address in the ladder as a first-class field,
    contracts/v0-legal. Rides unsigned beside derived_from, matching that
    posture; the signature-subset widening is its own future question."""
    return {k: v for k, v in (("objective", objective), ("intention", intention),
                              ("observation", observation), ("thought", thought))
            if v}


def make_aperture(agent: dict, kp, scope: str, *, of: str, for_agent: str,
                  law: str, task: dict, behavior: dict,
                  knowledge: list | None = None, output: dict | None = None,
                  objective: str | None = None) -> dict:
    """The aperture (0031 §2 — landed at the Phase D gate): the context envelope
    made first-class. Assembled at dispatch, signed by the DISPATCHING seat,
    content-addressed, everything by reference — what the mind could see, on
    the record. RunRecords pin it (context_hash, semantics widened at the
    gate); same aperture ⇒ the same run is re-cuttable."""
    body = {"aperture": {
        "of": of, "seat": agent["did"], "agent": for_agent, "law": law,
        "task": dict(task), "behavior": dict(behavior),
        "knowledge": list(knowledge or []),
        **({"output": dict(output)} if output else {}),
    }}
    rec = make_memory(agent, kp, scope, body, kind="semantic",
                      tags=["aperture", *coordinate_tags(objective, of)])
    rec["coordinate"] = coordinate(objective=objective, intention=of)
    return rec


def by_coordinate(node, *, objective: str | None = None,
                  intention: str | None = None) -> dict[str, dict]:
    """The index lookup the coordinate exists for: every record that served an
    objective (or a single intention) — a tag match, not a lineage recursion."""
    want = set(coordinate_tags(objective, intention))
    if not want:
        return {}
    return {rid: r for rid, r in node.records.items()
            if want <= set(r.get("tags") or [])}


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
            # the span (0043 sp1): start/end/status riding the branch — the
            # choreography record the glass already draws gains a stopwatch
            import time as _time
            started, t0 = NOW(), _time.perf_counter()
            branch.update(self._fingertip(target, beckys[target.scope], work, n,
                                          think, skills or {}))
            branch["span"] = {"started": started, "ended": NOW(),
                              "ms": int((_time.perf_counter() - t0) * 1000),
                              "status": branch["status"]}
            # review rides altitude (0027 §6): the DISPATCHING seat grades the
            # return — author ≠ agent, on the record, lanes route what follows
            severity = review_severity(branch["status"], branch.get("cycles"))
            mk = markers.make_marker(me, self.surface.kp, self.home.scope,
                                     [branch["outcome"]],
                                     reason=f"review of intention {n['id']}: "
                                            f"{branch['status']}",
                                     change_severity=severity,
                                     extra_tags=coordinate_tags(self.goal, work["id"]))
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
        # the shelf speaks at dispatch (0031 §4): the chassis runs under the HOME
        # floor's active asset versions — an adoption changes the next run, not
        # just the record. No asset yet → the genesis defaults, unchanged.
        beh = improver.resolve_behavior(self.home)
        prof = beh["profile"]
        coord = coordinate_tags(work["of"], work.get("id"))
        # the aperture (0031 §2, the gate): the dispatching seat assembles and
        # signs the whole opening BEFORE the mind runs — everything by reference
        ap = make_aperture({"did": self.surface.identity["did"],
                            "scope": self.home.scope},
                           self.surface.kp, self.home.scope,
                           of=work["id"], for_agent=fsurf.identity["did"],
                           law=resolver.resolve(target)["id"],
                           task={"intent": work["intent"],
                                 "budget": dict(work["budget"])},
                           behavior={"profile": crypto.content_hash(prof),
                                     "prompts": [crypto.content_hash({"t": beh["plan_template"]}),
                                                 crypto.content_hash({"t": beh["critic_template"]})]},
                           knowledge=list(work.get("refs") or []),
                           objective=work["of"])
        ap_id = self.home.write(ap)
        res = Chassis(fsurf, think, skills=skills,
                      persona=str(prof.get("persona", "")),
                      max_cycles=int(prof.get("max_cycles", 2)),
                      max_obs=int(prof.get("max_obs", 3)),
                      plan_template=beh["plan_template"],
                      critic_template=beh["critic_template"],
                      coordinate=coord, aperture=ap_id).run(work["intent"])
        outcome = make_memory({"did": fsurf.identity["did"], "scope": target.scope},
                              fsurf.kp, target.scope,
                              {"outcome": {"intention": n["id"], "of": work["of"],
                                           "status": res["status"],
                                           "answer": res.get("answer", ""),
                                           "cycles": res.get("cycles")}},
                              kind="semantic", tags=["intention-outcome", *coord])
        outcome["coordinate"] = coordinate(objective=work["of"],
                                           intention=work.get("id"))
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
                          tags=["objective-outcome", *coordinate_tags(self.goal)])
        rec["coordinate"] = coordinate(objective=self.goal)
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
