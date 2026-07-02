"""The Harness node — one recursive primitive, tier as a profile (0000 §1).

Implements the three flows in-process: policy cascades DOWN (floors never loosen),
memory rises UP (pruned; distillations carry provenance), retrieval escalates UP
(serve-what-you-have + delegate; remainder never silent; refusals leak nothing).
"""
from __future__ import annotations

import re
from datetime import datetime

from . import crypto, rollup
from .agent_surface import ModelGateway
from .identity import AuthzError, Becky, Nanda, NOW, is_within, tenant_of
from .schemas import validate


class Refusal(Exception):
    """Uniform caller-visible refusal — authz-miss and total-miss look identical (0002 §4)."""

    PUBLIC = "request cannot be served under this capability"

    def __init__(self, internal_reason: str):
        super().__init__(self.PUBLIC)
        self.internal_reason = internal_reason  # visible only in the privileged access log


class FloorViolation(Exception):
    pass


class ClockViolation(Exception):
    """Lived memory below the scope's high-water mark — you cannot quietly write yourself a past (0004 §1)."""


_DUR = re.compile(r"^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")


def dur_days(d: str) -> float:
    if d == "forever":
        return float("inf")
    m = _DUR.match(d)
    y, mo, w, dd, h, mi, s = (int(g) if g else 0 for g in m.groups())
    return y * 365 + mo * 30 + w * 7 + dd + h / 24 + mi / 1440 + s / 86400


