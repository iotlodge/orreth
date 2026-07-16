# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0033, the Physics of Memory
"""The information-theory harness (0033 §6): the science, computable from the log.

Pure functions over records that already exist — no new stores, no cognition, and
no gates (0033 rule 4: measures inform; the lanes decide). Each metric is the
formal footing under a claim the architecture already makes:

  reconstruction entropy    the headline: in an ordinary world the uncertainty of
                            reconstructing the past GROWS with time; here it is
                            bounded by contract — every link resolves to a live
                            record, an honest stub, or is loudly missing
  entropy · information gain  uncertainty on the record, and whether another look
                            is worth its cost (0029's modality gate, 0032's news)
  distillation ratio        the compression the auditor can see (0003)
  resolution fidelity       how much of a distillation still walks to source
                            (the contract-scored version arrives with sp2)
  context efficiency        decision value per token transmitted — 0027's
                            restraint, as a number
  provenance completeness   the % of lineage that resolves — to a record or an
                            honest stub, never to silence
  corroboration independence  voices vs echoes (0014: the same voice twice is
                            still one voice)
"""
from __future__ import annotations

import json
import math

from . import crypto

# an unresolvable reference — the cap on honest ignorance, flagged wherever it appears
MISSING_BITS = 32.0
# a tombstone stub — existence, author, and time remain certain; content uncertainty
# is bounded by the class's declared distortion (sp2 supplies per-class bounds)
STUB_BITS = 8.0


# ---- Shannon, plain -------------------------------------------------------------------

def entropy(dist: dict[str, float]) -> float:
    """H(X) in bits over a discrete distribution; tolerant of un-normalized input."""
    total = sum(v for v in dist.values() if v > 0)
    if total <= 0:
        return 0.0
    return -sum((v / total) * math.log2(v / total)
                for v in dist.values() if v > 0)


def information_gain(prior: dict[str, float], posterior: dict[str, float]) -> float:
    """IG = H(prior) − H(posterior): what the second look was worth, in bits."""
    return entropy(prior) - entropy(posterior)


# ---- resolution: the whole tree answers for a reference --------------------------------

def _tree(node) -> list:
    root = node
    while root.parent is not None:
        root = root.parent
    out: list = []

    def walk(n) -> None:
        out.append(n)
        for c in n.children:
            walk(c)

    walk(root)
    return out


def resolve(node, ref: str) -> tuple[dict | None, str]:
    """Where a reference leads: ('live') a record with its body · ('stub') a
    tombstoned record or a purge-set entry — honest remains, existence proven ·
    ('missing') silence, the one state the architecture is built to prevent."""
    for n in _tree(node):
        rec = n.records.get(ref)
        if rec is not None:
            return (rec, "live" if "body" in rec else "stub")
        if ref in n.purged:
            return (None, "stub")
    return (None, "missing")


def _body(rec: dict) -> dict:
    return json.loads(crypto._b64d(rec["body"]).decode()) if "body" in rec else {}


def _body_bytes(rec: dict) -> int:
    return len(crypto._b64d(rec["body"])) if "body" in rec else 0


# ---- the headline: reconstruction entropy ----------------------------------------------

def reconstruction_entropy(node, record_id: str, *, stub_bits: float = STUB_BITS,
                           missing_bits: float = MISSING_BITS) -> dict:
    """Uncertainty, in bits, of re-deriving a record's full evidential past.

    Walks derived_from transitively; every link contributes by what it resolves
    to: live = 0.0 (re-derivable exactly) · stub = bounded by declared class
    distortion · missing = the cap, flagged. In Orreth the answer is bounded by
    contract however old the record; a world without provenance staircases to
    links × missing_bits (see mortal_reconstruction_entropy — the demo's foil)."""
    seen: set[str] = set()
    frontier = [record_id]
    bits, live, stubs, missing = 0.0, 0, 0, 0
    while frontier:
        ref = frontier.pop()
        if ref in seen:
            continue
        seen.add(ref)
        rec, state = resolve(node, ref)
        if state == "live":
            live += 1
            if ref != record_id:              # the target itself is the question, not a link
                bits += 0.0
            frontier.extend(rec.get("derived_from", []))
        elif state == "stub":
            stubs += 1
            bits += stub_bits
        else:
            missing += 1
            bits += missing_bits
    links = len(seen) - 1                      # links, not counting the target
    return {"bits": round(bits, 4), "links": max(links, 0),
            "live": max(live - 1, 0), "stubs": stubs, "missing": missing}


def mortal_reconstruction_entropy(link_ages_days: list[float], *,
                                  retention_days: float = 90.0,
                                  missing_bits: float = MISSING_BITS) -> float:
    """The counterfactual an ordinary enterprise lives in: logs expire, nothing
    leaves a stub, provenance was never written. Every link older than the
    retention horizon is simply gone — entropy is a staircase that only climbs."""
    return round(sum(missing_bits for a in link_ages_days if a > retention_days), 4)


# ---- the auditor's numbers --------------------------------------------------------------

def distillation_ratio(node) -> dict:
    """Raw bytes in vs distilled bytes out, over this node's distillations —
    the shape of the pyramid (0003), measured. Coverage is honest: sources that
    no longer hold bytes are counted as links but not sized."""
    raw, distilled, links, sized = 0, 0, 0, 0
    for rec in node.records.values():
        if rec.get("kind") != "distillation":
            continue
        distilled += _body_bytes(rec)
        for ref in rec.get("derived_from", []):
            links += 1
            src, state = resolve(node, ref)
            if state == "live":
                sized += 1
                raw += _body_bytes(src)
    return {"raw_bytes": raw, "distilled_bytes": distilled,
            "ratio": round(raw / distilled, 4) if distilled else 0.0,
            "links": links, "sized": sized}


