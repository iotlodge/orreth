# PROVENANCE: Fable 5 (claude-fable-5) — 0052, quinn's browser eyes · 2026-08-12
"""quinn-web — the newcomer looks at the REAL rendered glass.

JB's ask, verbatim: "ensure that when you do the UAT agent they look at
things like this" — layout, redundancy, tiny inputs, inconsistent
placement: the class of wound only a rendered page can show. quinn's wire
walker (run.py) judges what the cards SAY; this walker judges what the
room LOOKS LIKE: headless Chrome renders each Console view, her persona
judges the screenshot through a governed, metered vision thought (her own
DID, her own lease — an eye is metered like a thought), and the whole
list lands as ONE uat-report at the architect's queue.

v1 is view-level (no clicking yet — the click-flow walk is the named next
step). Requires Google Chrome on the host; no new browser downloads.

    uv run --with litellm --with cryptography python agents/flavors/04-uat/web.py --once
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

from orreth_agent.chassis import GovernedThink          # noqa: E402
from orreth_agent.client import FieldClient             # noqa: E402
from orreth_agent.craft import acquire                  # noqa: E402

UNIVERSE = "http://localhost:4500"
FIELD = "http://localhost:4502"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VIEWS = [("inbox", "the Inbox — everything waiting on the human"),
         ("obj", "the Objectives ledger — composing and reading reports"),
         ("uni", "the Universe view — the orrery and the world rail"),
         ("gov", "the Governance room — the machine's craft on its shelf"),
         ("farm", "the Farm — tools and services"),
         ("stable", "the Stable — minds and models"),
         ("pulse", "the Pulse"), ("obs", "the Observatory")]


def capability_views() -> list:
    """Her eye follows DISCOVERY (0055): the landing plus every installed
    world, read from the portal's own door — a dropped folder is under
    the UAT walk from birth, and nothing is ever hardcoded again."""
    views = [("obs&cap=1", "the Capabilities landing — the portal of worlds atop Orreth")]
    try:
        with urllib.request.urlopen("http://localhost:4562/desk", timeout=8) as r:
            for w in json.load(r).get("worlds", []):
                if w.get("retired"):
                    continue
                views.append((f"obs&cap=1&capw={w['key']}",
                              f"{w.get('name', w['key'])} — a world's rooms from its manifest"))
    except Exception:
        pass
    return views


# 0064 — THE OPEN BOOK: the public documentation is a first-contact surface
# too, so the stranger walks it with the same eyes. Absolute URLs; the live
# site, exactly as a stranger reaches it.
BOOK = "https://docs.orreth.ai"
BOOK_VIEWS = [
    ("/", "the documentation landing — 'What is Orreth', a stranger's very first page"),
    ("/learn/anatomy/", "the anatomy page — what exists when Orreth runs"),
    ("/learn/what-works-today/", "the honest register — proven vs partial vs not-yet"),
    ("/learn/glossary/", "the glossary — the machine's own dictionary as a docs page"),
    ("/build/quickstart/", "the quickstart — ten minutes to a running world"),
    ("/build/first-world/", "the first-world tutorial — a universe from three files"),
    ("/reference/http-api/", "the HTTP API reference — every door of a running world"),
]


def _post(base: str, path: str, payload: dict) -> dict:
    req = urllib.request.Request(base + path, method="POST",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.load(r)


def shoot(view: str, url: str | None = None) -> str | None:
    """One view, rendered by real Chrome, returned as base64 PNG. The
    universe view animates forever, so virtual time never settles there —
    the second attempt shoots without it (her first walk's own finding).
    An absolute url overrides the console route (the book walk, 0064)."""
    out = Path(tempfile.mkdtemp()) / f"{view.replace('/', '_') or 'root'}.png"
    for budget in ("--virtual-time-budget=9000", None):
        args = [CHROME, "--headless=new", f"--screenshot={out}",
                "--window-size=1512,900", "--hide-scrollbars",
                "--disable-gpu"]
        if budget:
            args.append(budget)
        args.append(url or f"{UNIVERSE}/window#f=4500&v={view}")
        try:
            subprocess.run(args, capture_output=True, timeout=45)
            if out.exists() and out.stat().st_size > 10000:
                return base64.b64encode(out.read_bytes()).decode()
        except Exception as e:
            print(f"· the eye blinked on «{view}» ({'timed' if budget else 'plain'}): {e}")
    return None


def judge(think: GovernedThink, persona: str, shot_b64: str,
          context: str) -> list[str] | None:
    """The persona looks at the picture — a governed, metered vision
    thought. A refusal or an unparseable reply returns None — A MUTE IS
    NEVER A CLEAN ROOM (the 2026-08-25 verify walk printed a network
    refusal as «0 friction(s)», indistinguishable from a spotless view);
    only a PARSED empty list may say the room read clean."""
    prompt = (persona.replace("⟦surface⟧", "(the attached SCREENSHOT of the "
              "screen — judge the LAYOUT and the EXPERIENCE: crowding, "
              "redundancy, inconsistent placement of inputs and buttons, "
              "tiny fields, anything that would make a newcomer bounce or "
              "squint)").replace("⟦context⟧", context))
    try:
        raw = think("medium", prompt, content=[
            {"type": "text", "text": prompt},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{shot_b64}"}}])
    except Exception as e:
        print(f"· the mind refused the picture: {e}")
        return None
    import re
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return None
    try:
        got = json.loads(m.group(0))
        return [str(x)[:220] for x in (got.get("frictions") or [])][:6]
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--book", action="store_true",
                    help="walk the public documentation (docs.orreth.ai) "
                         "instead of the console")
    args = ap.parse_args()
    if not Path(CHROME).exists():
        print("no Chrome on this host — quinn-web has no eyes here")
        return 1
    client = FieldClient(FIELD, "quinn", role="workforce")
    print(f"· quinn-web is {client.did[:28]}… — the same self, now with eyes")
    client.join()
    print(f"· lease held on {client.scope} — looking at the real glass")
    think = GovernedThink(client, max_tokens=700)
    persona = acquire("uat-persona-quinn", did=client.did).text or ""
    findings: list[str] = []
    walk = ([(p, c) for p, c in BOOK_VIEWS] if args.book
            else [*VIEWS, *capability_views()])
    for view, ctx in walk:
        shot = shoot(view, url=(BOOK + view) if args.book else None)
        if not shot:
            findings.append(f"[{view}] the view would not render for the eye "
                            "— itself a finding")
            continue
        fr = judge(think, persona, shot, ctx)
        if fr is None:                     # a mute, confessed — never a clean room
            findings.append(f"[{view}] the eye saw but no verdict came back "
                            "— a refusal or an unreadable reply, NOT a clean room")
            print(f"· quinn looked at «{view}»: NO VERDICT — a mute, not a clean room")
            continue
        print(f"· quinn looked at «{view}»: {len(fr)} friction(s)")
        for x in fr:
            print(f"   · {x}")
        findings.extend(f"[{view}] {x}" for x in fr)
        time.sleep(1)
    body = " · ".join(findings) or "no frictions — the rooms read clean"
    if len(body) > 3800:                       # the card has edges; the cut confesses
        body = body[:3680] + " · (…the card's edge cut the tail — the FULL list "
        body += "is in the walker's own log, every line printed as found)"
    surface = ("the public book (docs.orreth.ai)" if args.book
               else "the console's rooms")
    out = _post(UNIVERSE, "/requests",
                {"kind": "uat-report", "text": f"👁 quinn-web walked "
                 f"{len(walk)} pages of {surface} with real eyes — {len(findings)} "
                 f"friction(s): {body}"})
    print(f"· the report stands: {out.get('id')} — {len(findings)} finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
