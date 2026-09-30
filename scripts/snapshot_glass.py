#!/usr/bin/env python3
# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — THE SPECTATOR: the panel's photograph for demo.orreth.ai
#             (the refresh season's step 3, JB 2026-09-30); the 0.72 Console's snapshot_console.py rests in archive/
"""Capture a moment of a live kernel as a static, view-only PANEL.

Reads every door the glass reads — with a REAL seat, used here and never shipped —
records some minutes of the feed, and writes a self-contained site:

    site/index.html          the glass with `window.ORRETH_DEMO` injected (spectator mode)
    site/fixtures/<door>.json  one file per captured door, named by its path and query
                               (`/sessions?person=jb` → `sessions~person-jb.json`;
                                `/ask/ask_12` → `ask__ask_12.json`)
    site/fixtures/feed.json    the captured minutes of the feed, replayed on a loop

Nothing of the kernel ships: no seat, no key, no endpoint. A sweep refuses to write a
site whose fixtures carry a key-shaped secret.

    ORRETH_SEAT='<the seat wire>' python3 scripts/snapshot_glass.py [--kernel http://127.0.0.1:4600]
        [--out site] [--feed-seconds 150] [--sessions 3] [--asks 120]

The seat: take yours in the glass, then copy localStorage["orreth.seat"] from the browser.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLASS = ROOT / "spine/glass/index.html"

# every GET the glass makes on its own (the keyed doors are harvested from these answers)
STILL = ["/health", "/seat", "/guide", "/world", "/crew", "/monitor", "/analyzer", "/bodies",
         "/minds", "/services", "/markers", "/markers/kinds", "/intentions", "/levers",
         "/harness", "/asks", "/residents", "/parked"]
PERSONAL = ["/profile?person={p}", "/proof?person={p}", "/sessions?person={p}", "/mitl?person={p}&session="]

SECRET_SHAPES = re.compile(r"(sk-ant-|sk-or-|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[abp]-|-----BEGIN)")


def fixture_name(path: str) -> str:
    """One name per door, the same law as the glass's `fixture()`: safe on any bucket (no `/` `?` `&` `=` `:` `%`)."""
    p = re.sub(r"[/?&=]", lambda m: {"/": "__", "?": "~", "&": "~", "=": "-"}[m.group()], urllib.parse.unquote(path.lstrip("/")))
    return re.sub(r"[^A-Za-z0-9._~-]", "_", p) + ".json"


class Kernel:
    def __init__(self, base: str, seat: str):
        self.base, self.seat = base.rstrip("/"), seat

    def get(self, path: str, timeout: int = 20) -> tuple[int, str]:
        req = urllib.request.Request(self.base + path, headers={"authorization": "Bearer " + self.seat})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode(errors="replace")


