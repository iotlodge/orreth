# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp2, the ask door · 2026-09-08
"""The ask door's law (0071 §3.1): one request kind — "here is my question, answer it
with your governed retrieval" — worn by agents, the librarian's selector, and the
external API alike.

Three rules, none negotiable:

1. **Signature, never bearer.** An ask files on the PUBLIC queue, so it must carry
   nothing a reader could steal. The asker SIGNS the ask with its own key over a
   declared subset; the door verifies against the DID itself (did:key is
   self-certifying). A lease token never rides a queue row.
2. **The envelope is structured, and refs are WHOLE.** The reply comes back with its
   citations, the variant that served it, the full dispatch-choice record id, and the
   judgeable exchange ref — the kernel's own law (2026-08-23): a shortened id can
   never open any door on any floor.
3. **The selection is never a secret.** Auto or chosen, the variant the retrieval rode
   is a field in the envelope and a fact on the record.
"""
from __future__ import annotations

from . import crypto

# The signed subset — the SDK carries this constant verbatim (the RUN_SIG_KEYS
# convention): did · text · at. Tamper any of the three and the door refuses.
ASK_SIG_KEYS = ("did", "text", "at")

REFUSAL = "request cannot be served under this capability"


def guardrails_version() -> str:
    """The guardrail-set version the ask-cache keys on (0071 sp5). One truth,
    one place: dive 0068's build replaces this body with the real set's
    version (and grows the envelope's guardrails field to match) — and every
    cached answer given under the old law revalidates by construction,
    because the version lives inside the cache key."""
    return "pre-0068"


def make_ask(kp: crypto.KeyPair, did: str, text: str, *,
             at: str, variant: str | None = None,
             attributes: dict | None = None) -> dict:
    """Compose a signed ask body — the reference twin of the SDK's ask()."""
    body = {"kind": "ask", "did": did, "text": text, "at_signed": at}
    if variant:
        body["variant"] = variant
    if attributes:
        body["attributes"] = attributes
    body["sig"] = kp.sign(did, {k: {"did": did, "text": text, "at": at}[k]
                                for k in ASK_SIG_KEYS})
    return body


def verify_ask(req: dict) -> tuple[bool, str]:
    """The door's check: the signature over the declared subset, against the DID's
    own key. Returns (ok, why) — the why is for the record, never for a prober
    (the wire answers with the one face either way)."""
    did = str(req.get("did") or "")
    if not did.startswith("did:key:"):
        return False, "only self-certifying DIDs may sign an ask"
    sig = req.get("sig")
    if not sig:
        return False, "no signature — an ask is signed or it is not an ask"
    subset = {"did": did, "text": str(req.get("text") or ""),
              "at": str(req.get("at_signed") or "")}
    try:
        pub = crypto.public_from_did(did)
        ok = bool(pub) and crypto.verify_sig(
            sig, {k: subset[k] for k in ASK_SIG_KEYS}, pub)
    except Exception:
        return False, "the signature did not verify"
    return (True, "verified") if ok else (False, "the signature did not verify")


def envelope(*, reply: str, by: str, citations: list[dict],
             variant: str, choice_ref: str, exchange: str,
             cost: dict | None = None,
             attributes: dict | None = None,
             honored: list | None = None,
             confession: str | None = None) -> dict:
    """The structured answer, with the refs held whole. `guardrails` speaks
    honestly until 0068's build lands: the field exists, the value confesses."""
    for c in citations:
        ref = str(c.get("ref") or "")
        if ref.endswith("…") or (0 < len(ref) < 24):
            raise ValueError("a citation ref must be whole — a shortened id "
                             "can never open any door on any floor")
    if choice_ref.endswith("…"):
        raise ValueError("the choice ref must be whole")
    env = {"reply": reply, "by": by, "citations": citations,
           "variant": variant, "choice_ref": choice_ref,
           "exchange": exchange,
           "cost": cost or {"tokens": 0},
           "guardrails": {"set_version": None,
                          "note": "guardrail enforcement arrives with dive 0068's build"}}
    if attributes:
        # 0066 sp2 — the first honored attribute: an asker's latency
        # preference gates the router's escalation ("fast" never waits on a
        # thought); everything else stays received-and-confessed until its
        # dive gives it meaning
        env["attributes"] = {"received": attributes,
                             "honored": list(honored or [])}
    if confession:
        env["confession"] = confession
    return env
