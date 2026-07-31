# PROVENANCE: Fable 5 (claude-fable-5) — 0043 sp4, the experiment · 2026-07-30
"""The Experiment (0043 §7): A/B where each arm is a MACHINE.

Every other stack tags requests with a config name and hopes somebody wrote
down what the config was. Here the arm IS the fingerprint: the floor's whole
machine (0041) with the variant standing as the asset's head — content-hashed,
signed onto the shelf. No "did we record the config?"; the question cannot
arise.

The laws:

 1. **An arm is a named machine.** `arm_machine` = the floor's fingerprint
    with the variant as the asset head; the arm's name is that content's
    hash. Two arms differ in exactly the asset under test — provably.
 2. **The split waits for a human** (0012). A proposed experiment serves
    NOTHING — the standing Canon serves alone until the word lands. The
    policy is declared (kind · unit · share) and rides the signed
    declaration.
 3. **The split is deterministic.** The unit's hash falls through the
    shares' ladder: same unit, same arm, forever — auditable, replayable,
    no coin anyone has to trust.
 4. **Standings accumulate by the LOG JOIN.** A verdict cites its work;
    the work wears its arm's tag; per-arm quality is a projection over
    records that already exist (rule 7) — never a side-table.
 5. **An experiment never concludes on thin evidence.** min_n verdicts per
    arm, declared up front; a premature conclusion is refused, loudly.
 6. **The conclusion is not a dashboard** (§7, locked). It is a promotion
    card carrying winner, standings, and every evidence ref — staged for
    the gate. Adoption moves on the human's word ONLY: the winner becomes
    the head wearing `adopted_from` + `derived_from` naming the variant
    AND the experiment (the 0038 orphan law); the loser stays on the
    shelf, outranked, history whole.

*A/B testing where each arm is a cryptographically named machine and the
rollout is a signed constitutional act.*
"""
from __future__ import annotations

import hashlib
import json as _json

from . import crypto, epoch, improver
from .identity import NOW
from .node import make_memory

STATES = ("proposed", "running", "concluded", "adopted", "declined")

LEGAL: dict[str, set[str]] = {
    "proposed": {"running", "declined"},     # the human's word · or never opened
    "running": {"concluded", "declined"},    # evidence gathered · or abandoned
    "concluded": {"adopted", "declined"},    # the rollout · or the word is no
    "adopted": set(), "declined": set(),     # terminal — history remains
}


class IllegalMove(Exception):
    pass


class SplitRefused(Exception):
    """A staged experiment serves nothing — the standing Canon serves alone."""


def arm_machine(node, *, asset: str, variant: str, plane_version: str = "sim",
                worldlines: dict | None = None) -> dict:
    """The arm as a MACHINE (law 1): the floor's fingerprint (0041) with the
    variant standing as the asset's head. Content first, then the hash — the
    arm's name can never drift from what the arm is."""
    fp = epoch.machine_fingerprint(node, plane_version=plane_version,
                                   worldlines=worldlines)
    fp["assets"] = dict(fp["assets"], **{asset: variant})
    return {"fingerprint": fp, "machine": crypto.content_hash(fp)}


def assign(policy: dict, unit: str) -> str:
    """The declared split, deterministically (law 3): the unit's hash falls
    through the shares' cumulative ladder. Same unit, same arm, forever."""
    share = policy.get("share") or {}
    if not share:
        raise SplitRefused("a split with no declared shares routes nothing")
    h = int(hashlib.sha256(unit.encode()).hexdigest()[:8], 16) / 0x100000000
    acc = 0.0
    labels = sorted(share)
    for label in labels:
        acc += float(share[label])
        if h < acc:
            return label
    return labels[-1]


def _short(machine: str) -> str:
    return machine.split(":", 1)[-1][:12]


