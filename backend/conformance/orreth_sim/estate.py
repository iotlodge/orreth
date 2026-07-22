# PROVENANCE: Fable 5 (claude-fable-5) — 0037, the Estate · 2026-07-22
"""The Estate (0037): allen, the cloud architect — the first embodied tier.

allen IS a field: the tier's DID is his identity, its staff his control plane,
its incarnations his hands. This module is spoonful 1 — the resident stands:
the TYPED DOOR (the 0030 ladder enforced at his gateway) and the acceptance
gate (locked 2026-07-22: the estate adopts before it creates).

The door's law: humans alone originate Objectives; an agent speaks Intentions
or Observations, and every one carries lineage to a human Objective — or it is
refused, LOUDLY. This is a protocol refusal, deliberately not the uniform
authz shape (0002 §4 protects retrieval from probes; the door here TEACHES the
ladder to whoever knocks). Nobody builds infrastructure because a machine
wanted it.
"""
from __future__ import annotations

from .identity import NOW
from .node import make_memory

SPEECH = ("objective", "intention", "observation")


class DoorRefusal(Exception):
    """The typed door, refusing loudly — the message names the missing rung."""


class GateStands(Exception):
    """The acceptance gate (0037 §8.7): Create waits for the brownfield walk."""


def receive(node, allen: dict, allen_kp, speech: dict) -> str:
    """One utterance through allen's door. `speech` carries `kind` (a rung of the
    0030 ladder), `speaker` ({did, human}), `text`, and — for agents — `lineage`
    (the record ids walking back to a human Objective). Accepted speech lands as
    a signed memory record tagged with its rung; the ladder is stored so the
    spacetime window can WALK it: why does this bucket exist? is a query."""
    kind = str(speech.get("kind") or "")
    speaker = speech.get("speaker") or {}
    text = str(speech.get("text") or "").strip()
    lineage = [str(x) for x in speech.get("lineage") or []]
    if kind not in SPEECH:
        raise DoorRefusal(f"“{kind or '?'}” is not a rung — the ladder is "
                          "objective · intention · observation (0030)")
    if not text:
        raise DoorRefusal("empty speech — the door opens for words")
    if not speaker.get("human"):
        if kind == "objective":
            raise DoorRefusal("humans alone originate objectives (0030) — an "
                              "agent may speak an intention or an observation, "
                              "never a why")
        if not lineage:
            raise DoorRefusal("no ancestry — every agent ask descends from a "
                              "human objective; name the lineage or the door "
                              "stays shut")
        missing = [r for r in lineage if r not in node.records]
        if missing:
            raise DoorRefusal("lineage names records this floor cannot see — "
                              "an ancestry must be walkable, not merely claimed")
    elif kind != "objective":
        raise DoorRefusal("a human speaks objectives at this door — intentions "
                          "and observations are the agents' rungs; charter "
                          "answers ride the gate's card (0037 §3)")
    body = {"estate_speech": {"kind": kind, "speaker": speaker.get("did", ""),
                              "human": bool(speaker.get("human")), "text": text,
                              **({"lineage": lineage} if lineage else {}),
                              "at": NOW()}}
    # the lineage rides INSIDE the signed body — the ladder is data, walkable by
    # query; no unsigned top-level field to keep honest separately
    rec = make_memory(allen, allen_kp, node.scope, body, kind="episodic",
                      tags=["estate", kind])
    return node.write(rec)


def adopted(node) -> list[dict]:
    """The brownfield walk's receipts: every adoption record on this floor."""
    return [r for r in node.records.values() if "estate-adopted" in (r.get("tags") or [])]


def create_unlocked(node) -> bool:
    """The acceptance gate (locked 2026-07-22): greenfield Create is possible
    only after the read-only adoption walk has landed its receipts."""
    return bool(adopted(node))


def record_adoption(node, allen: dict, allen_kp, stacks: list[str]) -> str:
    """The adoption walk's landing — observed stacks, read-only, attested by
    allen's key. Spoonful 4 drives this against the real estate (OrrethDemoStack,
    the pipeline); the mechanism stands now so the gate is real, not rhetorical."""
    if not stacks:
        raise DoorRefusal("an adoption names what it observed — no stacks, no walk")
    body = {"estate_adoption": {"stacks": sorted(stacks), "posture": "read-only",
                                "at": NOW()}}
    rec = make_memory(allen, allen_kp, node.scope, body, kind="semantic",
                      tags=["estate", "estate-adopted"])
    return node.write(rec)


def stage_create(node, ask: str) -> dict:
    """A greenfield Create, asked. Behind the acceptance gate it refuses with
    the gate's own words; past the gate it stages toward 0012 — the charter
    (spoonful 2) will interrogate before any plan may compile."""
    if not create_unlocked(node):
        raise GateStands("the acceptance gate stands (0037 §8.7): the estate "
                         "adopts before it creates — the brownfield walk has "
                         "not completed")
    return {"staged": True, "ask": (ask or "").strip(),
            "note": "consequence waits at the gate (0012); the charter "
                    "interrogates before the plan compiles (0037 §3)"}
