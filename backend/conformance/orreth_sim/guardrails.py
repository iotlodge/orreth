# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0068 sp1, the guardrail grammar · 2026-09-09
"""The guardrail grammar (0068 §3.1–§3.2) — KCR-0003's payment begins.

In plain words: a guardrail is a written rule about content — "card numbers
never leave in an answer," "social-security numbers are masked at the door"
— kept as a versioned, human-edited asset, checked by machinery that cannot
be quietly edited. The DETECTORS are firmware (they arrive with sp4, the
warden's split promoted); THE RULES are craft in their own gated drawer,
landing only through the one door with teachings on every sibling.

A rule says three things, and every rule says WHY:
    match  — what content it watches (a category the firmware can detect —
             pii · pci — or a custom pattern list by reference) and which
             DIRECTION (entering · leaving · both);
    action — what happens on a hit, on a ladder of strength:
             annotate < mask < quarantine < refuse;
    reason — the human sentence the audit trail starts from.

TWO LAYERS, ONE LATTICE (§3.2, the tighten-only law): the Universal set
cascades down; a Capability set may ADD rules, WIDEN a rule's direction, or
STRENGTHEN its action — never remove, narrow, or weaken. Mask may become
refuse; refuse may never become mask. The check is real on both sides: at
publication (the gate refuses a loosening edit with a teaching) and at
compose (the merged set is verified monotone).

An EMPTY set is legal but explicit and scary — the charter's own words —
and sp5's stamp law will demand a human's windowed, undoable signature
before an empty or weakened set governs anything. The set's VERSION is the
content hash of the composed rules: the 0071 ask-cache keys on it, so every
guardrail change revalidates every cached answer BY CONSTRUCTION.
"""
from __future__ import annotations

from . import crypto

UNIVERSAL_NAME = "guardrail-universal"

CATEGORIES = ("pii", "pci", "pattern")
DIRECTIONS = ("entering", "leaving", "both")
ACTIONS = ("annotate", "mask", "quarantine", "refuse")   # weakest → strongest

# PII masked, PCI refused — the first rails, mask-by-default where masking
# serves and refusal where the charter's own example (card numbers) demands
GENESIS_UNIVERSAL = {
    "rules": [
        {"match": {"category": "pii", "direction": "leaving"},
         "action": "mask",
         "reason": "personal identifiers (names beside ids, SSNs, emails, "
                   "phone numbers) are masked before any answer leaves — "
                   "people's details are not retrieval output"},
        {"match": {"category": "pci", "direction": "both"},
         "action": "refuse",
         "reason": "payment-card data never rides a prompt or an answer — "
                   "a hit refuses the whole exchange, loudly"},
    ],
}


def _strength(action: str) -> int:
    return ACTIONS.index(action)


def _identity(rule: dict) -> tuple:
    m = rule.get("match") or {}
    return (m.get("category"), m.get("pattern_ref"))


def rule_flaw(rule: dict) -> str | None:
    """One rule's shape law — every field present, every value declared,
    every rule saying why."""
    if not isinstance(rule, dict):
        return "a rule is an object with match · action · reason"
    m = rule.get("match")
    if not isinstance(m, dict):
        return "a rule needs a match — what content it watches"
    if m.get("category") not in CATEGORIES:
        return (f"unknown category «{m.get('category')}» — the firmware "
                f"detects only: {', '.join(CATEGORIES)}")
    if m.get("category") == "pattern" and not m.get("pattern_ref"):
        return ("a pattern rule names its list by reference "
                "(pattern_ref) — the list itself is craft too")
    if m.get("direction") not in DIRECTIONS:
        return (f"direction must be one of {', '.join(DIRECTIONS)} — "
                "which way the content is moving when the rule watches")
    if rule.get("action") not in ACTIONS:
        return (f"unknown action «{rule.get('action')}» — the ladder is "
                f"{' < '.join(ACTIONS)} (weakest to strongest)")
    if not str(rule.get("reason") or "").strip():
        return ("every rule says WHY — the audit trail starts in the "
                "policy, never in the incident")
    return None


