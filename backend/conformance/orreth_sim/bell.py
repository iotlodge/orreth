# PROVENANCE: Fable 5 (claude-fable-5) — 0044 sp2, the bell service · 2026-08-02
"""The bell (0044 §2, laws 2–6): the one organ allowed to reach a human who
is NOT at the glass — under consent, on the record, content-minimal.

Its laws, executable:

 2. **A resident, not a side door.** The bell has its own DID and a pinned
    manifest naming its transport — a signed record whose content-hash IS
    the pin. Its sends are metered under its DID (0019).
 3. **No send without standing consent.** A consent record (0034's grammar
    wearing the bell's purpose) names the endpoint and the ring kinds
    permitted. No consent, wrong kind, lapsed window, revoked posture —
    all refuse with the ONE face (0002 §4): a prober at the bell's door
    learns nothing, not even which law it tripped.
 4. **Content-minimal, pointers never payloads.** A ring carries kind,
    scope, subject, age, and a pointer to the Console — and NOTHING the
    requester tried to smuggle alongside. The requester's words never pass
    through verbatim.
 5. **The record precedes the wire.** The ring record lands BEFORE
    transport is attempted; the transport's outcome (sent · failed) lands
    as a second record derived from the first. A bell that rang off the
    record never rang.
 6. **The bell must not become noise.** One ring per (kind · subject) per
    cooldown window; a repeat inside the window ages into the standing
    ring and never touches the wire. Alarm fatigue is the monitoring
    organ's own failure mode.

Law 7 (a ring never moves a clock) is structural: the bell holds no lever
to any gate — there is nothing here that COULD extend, approve, or
escalate. The transport is injected; the sim never touches a real wire.
"""
from datetime import datetime, timedelta, timezone

from .node import make_memory

RING_KINDS = ("witness", "gate-age", "tamper")

# the one face (0002 §4) — every refusal at this door, identical
REFUSAL = "request cannot be served under this capability"

_MINIMAL = ("kind", "scope", "subject", "age", "pointer")


def make_manifest(agent: dict, kp, scope: str, *, transport: str,
                  sender: str) -> dict:
    """The pinned manifest: WHAT the bell is and HOW it speaks — a signed
    record; its content-hash id is the pin (the 0018 worldline idiom)."""
    body = {"bell_manifest": {"transport": transport, "sender": sender,
                              "kinds": list(RING_KINDS)}}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["bell", "bell-manifest"])


def make_ring_consent(agent: dict, kp, scope: str, *, endpoint: str,
                      kinds: list, window_days: int = 90,
                      approved_ref: str = "", posture: str = "granted") -> dict:
    """0034's consent grammar wearing the bell's purpose: the human's word
    that the bell may reach THIS endpoint for THESE kinds, time-bound and
    revocable — minted only from the human's word (0012). Revocation is the
    same record with posture "revoked" on the same worldline: withdrawn is
    a state, never an absence (the 0032 idiom)."""
    for k in kinds:
        if k not in RING_KINDS:
            raise ValueError(f"unknown ring kind: {k!r} — the bell knows: "
                             + ", ".join(RING_KINDS))
    frm = datetime.now(timezone.utc)
    body = {"consent": {
        "purpose": "the bell may reach you beyond the glass (0044)",
        "endpoint": endpoint, "kinds": list(kinds),
        "window": {"from": frm.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "until": (frm + timedelta(days=int(window_days)))
                   .strftime("%Y-%m-%dT%H:%M:%SZ")},
        "posture": posture, "approved": approved_ref,
    }}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["consent", "consent-bell"])


def consent_head(rows: list[dict]) -> dict | None:
    """Latest posture on the bell's consent worldline wins, oldest-first
    rows of {consent, at} — revoked is returned WITH its posture (a state,
    never an absence); the bell's own check then refuses it one-faced."""
    head = None
    for r in sorted(rows, key=lambda x: x.get("at", "")):
        if isinstance(r.get("consent"), dict):
            head = r["consent"]
    return head


class Bell:
    """The bell service. Transport and clock are injected — the sim proves
    the LAWS; the wire supplies SES and the world supplies the hour."""

    def __init__(self, agent: dict, kp, scope: str, manifest: dict, *,
                 transport, cooldown_s: int = 3600):
        self.agent, self.kp, self.scope = agent, kp, scope
        self.manifest = manifest
        self.transport = transport            # fn(payload: dict) -> None; raises on failure
        self.cooldown_s = cooldown_s
        self.rung: dict[tuple, dict] = {}     # (kind, subject) -> {at, ring, repeats}

    def ring(self, request: dict, consent: dict | None, *, at: str) -> dict:
        """One ring, all laws enforced. Returns {"refused"} · {"aged_into"}
        · {"ring", "delivery"} — the records minted, in landing order."""
        kind = request.get("kind")
        # law 3 — one face for EVERY miss: absence, revocation, lapse, kind
        if (not consent
                or consent.get("posture") != "granted"
                or kind not in (consent.get("kinds") or [])
                or not (consent.get("window", {}).get("until", "") >= at)):
            return {"refused": REFUSAL}
        # law 6 — the standing ring absorbs the repeat; the wire stays quiet
        key = (kind, str(request.get("subject", "")))
        prior = self.rung.get(key)
        if prior is not None and _seconds_between(prior["at"], at) < self.cooldown_s:
            prior["repeats"] += 1
            return {"aged_into": prior["ring"]["id"], "repeats": prior["repeats"]}
        # law 4 — the minimal shape, and nothing else survives the door
        payload = {k: request[k] for k in _MINIMAL if k in request}
        payload["endpoint"] = consent["endpoint"]
        # law 5 — the record first; the wire second; the outcome always
        ring_rec = make_memory(self.agent, self.kp, self.scope,
                               {"ring": {**{k: payload.get(k) for k in _MINIMAL},
                                         "manifest": self.manifest["id"],
                                         "consent_endpoint": consent["endpoint"]}},
                               kind="episodic", tags=["bell", "ring", str(kind)])
        try:
            self.transport(payload)
            outcome = "sent"
        except Exception:
            outcome = "failed"                # named, never silent — but no detail
        delivery = make_memory(self.agent, self.kp, self.scope,
                               {"delivery": {"ring": ring_rec["id"],
                                             "outcome": outcome}},
                               kind="episodic", tags=["bell", "delivery"])
        delivery["derived_from"] = [ring_rec["id"]]
        self.rung[key] = {"at": at, "ring": ring_rec, "repeats": 0}
        return {"ring": ring_rec, "delivery": delivery, "outcome": outcome}


def _seconds_between(a: str, b: str) -> float:
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return abs((datetime.strptime(b, fmt) - datetime.strptime(a, fmt))
               .total_seconds())
