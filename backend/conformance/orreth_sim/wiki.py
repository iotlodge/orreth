# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp4, the wiki · 2026-09-10
"""The wiki (0069 §3.4) — OpenKB's skeleton, openwiki's conscience, under
Orreth law.

In plain words: the machine keeps a small encyclopedia of what its imported
documents SAY — a page per origin, a page per concept that recurs across
origins, and a catalog — where every material statement is a GROUNDED CLAIM
tied to the signed evidence record it came from. Nothing on a page is ever
just prose: click a claim, and the evidence opens.

The three adopted disciplines, made mechanical:
  · from OpenKB — the taxonomy (origin · concept · catalog pages), the
    LINK WHITELIST (a page may reference only subjects that exist — a
    hallucinated cross-reference is refused at validation), the removal
    cascade;
  · from openwiki — GROUNDED CLAIMS (evidence is a content-addressed
    record id, so evidence VERSION is the id itself; a page refuses to
    call itself current while a retracted claim lacks an explicit,
    recorded decision);
  · under Orreth law — pages are DERIVED, REBUILDABLE records of the
    signed log (a rebuild is a sibling with lineage, never an edit), and
    THE PURGE CASCADE RUNS THROUGH CLAIMS: an origin's death retracts
    every claim its evidence carried, flags every page wearing one, and
    the rebuild that follows NAMES the retraction — stronger than either
    source project holds it.

The pages here are deterministic compositions of claims (the honest v1);
a voiced summary is a governed thought some later hand may add on top —
never a replacement for the claim chain beneath it.
"""
from __future__ import annotations

import json as _json
import re

from . import crypto
from .identity import NOW
from .node import make_memory

SCHEMA_NAME = "wiki-schema"
SCHEMA_GENESIS = {
    "version": 1,
    "kinds": ["origin", "concept", "catalog"],
    "claims_per_document": 6,
    "claim_min_chars": 30,
    "concept_min_origins": 2,
}


def _body(rec: dict) -> dict:
    return _json.loads(crypto._b64d(rec["body"]).decode())


# ---- grounded claims ------------------------------------------------------------------

def claim_texts(text: str, schema: dict | None = None) -> list[str]:
    """The material statements of one document's knowledge — sentence-split,
    short noise dropped, capped by the schema. Deterministic: the same text
    always yields the same claims."""
    s = schema or SCHEMA_GENESIS
    parts = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    out = []
    for p in parts:
        p = p.strip()
        if len(p) >= int(s.get("claim_min_chars", 30)):
            out.append(p[:300])
        if len(out) >= int(s.get("claims_per_document", 6)):
            break
    return out


def mint_claims(node, author: dict, kp, knowledge_ref: str,
                schema: dict | None = None) -> list[str]:
    """One knowledge record's grounded claims, signed: each cites its
    EVIDENCE (the knowledge record — content-addressed, so the id IS the
    version) and its ORIGIN (the artifact the knowledge derived from).
    Idempotent by the caller's sweep (a knowledge with standing claims is
    not re-claimed)."""
    rec = node.records.get(knowledge_ref)
    if rec is None:
        return []
    b = _body(rec)
    text = str(b.get("knowledge") or b.get("claim") or "")
    origin = (rec.get("derived_from") or [""])[0]
    out = []
    for t in claim_texts(text, schema):
        c = make_memory(author, kp, node.scope,
                        {"claim": {"text": t, "evidence": knowledge_ref,
                                   "origin": origin,
                                   "grounded": True, "at": NOW()}},
                        kind="semantic", tags=["wiki-claim"])
        c["derived_from"] = [knowledge_ref]
        out.append(node.write(c))
    return out


def claimed_evidence(node) -> set[str]:
    """Which knowledge the wiki has already claimed — the sweep's memory."""
    out = set()
    for rec in node.records.values():
        if "wiki-claim" in (rec.get("tags") or []):
            out.update(rec.get("derived_from") or [])
    return out


def live_claims(node) -> dict[str, dict]:
    """Every standing claim (retractions applied): ref -> claim body."""
    retracted = set()
    for rec in node.records.values():
        if "claim-retracted" in (rec.get("tags") or []):
            retracted.update(rec.get("derived_from") or [])
    out = {}
    for rid, rec in node.records.items():
        if "wiki-claim" in (rec.get("tags") or []) and rid not in retracted:
            out[rid] = _body(rec).get("claim") or {}
    return out


