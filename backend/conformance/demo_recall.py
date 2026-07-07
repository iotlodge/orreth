# PROVENANCE: Fable 5 (claude-fable-5) — 0014 §4 on the wire, the recall walk · 2026-07-07
"""The Recall, live (0014 §4): discredit a source, and its knowledge dies visibly.

The poisoned-almanac story, against the running rig (scripts/dev.sh start first):

  I.   A stub source — local.demo/almanac, wearing did:web:almanac.example — is
       planted through the queue, approved, and earns serving.
  II.  Knowledge citing that source enters the Window: two entries admitted
       quarantined, plus a corroborated version DERIVED from the first — a lineage.
  III. The human decommissions the almanac WITH DISCREDIT. charlotte discredits the
       source on its worldline and hands the recall to the queue; the librarian walks
       the lineage under her own authority and re-versions every tainted entry to
       'recalled' — annotate-never-rewrite. The originals stay; the poison is
       visibly dead (fidelity: recalled) in the spacetime window.
  IV.  The librarian is asked, in the parlor, what was recalled — and answers.

    uv run python demo_recall.py [field_port]
"""
from __future__ import annotations

import json
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from orreth_sim import crypto
from orreth_sim.identity import NOW, Becky, Nanda
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4502
BASE = f"http://127.0.0.1:{PORT}"
SCOPE = "u:demo/e:cloud/f:prod"
STUB_PORT = 9923
ALMANAC = "local.demo/almanac"
ALMANAC_DID = "did:web:almanac.example"
SESSION = f"pa-recall-{int(time.time())}"


def call(method: str, path: str, payload=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        b = r.read()
        return json.loads(b) if b[:1] in (b"{", b"[") else b


def say(line: str = "", beat: float = 0.6):
    print(line)
    time.sleep(beat)


class _Stub(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"almanac")
    def log_message(self, *_): pass


def wait_request(rid: str, want: str = "done", patience: int = 45) -> dict:
    t0 = time.time()
    while time.time() - t0 < patience:
        r = next((x for x in call("GET", "/requests")["requests"]
                  if x.get("id") == rid), {})
        if r.get("status") == want:
            return r
        time.sleep(1)
    raise SystemExit(f"\n  request {rid} never reached {want} — is the worker tending?")


def wait_recall(after: float, patience: int = 60) -> dict:
    """The recall request is charlotte's, not ours — find it by kind + source."""
    t0 = time.time()
    while time.time() - t0 < patience:
        for r in call("GET", "/requests")["requests"]:
            if r.get("kind") == "recall" and r.get("source_did") == ALMANAC_DID \
                    and r.get("status") == "done":
                return r
        time.sleep(1)
    raise SystemExit("\n  the librarian never walked — is the worker tending?")


def window_knowledge() -> list[dict]:
    """Read the Window as any tokened client would — fidelity travels with the hit."""
    kp = crypto.KeyPair()
    did = crypto.did_key_for(kp.public)
    root = Becky("u:demo", Nanda(), universe_name="demo", kp=root_keypair())
    token = root.issue_token(did, "u:demo", [{"action": "retrieve", "space": "self"}])
    frm = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = call("POST", "/retrieve", {
        "query": {"requester": did, "subject": {"cohort": {"scope": SCOPE}},
                  "space": "self", "time": {"from": frm}, "intent": "recall",
                  "budget": {"cost": 4}, "auth": "biscuit-sim"},
        "token": token, "requester_scope": SCOPE})
    return [h for h in r.get("hits", []) if "knowledge" in (h.get("tags") or [])]


def main() -> None:
    say("\n═══ THE RECALL (0014 §4) — discredit a source; its knowledge dies visibly ═══\n")

    say("── I. a source takes the field ──")
    srv = HTTPServer(("127.0.0.1", STUB_PORT), _Stub)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    req = call("POST", "/requests",
               {"kind": "service", "action": "plant", "name": ALMANAC,
                "svc_kind": "http", "transport": "rest", "did": ALMANAC_DID,
                "endpoint": f"http://127.0.0.1:{STUB_PORT}/",
                "manifest": [{"name": "almanac-lookup", "description": "field almanac"}],
                "text": f"plant {ALMANAC}"})
    wait_request(req["id"], "staged")
    call("POST", "/requests/resolve", {"id": req["id"], "status": "approved"})
    say(f"  {ALMANAC} planted and approved — its DID is {ALMANAC_DID}\n")

    say("── II. the almanac speaks; the Window files it — quarantined ──")
    scribe = crypto.KeyPair()
    scribe_did = crypto.did_key_for(scribe.public)
    ids = []
    for claim in ("frost arrives two weeks early on north slopes",
                  "clay soil drains poorly below the tree line"):
        rec = make_memory({"did": scribe_did, "scope": SCOPE}, scribe, SCOPE,
                          {"knowledge": claim, "source": {"did": ALMANAC_DID, "ref": "p.12"},
                           "state": "untrusted", "intent": "field planning"},
                          kind="semantic", tags=["knowledge", "gathered"],
                          provenance_class="ingested-archive")
        ids.append(call("POST", "/records", rec)["id"])
        say(f'  admitted at 0.0000: “{claim}”', 0.3)
    # the derived version cites the SCRIBE, not the almanac — only the lineage walk
    # (derived_from), never direct source taint, can reach it. That's the proof.
    derived = make_memory({"did": scribe_did, "scope": SCOPE}, scribe, SCOPE,
                          {"knowledge": "plant hardy stock on north slopes (frost planning)",
                           "source": {"did": scribe_did, "ref": "synthesis"},
                           "state": "corroborated", "intent": "field planning"},
                          kind="semantic", tags=["knowledge"])
    derived["derived_from"] = [ids[0]]
    call("POST", "/records", derived)
    say("  and one version DERIVED from the first — its own source is internal;")
    say("  only the lineage walk can reach it\n")

    say("── III. the discredit, and the walk ──")
    t0 = time.time()
    dec = call("POST", "/requests",
               {"kind": "service", "action": "decom", "name": ALMANAC, "discredit": True,
                "text": f"decommission {ALMANAC} + discredit the source"})
    wait_request(dec["id"], "staged")
    call("POST", "/requests/resolve", {"id": dec["id"], "status": "approved"})
    say("  the human approves: decommission + DISCREDIT — consequence had waited (0012)")
    walk = wait_recall(t0)
    say(f"  charlotte handed the queue: “{walk.get('text', '')}”")
    say(f"  the librarian walked: {walk.get('result', '')}\n")

    say("── IV. the record ──")
    time.sleep(2)
    hits = window_knowledge()
    recalled = [h for h in hits if h.get("fidelity") == "recalled"]
    for h in recalled:
        say(f"  {h['occurred_at']} · fidelity={h['fidelity']} · lineage={h.get('derived_from')}", 0.3)
    say(f"\n  {len(recalled)} recall version(s) in the spacetime window — the originals")
    say("  still stand (annotate, never rewrite); the poison is visibly dead.")

    say("\n── and the librarian will tell you herself ──")
    ask = call("POST", "/requests", {"kind": "parlor", "to": "librarian",
                                     "session": SESSION,
                                     "text": "has anything been recalled?"})
    done = wait_request(ask["id"])
    say(f'  librarian: “{(done.get("result") or {}).get("reply", "")}”\n')
    srv.shutdown()


if __name__ == "__main__":
    main()
