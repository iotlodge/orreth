# PROVENANCE: Fable 5 (claude-fable-5) — 0015 maturation · 2026-07-08
"""GraphSpec v0 (0008 §2), sim-first: the chassis as a compile target.

One artifact, two projections: the graph IS the loop (nodes typed agent/tool/memory,
edges carrying the DONE/RETRY/breaker conditions) and the narrative IS the graph —
every sentence names the nodes and edges it renders (the 0008 §3 bijection, kept by
construction, so there is nothing to sync). Content-addressed like everything else;
steward-signed like any Standard; policy-checkable at SAVE: a spec naming a skill the
floor cannot bind, or an artifact that moved under its id, fails at compile — never at
incident review. Compiles DOWN to the Chassis (0015); governance, diff, and the pane
speak GraphSpec only, and no SDK ever leaks up.

The schema hardens into `contracts/` only after 0008 is blessed (JB's call) — the sim
proves the shape first (0000 §9).
"""
from __future__ import annotations

from . import crypto
from .chassis import Chassis

VERSION = "0.1.0"


class GraphSpecError(Exception):
    """Refused at save — never at incident review."""


def _content(spec: dict) -> dict:
    """What the id covers: everything but the id and the signature."""
    return {k: spec[k] for k in
            ("version", "scope", "title", "nodes", "edges", "objectives", "narrative")}


def chassis_spec(scope: str, *, title: str, persona: str = "", skills: tuple = (),
                 klass: str = "low", ladder: list[str] | None = None,
                 max_cycles: int = 3, max_obs: int = 3) -> dict:
    """The fixed loop as an artifact. Profile (persona, bounds, the ladder) rides the
    planner node — behavior arrives as data in the graph too. The narrative is built
    beside the nodes, one sentence per element, so the bijection cannot drift."""
    tier = ladder[0] if ladder else klass
    skill_nodes = [{"id": f"skill:{s}", "kind": "tool", "binding": {"skill": s}}
                   for s in skills]
    nodes = [
        {"id": "plan", "kind": "agent", "role": "planner", "model_tier": tier,
         "profile": {"persona": persona, "max_cycles": max_cycles, "max_obs": max_obs,
                     **({"ladder": list(ladder)} if ladder else {})}},
        *skill_nodes,
        {"id": "reason", "kind": "agent", "role": "reason", "model_tier": tier},
        {"id": "critic", "kind": "agent", "role": "critic", "model_tier": tier},
        {"id": "answer", "kind": "memory", "op": "write", "query_template": "run-record"},
        {"id": "park", "kind": "memory", "op": "write",
         "query_template": "knowledge-intent"},
    ]
    fan_out = [{"from": "plan", "to": n["id"]} for n in skill_nodes] \
        + [{"from": "plan", "to": "reason"}]
    fan_in = [{"from": n["id"], "to": "critic"} for n in skill_nodes] \
        + [{"from": "reason", "to": "critic"}]
    verdicts = [
        {"from": "critic", "to": "answer", "when": "DONE"},
        {"from": "critic", "to": "plan",
         "when": "RETRY" + (" — one class higher" if ladder else "")},
        {"from": "critic", "to": "park", "when": f"breaker: {max_cycles} cycles"},
    ]
    ref = lambda e: f"{e['from']}→{e['to']}"  # noqa: E731 — narrative edge naming
    narrative = [
        {"text": f"PLAN asks only the minimum observations (≤{max_obs}), in class "
                 f"{tier}, and fans them out in parallel.",
         "nodes": ["plan"], "edges": [ref(e) for e in fan_out]},
        *[{"text": f"Skill {s} answers deterministically — instant, free.",
           "nodes": [f"skill:{s}"], "edges": [f"skill:{s}→critic"]} for s in skills],
        {"text": "REASON thinks through the governed door, metered.",
         "nodes": ["reason"], "edges": ["reason→critic"]},
        {"text": "CRITIC judges: DONE lands the answer on the record; RETRY replans "
                 "with feedback"
                 + (", one class higher each time" if ladder else "") + ".",
         "nodes": ["critic", "answer"], "edges": ["critic→answer", "critic→plan"]},
        {"text": f"After {max_cycles} cycles the breaker PARKS the intent as a "
                 "knowledge assignment (0014) — failure is fuel.",
         "nodes": ["park"], "edges": ["critic→park"]},
    ]
    content = {"version": VERSION, "scope": scope, "title": title, "nodes": nodes,
               "edges": fan_out + fan_in + verdicts,
               "objectives": {"vector": "objective-met", "floors": []},
               "narrative": narrative}
    return {"id": crypto.content_hash(content), **content}


def sign(spec: dict, node) -> dict:
    """Authored + signed like any Standard (0008 §2)."""
    spec["signature"] = node.steward_kp.sign(
        node.steward["did"], {"id": spec["id"], "scope": spec["scope"],
                              "version": spec["version"]})
    return spec


def check(spec: dict, skills: dict) -> None:
    """The save gate: static validation BEFORE anything runs (0008 §2). Raises
    GraphSpecError with the reason — a refused artifact never becomes an incident."""
    if spec["id"] != crypto.content_hash(_content(spec)):
        raise GraphSpecError("the artifact moved under its id — refused at save")
    ids = {n["id"] for n in spec["nodes"]}
    for e in spec["edges"]:
        if e["from"] not in ids or e["to"] not in ids:
            raise GraphSpecError(f"edge {e['from']}→{e['to']} names a node that "
                                 "does not exist — refused at save")
    for n in spec["nodes"]:
        if n["kind"] == "agent" and not n.get("model_tier"):
            raise GraphSpecError(f"agent node {n['id']} has no model_tier — refused at save")
        if n["kind"] == "tool" and n["binding"]["skill"] not in skills:
            raise GraphSpecError(f"skill '{n['binding']['skill']}' is not bound on "
                                 "this floor — refused at save")
    roles = {n.get("role") for n in spec["nodes"] if n["kind"] == "agent"}
    pairs = {(e["from"], e["to"]) for e in spec["edges"]}
    if not ({"planner", "critic"} <= roles and ("critic", "plan") in pairs
            and ("critic", "park") in pairs):
        raise GraphSpecError("not chassis-shaped: the loop needs a planner, a critic, "
                             "the RETRY edge back to plan, and the breaker to park")
    named_n = [n for s in spec["narrative"] for n in s.get("nodes", [])]
    named_e = [e for s in spec["narrative"] for e in s.get("edges", [])]
    if sorted(named_n) != sorted(ids) or \
            sorted(named_e) != sorted(f"{a}→{b}" for a, b in pairs):
        raise GraphSpecError("narrative and graph disagree — the bijection broke; "
                             "refused at save")


def compile_chassis(spec: dict, surface, think, skills: dict) -> Chassis:
    """GraphSpec → a running Chassis. The compiled loop binds ONLY the skills the spec
    names (least-privilege attention starts at the artifact); profile flows from the
    planner node. Compiles down, never leaks up."""
    check(spec, skills)
    planner = next(n for n in spec["nodes"]
                   if n["kind"] == "agent" and n.get("role") == "planner")
    profile = planner.get("profile", {})
    bound = {n["binding"]["skill"]: skills[n["binding"]["skill"]]
             for n in spec["nodes"] if n["kind"] == "tool"}
    return Chassis(surface, think,
                   persona=profile.get("persona", ""), skills=bound,
                   max_cycles=profile.get("max_cycles", 3),
                   max_obs=profile.get("max_obs", 3),
                   klass=planner["model_tier"], ladder=profile.get("ladder"))