# ---- pages ----------------------------------------------------------------------------

def page_heads(node) -> dict[tuple, tuple[str, dict]]:
    """The latest page per (kind, subject) — oldest-first rows, last wins
    (the shelf idiom everywhere else)."""
    heads: dict[tuple, tuple[str, dict]] = {}
    for rid, rec in node.records.items():
        if "wiki-page" not in (rec.get("tags") or []):
            continue
        p = _body(rec).get("wiki_page") or {}
        heads[(p.get("kind"), p.get("subject"))] = (rid, p)
    return heads


def validate_links(links: list[str], subjects: set[str]) -> list[str]:
    """THE LINK WHITELIST: a page may reference only subjects that exist.
    A hallucinated cross-reference simply does not survive validation."""
    return [l for l in links or [] if l in subjects]


def build_origin_page(node, author: dict, kp, pointer_ref: str,
                      claim_refs: list[str], *, title: str,
                      links: list[str] | None = None,
                      subjects: set[str] | None = None,
                      prior: str | None = None, note: str = "") -> str:
    body = {"wiki_page": {
        "kind": "origin", "subject": pointer_ref, "title": title,
        "claims": list(claim_refs),
        "links": validate_links(links or [], subjects or set()),
        "status": "current", "built_at": NOW(),
        **({"note": note} if note else {})}}
    rec = make_memory(author, kp, node.scope, body, kind="semantic",
                      tags=["wiki-page", "wiki-origin"])
    rec["derived_from"] = [pointer_ref] + list(claim_refs) \
        + ([prior] if prior else [])
    return node.write(rec)


def concept_map(node, schema: dict | None = None) -> dict[str, dict]:
    """Concepts = terms recurring across DISTINCT origins (the one term law:
    graphlaw's extractor is the only tokenizer). term -> {origins, claims,
    recurrence}."""
    from . import graphlaw
    s = schema or SCHEMA_GENESIS
    seen: dict[str, dict] = {}
    for ref, c in live_claims(node).items():
        for t in set(graphlaw.terms(str(c.get("text") or ""))):
            row = seen.setdefault(t, {"origins": set(), "claims": []})
            row["origins"].add(str(c.get("origin") or ""))
            row["claims"].append(ref)
    return {t: {"origins": sorted(r["origins"]), "claims": r["claims"],
                "recurrence": len(r["origins"])}
            for t, r in seen.items()
            if len(r["origins"]) >= int(s.get("concept_min_origins", 2))}


def build_concept_page(node, author: dict, kp, term: str, row: dict,
                       prior: str | None = None) -> str:
    body = {"wiki_page": {
        "kind": "concept", "subject": term, "title": term,
        "claims": row["claims"], "links": row["origins"],
        "recurrence": row["recurrence"],
        "status": "current", "built_at": NOW()}}
    rec = make_memory(author, kp, node.scope, body, kind="semantic",
                      tags=["wiki-page", "wiki-concept"])
    rec["derived_from"] = row["claims"][:16] + ([prior] if prior else [])
    return node.write(rec)


def build_catalog(node, author: dict, kp, prior: str | None = None) -> str:
    heads = page_heads(node)
    rows = [{"kind": k, "subject": s, "page": rid,
             "title": p.get("title"), "status": p.get("status")}
            for (k, s), (rid, p) in sorted(heads.items(),
                                           key=lambda x: str(x[0]))
            if k in ("origin", "concept")]
    body = {"wiki_page": {"kind": "catalog", "subject": "catalog",
                          "title": "the catalog", "entries": rows,
                          "status": "current", "built_at": NOW()}}
    rec = make_memory(author, kp, node.scope, body, kind="semantic",
                      tags=["wiki-page", "wiki-catalog"])
    if prior:
        rec["derived_from"] = [prior]
    return node.write(rec)


# ---- the cascade (an origin's death runs THROUGH claims) ------------------------------

