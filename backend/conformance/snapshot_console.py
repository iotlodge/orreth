# PROVENANCE: Fable 5 (claude-fable-5) — 0019 demo, the spectator snapshot · 2026-07-06
"""Capture a moment of the live universe as a static, view-only Console.

Reads the running rig's public surfaces (topology, presence, rollup, farm, stable,
requests, health, plus one deep /retrieve cut), and writes a self-contained static
site: window.html with spectator mode baked in + the recorded fixtures. Nothing of
the rig itself ships — no keys, no tokens (the baked cfg carries a dummy), no
endpoints. The page is a photograph of a universe that really ran, labeled as such.

    uv run python snapshot_console.py [uni_port] [outdir]     (rig must be up)

Deploy the outdir anywhere static (S3+CloudFront via infrastructure/cdk).
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda
from smoke_orrethd import root_keypair

PORT = sys.argv[1] if len(sys.argv) > 1 else "4500"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "../../site").resolve()
SCOPE = "u:demo/e:cloud/f:prod"
WINDOW = Path(__file__).resolve().parents[1] / "plane/crates/orrethd/src/window.html"

FIXTURES = {"topology": "/topology", "presence": "/presence", "rollup": "/rollup",
            "farm": "/farm", "stable": "/stable", "requests": "/requests",
            "health": "/health"}


def get(path: str) -> dict:
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=10) as r:
        return json.loads(r.read())


def main() -> None:
    fx = OUT / "fixtures"
    fx.mkdir(parents=True, exist_ok=True)
    for name, path in FIXTURES.items():
        (fx / f"{name}.json").write_text(json.dumps(get(path)))
        print(f"  captured {path} → fixtures/{name}.json")

    # one deep spacetime cut, taken with a REAL capability minted here and used once —
    # the recorded response ships; the token never does
    kp = crypto.KeyPair()
    did = crypto.did_key_for(kp.public)
    root = Becky("u:demo", Nanda(), universe_name="demo", kp=root_keypair())
    token = root.issue_token(did, "u:demo", [{"action": "retrieve", "space": "self"}])
    frm = (datetime.now(timezone.utc) - timedelta(days=730)).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = {"query": {"requester": did, "subject": {"cohort": {"scope": "u:demo"}},
                      "space": "self", "time": {"from": frm}, "intent": "recall",
                      "budget": {"cost": 4}, "auth": "biscuit-sim"},
            "token": token, "requester_scope": SCOPE}
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/retrieve", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        (fx / "retrieve.json").write_text(r.read().decode())
    print("  captured /retrieve (730-day cut) → fixtures/retrieve.json")

    # ── the era-0.56 doors (2026-08-17): the worker's composed surfaces —
    # capabilities, brain, rooms, observatory — captured so the spectator's
    # pulls and modals breathe the same photograph
    def get2(path: str) -> dict:
        with urllib.request.urlopen(f"http://127.0.0.1:4562{path}",
                                    timeout=60) as r:
            return json.loads(r.read())

    for name, path in (("observatory", "/observatory"),
                       ("governance", "/governance"),
                       ("sentences", "/sentences"),
                       ("brain", "/brain"),
                       ("desk", "/desk"),
                       # the mini-dive doors (2026-08-19): the pulse's
                       # happening-now/standing-next/allocation, and the
                       # spacetime window's universe-wide lanes (52 days =
                       # the slider's first light, so the photograph's
                       # opening frame tells the truth)
                       ("pulse", "/pulse"),
                       ("spacetime", "/spacetime?days=52"),
                       # the era-0.58/0.59 doors (2026-08-21): the stable's
                       # five-eyed market, the allocation ledgers, and the
                       # farm's seed catalog — the photograph shows a real
                       # answer for every pane's opening frame
                       ("market", "/market?limit=60"),
                       ("assign", "/assign"),
                       ("seeds", "/seeds?q=search")):
        try:
            (fx / f"{name}.json").write_text(json.dumps(get2(path)))
            print(f"  captured :4562{path} → fixtures/{name}.json")
        except Exception as e:
            print(f"  ({path} did not answer — {e}; the room shows its honest miss)")
    try:
        landing = json.loads((fx / "desk.json").read_text())
        specialists = []
        for w in landing.get("worlds", []):
            key = w.get("key")
            if not key:
                continue
            (fx / f"desk-{key}.json").write_text(
                json.dumps(get2(f"/desk?key={key}")))
            print(f"  captured world «{key}»")
            if w.get("resident"):
                specialists.append(str(w["resident"]).lower())
        pres = json.loads((fx / "presence.json").read_text())
        names = [str(r.get("name", "")).lower()
                 for r in pres.get("residents", []) if r.get("name")]
        for n in sorted(set(names + specialists)):
            try:
                (fx / f"resident-{n}.json").write_text(
                    json.dumps(get2(f"/resident?name={n}")))
                print(f"  captured room «{n}»")
            except Exception:
                pass
    except Exception as e:
        print(f"  (the worlds/rooms sweep stumbled: {e})")

    at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    # the baked cfg drives lanes/tiers only; the token is a stone — nothing serves it
    cfg = {"token": "spectator", "requester": "spectator", "requester_scope": SCOPE,
           "tiers": [SCOPE, "u:demo/e:cloud", "u:demo"]}
    inject = ("<script>window.ORRETH_DEMO=" + json.dumps({"at": at}) +
              ";window.ORRETH_DEMO_CFG=" + json.dumps(cfg) + "</script>\n<script>")
    html = WINDOW.read_text()
    assert html.count("<script>") == 1, "window.html grew a second script block — update the injector"
    (OUT / "index.html").write_text(html.replace("<script>", inject, 1))
    print(f"\n  the moment is captured — {OUT}/index.html · recorded {at}")
    print("  preview:  python3 -m http.server -d site 8080  →  http://localhost:8080")


if __name__ == "__main__":
    main()
