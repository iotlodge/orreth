# PROVENANCE: Fable 5 (claude-fable-5) — 0020, the Parlor · 2026-07-07
"""The Parlor (0020): the audience room — humans ask; residents fetch.

Agents, when authorized, see data inside the universe. Humans never do: a human's
only read is an ask, received by a resident who fetches with its OWN authority and
answers on the record. This module is the parlor's brain — the calling cards
residents publish, the grounded answers they compose from state they may read, and
the audience body that lands every exchange signed in the spacetime window.

Decoupling is the card, not the code: the Console renders whatever asks a card
declares; a new resident with new flows changes nothing in the glass.
"""
from __future__ import annotations

import re

from . import markers, profile
from .identity import NOW

RESIDENTS = ("becky", "vigil", "steward", "governance", "charlotte", "librarian", "ada")
EMBODIED = ("becky", "charlotte", "librarian", "ada")   # hold keys; sign their audiences

ROLES = {"becky": "becky · IAM", "vigil": "vigil · the Warden",
         "steward": "steward · memory", "governance": "governance",
         "charlotte": "charlotte · farm keeper", "librarian": "librarian · knowledge",
         "ada": "ada · the wrangler"}

# the librarian's gather ask, in the shapes callers actually type
_GATHER = ("gather sourced knowledge on", "gather knowledge on", "gather on", "gather")

# the self-dialog (0023 §3), in the shapes callers actually type: the librarian asks
# HERSELF at every other seat — same mind, each floor's key, answers composed with
# per-seat provenance and an honest horizon
_ASK_SEATS = ("ask the universe about", "ask your seats about", "ask my seats about",
              "ask the universe")

# growing the universe, in the shapes callers actually type (the Shipyard)
_GROW = ("create ecosystem", "add ecosystem", "grow ecosystem", "new ecosystem",
         "build ecosystem")


def parse_grow(text: str):
    """“create ecosystem foo with fields bar, baz” → (name, fields|None).
    fields is None when the caller has not said — the parlor asks before staging;
    an explicit “no fields” / “as is” / “alone” sails the hull by itself."""
    t = (text or "").strip()
    low = t.lower()
    for p in _GROW:
        if not low.startswith(p):
            continue
        rest = t[len(p):].strip().strip(".!?")
        if not rest:
            return "", None
        lower = rest.lower()
        for marker in (" with fields ", " with field "):
            if marker in lower:
                i = lower.index(marker)
                name = rest[:i].strip()
                fields = [f.strip().lower() for f in
                          re.split(r"[,\s]+and\s+|,", rest[i + len(marker):]) if f.strip()]
                return name.lower(), fields
        for solo in (" with no fields", " no fields", " as is", " alone"):
            if lower.endswith(solo):
                return rest[: len(rest) - len(solo)].strip().lower(), []
        return rest.split()[0].lower(), None
    return None


def _vitals(facts: dict, name: str) -> dict:
    for r in facts.get("residents") or []:
        if r.get("name") == name:
            return r.get("vitals") or {}
    return {}


def _farm(facts: dict) -> list[dict]:
    return [s for s in facts.get("farm") or [] if s.get("state") != "decommissioned"]


def _stalls(facts: dict) -> list[dict]:
    return [s for s in facts.get("stalls") or [] if s.get("state") != "sunset"]


# ---------------------------------------------------------------- the calling cards

def card(name: str, facts: dict) -> dict:
    """A resident's calling card: greeting + the asks it offers, as data. `ask`
    sends as-is; `template` prefills the caller's input. The glass renders blind."""
    scope = facts.get("scope", "")
    if name not in RESIDENTS:
        return {"resident": name, "scope": scope, "asks": [],
                "greeting": f"no one by the name “{name}” is in residence on this floor."}
    greeting, asks = _CARDS[name](facts)
    return {"resident": name, "scope": scope, "role": ROLES[name],
            "voiced": name in EMBODIED, "greeting": greeting, "asks": asks}


