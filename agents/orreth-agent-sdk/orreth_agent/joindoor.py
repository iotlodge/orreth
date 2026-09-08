# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp3, the publishable join door · 2026-09-08
"""THE PUBLISHABLE JOIN DOOR (0071 sp3 — KCR-0001 paid): a small program an operator
runs beside their own kernel, holding only its OWN key. At setup, the operator's root
signs the door's credential ONCE (`mint`, run where the root seed lives); from then on
the door challenges joiners, verifies their proofs, waits for the operator's word, and
mints properly chained leases — while the root key stays in the operator's safe. The
kernel goes on verifying everything against the pinned root, as it always has.

    python -m orreth_agent.joindoor mint  --root-seed .root-seed --root-did did:web:example.com:u:first \\
                                          --scope u:first/f:main --out door.json
    python -m orreth_agent.joindoor serve --door door.json --field http://127.0.0.1:4601
    python -m orreth_agent.joindoor pending --field http://127.0.0.1:4601
    python -m orreth_agent.joindoor approve <req-id> --door door.json --field http://127.0.0.1:4601

Three laws, inherited whole from the reference desk (`orreth_sim/joindoor.py` — the twin):
the desk's own nonce is the truth (never the echoed one); a restart re-challenges rather
than verifying blind; an approval without a proven key mints nothing. Two honesty
upgrades ride this door from birth: the STANDING WELCOME is a signed record on the floor
(never a private file), and becky's side writes the ADMISSION record — the joiner's
birth memory stops being the only witness.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .crypto import (KeyPair, b64d, b64e, canonical, content_hash, did_key_for,
                     public_from_did, verify_sig)

RECORD_SIG_KEYS = ("id", "kind", "scope", "author", "occurred_at", "provenance_class")
REFUSAL = "request cannot be served under this capability"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _call(base: str, method: str, path: str, payload=None):
    req = urllib.request.Request(base + path, method=method,
                                 data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        b = r.read()
        return json.loads(b) if b[:1] in (b"{", b"[") else b


class Door:
    """The adopted delegate: seed + root-signed cert, loaded from the door file."""

    def __init__(self, door_file: str | Path):
        d = json.loads(Path(door_file).read_text())
        self.scope: str = d["scope"]
        self.kp = KeyPair(seed=b64d(d["seed"]))
        self.did = did_key_for(self.kp.public)
        self.cert: dict = d["cert"]
        if self.cert.get("subject") != self.did:
            raise SystemExit("the door file's cert does not name its own key — refuse to serve")
        self.root_did: str = d.get("root_did", self.cert.get("issuer", ""))
        self.lease_days: int = int(d.get("lease_days", 30))
        self.lease_tokens: int = int(d.get("lease_tokens", 400_000))
        self.renew_days: int = int(d.get("renew_days", 1))
        self.desk: dict[str, dict] = {}   # rid -> {nonce, did} — RAM; restart re-challenges

    # ---- issuing (the plane verifies; this door only signs its own hops) ----
    def _token(self, subject: str, grants: list[dict], *,
               budget: dict | None = None, days: int = 365) -> dict:
        expiry = (datetime.now(timezone.utc)
                  + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        constraints: dict = {"expiry": expiry, "direction": "within"}
        if budget:
            constraints["budget"] = budget
        hop = {"issuer": self.did, "subject": subject, "audience": self.scope,
               "grants": grants, "constraints": constraints}
        hop["sig"] = self.kp.sign(self.did, hop)
        return {"subject": subject, "audience": self.scope, "grants": grants,
                "constraints": constraints,
                "chain": [json.dumps(c, sort_keys=True)
                          for c in [self.cert, hop]],
                "sig": self.kp.sign(self.did, {"subject": subject,
                                               "audience": self.scope,
                                               "grants": grants,
                                               "constraints": constraints})}

    def pen(self) -> dict:
        return self._token(self.did, [{"action": "resolve", "space": "queue"}])

    def lease(self, did: str) -> dict:
        budget = {"tokens": self.lease_tokens}
        if self.renew_days > 0:
            budget["renew_days"] = self.renew_days
        return self._token(did, [{"action": "retrieve", "space": "self"}],
                           budget=budget, days=self.lease_days)

    # ---- records (welcomes + admissions — becky's side finally writes) ------
    def _record(self, body: dict, tags: list[str]) -> dict:
        rec = {"id": content_hash(body), "kind": "semantic", "scope": self.scope,
               "author": self.did, "occurred_at": _now(),
               "provenance_class": "lived",
               "body": b64e(canonical(body)), "retention": "active",
               "visibility": {"tenancy": "tenant-private", "mobility": "branch-bound"},
               "tags": tags}
        rec["signature"] = self.kp.sign(self.did,
                                        {k: rec[k] for k in RECORD_SIG_KEYS})
        return rec

    def write_welcome(self, base: str, did: str, req: str) -> None:
        body = {"welcome": {"did": did, "scope": self.scope, "req": req,
                            "by": self.did, "at": _now()}}
        try:
            _call(base, "POST", "/records",
                  self._record(body, ["welcome", "join"]))
        except Exception as e:
            print(f"· the welcome record did not land ({e}) — the click is not durable yet")

    def write_admission(self, base: str, did: str, name: str, req: str,
                        expiry: str) -> None:
        body = {"admission": {"did": did, "name": name, "scope": self.scope,
                              "req": req, "lease_expires": expiry,
                              "granted_by": self.did, "at": _now()}}
        try:
            _call(base, "POST", "/records",
                  self._record(body, ["admission", "join"]))
        except Exception as e:
            print(f"· the admission record did not land ({e})")

    def standing_welcome(self, base: str, did: str) -> str | None:
        """The durable click: a welcome RECORD on the floor for this did+scope.
        Read through the governed window with the door's own retrieve token."""
        tok = self._token(self.did, [{"action": "retrieve", "space": "self"}])
        q = {"requester": self.did, "subject": "self", "space": "self",
             "time": {"from": "2020-01-01T00:00:00Z"}, "intent": "recall",
             "budget": {"cost": 4}, "auth": "biscuit-sim"}
        try:
            out = _call(base, "POST", "/retrieve",
                        {"query": q, "token": tok, "requester_scope": self.scope})
        except Exception:
            return None
        for h in out.get("hits", []):
            if "welcome" not in (h.get("tags") or []):
                continue
            try:
                b = _call(base, "GET", f"/records/{h['ref']}/body")
            except Exception:
                continue
            w = (b or {}).get("welcome") or {}
            if w.get("did") == did and w.get("scope") == self.scope:
                return w.get("req") or h["ref"]
        return None

    # ---- the desk (the reference twin's state machine, verbatim in spirit) --
    def tend(self, base: str, r: dict) -> None:
        rid, status = str(r.get("id")), str(r.get("status"))
        did = str(r.get("did") or "")
        name = str(r.get("name") or "")
        pen = self.pen()
        if status in ("done", "denied", "cancelled"):
            self.desk.pop(rid, None)
            return
        if not did.startswith("did:key:"):
            if status == "pending":
                _call(base, "POST", "/requests/resolve",
                      {"token": pen, "id": rid, "status": "denied",
                       "result": {"note": "join refused — only self-certifying "
                                          "DIDs may be challenged"}})
            return
        if status == "pending":
            nonce = secrets.token_hex(16)
            self.desk[rid] = {"nonce": nonce, "did": did}
            _call(base, "POST", "/requests/resolve",
                  {"token": pen, "id": rid, "status": "challenged",
                   "result": {"nonce": nonce,
                              "note": "sign this nonce with your own key — "
                                      "the door verifies, never trusts"}})
            print(f"· join {rid}: challenged {name or did[:22] + '…'}")
            return
        if status == "proved":
            entry = self.desk.get(rid)
            if entry is None or entry["did"] != did:
                nonce = secrets.token_hex(16)
                self.desk[rid] = {"nonce": nonce, "did": did}
                _call(base, "POST", "/requests/resolve",
                      {"token": pen, "id": rid, "status": "challenged",
                       "result": {"nonce": nonce,
                                  "note": "the desk re-challenges — it never "
                                          "verifies blind"}})
                return
            proof = (r.get("result") or {}).get("proof") or {}
            public = public_from_did(did)
            ok = bool(public) and verify_sig(
                proof, {"join_nonce": entry["nonce"], "did": did}, public)
            if not ok:
                self.desk.pop(rid, None)
                _call(base, "POST", "/requests/resolve",
                      {"token": pen, "id": rid, "status": "denied",
                       "result": {"note": "join refused — the proof did not verify"}})
                print(f"· join {rid}: proof failed — turned away")
                return
            self.desk[rid]["proven"] = True
            w = self.standing_welcome(base, did)
            if w:
                _call(base, "POST", "/requests/resolve",
                      {"token": pen, "id": rid, "status": "approved",
                       "result": {"approved_by": f"your standing welcome ({w}) — "
                                                 "the same self, the same floor"}})
                print(f"· join {rid}: standing welcome honored — {name or did[:22]}…")
            else:
                _call(base, "POST", "/requests/resolve",
                      {"token": pen, "id": rid, "status": "staged",
                       "result": {"note": f"{name or did[:22]}… proved its key — "
                                          "the door waits for your word "
                                          "(joindoor approve <id>)"}})
                print(f"· join {rid}: proved — waiting for your word "
                      f"(joindoor approve {rid})")
            return
        if status == "approved":
            entry = self.desk.get(rid)
            if not entry or not entry.get("proven") or entry["did"] != did:
                nonce = secrets.token_hex(16)
                self.desk[rid] = {"nonce": nonce, "did": did}
                _call(base, "POST", "/requests/resolve",
                      {"token": pen, "id": rid, "status": "challenged",
                       "result": {"nonce": nonce,
                                  "note": "an approval without a proven key "
                                          "mints nothing — prove again"}})
                return
            token = self.lease(did)
            expiry = token["constraints"]["expiry"]
            self.desk.pop(rid, None)
            # the WHY survives the minting: a done that forgets who admitted it
            # would make the queue illegible (the walk's own find, 2026-09-08)
            prior = r.get("result") if isinstance(r.get("result"), dict) else {}
            approved_by = prior.get("approved_by", "the operator's word at the door")
            _call(base, "POST", "/requests/resolve",
                  {"token": pen, "id": rid, "status": "done",
                   "result": {"token": token, "granted_by": self.did,
                              "scope": self.scope,
                              "approved_by": approved_by,
                              "lease_terms": {
                                  "expires": expiry,
                                  "budget_tokens": self.lease_tokens,
                                  "note": "a lease with terms — re-joining "
                                          "renews it; the self, its name, and "
                                          "its diary survive"}}})
            self.write_welcome(base, did, rid)
            self.write_admission(base, did, name, rid, expiry)
            print(f"  ✓ lease granted — welcome to {self.scope}, "
                  f"{name or did[:22] + '…'} (welcome + admission on the record)")


