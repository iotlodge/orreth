# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-11 — 0029, Multimodal Capability
"""Multimodal admission (0029): upload is an ask — no side door for files.

The Librarian admits what the human hands her: the ARTIFACT lands content-addressed
and signed (`ingested-archive` — the store is modality-blind, 0022), and what the
modality yields as text becomes an EXTRACTION — knowledge derived from the artifact,
untrusted, quarantined at 0.0000 like everything from outside (0014). A format that
needs an eye is admitted honestly DARK and its extraction intent PARKS (JB lock
2026-07-11): failure is fuel, and the parked list is the retry list the day a
vision mind saddles on the Stable (0019). Bars are policy; past them, the uniform
refusal.
"""
from __future__ import annotations

import base64

from . import crypto
from .node import Refusal, make_memory

MAX_BYTES = 256 * 1024                      # JB lock 2026-07-11 — v0 bar
TYPES = {"txt", "md", "json", "csv", "pdf", "png", "jpg", "jpeg"}
_TEXTUAL = {"txt", "md", "json", "csv"}


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def check_policy(filename: str, data: bytes) -> None:
    """The bars (JB lock): size and type. Past them, one face — a prober learns
    nothing about which bar it hit."""
    if len(data) > MAX_BYTES or _ext(filename) not in TYPES:
        raise Refusal("upload outside the floor's bars")


def extract_text(filename: str, data: bytes) -> str | None:
    """The keyless floor: text-bearing formats yield deterministically — instant,
    free. Formats needing an eye return None; pretending to read is drift."""
    if _ext(filename) in _TEXTUAL:
        return data.decode("utf-8", errors="replace")
    return None


def admit_upload(node, agent: dict, kp, filename: str, mime: str,
                 data: bytes) -> dict:
    """The whole admission, on the record: artifact always; extraction when the
    floor can read it; a parked eye when it cannot. Returns the receipt."""
    check_policy(filename, data)
    artifact = make_memory(agent, kp, node.scope,
                           {"artifact": {"filename": filename, "mime": mime,
                                         "bytes_b64": base64.b64encode(data).decode(),
                                         "size": len(data)}},
                           kind="semantic", tags=["artifact"],
                           provenance_class="ingested-archive")
    aid = node.write(artifact)
    text = extract_text(filename, data)
    if text is not None:
        extraction = make_memory(agent, kp, node.scope,
                                 {"knowledge": text[:2000],
                                  "source": {"did": agent["did"], "ref": filename},
                                  "state": "untrusted", "intent": f"upload: {filename}"},
                                 kind="semantic", tags=["knowledge", "document"],
                                 provenance_class="ingested-archive")
        extraction["derived_from"] = [aid]
        return {"artifact": aid, "extraction": node.write(extraction),
                "status": "extracted"}
    parked = make_memory(agent, kp, node.scope,
                         {"parked_intent": f"extract the artifact {filename}",
                          "missing": "a vision mind on the Stable (0019)",
                          "handoff": "knowledge-acquisition", "artifact": aid},
                         kind="semantic", tags=["parked", "knowledge-intent"])
    parked["derived_from"] = [aid]
    return {"artifact": aid, "parked": node.write(parked), "status": "dark"}


def document_skill(node):
    """The agents' reach (0029 §1): extracted documents as a deterministic skill —
    the chassis binds it like any other; least-privilege attention holds."""
    import json as _json

    def read_document(question: str) -> str:
        words = {w for w in question.lower().split() if len(w) > 2}
        hits = []
        for rec in node.records.values():
            if "document" not in rec.get("tags", []) or "body" not in rec:
                continue
            body = _json.loads(crypto._b64d(rec["body"]).decode())
            text = str(body.get("knowledge", ""))
            if not words or any(w in text.lower() for w in words):
                hits.append(f"{(body.get('source') or {}).get('ref', '?')}: "
                            f"{text[:160]} ({body.get('state', '?')})")
        return " | ".join(hits[:4]) or "no readable documents held"
    return read_document