def resolution_fidelity(node, distillation_id: str) -> float:
    """The fraction of a distillation's sources that still walk to live bytes.
    (The contract-scored fidelity — distilled content judged against the sealed
    QA sample under the class's d(·,·) — arrives with 0033 spoonful 2.)"""
    rec, state = resolve(node, distillation_id)
    if state != "live" or rec.get("kind") != "distillation":
        return 0.0
    refs = rec.get("derived_from", [])
    if not refs:
        return 1.0
    alive = sum(1 for r in refs if resolve(node, r)[1] == "live")
    return round(alive / len(refs), 4)


def contract_fidelity(node, distillation_id: str) -> dict | None:
    """0033 sp2's yardstick: did the intolerables survive the climb? For a
    distillation carrying a distortion contract, the fraction of contract-named
    keys whose values were carried — each citing a source that still resolves
    (a stub resolves: the VALUE survived even where the bytes left; that is the
    contract doing its job). None when no contract applies."""
    rec, state = resolve(node, distillation_id)
    if state != "live" or rec.get("kind") != "distillation":
        return None
    body = _body(rec)
    # method-first (the Phase D gate promoted the contract, 0033 §5); records
    # written before the gate still carry it in the body — both stay readable
    contract = (rec.get("method") or {}).get("contract") or body.get("contract")
    preserved = body.get("preserved") or {}
    if not contract:
        return None
    keys = sorted(set(contract.get("must_preserve") or [])
                  | set(contract.get("prohibited_loss") or []))
    if not keys:
        return {"fidelity": 1.0, "keys": {}}
    live_sources = [s for s in (resolve(node, r)[0]
                                for r in rec.get("derived_from", []))
                    if s is not None and "body" in s]
    detail = {}
    for key in keys:
        entries = preserved.get(key) or []
        cited = sum(1 for e in entries if resolve(node, e.get("ref", ""))[1] != "missing")
        in_sources = any(key in _body(s) for s in live_sources)
        # carried-and-cited holds; never-present holds vacuously; present-but-dropped fails
        held = (len(entries) > 0 and cited == len(entries)) or \
               (len(entries) == 0 and not in_sources)
        detail[key] = {"carried": len(entries), "cited": cited, "held": held}
    held_n = sum(1 for k in keys if detail[k]["held"])
    return {"fidelity": round(held_n / len(keys), 4), "keys": detail}


def context_efficiency(node, *, goal_hash: str | None = None) -> dict:
    """Decision value per token transmitted (0027's restraint, as a number):
    outcome scores over aperture cost, from RunRecords that already exist.
    Deterministic thought is priceless, not infinitely efficient — zero-token
    runs are counted apart rather than dividing by zero."""
    metered_value, metered_tokens, free = 0.0, 0, 0
    n = 0
    for run in node.runs.values():
        if goal_hash is not None and run.get("goal_hash") != goal_hash:
            continue
        n += 1
        scores = run.get("scores") or []
        value = sum(s.get("score", 0.0) for s in scores) / max(len(scores), 1)
        tokens = int((run.get("cost") or {}).get("tokens", 0))
        if tokens > 0:
            metered_value += value
            metered_tokens += tokens
        else:
            free += 1
    return {"runs": n, "deterministic_runs": free,
            "value_per_kilotoken": round(1000.0 * metered_value / metered_tokens, 4)
            if metered_tokens else None,
            "metered_tokens": metered_tokens}


def provenance_completeness(node) -> dict:
    """Of every derived_from reference on this node, the fraction that resolves —
    to a live record or an honest stub. A stub IS a complete answer (0026: THAT
    it existed stays on the record); only silence counts against the universe."""
    total, resolved, missing_refs = 0, 0, []
    for rec in node.records.values():
        for ref in rec.get("derived_from", []):
            total += 1
            if resolve(node, ref)[1] == "missing":
                missing_refs.append(ref)
            else:
                resolved += 1
    return {"refs": total, "resolved": resolved,
            "completeness": round(resolved / total, 4) if total else 1.0,
            "missing": missing_refs}


def corroboration_independence(node, slug: str) -> dict:
    """Voices vs echoes for a knowledge category (0014 · 0033 §1): a receipt only
    counts as an independent voice if it came from a DIFFERENT source identity —
    one claim mirrored across ten sites is still one voice."""
    claims = []
    for rec in node.records.values():
        tags = rec.get("tags", [])
        if "knowledge" not in tags or slug not in tags:
            continue
        body = _body(rec)
        receipts = body.get("corroborated_by") or []
        if not receipts:
            continue
        own = (body.get("source") or {}).get("did", "")
        voices: set[str] = set()
        for ref in receipts:
            r, state = resolve(node, ref)
            if state == "live":
                did = (_body(r).get("source") or {}).get("did", "")
                if did and did != own:
                    voices.add(did)
        claims.append({"claim": str(body.get("claim", ""))[:60],
                       "receipts": len(receipts), "independent_voices": len(voices),
                       "echo": len(receipts) > len(voices)})
    return {"claims": claims,
            "echoes_detected": sum(1 for c in claims if c["echo"])}
