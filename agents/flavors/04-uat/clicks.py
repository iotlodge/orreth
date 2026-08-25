# PROVENANCE: Fable 5 (claude-fable-5) — quinn v2, the click-flow walk · 2026-08-25
"""quinn-clicks — the newcomer's HANDS (0060's remaining half).

Her view walker (web.py) judges what a room LOOKS like; this walker judges
what a click DELIVERS: the class of wound only interaction can show — dead
doors, clicks whose result betrays their words, panes that never open. The
same self re-joins (one DID, one meter); every judged flow is one governed
vision thought under her lease, and THE MUTE LAW holds: a refusal or an
unreadable reply confesses — only a parsed verdict may speak.

The hands are the host's own Chrome driven over CDP (playwright connects to
the running browser — no new browser downloads, the standing constraint).
A mechanical truth (did the pane open?) is asserted in code BEFORE her eye
is spent; a dead door is a finding all by itself, and the gravest kind.

    uv run --with litellm --with cryptography --with playwright \
        python agents/flavors/04-uat/clicks.py --once
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
CDP_PORT = 9339


def _post(base: str, path: str, payload: dict) -> dict:
    req = urllib.request.Request(base + path, method="POST",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.load(r)


def judge(think: GovernedThink, persona: str, shot_b64: str,
          context: str) -> list[str] | None:
    """Her eye on the AFTER-state of a click — a governed vision thought.
    None is a mute, never a clean flow (the 0060 verify-walk law)."""
    prompt = (persona.replace("⟦surface⟧", "(the attached SCREENSHOT shows "
              "the screen JUST AFTER your click — judge whether the click "
              "DELIVERED what its words promised: did the right thing open, "
              "does what opened explain itself, and would a newcomer know "
              "what to do next?)").replace("⟦context⟧", context))
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


def open_view(page, view: str, settle_ms: int = 6000):
    page.goto(f"{UNIVERSE}/window#f=4500&v={view}")
    page.wait_for_timeout(settle_ms)


def shot(page) -> str:
    return base64.b64encode(page.screenshot()).decode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.parse_args()
    if not Path(CHROME).exists():
        print("no Chrome on this host — quinn has no hands here")
        return 1
    client = FieldClient(FIELD, "quinn", role="workforce")
    print(f"· quinn-clicks is {client.did[:28]}… — the same self, now with hands")
    client.join()
    print(f"· lease held on {client.scope} — walking the flows")
    think = GovernedThink(client, max_tokens=700)
    persona = acquire("uat-persona-quinn", did=client.did).text or ""

    # the host's own Chrome, opened for driving — no new browser downloads
    prof = tempfile.mkdtemp()
    chrome = subprocess.Popen(
        [CHROME, "--headless=new", f"--remote-debugging-port={CDP_PORT}",
         f"--user-data-dir={prof}", "--window-size=1512,900",
         "--hide-scrollbars", "--disable-gpu", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):                      # wait for the CDP door
        try:
            urllib.request.urlopen(
                f"http://localhost:{CDP_PORT}/json/version", timeout=1)
            break
        except Exception:
            time.sleep(0.5)

    findings: list[str] = []
    walked = 0

    def mechanical(flow: str, truth: str):
        findings.append(f"[{flow}] THE CLICK DID NOT DELIVER — {truth} "
                        "(a dead door is the gravest friction)")
        print(f"· «{flow}»: DEAD DOOR — {truth}")

    def judged(flow: str, page, ctx: str):
        fr = judge(think, persona, shot(page), ctx)
        if fr is None:
            findings.append(f"[{flow}] the hand clicked true but no verdict "
                            "came back — a mute, never a clean flow")
            print(f"· «{flow}»: NO VERDICT — a mute, not a clean flow")
            return
        print(f"· quinn walked «{flow}»: {len(fr)} friction(s)")
        for x in fr:
            print(f"   · {x}")
        findings.extend(f"[{flow}] {x}" for x in fr)

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(
                f"http://localhost:{CDP_PORT}")
            ctx = browser.contexts[0] if browser.contexts \
                else browser.new_context()
            page = ctx.new_page()

            # ── flow 1 · THE DICTIONARY DOOR (0060's closing measure) ──
            walked += 1
            open_view(page, "inbox")
            gw = page.locator(".gw").first
            if gw.count() and gw.is_visible():
                word = gw.inner_text()
                gw.click()
                page.wait_for_timeout(600)
                if page.locator("#glosscard").is_visible():
                    judged("dictionary-door", page,
                           f"you clicked the dotted word «{word}» — a small "
                           "card opened claiming to define it. Is the "
                           "definition plain enough to actually teach you?")
                else:
                    mechanical("dictionary-door",
                               f"the dotted word «{word}» was clicked and no "
                               "definition card appeared")
            else:
                mechanical("dictionary-door",
                           "no dotted dictionary word was on the screen at all")

            # ── flow 2 · THE WELCOME DISMISSAL (mechanical, no eye spent) ──
            walked += 1
            open_view(page, "uni", settle_ms=4000)
            wl = page.locator("#welcome .lnk").first
            if wl.count() and wl.is_visible():
                wl.click()
                page.wait_for_timeout(300)
                if page.locator("#welcome").is_visible():
                    mechanical("welcome-dismiss",
                               "«got it» was clicked and the band stayed")
                else:
                    open_view(page, "inbox", settle_ms=3000)
                    if page.locator("#welcome").is_visible():
                        mechanical("welcome-dismiss",
                                   "the dismissal did not survive a reload — "
                                   "the band forgot the human's word")
                    else:
                        print("· «welcome-dismiss»: clean — dismissed, and "
                              "the word survived a reload")
            else:
                mechanical("welcome-dismiss", "the welcome band never showed "
                           "for a fresh visitor")

            # ── flow 3 · THE LENS (the librarian, one click away) ──
            walked += 1
            open_view(page, "obj", settle_ms=4000)
            lens = page.locator("#lens")
            if lens.count() and lens.is_visible():
                lens.click()
                page.wait_for_timeout(4000)   # her calling card takes a beat
                if "on" in (page.locator("#parlor").get_attribute("class") or ""):
                    judged("the-lens", page,
                           "you clicked the glowing «ask the librarian» pill "
                           "— her audience opened on the right. Could you "
                           "tell who she is and how to ask her something?")
                else:
                    mechanical("the-lens", "the lens was clicked and no "
                               "audience opened")
            else:
                mechanical("the-lens", "the lens pill was not on the screen")

            # ── flow 4 · A RESIDENT'S ROOM (the ⚙ beside a name) ──
            walked += 1
            open_view(page, "pulse", settle_ms=5000)
            door = page.locator(".roomdoor").first
            if door.count():
                door.click()
                page.wait_for_timeout(2500)
                if "on" in (page.locator("#rsm-back").get_attribute("class") or ""):
                    judged("resident-room", page,
                           "you clicked the small ⚙ beside a resident's name "
                           "— their room opened as a card with tabs. Does it "
                           "tell you who this is and what you can do here?")
                    page.keyboard.press("Escape")
                else:
                    mechanical("resident-room",
                               "the ⚙ room door was clicked and no room opened")
            else:
                mechanical("resident-room", "no resident wore a room door")

            # ── flow 5 · THE CRAFT SHELF (a word opens to be read) ──
            walked += 1
            open_view(page, "gov", settle_ms=5000)
            row = page.locator(".gvrow").first
            if row.count():
                name = row.inner_text().split("\n")[0][:40]
                row.click()
                page.wait_for_timeout(2000)
                hidden = "hide" in (page.locator("#gov-read")
                                    .get_attribute("class") or "")
                if not hidden:
                    judged("craft-shelf", page,
                           f"you clicked «{name}» on the machine's shelf — "
                           "its full text opened on the right. Can you tell "
                           "what this word is for and whether you may edit it?")
                else:
                    mechanical("craft-shelf",
                               f"«{name}» was clicked and nothing opened")
            else:
                mechanical("craft-shelf", "the shelf showed no words at all")

            # ── flow 6 · STEP ONTO A FLOOR (the rail's one promise) ──
            walked += 1
            open_view(page, "inbox", settle_ms=4000)
            row = page.locator(".trow.t2:not(.me):not(.up)").first
            if row.count():
                stepped = row.inner_text().split("\n")[0].strip()[:24]
                row.dispatch_event("pointerdown", {"button": 0})
                page.wait_for_timeout(5000)
                pulse = page.locator("#hpulse").inner_text()
                if stepped and stepped.split()[0] in pulse:
                    print(f"· «floor-step»: clean — clicked «{stepped}» and "
                          f"the header now names it")
                else:
                    mechanical("floor-step",
                               f"clicked «{stepped}» but the header still "
                               f"says «{pulse.splitlines()[0] if pulse else '?'}» "
                               "— the step went nowhere a newcomer can see")
            else:
                mechanical("floor-step", "the rail held no floor to step onto")

            page.close()
    finally:
        chrome.terminate()

    body = " · ".join(findings) or ("every walked flow delivered — the doors "
                                    "open where their words point")
    if len(body) > 3800:
        body = body[:3680] + " · (…the card's edge cut the tail — the FULL "
        body += "list is in the walker's own log, every line printed as found)"
    out = _post(UNIVERSE, "/requests",
                {"kind": "uat-report", "text": f"🖱 quinn-clicks walked "
                 f"{walked} flow(s) with real hands — {len(findings)} "
                 f"finding(s): {body}"})
    print(f"· the report stands: {out.get('id')} — {len(findings)} finding(s) "
          f"across {walked} flow(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