def sealed_refs(node) -> set[str]:
    """The signed death notices: every ref a standing seal darkens (0026 §3
    — the read paths exclude what it names). The cascade READS THE LAW
    rather than probing a door's side effect: a sealed origin's claims
    retract the moment the seal is visible, and a dark wire can never be
    mistaken for a death (the 0042 blindness law, structural here)."""
    out = set()
    for rec in node.records.values():
        if "seal" in (rec.get("tags") or []) and "purge" in (rec.get("tags") or []):
            out.update((_body(rec).get("seal") or {}).get("refs") or [])
    return out


def cascade(node, author: dict, kp, dead_ref: str) -> dict:
    """THE PURGE CASCADE: every claim whose evidence or origin was dead_ref
    RETRACTS (a signed retraction on the claim's own worldline), and every
    current page wearing one of those claims is FLAGGED — it may not call
    itself current again until an explicit, recorded rebuild. Nothing is
    deleted; the whole story stays readable."""
    retracted = []
    for ref, c in live_claims(node).items():
        if dead_ref in (c.get("evidence"), c.get("origin")):
            r = make_memory(author, kp, node.scope,
                            {"claim_retraction": {
                                "claim": ref, "because": dead_ref,
                                "why": "the origin died — its evidence can "
                                       "no longer ground this claim",
                                "at": NOW()}},
                            kind="episodic", tags=["claim-retracted"])
            r["derived_from"] = [ref]
            node.write(r)
            retracted.append(ref)
    flagged = []
    if retracted:
        dead = set(retracted)
        for (kind, subject), (rid, p) in page_heads(node).items():
            if p.get("status") != "current" or kind == "catalog":
                continue
            worn = [c for c in p.get("claims") or [] if c in dead]
            if not worn:
                continue
            f = make_memory(author, kp, node.scope,
                            {"wiki_page_flag": {
                                "page": rid, "kind": kind, "subject": subject,
                                "retracted": worn,
                                "why": "a claim this page wears was "
                                       "retracted — the page may not call "
                                       "itself current until rebuilt",
                                "at": NOW()}},
                            kind="episodic", tags=["wiki-page-flag"])
            f["derived_from"] = [rid]
            node.write(f)
            flagged.append(rid)
    return {"retracted": retracted, "flagged": flagged}


def flagged_pages(node) -> dict[str, str]:
    """page ref -> flag ref, for flags no rebuild has answered."""
    answered = set()
    for rec in node.records.values():
        if "wiki-page" in (rec.get("tags") or []):
            answered.update(rec.get("derived_from") or [])
    out = {}
    for rid, rec in node.records.items():
        if "wiki-page-flag" in (rec.get("tags") or []) and rid not in answered:
            out[(_body(rec).get("wiki_page_flag") or {}).get("page", "")] = rid
    return out


def page_status(node, page_ref: str) -> str:
    """A page's honest standing: flagged outranks its own written status —
    openwiki's refusal, mechanical."""
    for rec in node.records.values():
        if "wiki-page-flag" in (rec.get("tags") or []) \
                and page_ref in (rec.get("derived_from") or []):
            answered = any(page_ref in (r2.get("derived_from") or [])
                           and "wiki-page" in (r2.get("tags") or [])
                           for r2 in node.records.values())
            if not answered:
                return "flagged"
    p = _body(node.records[page_ref]).get("wiki_page") or {}
    return str(p.get("status") or "current")


def rebuild_after_flag(node, author: dict, kp, page_ref: str,
                       flag_ref: str) -> str:
    """The explicit, recorded decision the flag demands: a SIBLING page
    without the retracted claims, deriving from the old page AND the flag —
    the retraction named in its own note, never smoothed over."""
    old = _body(node.records[page_ref]).get("wiki_page") or {}
    dead = set((_body(node.records[flag_ref])
                .get("wiki_page_flag") or {}).get("retracted") or [])
    kept = [c for c in old.get("claims") or [] if c not in dead]
    body = {"wiki_page": {
        **old, "claims": kept, "status": "current", "built_at": NOW(),
        "note": f"rebuilt after the retraction of {len(dead)} claim(s) — "
                f"the flag at {flag_ref[:18]}… is answered, the story whole"}}
    rec = make_memory(author, kp, node.scope, body, kind="semantic",
                      tags=["wiki-page", f"wiki-{old.get('kind', 'origin')}"])
    rec["derived_from"] = [page_ref, flag_ref] + kept[:12]
    return node.write(rec)