def cmd_mint(a) -> int:
    """Runs WHERE THE ROOT LIVES, once. The root's seed is read, the credential is
    signed, and the seed never rides the door file."""
    root_kp = KeyPair(seed=Path(a.root_seed).read_bytes())
    delegate = KeyPair()
    cert = {"issuer": a.root_did, "subject": did_key_for(delegate.public),
            "scope": a.scope, "at": _now()}
    cert["sig"] = root_kp.sign(a.root_did, cert)
    out = {"scope": a.scope, "seed": b64e(delegate.seed), "cert": cert,
           "root_did": a.root_did, "lease_days": a.lease_days,
           "lease_tokens": a.lease_tokens, "renew_days": a.renew_days}
    p = Path(a.out)
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    p.chmod(0o600)
    print(f"door credential minted → {a.out}")
    print(f"  door DID: {cert['subject'][:40]}…  (the root's key never left "
          f"{a.root_seed})")
    return 0


def cmd_serve(a) -> int:
    door = Door(a.door)
    print(f"the join door is open — {door.scope} at {a.field}")
    print(f"  door DID {door.did[:40]}… · credential signed by {door.root_did}")
    while True:
        try:
            q = _call(a.field, "GET", "/requests").get("requests", [])
            for r in q:
                if r.get("kind") == "join":
                    door.tend(a.field, r)
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            print(f"· the kernel did not answer ({e}) — trying again")
        time.sleep(a.poll)


