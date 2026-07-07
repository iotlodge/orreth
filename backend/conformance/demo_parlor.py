# PROVENANCE: Fable 5 (claude-fable-5) — 0020, the Parlor · 2026-07-07
"""The Parlor, live (0020): humans ask; residents fetch; the audience lands signed.

Three audiences against the running rig (scripts/dev.sh start first):

  I.   charlotte hands her calling card and answers "what is serving?" — grounded in
       the farm she is authorized to read; the caller never touches a record.
  II.  ada reads her own meter back to the caller — the universal meter, in words.
  III. a knock on vigil's door: the unembodied organ receives the caller and says
       honestly that it has no voice yet.

Then the audiences are read back off the spacetime window — every exchange a
resident-signed memory, tagged ["parlor", <name>]. Humans at the gates, signatures
on the record. When the floor is fueled (ANTHROPIC/OPENAI key), replies arrive
voiced — one governed thought, metered under the resident's own DID.

    uv run python demo_parlor.py [field_port]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda
from smoke_orrethd import root_keypair

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4502
BASE = f"http://127.0.0.1:{PORT}"
SCOPE = "u:demo/e:cloud/f:prod"
SESSION = f"pa-demo-{int(time.time())}"


def call(method: str, path: str, payload=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read() or b"{}")


def say(line: str = "", beat: float = 0.6):
    print(line)
    time.sleep(beat)


def audience(to: str, *, verb: str | None = None, text: str = "", patience: int = 30) -> dict:
    """One exchange through the queue — exactly what the Console's parlor does."""
    body = {"kind": "parlor", "to": to, "session": SESSION,
            "text": text or f"{verb} · {to}"}
    if verb:
        body["verb"] = verb
    req = call("POST", "/requests", body)
    t0 = time.time()
    while time.time() - t0 < patience:
        r = next((x for x in call("GET", "/requests")["requests"]
                  if x.get("id") == req["id"]), {})
        if r.get("status") == "done":
            return r.get("result") or {}
        time.sleep(1)
    raise SystemExit(f"\n  {to} never answered — is the worker tending? (scripts/dev.sh start)")


def worldline_audiences() -> list[tuple[str, str, str, str]]:
    """The exchanges, read back off the Window — signed memory, in time."""
    kp = crypto.KeyPair()
    did = crypto.did_key_for(kp.public)
    root = Becky("u:demo", Nanda(), universe_name="demo", kp=root_keypair())
    token = root.issue_token(did, "u:demo", [{"action": "retrieve", "space": "self"}])
    frm = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = call("POST", "/retrieve", {
        "query": {"requester": did, "subject": {"cohort": {"scope": SCOPE}},
                  "space": "self", "time": {"from": frm}, "intent": "recall",
                  "budget": {"cost": 4}, "auth": "biscuit-sim"},
        "token": token, "requester_scope": SCOPE})
    out = []
    for h in r["hits"]:
        if "parlor" in (h.get("tags") or []):
            ref = urllib.parse.quote(h["ref"], safe="")
            b = json.loads(urllib.request.urlopen(
                f"{BASE}/records/{ref}/body", timeout=8).read())
            if b.get("session") == SESSION:
                out.append((b["at"], b["parlor"], b["asked"], b["reply"]))
    return sorted(out)


def main() -> None:
    say("\n═══ THE PARLOR (0020) — humans ask; residents fetch ═══\n")
    say("  The law: agents, when authorized, see data inside the universe.")
    say("  Humans never do — a human's only read is an ask, received by a resident")
    say("  who fetches with its OWN authority and answers on the record.\n")

    say("── I. an audience with charlotte, the farm keeper ──")
    card = audience("charlotte", verb="card").get("card", {})
    say(f'  her calling card: “{card.get("greeting", "")}”')
    say(f"  she offers: {' · '.join(a['label'] for a in card.get('asks', []))}\n")
    ans = audience("charlotte", text="what is serving right now?")
    say(f'  you ask: “what is serving right now?”')
    say(f'  charlotte: “{ans.get("reply", "")}”')
    say(f"  ({'voiced — one governed thought, metered under her DID' if ans.get('voiced') else 'answered from the record — the floor is unfueled, and honest about it'})\n")

    say("── II. an audience with ada, the wrangler ──")
    ans = audience("ada", text="what does thinking cost here?")
    say(f'  you ask: “what does thinking cost here?”')
    say(f'  ada: “{ans.get("reply", "")}”\n')

    say("── III. a knock on vigil's door ──")
    ans = audience("vigil", text="what have you seen?")
    say(f'  vigil: “{ans.get("reply", "")}”')
    say("  (the unembodied receive callers too — and never pretend to a voice)\n")

    say("── the record ──")
    time.sleep(2)  # let the last audience record land
    lines = worldline_audiences()
    for at, who, asked, reply in lines:
        say(f"  {at} · {who} ← “{asked[:44]}”", 0.3)
    say(f"\n  {len(lines)} audience(s) on the spacetime window — resident-signed,")
    say("  human-witnessed, navigable across all of time. Open the Console and")
    say("  click any resident: the parlor is theirs, and the record is yours.\n")


if __name__ == "__main__":
    main()
