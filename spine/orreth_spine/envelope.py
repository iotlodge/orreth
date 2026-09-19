# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P0 sp1, the rig breathes · 2026-09-16
"""The shared transport envelope (orreth.transport/1), v0.

One broker-neutral metadata contract for every rail (canon 0002). An
envelope is encoded as canonical bytes — sorted keys, compact separators,
ASCII — so the same message is the same bytes on every rail and in every
language. Payloads are pointer-shaped by default: a ref and a hash, never
bodies or prompts. The authority chain says who created and who requested
(canon 0004: attribution is the point) — the origin human first, then
each delegating identity in order.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone


def scope() -> str:
    """The world this process belongs to (SPINE_SCOPE, default u:dev).
    Facts wear it, and a dispatcher only dispatches its OWN world's
    facts — two rigs on one broker stay two worlds (found live: the
    running Bridge's dispatcher bridged a test's facts onto its own
    benches and its librarian answered them)."""
    return os.environ.get("SPINE_SCOPE", "u:dev")

SPECVERSION = "orreth.transport/1"
KINDS = ("command", "event")
REQUIRED = ("specversion", "message_id", "message_kind", "type",
            "universe_id", "scope_path", "occurred_at", "payload")


def canonical(obj) -> bytes:
    """The one true byte form: sorted keys, compact, ASCII."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def content_hash(obj) -> str:
    """sha256 over the canonical bytes, prefixed so the algorithm is named."""
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def now_iso() -> str:
    """UTC, millisecond precision, Z-suffixed — one clock spelling everywhere."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def make_envelope(*, kind: str, type: str, universe_id: str, scope_path: str,
                  payload: dict, correlation_id: str | None = None,
                  authority_chain: list[str] | None = None,
                  aggregate: dict | None = None,
                  marker: dict | None = None) -> dict:
    """Mint one envelope. The message id is globally unique and immutable
    (commands wear cmd_, events wear msg_); everything else is plain data.
    `aggregate` ({type, id, sequence}) names the one thing whose order
    matters — sequences are monotonic PER AGGREGATE, never globally
    (canon 0002: there is no useful global order)."""
    if kind not in KINDS:
        raise ValueError(f"message_kind must be one of {KINDS}, not {kind!r}")
    env = {
        "specversion": SPECVERSION,
        "message_id": ("cmd_" if kind == "command" else "msg_")
                      + secrets.token_hex(12),
        "message_kind": kind,
        "type": type,
        "universe_id": universe_id,
        "scope_path": scope_path,
        "occurred_at": now_iso(),
        "payload": payload,
    }
    if correlation_id:
        env["correlation_id"] = correlation_id
    if authority_chain:
        env["authority_chain"] = list(authority_chain)
    if aggregate:
        env["aggregate"] = dict(aggregate)
    if marker:                      # the typed origin this fact serves (0006):
        env["marker"] = dict(marker)   # {kind, id, parent, by} — WHY, never who
    return env


def encode(env: dict) -> bytes:
    """Canonical bytes of a complete envelope; an incomplete one is refused
    with its missing fields named — never guessed at."""
    missing = [k for k in REQUIRED if k not in env]
    if missing:
        raise ValueError("envelope missing required fields: " + ", ".join(missing))
    if env["specversion"] != SPECVERSION:
        raise ValueError(f"unknown specversion {env['specversion']!r}")
    return canonical(env)


def decode(raw: bytes) -> dict:
    """Read an envelope back. Unknown additive fields are preserved (a newer
    publisher never breaks an older reader); missing required ones refuse."""
    env = json.loads(raw.decode("ascii"))
    missing = [k for k in REQUIRED if k not in env]
    if missing:
        raise ValueError("envelope missing required fields: " + ", ".join(missing))
    return env