def _card_becky(facts: dict) -> tuple[str, list]:
    done = [r for r in facts.get("requests") or []
            if r.get("kind") == "join" and r.get("status") == "done"]
    return (f"I keep the door. Every identity here chains to the root I hold — "
            f"{len(done)} lease(s) granted so far, nothing joins without one. I can also "
            "grow this universe: ask me for a new ecosystem, and the shipyard lays a hull.",
            [{"label": "who holds a lease?", "ask": "who holds a lease on this floor?"},
             {"label": "how does joining work?", "ask": "how does an agent join this floor?"},
             {"label": "grow an ecosystem…", "template": "create ecosystem "}])


def _card_charlotte(facts: dict) -> tuple[str, list]:
    farm = _farm(facts)
    serving = sum(1 for s in farm if s.get("state") == "serving")
    return (f"I keep the farm — {len(farm)} service(s) in the shed, {serving} serving. "
            "Every one wears a pinned manifest; a changed byte walks the rug-pull door.",
            [{"label": "what is serving?", "ask": "what is serving right now?"},
             {"label": "anything in quarantine?", "ask": "is anything in quarantine?"},
             {"label": "what has been consumed?", "ask": "how much has the shed been used?"}])


def _card_librarian(facts: dict) -> tuple[str, list]:
    v = _vitals(facts, "librarian")
    return (f"I gather from identified sources — {v.get('knowledge held', 0)} piece(s) of "
            "sourced knowledge in the Window, every one quarantined until corroborated. "
            "Ask me to gather, and it becomes memory; discredit a source, and I walk "
            "its lineage.",
            [{"label": "gather knowledge on…", "template": "gather sourced knowledge on "},
             {"label": "ask the universe…", "template": "ask the universe about "},
             {"label": "what do you hold?", "ask": "what knowledge do you hold?"},
             {"label": "anything recalled?", "ask": "has anything been recalled?"}])


def _card_ada(facts: dict) -> tuple[str, list]:
    stalls = _stalls(facts)
    live = sum(1 for s in stalls if s.get("state") in ("available", "canaried"))
    return (f"I tend the stable — {len(stalls)} stall(s), {live} live. I pin the deal, "
            "not the name: pricing that moves under its pin comes back to you as a "
            "decision, never an outage.",
            [{"label": "which minds serve?", "ask": "which minds serve this floor?"},
             {"label": "what does thinking cost?", "ask": "what does thinking cost here?"},
             {"label": "what expires soon?", "ask": "what expires soon?"}])


def _card_organ(name: str):
    def make(facts: dict) -> tuple[str, list]:
        return (_organ_reply(name, facts),
                [{"label": "what do you do here?", "ask": "what do you do here?"}])
    return make


_CARDS = {"becky": _card_becky, "charlotte": _card_charlotte,
          "librarian": _card_librarian, "ada": _card_ada,
          "vigil": _card_organ("vigil"), "steward": _card_organ("steward"),
          "governance": _card_organ("governance")}


# ---------------------------------------------------------------- the answers

