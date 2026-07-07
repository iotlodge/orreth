"""The librarian tends the parking lot (0014 ∘ 0015): parked intents become knowledge.

The chassis parks what it cannot solve; the librarian sweeps the lot, gathers from
identified sources, admits the findings quarantined, and hands back a lookup skill —
so the retry succeeds on knowledge the failure itself commissioned. Failure is fuel,
automatically.
"""
from __future__ import annotations

from .knowledge import KnowledgeCategory
from .node import make_memory


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
            import json
            from . import crypto
            body = json.loads(crypto._b64d(rec["body"]).decode())
            out.append((rid, body))
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
