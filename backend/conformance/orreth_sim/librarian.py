"""The librarian tends the parking lot (0014 ∘ 0015): parked intents become knowledge.

The chassis parks what it cannot solve; the librarian sweeps the lot, gathers from
identified sources, admits the findings quarantined, and hands back a lookup skill —
so the retry succeeds on knowledge the failure itself commissioned. Failure is fuel,
automatically: `retry_parked` closes the circuit end to end (0015 maturation,
2026-07-08) — every handled assignment is retried with its commissioned knowledge, and
a DONE writes a `parked-closed` record deriving from the whole arc. The lot empties
itself, on the record, annotate-never-rewrite.
"""
from __future__ import annotations

import json

from . import crypto
from .knowledge import KnowledgeCategory
from .node import make_memory


def _body(rec: dict) -> dict:
    return json.loads(crypto._b64d(rec["body"]).decode()) if "body" in rec else {}


def tainted_refs(entries: list[dict], source_did: str) -> list[str]:
    """The 0014 §4 walk over wire-shaped entries [{ref, source_did, derived_from}]:
    everything the discredited source said, plus everything derived from those —
    transitively, however deep the lineage runs. Pure; the wire worker feeds it hits."""
    tainted = {e["ref"] for e in entries if e.get("source_did") == source_did}
    grew = True
    while grew:
        grew = False
        for e in entries:
            if e["ref"] not in tainted and any(d in tainted
                                               for d in e.get("derived_from") or []):
                tainted.add(e["ref"])
                grew = True
    return sorted(tainted)


def parked_intents(node) -> list[tuple[str, dict]]:
    handled = set()
    for rec in node.records.values():
        if "librarian-handled" in rec.get("tags", []):
            for d in rec.get("derived_from", []):
                handled.add(d)
    out = []
    for rid, rec in node.records.items():
        if "knowledge-intent" in rec.get("tags", []) and "parked" in rec.get("tags", []) \
                and rid not in handled:
            out.append((rid, _body(rec)))
    return out


def tend(node, gather) -> list[KnowledgeCategory]:
    """Sweep the lot. `gather(intent) -> [{claim, source_did, ref}]` — the world, identified."""
    built = []
    for rid, body in parked_intents(node):
        intent = body["parked_intent"]
        slug = "kb-" + str(abs(hash(intent)) % 99999)
        cat = KnowledgeCategory(node, intent, slug)
        ids = [cat.admit(f["claim"], {"did": f["source_did"], "ref": f.get("ref", "")})
               for f in gather(intent)]
        if len(ids) > 1:                                  # a second voice earns promotion
            cat.corroborate(ids[0], receipt_ids=ids[1:])
        marker = make_memory(node.steward, node.steward_kp, node.scope,
                             {"handled_intent": intent, "category": slug,
                              "admitted": len(ids)},
                             kind="semantic", tags=["librarian-handled"])
        marker["derived_from"] = [rid]                    # the assignment, receipted
        node.write(marker)
        built.append(cat)
    return built


def lookup_skill(cat: KnowledgeCategory):
    """The skill the librarian hands back: the category's current claims, each wearing
    its state honestly — provenance is UI even in a string (0008 §1). Deterministic,
    instant, free; recalled knowledge never speaks."""
    def lookup(_question: str) -> str:
        claims = [f"{e['claim']} ({e['state']})" for e in cat.current()
                  if e.get("state") != "recalled"]
        return " | ".join(claims) or "no admitted knowledge yet"
    return lookup


def handled_open(node) -> list[tuple[str, str, dict]]:
    """(parked_rid, marker_rid, marker_body) for every handled assignment whose parked
    intent no closure record has yet claimed — the retry's worklist."""
    closed = set()
    for rec in node.records.values():
        if "parked-closed" in rec.get("tags", []):
            closed.update(rec.get("derived_from", []))
    out = []
    for rid, rec in node.records.items():
        if "librarian-handled" not in rec.get("tags", []):
            continue
        for parked_rid in rec.get("derived_from", []):
            if parked_rid not in closed:
                out.append((parked_rid, rid, _body(rec)))
    return out


def retry_parked(node, run) -> list[dict]:
    """Close the circuit (0015 ∘ 0014, automatically): every handled assignment still
    open is retried WITH its commissioned knowledge as a lookup skill. DONE writes a
    `parked-closed` record deriving from the whole arc — the parked intent AND the
    handled marker — so the lot empties itself, receipted. A retry that still falls
    short leaves the assignment standing; the lot keeps honest books.
    `run(intent, skills) -> {"status", ...}`: chassis construction stays the caller's —
    cognition is injected here too."""
    closures = []
    for parked_rid, marker_rid, body in handled_open(node):
        intent, slug = body["handled_intent"], body["category"]
        out = run(intent, {"lookup": lookup_skill(KnowledgeCategory(node, intent, slug))})
        if out.get("status") != "done":
            continue                                      # still short — the lot keeps it
        closure = make_memory(node.steward, node.steward_kp, node.scope,
                              {"closed_intent": intent, "category": slug,
                               "answer": out.get("answer", ""),
                               "cycles": out.get("cycles")},
                              kind="semantic", tags=["parked-closed"])
        closure["derived_from"] = [parked_rid, marker_rid]  # the whole arc, one lineage
        closures.append({"intent": intent, "record": node.write(closure),
                         "answer": out.get("answer", "")})
    return closures