def gate_check(asset_name: str, profile) -> tuple[str | None, dict | None]:
    """The craft door's law for guardrail-* assets (the dial gate's family):
    a whole set validates rule by rule; an EMPTY set is legal but lands
    loudly (sp5's stamp law will demand a human's signature before it
    governs). A clean set lands canonical."""
    if not isinstance(profile, dict) or not isinstance(
            profile.get("rules"), list):
        return ("a guardrail set is {\"rules\": [...]} — a written list of "
                "content rules; an empty list is legal, explicit, and "
                "scary by the charter's own words", None)
    clean = []
    for i, r in enumerate(profile["rules"]):
        flaw = rule_flaw(r)
        if flaw:
            return (f"rule {i + 1} refuses — {flaw}", None)
        clean.append({"match": {"category": r["match"]["category"],
                                **({"pattern_ref": r["match"]["pattern_ref"]}
                                   if r["match"].get("pattern_ref") else {}),
                                "direction": r["match"]["direction"]},
                      "action": r["action"],
                      "reason": str(r["reason"]).strip()[:300]})
    return None, {"rules": clean}


def monotone_flaws(universal: dict, capability: dict) -> list[str]:
    """The lattice, checked (§3.2): a capability set may ADD, WIDEN, or
    STRENGTHEN — never remove, narrow, or weaken. Returns every violation
    with its teaching; empty means lawful."""
    flaws = []
    uni = {_identity(r): r for r in (universal or {}).get("rules") or []}
    cap = {_identity(r): r for r in (capability or {}).get("rules") or []}
    for ident, ur in uni.items():
        cr = cap.get(ident)
        if cr is None:
            continue                  # absence never removes — compose keeps it
        if _strength(cr["action"]) < _strength(ur["action"]):
            flaws.append(
                f"the {ident[0]} rule may not weaken: universal says "
                f"«{ur['action']}», this set says «{cr['action']}» — "
                "a child tightens, never loosens (mask may become refuse; "
                "refuse may never become mask)")
        ud, cd = ur["match"]["direction"], cr["match"]["direction"]
        if ud != cd and not (cd == "both"):
            flaws.append(
                f"the {ident[0]} rule may not narrow its direction: "
                f"universal watches «{ud}», this set watches «{cd}» — "
                "widen to «both» or leave it inherited")
    return flaws


def compose(universal: dict, capability: dict | None = None) -> dict:
    """The composed law a floor actually lives under: every universal rule
    always present (absence never removes), the capability's lawful
    strengthenings applied, its additions joined. Deterministic — the
    version below is its content hash."""
    uni = {_identity(r): dict(r) for r in (universal or {}).get("rules") or []}
    for r in (capability or {}).get("rules") or []:
        ident = _identity(r)
        if ident in uni:
            u = uni[ident]
            if _strength(r["action"]) > _strength(u["action"]):
                u["action"] = r["action"]
            if r["match"]["direction"] == "both":
                u["match"] = dict(u["match"], direction="both")
        else:
            uni[ident] = dict(r)
    rules = [uni[k] for k in sorted(uni, key=lambda x: (str(x[0]), str(x[1])))]
    return {"rules": rules}


def set_version(composed: dict) -> str:
    """The version the 0071 ask-cache keys on: the composed rules' content
    hash — a changed guardrail set revalidates every cached answer by
    construction, exactly as the caching charter law demanded."""
    return "gr-" + crypto.content_hash({"rules": composed.get("rules") or []})[7:23]


def teachings(name: str) -> dict:
    """What rides every guardrail sibling — no set is a bare list with
    amnesia."""
    return {
        "what": "a written rule about content — watched by firmware "
                "detectors, acted on before anything leaves or enters",
        "ladder": " < ".join(ACTIONS) + " (a child may climb, never descend)",
        "law": "the Universal set cascades down; a capability may add, "
               "widen, or strengthen — never remove, narrow, or weaken",
        "empty": "an empty set is legal, explicit, and scary — the stamp "
                 "law (0068 sp5) demands a human's windowed, undoable "
                 "signature before it governs",
        "version": "the composed set's content hash — every change "
                   "revalidates every cached answer",
    }