def cmd_pending(a) -> int:
    q = _call(a.field, "GET", "/requests").get("requests", [])
    rows = [r for r in q if r.get("kind") == "join"
            and r.get("status") == "staged"]
    if not rows:
        print("no joins wait for your word")
    for r in rows:
        print(f"{r['id']}  {r.get('name') or (r.get('did') or '?')[:30] + '…'}  "
              f"(staged {r.get('at', '?')})")
    return 0


def cmd_approve(a) -> int:
    door = Door(a.door)
    _call(a.field, "POST", "/requests/resolve",
          {"token": door.pen(), "id": a.req_id, "status": "approved",
           "result": {"approved_by": "the operator's word at the door"}})
    print(f"approved {a.req_id} — the serving door mints on its next tend")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="orreth_agent.joindoor")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mint", help="root signs the door's credential, once, offline")
    m.add_argument("--root-seed", required=True)
    m.add_argument("--root-did", required=True)
    m.add_argument("--scope", required=True)
    m.add_argument("--out", default="door.json")
    m.add_argument("--lease-days", type=int, default=30)
    m.add_argument("--lease-tokens", type=int, default=400_000)
    m.add_argument("--renew-days", type=int, default=1)
    m.set_defaults(fn=cmd_mint)
    s = sub.add_parser("serve", help="tend the kernel's join queue")
    s.add_argument("--door", required=True)
    s.add_argument("--field", required=True)
    s.add_argument("--poll", type=float, default=1.5)
    s.set_defaults(fn=cmd_serve)
    p = sub.add_parser("pending", help="joins waiting for your word")
    p.add_argument("--field", required=True)
    p.set_defaults(fn=cmd_pending)
    ap2 = sub.add_parser("approve", help="your word, from your own terminal")
    ap2.add_argument("req_id")
    ap2.add_argument("--door", required=True)
    ap2.add_argument("--field", required=True)
    ap2.set_defaults(fn=cmd_approve)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