class Experiment:
    """One question, two named machines, a human at both doors."""

    def __init__(self, node, proposer: dict, kp, *, name: str, asset: str,
                 variants: dict[str, str], share: dict[str, float] | None = None,
                 min_n: int = 3):
        if len(variants) < 2:
            raise IllegalMove("an experiment argues between at least two arms")
        for ref in variants.values():
            if ref not in node.records:
                raise IllegalMove("an arm's variant must stand on the shelf — "
                                  "hypotheticals are not machines")
        share = share or {a: 1.0 / len(variants) for a in variants}
        if set(share) != set(variants) or abs(sum(share.values()) - 1.0) > 1e-6:
            raise IllegalMove("the declared shares must name every arm and sum to one")
        self.node, self.proposer, self.kp = node, proposer, kp
        self.name, self.asset = name, asset
        self.share, self.min_n = dict(share), int(min_n)
        self.state = "proposed"
        self.card: dict | None = None
        self.arms: dict[str, dict] = {}
        for label, ref in sorted(variants.items()):
            m = arm_machine(node, asset=asset, variant=ref)
            rec = make_memory(proposer, kp, node.scope,
                              {"experiment_arm": {"experiment": name,
                                                  "arm": label, "asset": asset,
                                                  "variant": ref, **m}},
                              kind="semantic", tags=["experiment-arm", name])
            rec["derived_from"] = [ref]
            self.arms[label] = {"variant": ref, **m, "record": node.write(rec)}
        decl = {"experiment": {
            "name": name, "asset": asset,
            "arms": {a: {"variant": v["variant"], "machine": v["machine"]}
                     for a, v in self.arms.items()},
            "policy": {"kind": "hash-split", "unit": "ask", "share": self.share},
            "min_n": self.min_n, "declared_at": NOW()}}
        rec = make_memory(proposer, kp, node.scope, decl, kind="semantic",
                          tags=["experiment", name])
        rec["derived_from"] = [v["record"] for v in self.arms.values()]
        self.record = node.write(rec)

    # ---- the state machine: every move legal, the human at both doors ------------------
    def _move(self, to: str) -> None:
        if to not in LEGAL[self.state]:
            raise IllegalMove(f"{self.state} → {to} is not a move an experiment knows")
        self.state = to

    def open(self, *, human_word: bool) -> None:
        """Law 2: the split is a consequence — it changes what serves. It
        opens on a human's word only; the declared policy is what was
        approved, never a knob turned after."""
        if not human_word:
            raise IllegalMove("the split waits for its human (0012) — the "
                              "policy is declared AND approved, or nothing runs")
        self._move("running")

    def route(self, unit: str) -> dict:
        """Which machine serves this unit — with the arm's tag for the work
        to wear (law 4's join) and the arm's PROFILE so the caller serves
        under the variant, not around it."""
        if self.state != "running":
            raise SplitRefused("no experiment serves before the human's word — "
                               "the standing Canon serves alone")
        label = assign({"share": self.share}, unit)
        a = self.arms[label]
        return {"arm": label, "variant": a["variant"], "machine": a["machine"],
                "tag": f"arm:{_short(a['machine'])}",
                "profile": improver._profile_of(self.node.records[a["variant"]])}

    # ---- the standings: a projection over the log (law 4) ------------------------------
    def arm_standings(self) -> dict:
        """Verdict → its work → the arm tag the work wears. Per-arm quality
        without a single new store."""
        from . import vera as vera_mod
        by_tag = {f"arm:{_short(a['machine'])}": label
                  for label, a in self.arms.items()}
        out = {label: {"n": 0, "scores": []} for label in self.arms}
        for v in vera_mod.verdicts(self.node):
            vrec = self.node.records.get(v["id"]) or {}
            work = self.node.records.get((vrec.get("derived_from") or [""])[0])
            if not work:
                continue
            for t in work.get("tags") or []:
                if t in by_tag:
                    s = out[by_tag[t]]
                    s["n"] += 1
                    s["scores"].append(float(v["assay"].get("score", 0.0)))
        for s in out.values():
            s["mean"] = round(sum(s["scores"]) / s["n"], 4) if s["n"] else None
            del s["scores"]
        return out

    # ---- the conclusion: a card, never a dashboard (law 6) -----------------------------
    def conclude(self) -> dict:
        """min_n per arm HOLDS (law 5); the card carries winner, standings,
        and every evidence ref. Nothing on the shelf moves."""
        if self.state != "running":
            raise IllegalMove("only a running experiment concludes")
        stand = self.arm_standings()
        thin = sorted(label for label, s in stand.items() if s["n"] < self.min_n)
        if thin:
            raise IllegalMove(
                f"arm(s) {', '.join(thin)} hold fewer than {self.min_n} "
                "verdict(s) — an experiment never concludes on thin evidence")
        winner = max(stand, key=lambda a: stand[a]["mean"])
        self._move("concluded")
        self.card = {"kind": "experiment-promotion", "experiment": self.record,
                     "name": self.name, "asset": self.asset, "winner": winner,
                     "variant": self.arms[winner]["variant"],
                     "machine": self.arms[winner]["machine"],
                     "standings": stand,
                     "evidence": [self.record]
                     + [a["record"] for a in self.arms.values()]}
        return self.card

    def adopt(self, agent: dict, kp, *, human_word: bool) -> str:
        """The rollout as a signed constitutional act: on the human's word
        ONLY, the winner becomes the head — adopted_from the winning variant,
        derived_from naming the variant AND the experiment (the 0038 orphan
        law: a promoted standard is never an orphan). The loser stays on the
        shelf, outranked, nothing deleted."""
        if not human_word:
            raise IllegalMove("the rollout moves only on a human's word — "
                              "the gate holds the evidence")
        if self.state != "concluded":
            raise IllegalMove("adoption follows a concluded experiment only")
        win = self.arms[self.card["winner"]]
        prof = improver._profile_of(self.node.records[win["variant"]])
        sib = improver.make_asset(agent, kp, self.node.scope, name=self.asset,
                                  profile=prof, adopted_from=win["variant"],
                                  derived_from=[win["variant"], self.record])
        rid = self.node.write(sib)
        self._move("adopted")
        return rid

    def decline(self, *, human_word: bool) -> None:
        """The word may be no — at any door. History remains; nothing serves
        that was not already serving."""
        if not human_word:
            raise IllegalMove("only a human declines an experiment")
        self._move("declined")


def experiments_on(node) -> list[dict]:
    """Every declaration on the shelf, oldest first — the glass's list."""
    rows = [(r.get("received_at", ""), _json.loads(
        crypto._b64d(r["body"]).decode())["experiment"])
        for r in node.records.values()
        if "experiment" in (r.get("tags") or [])
        and "experiment-arm" not in (r.get("tags") or [])]
    return [body for _, body in sorted(rows, key=lambda x: x[0])]