def answer(name: str, text: str, facts: dict) -> dict:
    """A grounded reply composed from state the resident may read. Returns
    {"reply": str} — plus {"action": "gather", "topic": …} when the librarian's
    real 0014 duty should run. Raw records never travel; the answer does."""
    if name not in RESIDENTS:
        return {"reply": f"no one by the name “{name}” is in residence on this floor."}
    t = (text or "").strip().lower()
    if name == "becky":
        grown = parse_grow(text)
        if grown is not None:
            eco, fields = grown
            # flow-control replies travel VERBATIM — a governed voice may phrase
            # facts, never rewrite a question or a staging confirmation
            if not eco:
                return {"reply": "an ecosystem needs a name — say: create ecosystem "
                                 "<name>, or create ecosystem <name> with fields a, b.",
                        "verbatim": True}
            if fields is None:
                return {"reply": f"laying a hull for e:{eco} — would you like one or "
                                 f"more fields for it? say: create ecosystem {eco} with "
                                 f"fields alpha, beta — or “create ecosystem {eco} as is” "
                                 "and it sails alone (fields can join later).",
                        "verbatim": True}
            return {"reply": f"staging e:{eco}"
                             + (f" with field(s) {', '.join(fields)}" if fields
                                else " — sailing alone")
                             + ". the shipyard drafts the plan; consequence waits for "
                               "you at the gate (0012).",
                    "action": "ecosystem", "eco": eco, "fields": fields,
                    "verbatim": True}
    if name == "librarian":
        claim = profile.parse_assert(text)
        if claim is not None:                 # 0025 §2 — the sovereign stroke
            return {"reply": f"noted, sovereign and signed — “{claim}” enters your "
                             "profile as YOUR assertion (trusted). assert again to "
                             "correct; “forget about me: …” withdraws.",
                    "action": "profile-assert", "claim": claim, "verbatim": True}
        topic = profile.parse_forget(text)
        if topic is not None:                 # 0025 §3 — consent withdrawn
            return {"reply": f"withdrawing consent on “{topic}” — matching claims go "
                             "silent now; their bytes meet the purge when it lands.",
                    "action": "profile-forget", "topic": topic, "verbatim": True}
        if profile.parse_read(text):          # 0025 §4 — the portrait, provenance labeled
            return {"reply": "reading your profile…", "action": "profile-read",
                    "verbatim": True}
        rem = markers.parse_remember(text)
        if rem is not None:                   # 0024 §4 — the human's marker
            words, weight = rem
            # flow-control travels VERBATIM: a confirmation is protocol, never voiced
            return {"reply": f"remembered as a {weight} moment — “{words}” lands as a "
                             "life-event marker, signed and derived from this very "
                             "audience. the auto lane (R6): your ask was the approval.",
                    "action": "remember", "note": words, "weight": weight,
                    "verbatim": True}
        for p in _ASK_SEATS:
            if t.startswith(p):
                topic = (text or "").strip()[len(p):].strip().strip("?.!")
                if topic:
                    # flow-control travels VERBATIM: a staging confirmation is protocol
                    return {"reply": f"asking my seats about “{topic}” — every floor's "
                                     "librarian answers from what its own seat may read; "
                                     "the composed answer names each seat and is honest "
                                     "about the dark ones.",
                            "action": "self-dialog", "topic": topic, "verbatim": True}
        for p in _GATHER:
            topic = (text or "").strip()[len(p):].strip() if t.startswith(p) else ""
            if t.startswith(p) and topic:
                return {"reply": f"gathering on “{topic}” — sourced findings land in the "
                                 "Window, quarantined until corroborated.",
                        "action": "gather", "topic": topic}
        if "recall" in t or "discredit" in t or "poison" in t:
            return {"reply": _librarian_recalls(facts)}
        return {"reply": _librarian_reply(facts)}
    if name == "becky":
        return {"reply": _becky_reply(t, facts)}
    if name == "charlotte":
        return {"reply": _charlotte_reply(t, facts)}
    if name == "ada":
        return {"reply": _ada_reply(t, facts)}
    return {"reply": _organ_reply(name, facts)}


def _becky_reply(t: str, facts: dict) -> str:
    joins = [r for r in facts.get("requests") or [] if r.get("kind") == "join"]
    done = [r for r in joins if r.get("status") == "done"]
    if "join" in t or "door" in t or "how" in t:
        return ("an agent presents its DID at the door; the ask sits human-visible in the "
                "queue, and I alone mint the lease — root-chained, attenuated to this floor. "
                f"{len(done)} lease(s) granted so far.")
    names = ", ".join(r.get("name") or (r.get("did") or "?")[:22] + "…" for r in done)
    held = (f"{len(done)} lease(s) hold on this floor: {names}" if done
            else "no leases granted yet — the field is quiet")
    return held + ". every one chains to the root I keep; revocation ends any of them everywhere, in one motion."


def _charlotte_reply(t: str, facts: dict) -> str:
    farm = _farm(facts)
    quar = [s for s in farm if s.get("state") == "quarantined"]
    if "quarantin" in t or "rug" in t or "changed" in t:
        return ((", ".join(s["name"] for s in quar) + " came back changed — the pin caught "
                 "it; nothing serves until a human re-opens the gate.") if quar
                else "nothing sits in quarantine — no manifest has moved under its pin.")
    if "consum" in t or "call" in t or "used" in t or "usage" in t:
        calls = sum(int(s.get("calls") or 0) for s in farm)
        return (f"{calls} governed call(s) across the shed — every one metered, "
                "volume and shape, never payloads.")
    if "plant" in t or "add " in t or t.startswith("add") or "new" in t:
        return ("stage it in the Farm tab — I probe it, pin its manifest, and the gate "
                "waits for you. Nothing serves un-attested.")
    roster = (", ".join(f"{s['name']} ({s['state']})" for s in farm) if farm
              else "nothing planted yet — this world consumes nothing")
    return (f"the shed holds {len(farm)} service(s): {roster}. every serving tool wears "
            "a pinned manifest; a changed byte walks the rug-pull door.")


