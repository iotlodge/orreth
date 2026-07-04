"""The Knowledge Loop (0014): learning from the world — quarantined, promoted, recallable.

External knowledge enters as ingested-archive, state 'untrusted' (0.0000). Promotion is
earned (corroboration mints a new version with receipts). Discrediting a source recalls
every entry from it AND every version derived from those — annotate-never-rewrite, the
lineage preserved. Sources are identities: the world gets DIDs too.
"""
from __future__ import annotations

from . import crypto
from .identity import NOW
from .node import make_memory

STATES = ("untrusted", "investigating", "corroborated", "trusted", "recalled")


class SourceRegistry:
    """External sources as identities (0014 §2): who the world is, before we listen to it."""

    def __init__(self) -> None:
        self.sources: dict[str, dict] = {}

    def register(self, did: str, *, kind: str, posture: str = "untrusted-by-default") -> None:
        self.sources[did] = {"did": did, "kind": kind, "posture": posture, "status": "active"}

    def discredit(self, did: str, reason: str) -> None:
        self.sources[did] = {**self.sources[did], "status": "discredited", "reason": reason}


class KnowledgeCategory:
    """A versioned-by-universe-time corpus with an intent. Entries are MemoryRecords on the
    node; versions supersede via derived_from; 'as of T' is a spacetime query."""

    def __init__(self, node, intent: str, slug: str):
        self.node, self.intent, self.slug = node, intent, slug

    def _write(self, body: dict, derived_from: list[str] | None = None) -> str:
        rec = make_memory(self.node.steward, self.node.steward_kp, self.node.scope,
                          body, kind="semantic", tags=["knowledge", self.slug],
                          provenance_class="ingested-archive"
                          if body.get("state") == "untrusted" else "lived")
        if derived_from:
            rec["derived_from"] = derived_from
        return self.node.write(rec)

    # ---- admission: quarantined, always (0014 §3) ---------------------------------------
    def admit(self, claim: str, source: dict, *, generation: int = 1) -> str:
        """The world speaks; we file it at 0.0000 and remember who said it."""
        return self._write({
            "category": self.slug, "claim": claim,
            "source": {"did": source["did"], "ref": source.get("ref", "")},
            "state": "untrusted", "confidence": 0.0,
            "generation": generation, "admitted_at": NOW(),
        })

    # ---- promotion: earned, with receipts -------------------------------------------------
    def corroborate(self, entry_id: str, receipt_ids: list[str]) -> str:
        prior = self.node.records[entry_id]
        body = self._body(prior)
        return self._write({**body, "state": "corroborated",
                            "corroborated_by": receipt_ids},
                           derived_from=[entry_id])

    # ---- the recall: by source, through the lineage (0014 §4) ----------------------------
    def recall_source(self, source_did: str, reason: str) -> list[str]:
        """Every entry from the source, and every version derived from those — re-versioned
        to 'recalled'. Nothing rewritten; the poison visibly dead."""
        entries = self.entries()
        tainted = {eid for eid, b in entries.items()
                   if b.get("source", {}).get("did") == source_did}
        grew = True
        while grew:  # walk the derivation lineage forward
            grew = False
            for eid, _ in entries.items():
                rec = self.node.records[eid]
                if eid not in tainted and any(d in tainted
                                              for d in rec.get("derived_from", [])):
                    tainted.add(eid)
                    grew = True
        recalled = []
        for eid in sorted(tainted):
            body = self._body(self.node.records[eid])
            if body.get("state") == "recalled":
                continue
            recalled.append(self._write({**body, "state": "recalled",
                                         "recall_reason": reason},
                                        derived_from=[eid]))
        return recalled

    # ---- reading: current view + as-of-T (versions are time) ------------------------------
    def entries(self) -> dict[str, dict]:
        out = {}
        for rid, rec in self.node.records.items():
            if self.slug in rec.get("tags", []) and "knowledge" in rec.get("tags", []):
                out[rid] = self._body(rec)
        return out

    def current(self) -> list[dict]:
        """Latest version per lineage head: superseded entries drop away."""
        entries = self.entries()
        superseded = set()
        for rid in entries:
            for d in self.node.records[rid].get("derived_from", []):
                superseded.add(d)
        return [{**b, "id": rid} for rid, b in sorted(entries.items())
                if rid not in superseded]

    def _body(self, rec: dict) -> dict:
        import json
        return json.loads(crypto._b64d(rec["body"]).decode()) if "body" in rec else {}
