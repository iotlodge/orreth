# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp6, the standing doors · 2026-08-07
"""The standing doors (0047 sp6, JB's vectors 2026-08-07): the two SENDERS
that speak through the one governed wire — no new transport, only new voices.

**The Schedule — the machine's standing duty.** An Objective ASSIGNED to a
Resident/machine: the charter is approved ONCE at the human's gate, then the
MACHINE owns the cadence — each instance a normal governed objective under
the machine's own name, inside the charter's declared budget, until the
declared instance ceiling rests the charter at the gate for renewal. Never a
human re-asking on a timer.

**The Trigger — the reflex arc.** An event fires a REFLEX whose response is
one of exactly three shapes: an OBSERVATION (a finding lands on the record),
an ESCALATION (a card stages, the bell rings — detection wears no levers),
or an ACTION (a governed act within standing authority; consequence still
gates because acts ARE requests). An objective is one possible response,
never the definition.

Both are CRAFT: declared artifacts, human-approved at the gate, readable and
revocable like every driving word. A2A needs no door here — the queue is the
wire, and these are two more citizens speaking through it.
"""
from __future__ import annotations

RESPONSES = ("observe", "escalate", "act")


def charter_due(charter: dict, now_s: float) -> bool:
    """The cadence law: due when active, never-yet-fired or past its
    every_s, and still under its declared instance ceiling. A charter at
    its ceiling is NOT due — it rests honestly (the renewal is the gate's)."""
    if not charter.get("active"):
        return False
    if int(charter.get("fired", 0)) >= int(charter.get("max_instances", 100)):
        return False
    last = charter.get("last_fired_s")
    return last is None or (now_s - float(last)) >= float(charter["every_s"])


def charter_resting(charter: dict) -> bool:
    """At the declared ceiling: the charter rests and says so — instances
    stop, the renewal waits at the gate, nothing silently continues."""
    return (bool(charter.get("active"))
            and int(charter.get("fired", 0)) >= int(charter.get("max_instances", 100)))


def reflex_matches(reflex: dict, record: dict) -> bool:
    """The v1 condition vocabulary: record-tagged — a record wearing the
    declared tag (on the declared scope, when one is declared). Unknown
    condition kinds match NOTHING: a reflex the law cannot read never fires."""
    when = reflex.get("when") or {}
    if when.get("kind") != "record-tagged":
        return False
    if when.get("tag") not in (record.get("tags") or []):
        return False
    scope = when.get("scope")
    return scope is None or record.get("scope") == scope


def reflex_response(reflex: dict, ref: str) -> dict:
    """The reflex's answer, typed: exactly one of the three shapes, refused
    loudly otherwise — a reflex with an unreadable response is a defect at
    DECLARATION time, never a surprise at firing time."""
    then = reflex.get("then") or {}
    shape = then.get("shape")
    if shape not in RESPONSES:
        raise ValueError(f"a reflex answers with observe, escalate, or act — "
                         f"never \"{shape}\"")
    out = {"shape": shape, "reflex": reflex.get("id", ""), "of": ref}
    if shape == "act":
        act = then.get("request") or {}
        if not isinstance(act, dict) or not act.get("kind"):
            raise ValueError("an act-reflex declares the governed request it "
                             "will post — kind and all; acts ARE requests")
        out["request"] = act
    if shape == "escalate":
        out["text"] = str(then.get("text") or "a watched condition fired")
    if shape == "observe":
        out["note"] = str(then.get("note") or "a watched condition fired")
    return out