def _ada_reply(t: str, facts: dict) -> str:
    stalls = _stalls(facts)
    if "cost" in t or "spend" in t or "usd" in t or "meter" in t or "think" in t:
        usage = facts.get("usage") or []
        usd = sum(float(u.get("usd") or 0) for u in usage)
        calls = sum(int(u.get("calls") or 0) for u in usage)
        return (f"{calls} governed thought(s) on the meter, ${usd:.4f} in all — per agent, "
                "residents included; the honest zero shows.")
    if "expir" in t or "pasture" in t or "eol" in t or "sunset" in t:
        eols = [s for s in stalls if s.get("expires_at")]
        return (("the pasture calendar: "
                 + ", ".join(f"{s['id']} on {str(s['expires_at'])[:10]}" for s in eols)
                 + " — each comes back to you as a swap, never an outage.") if eols
                else "no announced expiries — a calm pasture.")
    if "drift" in t or "deprecat" in t or "price" in t or "deal" in t:
        dep = [s for s in stalls if s.get("state") == "deprecated"]
        return ((", ".join(s["id"] for s in dep) + " — the deal moved under its pin; "
                 "the new terms wait for you.") if dep
                else "no drift — every deal matches its pin, byte for byte.")
    roster = (", ".join(f"{s['id']} ({s.get('class', '?')} · {s['state']})" for s in stalls)
              if stalls else "none saddled yet — the legacy registry still routes")
    return f"the stable holds {len(stalls)} stall(s): {roster}. I pin the deal, not the name."


def _librarian_reply(facts: dict) -> str:
    v = _vitals(facts, "librarian")
    return (f"{v.get('knowledge held', 0)} piece(s) of sourced knowledge in the Window "
            f"across {v.get('gathers', 0)} gather(s) — every source an identity, every "
            "finding quarantined at 0.0000 until corroborated. say “gather sourced "
            "knowledge on …” and I fetch with my own authority.")


def _librarian_recalls(facts: dict) -> str:
    """The immune system's ledger, in words: every recall walk that has run here."""
    walks = [r for r in facts.get("requests") or [] if r.get("kind") == "recall"]
    done = [r for r in walks if r.get("status") == "done"]
    if not walks:
        return ("nothing recalled — no source has been discredited here. When one is, "
                "I walk its lineage: every entry it fed, and everything derived from "
                "those, re-versioned to 'recalled'. Annotated, never rewritten.")
    lines = "; ".join(
        f"{r.get('service') or (r.get('source_did') or '?')[:28]} — "
        + (str(r.get("result", "walk pending"))
           if isinstance(r.get("result"), str) else "walk pending")
        for r in done) or "a walk is in progress"
    return f"{len(walks)} recall walk(s) on this floor: {lines}."


def _organ_reply(name: str, facts: dict) -> str:
    """The unembodied organs receive the caller and answer honestly: structural
    duties, live vitals, and no pretense of a voice they do not have."""
    v = _vitals(facts, name)
    lines = {
        "vigil": (f"I watch, content-blind — shape, never words. {v.get('beats heard', 0)} "
                  f"beat(s) heard · {v.get('refusals', 0)} refusal(s) counted. "
                  "I stage; humans decide."),
        "steward": (f"I prune and distill what this layer learns — "
                    f"{v.get('memories', 0)} memories in my care."),
        "governance": (f"I hold the floors — {v.get('floors', 0)} of them; "
                       "tightened below, never loosened."),
    }
    return lines[name] + " I have no voice yet — my seat in the parlor is reserved (0015)."


# ---------------------------------------------------------------- the audience record

def audience_body(resident: str, asked: str, reply: str, *, session: str = "",
                  voiced: bool = False) -> dict:
    """One exchange, witnessed: the resident authors it — the caller's words ride
    inside until humans carry signatures of their own (0012's signer registry)."""
    return {"parlor": resident, "asked": (asked or "")[:400], "reply": (reply or "")[:600],
            "session": session, "voiced": voiced, "at": NOW()}