def seat_person(wire: str) -> tuple[str, bool]:
    pad = wire + "=" * (-len(wire) % 4)
    t = json.loads(base64.urlsafe_b64decode(pad))
    governs = any(g.get("action") == "govern" for g in t.get("grants", []) if isinstance(g, dict))
    return t["subject"], governs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kernel", default="http://127.0.0.1:4600")
    ap.add_argument("--out", default=str(ROOT / "site"))
    ap.add_argument("--feed-seconds", type=int, default=150)
    ap.add_argument("--sessions", type=int, default=3, help="the newest N sessions captured whole (0: the chat opens empty)")
    ap.add_argument("--asks", type=int, default=120, help="at most N asks read through /ask/<id>")
    a = ap.parse_args()
    seat = os.environ.get("ORRETH_SEAT", "").strip()
    if not seat:
        print("ORRETH_SEAT is empty — take a seat in the glass and copy localStorage[\"orreth.seat\"]", file=sys.stderr)
        return 2
    person, governs = seat_person(seat)
    k = Kernel(a.kernel, seat)
    st, _ = k.get("/crew")
    if st == 401:
        print("the seat is not accepted (401) — expired, left, or from another ground", file=sys.stderr)
        return 2

    out = Path(a.out).resolve(); fx = out / "fixtures"; fx.mkdir(parents=True, exist_ok=True)
    for old in fx.glob("*.json"):
        old.unlink()
    captured: dict[str, str] = {}

    def capture(path: str, quiet: bool = False) -> str | None:
        if path in captured:
            return captured[path]
        st, body = k.get(path)
        if st != 200:
            if not quiet:
                print(f"  {path} → {st} (not in the photograph)")
            return None
        (fx / fixture_name(path)).write_text(body)
        captured[path] = body
        if not quiet:
            print(f"  {path} → fixtures/{fixture_name(path)}")
        return body

    at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print(f"the still panel — every door, as {person}{' (governs)' if governs else ''}")
    for p in STILL:
        capture(p)
    for p in PERSONAL:
        capture(p.format(p=urllib.parse.quote(person)))

    # the feed: its captured minutes, each notice with the moment it arrived
    print(f"the feed — {a.feed_seconds}s of notices")
    events: list[dict] = []
    req = urllib.request.Request(f"{a.kernel}/feed?seat={urllib.parse.quote(seat)}", headers={"accept": "text/event-stream"})
    t0 = time.monotonic(); name = None; data: list[str] = []
    try:
        with urllib.request.urlopen(req, timeout=a.feed_seconds + 5) as r:
            while time.monotonic() - t0 < a.feed_seconds:
                line = r.readline()
                if not line:
                    break
                line = line.decode().rstrip("\n")
                if line.startswith(":"):
                    continue
                if line.startswith("event:"):
                    name = line[6:].strip()
                elif line.startswith("data:"):
                    data.append(line[5:].strip())
                elif line == "" and data:
                    events.append({"t": int((time.monotonic() - t0) * 1000), "event": name, "data": "\n".join(data)})
                    name = None; data = []
    except Exception as e:  # the stream closed or timed out — what was heard is the photograph
        print(f"  (the feed closed: {e})")
    (fx / "feed.json").write_text(json.dumps({"at": at, "seconds": a.feed_seconds, "events": events}))
    print(f"  {len(events)} notices → fixtures/feed.json")

    # the keyed doors, harvested from every answer so far: asks · facts · sessions · analyzer roots · markers · minds · services · schedules
    print("the keyed doors")
    text = "\n".join(captured.values()) + "\n".join(e["data"] for e in events)
    sessions = json.loads(captured.get(f"/sessions?person={urllib.parse.quote(person)}", '{"sessions": []}')).get("sessions", [])
    kept = sessions[: a.sessions]
    (fx / fixture_name(f"/sessions?person={urllib.parse.quote(person)}")).write_text(json.dumps({"sessions": kept}))
    for s in kept:
        body = capture(f"/session/{s['session_id']}")
        if body:
            text += body
    ask_ids = list(dict.fromkeys(re.findall(r"\bask_[0-9a-f]{8,16}\b", text)))
    for aid in ask_ids[-a.asks:]:
        capture(f"/ask/{aid}", quiet=True)
    print(f"  {min(len(ask_ids), a.asks)} of {len(ask_ids)} asks")
    msg_ids = list(dict.fromkeys(re.findall(r"\bmsg_[0-9a-f]{24}\b", "\n".join(e["data"] for e in events))))
    for mid in msg_ids:
        capture(f"/fact/{mid}", quiet=True)
    print(f"  {len(msg_ids)} facts the feed points at")
    for root in {o.get("root") for o in json.loads(captured.get("/analyzer", "{}")).get("origins", []) if isinstance(o, dict) and o.get("root")}:
        capture(f"/analyzer?origin={urllib.parse.quote(str(root))}", quiet=True)
    for mk in sorted(set(re.findall(r"\bmk_[0-9a-f]{12}\b", text))):
        capture(f"/markers?from={mk}", quiet=True)
    for m in json.loads(captured.get("/minds", "{}")).get("minds", []):
        if isinstance(m, dict) and m.get("name"):
            capture(f"/minds/fuel?name={urllib.parse.quote(str(m['name']))}", quiet=True)
    for kind in {s.get("kind") for s in json.loads(captured.get("/services", "{}")).get("services", []) if isinstance(s, dict) and s.get("kind")}:
        capture(f"/services?kind={urllib.parse.quote(str(kind))}", quiet=True)
    for c in json.loads(captured.get("/crew", "{}")).get("crew", []):
        if isinstance(c, dict) and c.get("name"):
            capture(f"/schedules/{urllib.parse.quote(str(c['name']))}", quiet=True)
    for s in kept:
        capture(f"/mitl?person={urllib.parse.quote(person)}&session={s['session_id']}", quiet=True)
    print(f"  {len(captured)} doors in the photograph")

    # the sweep: a key-shaped secret anywhere in the fixtures stops the press
    hits = [f.name for f in fx.glob("*.json") if SECRET_SHAPES.search(f.read_text())]
    if hits or seat in text:
        print(f"REFUSED — a secret shape in the fixtures: {hits or ['the seat wire itself']}", file=sys.stderr)
        return 3

    # the page: the glass with the spectator's word injected before its main script
    world = json.loads(captured.get("/world", "{}"))
    demo = {"at": at, "person": person, "governs": governs,
            "world": world.get("world") or world.get("scope") or json.loads(captured.get("/health", "{}")).get("world"),
            "refusal": "a spectator may watch this world turn, not move it — this page is a photograph of a kernel that ran; run your own from the book"}
    html = GLASS.read_text()
    assert html.count("\n<script>\n") == 1, "the glass's main <script> is not where the injector expects — update snapshot_glass.py"
    html = html.replace("\n<script>\n", "\n<script>window.ORRETH_DEMO=" + json.dumps(demo) + "</script>\n<script>\n", 1)
    (out / "index.html").write_text(html)
    print(f"\nthe moment is captured — {out}/index.html · {at} · as {person}")
    print(f"preview:  python3 -m http.server -d {out} 8080  →  http://localhost:8080")
    return 0


if __name__ == "__main__":
    sys.exit(main())
