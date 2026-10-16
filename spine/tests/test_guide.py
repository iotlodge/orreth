# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — the guide held to the glass (JB's law 2026-10-06: the guide turns with every word the glass learns or stops hearing) · 2026-10-06
# Amended: Claude Fable 5.1 (claude-fable-5-1) — THE WIZARD's words (new agent · make an agent · open the wizard) · 2026-10-12
"""THE GUIDE NEVER DRIFTS FROM THE GLASS (JB, 2026-10-06, after the sp2 walk: "ensure that it
remains updated so it doesn't drift too far from what we know we can do").

`spine/guide/guide.v0.json` is what a newcomer trusts — the same words on every door. Every
"say" line that is a COMMAND the glass parses (a word the chat catches before any body hears it)
must still be caught by one of the glass's parsers; a line the glass stopped hearing is drift.
The parsers are the anchored regexes in `spine/glass/index.html`; most compile under Python's
`re` (the JS-only ones are skipped and counted, never silently). A line in parentheses is a
click or a form, a terminal command or a dial is not the chat's, and free words to a body
(“what is the temperature outside?”) are the body's to answer — none of those are checked here.
The COMMAND lines are recognised by their opening words (the list below grows with the glass)."""
import json
import re
from pathlib import Path

SPINE = Path(__file__).resolve().parents[1]
GUIDE = SPINE / "guide" / "guide.v0.json"
GLASS = SPINE / "glass" / "index.html"

# the opening words of a line the GLASS catches (not a body) — grown with each spoonful
COMMAND_HEADS = (
    "show ", "what services", "what tools", "what minds", "what llms", "which services", "check the ", "retire ", "restore ",
    "toolkeeper, add", "stablekeeper, add", "assign ", "unassign ", "refill ", "restart the ", "advance past",
    "stop the kernel", "restart intention", "my seat", "who am i seated", "leave my seat", "enroll ", "who is at the door",
    "my name is", "call me ", "i live in", "my place is", "my time zone", "my clock is", "remember about me", "what do you know about me",
    "show my profile", "who am i", "forget ", "list my sessions", "new session", "export compliance", "summon ", "guide", "help",
    "tour", "show me around", "what am i looking at", "what world is this", "re-home ", "what levels", "open floor", "open room",
    "who wears", "what is ", "my drafts", "draft a", "draft an", "cut the", "discard the", "thought:", "objective:",
    "librarian's fuel", "echo, every", "propose a watch", "watch for",
    "open the workshop", "close the workshop", "load ", "workshop,",            # Phase 8 sp3: THE WORKSHOP
    "promote ", "decline the ", "rest ", "decommission ",                       # Phase 8 sp4: THE EXPERIMENT AND THE CUT
    "dismiss ", "register the source",                                           # Phase 8 sp5: THE OPERATING STATE
    "new agent", "make an agent", "open the wizard",                             # THE WIZARD (JB's lock 2026-10-12)
    "close the draft", "clear the workshop",                                     # W127: the first screen again (JB, 2026-10-12)
    "open the ", "resume the ", "my benches", "let the ", "close the ",          # Phase 8 sp8 THE BENCH (canon 0011)
    "how the kernel", "how does the kernel", "the map",                         # THE STUDIO sp9c: HOW THE KERNEL WORKS (canon 0011 §4c)
    "put ",                                                                     # THE STUDIO sp10: ONE WORD TO WORK (canon 0011 §5)
)
# lines the glass hears through a body or a door, not a parser — named, never silently skipped
BODY_OR_DOOR = (
    "what is the temperature outside", "what is echo made of",     # the second IS a parser; listed here only as a reminder that "what is " is wide
    "between 9am and noon", "follow up on this", "librarian, remember", "what do you remember", "librarian@two",
    "expected impact", "run the harness", "keep this world resilient", "propose a watch that", "watch for asks left waiting",
    "schedule an ask", "cancel", "yes — do it", "take my seat", "enroll",
    "librarian, forget",                                             # the librarian's purge, held at the interlock — a body's word
)


def _parsers() -> tuple[list[re.Pattern], int]:
    html = GLASS.read_text("utf-8")
    out, skipped = [], 0
    for m in re.finditer(r"/((?:\\/|\[[^\]]*\]|[^/\n])+)/([gimsuy]*)(?=[\s.),;])", html):
        src, flags = m.group(1), m.group(2)
        if not src.startswith("^") or len(src) < 4:
            continue
        try:
            out.append(re.compile(src, re.I if "i" in flags else 0))
        except re.error:
            skipped += 1
    return out, skipped


def _lines():
    g = json.loads(GUIDE.read_text("utf-8"))
    for s in g["sections"]:
        for e in s["entries"]:
            for say in str(e["say"]).split(" · "):
                say = say.strip()
                if not say or say.startswith("(") or "scripts/" in say or "SPINE_" in say or say.isupper():
                    continue
                yield s["id"], say


def test_every_command_the_guide_teaches_is_still_heard_by_the_glass():
    parsers, skipped = _parsers()
    assert len(parsers) > 60, f"the glass's parsers were not found ({len(parsers)} compiled, {skipped} JS-only)"
    drift = []
    checked = 0
    for sid, say in _lines():
        t = re.sub(r"[.!?]+$", "", say.lower()).strip()
        if any(t.startswith(b) for b in BODY_OR_DOOR) and t != "what is echo made of":
            continue
        if not any(t.startswith(h) for h in COMMAND_HEADS):
            continue
        checked += 1
        if not any(p.search(t) for p in parsers):
            drift.append(f"[{sid}] {say}")
    assert checked >= 40, f"too few command lines checked ({checked}) — the heads list drifted from the guide"
    assert not drift, "the guide teaches words the glass no longer hears:\n  " + "\n  ".join(drift)


def test_the_guide_reads_whole():
    g = json.loads(GUIDE.read_text("utf-8"))
    assert g["format"] == "orreth-guide/1" and g["sections"]
    ids = [s["id"] for s in g["sections"]]
    assert len(ids) == len(set(ids)), "a section id repeats"
    for s in g["sections"]:
        assert s.get("when") in ("chat", "crew", "monitor", "band", "workshop"), f"section {s['id']}: `when` names the pull it stands in"
        assert s.get("title") and s.get("lead") and s.get("entries"), f"section {s['id']} is whole: title, lead, entries"
        for e in s["entries"]:
            assert e.get("say") and e.get("does"), f"section {s['id']}: every entry says and does"