def _ts(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


_ACTION_RANK = {"keep-raw": 3, "distill": 2, "drop-after-distill": 1}


class HarnessNode:
    def __init__(self, profile: dict, becky: Becky, nanda: Nanda,
                 parent: "HarnessNode | None" = None):
        self.profile = validate(profile, "tier-profile.schema.json")
        self.scope: str = profile["scope"]
        self.becky, self.nanda, self.parent = becky, nanda, parent
        self.children: list[HarnessNode] = []
        self.records: dict[str, dict] = {}          # ContentHash -> MemoryRecord
        self.purged: set[str] = set()               # bodies dropped (tombstone schedule)
        self.undistilled: list[str] = []
        self.inherited_floors: dict[str, dict] = {} # match-hash -> KeepRule (non-loosenable)
        self.local_floors: dict[str, dict] = {}
        self.access_log: list[dict] = []
        self.high_water: str | None = None          # the scope's universe-time frontier (0004 §1)
        self.runs: dict[str, dict] = {}             # ContentHash -> RunRecord (0005)
        self.child_rollups: list[dict] = []         # RollUps pushed up by children
        self.model_gateway = ModelGateway()         # the governed door to models (0010)
        self.signal_count = 0                       # vigil's tap: signal volume, content-blind
        self.stamped_live = 0                       # live incarnations vs the stamp_quota (0011)
        self._bundle: dict | None = None            # what children PULL
        # a layer is born with its staff (0006 §2): the steward exists before any workforce
        self.steward, self.steward_kp = becky.issue_identity(
            "instance", self.scope, resident=True)
        if parent is not None:
            parent._register_child(self)

    # ---- join (0000 §1: the whole tree is ScopePath + parent + joined children) ----
    def _register_child(self, child: "HarnessNode") -> None:
        join = {
            "child_did": child.steward["did"],
            "child_scope": child.scope,
            "parent_scope": self.scope,
            "join_level": child.profile["join_default"],
            "floors_ack": [{"id": crypto.content_hash(r), "version": "0.0.1"}
                           for r in self.all_floors().values()],
            "at": NOW(),
        }
        join["sig"] = child.steward_kp.sign(child.steward["did"], join)
        validate(join, "join.schema.json")
        self.children.append(child)

    # ---- flow 1: policy cascades DOWN --------------------------------------------
    def all_floors(self) -> dict[str, dict]:
        return {**self.inherited_floors, **self.local_floors}

    def publish_floors(self, rules: list[dict], version: str = "0.0.1") -> None:
        """Parent side: sign a bundle; children PULL and verify — never pushed in."""
        for r in rules:
            self.local_floors[crypto.content_hash(r["match"])] = r
        bundle = {
            "standards": [{"id": crypto.content_hash(r), "version": version} for r in rules],
            "target": "all",
            "issued_by": self.becky.did,
            "issued_at": NOW(),
        }
        bundle["sig"] = self.becky.kp.sign(self.becky.did, bundle)
        self._bundle = validate(bundle, "signed-record.schema.json#/$defs/SignedBundle")
        self._bundle_rules = rules

    def pull_standards(self) -> None:
        """Child side: PULL from parent, VERIFY authenticity, apply. Floors merge down.
        A pull refreshes the ancestry first — the cascade is tier-by-tier, never skipped."""
        if self.parent is None:
            return
        self.parent.pull_standards()
        if self.parent._bundle is not None:
            b = self.parent._bundle
            pub = self.nanda.public(b["issued_by"])
            if not crypto.verify_sig(b["sig"], b, pub):
                raise AuthzError("bundle signature invalid — poisoned standard rejected")
            for r in getattr(self.parent, "_bundle_rules", []):
                self.inherited_floors[crypto.content_hash(r["match"])] = r
        for r in self.parent.inherited_floors.values():  # grandparent floors cascade too
            self.inherited_floors[crypto.content_hash(r["match"])] = r

    def add_local_floor(self, rule: dict) -> None:
        """A layer may TIGHTEN an inherited floor, never loosen it (lexicographic, 0000 §1)."""
        mh = crypto.content_hash(rule["match"])
        inh = self.inherited_floors.get(mh)
        if inh:
            weaker_action = _ACTION_RANK[rule["action"]] < _ACTION_RANK[inh["action"]]
            shorter = (rule["keep_for"] != "promote" and inh["keep_for"] != "promote"
                       and dur_days(rule["keep_for"]) < dur_days(inh["keep_for"]))
            if weaker_action or shorter:
                raise FloorViolation("inherited floors are non-overridable — tighten only")
        self.local_floors[mh] = rule

    # ---- flow 2: memory rises UP, pruned ------------------------------------------
    def write(self, record: dict) -> str:
        validate(record, "memory-record.schema.json")
        if not self.nanda.active(record["author"]):
            raise AuthzError("author revoked")
        pub = self.nanda.public(record["author"])
        if not crypto.verify_sig(record["signature"], _sig_subset(record), pub):
            raise AuthzError("bad record signature — Sourced or nothing")
        if not is_within(record["scope"], self.scope):
            raise AuthzError("record scope outside this harness")
        record = dict(record)
        # the declared clock (0004 §1): lived memory only moves forward; archives are labeled
        if record.get("provenance_class", "lived") == "lived":
            if self.high_water is not None and _ts(record["occurred_at"]) < _ts(self.high_water):
                raise ClockViolation("occurred_at below scope high-water")
            if self.high_water is None or _ts(record["occurred_at"]) > _ts(self.high_water):
                self.high_water = record["occurred_at"]
        record["received_at"] = NOW()               # gateway stamp — physics, nobody's claim
        record["keep_class"] = self._classify(record)
        self.records[record["id"]] = record
        # each layer distills what rises to it — including children's distillations;
        # only this node's OWN distillations are exempt (they're the output, not the input)
        if record["author"] != self.steward["did"]:
            self.undistilled.append(record["id"])
        return record["id"]

    def _classify(self, record: dict) -> str:
        for rule in self.all_floors().values():
            m = rule["match"]
            if m.get("outcome") and m["outcome"] != "any":
                if m["outcome"] in record.get("tags", []):
                    return rule["action"] if rule["action"] == "keep-raw" else "distilled-raw-retained"
            if m.get("tags") and set(m["tags"]) & set(record.get("tags", [])):
                return "keep-raw" if rule["action"] == "keep-raw" else "distilled-raw-retained"
        return "distilled-raw-retained"

    def run_distillation(self) -> dict | None:
        """The steward's ingress pass (0003 §4): distill what floors didn't pin, push UP."""
        if not self.undistilled:
            return None
        ids = list(self.undistilled)
        self.undistilled.clear()
        times = sorted(self.records[i]["occurred_at"] for i in ids)
        body = {"summary": f"distilled {len(ids)} records at {self.scope}", "count": len(ids)}
        dist = {
            "id": crypto.content_hash({"body": body, "derived_from": ids}),
            "kind": "distillation",
            "scope": self.scope,
            "author": self.steward["did"],
            "occurred_at": self._universe_now(),
            "provenance_class": "lived",
            "retention": "active",
            "visibility": {"tenancy": "tenant-private", "mobility": "branch-bound"},
            "derived_from": ids,
            "method": {"steward": self.steward["did"],
                       "rubric": {"id": crypto.content_hash({"rubric": "sim-v0"}), "version": "0.0.1"},
                       "model": "deterministic-sim"},
            "window": {"from": times[0], "to": times[-1]},
            "redactions": [],
        }
        dist["signature"] = self.steward_kp.sign(self.steward["did"], _sig_subset(dist))
        self.write(dist)
        if self.parent is not None:
            env = {
                "payload_hash": dist["id"],
                "payload_type": "https://orreth.ai/contracts/v0/memory-record.schema.json",
                "scope": self.scope,
                "author": self.steward["did"],
                "created_at": NOW(),
            }
            env["sig"] = self.steward_kp.sign(self.steward["did"], env)
            validate(env, "signed-record.schema.json#/$defs/SignedRecord")
            self.parent.write(dist)  # PUSH up — the parent verifies for itself
        return dist

    # ---- 0005: run records + the monoidal roll-up -----------------------------------
    def record_run(self, run: dict) -> str:
        """Resident-authored only (0001: no agent grades its own yardstick)."""
        validate(run, "run-record.schema.json")
        pub = self.nanda.public(run["author"])
        if not crypto.verify_sig(run["sig"], {k: run[k] for k in
                                              ("id", "agent", "scope", "goal_hash", "occurred_at")}, pub):
            raise AuthzError("bad run signature")
        if run["author"] == run["agent"]:
            raise AuthzError("self-asserted evaluation — resident-authored only (0001)")
        self.runs[run["id"]] = run
        return run["id"]

    def roll_up(self, bucket: dict, goal_hash: str | None = None) -> dict:
        """Aggregate own runs in the universe-time bucket + child bundles, sign, push UP.

        The stats are identical whether built from RunRecords or child RollUps — the
        monoid law is the 'one truth' property the conformance tests pin."""
        stats = rollup.empty_bundle()
        contributors: list[str] = []
        for r in self.runs.values():
            in_bucket = bucket["from"] <= r["occurred_at"] <= bucket.get("to", r["occurred_at"])
            if in_bucket and (goal_hash is None or r["goal_hash"] == goal_hash):
                stats = rollup.merge(stats, rollup.bundle_of(r))
                contributors.append(r["id"])
        for child_ru in self.child_rollups:
            if child_ru["bucket"] == bucket and \
                    (goal_hash is None or child_ru["cohort"].get("goal_hash") == goal_hash):
                stats = rollup.merge(stats, child_ru["stats"])
                contributors.append(child_ru["id"])
        ru = {
            "id": crypto.content_hash({"scope": self.scope, "bucket": bucket,
                                       "goal_hash": goal_hash, "contributors": contributors}),
            "scope": self.scope,
            "cohort": {"scope": self.scope, **({"goal_hash": goal_hash} if goal_hash else {})},
            "bucket": bucket,
            "stats": stats,
            "contributors": contributors,
            "author": self.steward["did"],
            "version": "0.0.1",
        }
        ru["sig"] = self.steward_kp.sign(self.steward["did"],
                                         {k: ru[k] for k in ("id", "scope", "bucket", "stats")})
        validate(ru, "run-record.schema.json#/$defs/RollUp")
        if self.parent is not None:
            self.parent.child_rollups.append(ru)   # PUSH up — pointers travel, raw runs never do
        return ru

    # ---- erasure: governed tombstone; derived memories annotate, never rewrite -----
    def tombstone(self, record_id: str, by: str, reason: str) -> None:
        rec = self.records[record_id]
        policy_ref = {"id": crypto.content_hash({"policy": "consent-withdrawal"}), "version": "0.0.1"}
        stone = {"by": by, "policy_ref": policy_ref, "reason": reason, "at": NOW()}
        stone["signature"] = self.steward_kp.sign(self.steward["did"], stone)
        rec["retention"] = {"tombstoned": stone}
        rec.pop("body", None)
        self.purged.add(record_id)
        marker = {"tombstone_ref": record_id, "at": NOW(), "policy_ref": policy_ref}
        marker["sig"] = self.steward_kp.sign(self.steward["did"], marker)
        for node in self._lineage_up():
            for r in node.records.values():
                if r["kind"] == "distillation" and record_id in r.get("derived_from", []):
                    r.setdefault("redactions", []).append(marker)

    def _lineage_up(self):
        n: HarnessNode | None = self
        while n is not None:
            yield n
            n = n.parent

    def _universe_now(self) -> str:
        """The universe's own 'now' — the high-water frontier (wall for a young/wall-mode scope)."""
        return self.high_water or NOW()

    # ---- flow 3: retrieval escalates UP --------------------------------------------
    def retrieve(self, query: dict, token: dict, requester_scope: str) -> dict:
        validate(query, "retrieval.schema.json#/$defs/Query")
        try:
            self.becky.verify_token(token)
            grant = _covering_grant(token, "retrieve")
        except AuthzError as e:
            self._log(query, refused=str(e))
            raise Refusal(str(e))
        interview = query["intent"] == "interview"
        if interview and "portfolio" not in (grant.get("visibility") or []):
            self._log(query, refused="interview without portfolio grant")
            raise Refusal("interview without portfolio grant")

        budget_visits = max(1, int(query["budget"].get("cost", 1)))
        hits_raw: dict[str, dict] = {}
        served_by: list[str] = []
        not_served_from: str | None = None
        node: HarnessNode | None = self
        window_from = query["time"]["from"]

        while node is not None:
            # presenting the token AT a node requires the node to be within its audience
            authorized_here = is_within(node.scope, token["audience"])
            if budget_visits <= 0 or not authorized_here:
                # budget-miss ≡ authz-miss: both become un-served coverage, never an error shape
                not_served_from = window_from
                break
            budget_visits -= 1
            served_by.append(node.scope)
            for r in node.records.values():
                if self._readable(r, query, token, requester_scope, interview):
                    hits_raw.setdefault(r["id"], r)
            horizon_days = dur_days(node.profile["retrieval"]["horizon"])
            # horizons are universe-time (0004 §1): age is measured against the scope's own now
            window_age_days = (_ts(node._universe_now()) - _ts(window_from)).total_seconds() / 86400
            if window_age_days <= horizon_days:
                break  # this tier's horizon covers the window — done ('forever' always covers)
            node = node.parent  # time-horizon miss: delegate the deeper remainder UP

        ordered = sorted(hits_raw.values(), key=lambda r: r["occurred_at"], reverse=True)
        hits = [{
            "ref": r["id"], "source": r["author"], "scope": r["scope"],
            "fidelity": self._fidelity(r),
        } for r in ordered]
        result: dict = {
            "hits": hits,
            "provenance": {
                "served_by": served_by,
                "time_span": query["time"],
                "budget_spent": {"cost": int(query["budget"].get("cost", 1)) - budget_visits},
            },
            "verification": "partial" if not_served_from else "verified",
        }
        if not_served_from:
            result["remainder"] = {"not_served": {"from": not_served_from,
                                                  "to": served_by and NOW() or None}}
            result["remainder"]["not_served"] = {"from": not_served_from}
        validate(result, "retrieval.schema.json#/$defs/RetrievalResult")
        self._log(query, hits=len(hits))
        return result

    def _readable(self, r: dict, query: dict, token: dict, requester_scope: str,
                  interview: bool) -> bool:
        if r["kind"] != "distillation" and r["id"] in self.purged:
            return False
        if not is_within(r["scope"], token["audience"]):
            return False  # a token never reads outside its audience subtree
        subj = query["subject"]
        if subj == "self":
            if r["author"] != query["requester"]:
                return False
        elif "identity" in subj:
            if r["author"] != subj["identity"]:
                return False
        elif "cohort" in subj and isinstance(subj["cohort"], dict) and "scope" in subj["cohort"]:
            if not is_within(r["scope"], subj["cohort"]["scope"]):
                return False
        if not (_ts(query["time"]["from"]) <= _ts(r["occurred_at"])):
            return False
        tenancy = r["visibility"]["tenancy"] if "visibility" in r else "tenant-private"
        if interview:
            return tenancy == "portfolio"
        if tenancy == "tenant-private":
            same_tenant = tenant_of(r["scope"]) == tenant_of(requester_scope) or \
                is_within(r["scope"], requester_scope)
            apex_grant = any(g.get("space") == "apex" for g in token["grants"])
            if not (same_tenant or apex_grant):
                return False
        return True

    def _fidelity(self, r: dict) -> str:
        if r["kind"] != "distillation":
            return "verified"
        chain_purged = any(src in self._purged_anywhere() for src in r.get("derived_from", []))
        return "distilled-raw-expired" if chain_purged else "distilled"

    def _purged_anywhere(self) -> set[str]:
        out: set[str] = set()
        for n in self._lineage_up():
            out |= n.purged
        root = self
        while root.parent:
            root = root.parent
        def walk(n):
            out.update(n.purged)
            for c in n.children:
                walk(c)
        walk(root)
        return out

    # ---- sibling benchmarks: aggregates only, computed at the common parent ---------
    def benchmark(self) -> dict:
        """Anonymized aggregate across children — no refs, no DIDs, no scopes leak."""
        counts = sorted(len(c.records) for c in self.children)
        n = len(counts)
        median = counts[n // 2] if n % 2 else (counts[n // 2 - 1] + counts[n // 2]) / 2
        return {"cohort_size": n, "median_record_count": median}

    def _log(self, query: dict, **detail) -> None:
        entry = {"requester": query["requester"], "intent": query["intent"],
                 "at": NOW(), **detail}
        entry["sig"] = self.steward_kp.sign(self.steward["did"], entry)
        self.access_log.append(entry)


def _sig_subset(record: dict) -> dict:
    # occurred_at and provenance_class are SIGNED (backdating and archive-flipping are author claims);
    # received_at is gateway physics and deliberately outside the signature (0004 §1)
    return {k: record[k] for k in ("id", "kind", "scope", "author", "occurred_at", "provenance_class")}


def _covering_grant(token: dict, action: str) -> dict:
    for g in token["grants"]:
        if g["action"] == action:
            return g
    raise AuthzError(f"no grant covers '{action}'")


def make_memory(author: dict, kp, scope: str, body: dict, *, kind: str = "episodic",
                tenancy: str = "tenant-private", mobility: str = "branch-bound",
                tags: list[str] | None = None, occurred_at: str | None = None,
                provenance_class: str = "lived") -> dict:
    rec = {
        "id": crypto.content_hash(body),
        "kind": kind,
        "scope": scope,
        "author": author["did"],
        "occurred_at": occurred_at or NOW(),
        "provenance_class": provenance_class,
        "body": crypto._b64e(crypto.canonical(body)),
        "retention": "active",
        "visibility": {"tenancy": tenancy, "mobility": mobility},
        "tags": tags or [],
    }
    rec["signature"] = kp.sign(author["did"], _sig_subset(rec))
    return rec
