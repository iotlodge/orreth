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

from . import continuity, markers, profile
from .identity import NOW

RESIDENTS = ("becky", "vigil", "steward", "governance", "charlotte", "librarian",
             "ada", "grace")
EMBODIED = ("becky", "charlotte", "librarian", "ada", "grace")  # hold keys; sign their audiences

ROLES = {"becky": "becky · IAM", "vigil": "vigil · the Warden",
         "steward": "steward · memory", "governance": "governance",
         "charlotte": "charlotte · farm keeper", "librarian": "librarian · knowledge",
         "ada": "ada · the wrangler", "grace": "grace · the smith"}

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

# the smith's doors (0031 §4), in the shapes callers actually type
_WALK = ("show asset", "walk asset", "asset walk for")
_FEEDBACK = ("feedback on", "feedback for")

# the librarian's freshness doors (0031 §5), in the shapes callers actually type
_CHALLENGE = ("challenge knowledge on", "challenge")
_DOMAIN = ("show domain packages", "show domains", "domain packages",
           "show domain", "domain package for")

# the serials desk (0032 §1), in the shapes callers actually type
_SUBSCRIBE = ("subscribe to", "subscribe")
_UNSUBSCRIBE = ("unsubscribe from", "unsubscribe", "cancel subscription to",
                "cancel the subscription to")
_DESK = ("show the desk", "the serials desk", "show subscriptions",
         "what do you watch")


def parse_feedback(text: str):
    """“feedback on prompt-plan: too wordy under pressure” → (name, words)."""
    t = (text or "").strip()
    low = t.lower()
    for p in _FEEDBACK:
        if low.startswith(p) and ":" in t:
            head, words = t[len(p):].split(":", 1)
            if head.strip() and words.strip():
                return head.strip().lower(), words.strip()
    return None


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


def parse_testament(text: str):
    """“testament: journals shred, identity pass — executor did:key:zE, witness
    did:key:zW, silence 21 days” → {fates, executor, witnesses, silence_days},
    or None when the ask is not a testament. Parsed on the RAW text: DIDs keep
    their case; fates and domains fold to lower (0035 §2)."""
    m = re.match(r"^(?:my |the |write (?:my )?|set (?:my )?)?testament:?\s+(.+)$",
                 (text or "").strip(), flags=re.IGNORECASE)
    if not m:
        return None
    body = m.group(1)
    executor = ""
    em = re.search(r"executor\s+(\S+)", body, flags=re.IGNORECASE)
    if em:
        executor = em.group(1).rstrip(",.;—")
    witnesses = [w.rstrip(",.;—") for w in
                 re.findall(r"witness(?:es)?\s+(\S+)", body, flags=re.IGNORECASE)]
    silence_days = 30                     # the desk default; the human tunes it
    sm = re.search(r"silence\s+(\d+)\s*days?", body, flags=re.IGNORECASE)
    if sm:
        silence_days = int(sm.group(1))
    cleaned = re.sub(r"(executor|witness(?:es)?)\s+\S+", " ", body,
                     flags=re.IGNORECASE)
    cleaned = re.sub(r"silence\s+\d+\s*days?", " ", cleaned, flags=re.IGNORECASE)
    fates = {d.lower(): f.lower() for d, f in
             re.findall(r"([A-Za-z][\w-]*)\s+(seal|pass|shred)\b", cleaned,
                        flags=re.IGNORECASE)}
    return {"fates": fates, "executor": executor, "witnesses": witnesses,
            "silence_days": silence_days}


_TEMPLATES = ("continuity",)          # 0009's named templates the parlor knows


def grow_template(text: str):
    """“create continuity ecosystem foo …” → ("continuity", the same ask with
    the template word lifted out) — parse_grow keeps its shape; the template
    rides beside it (0034 §7 sp1)."""
    t = (text or "").strip()
    low = t.lower()
    for tpl in _TEMPLATES:
        for p in _GROW:
            head, _, tail = p.partition(" ecosystem")
            marked = f"{head} {tpl} ecosystem"
            if low.startswith(marked):
                return tpl, head + " ecosystem" + t[len(marked):]
    return None, t


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
            "voiced": name in EMBODIED, "workspace": name in EMBODIED,
            # upload is an ask, and the card declares who receives files (0029 §2)
            "accepts": ["upload"] if name == "librarian" else [],
            "greeting": greeting, "asks": asks}


def _card_becky(facts: dict) -> tuple[str, list]:
    done = [r for r in facts.get("requests") or []
            if r.get("kind") == "join" and r.get("status") == "done"]
    return (f"I keep the door. Every identity here chains to the root I hold — "
            f"{len(done)} lease(s) granted so far, nothing joins without one. I can also "
            "grow this universe: ask me for a new ecosystem, and the shipyard lays a hull.",
            [{"label": "who holds a lease?", "ask": "who holds a lease on this floor?"},
             {"label": "how does joining work?", "ask": "how does an agent join this floor?"},
             {"label": "grow an ecosystem…", "template": "create ecosystem "},
             {"label": "grant access…", "template": "grant caregiver access to "},
             {"label": "the consent ledger", "ask": "show consents"},
             {"label": "stop recording…", "template": "stop recording conversation"},
             {"label": "my testament…", "template": "testament: "},
             {"label": "the testament", "ask": "show testament"},
             {"label": "the passage", "ask": "show the passage"}])


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
             {"label": "subscribe…", "template": "subscribe to "},
             {"label": "the serials desk", "ask": "show the desk"},
             {"label": "domain packages", "ask": "show domain packages"},
             {"label": "challenge…", "template": "challenge "},
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


def _card_grace(facts: dict) -> tuple[str, list]:
    rows = facts.get("shelf") or []
    open_p = sum(1 for r in rows if r.get("open"))
    return (f"I keep the workshop, on the universe floor — {len(rows)} asset(s) on the "
            f"shelf, {open_p} proposal(s) open. Prompts, profiles, and workflows are "
            "versioned data here: I propose from receipts, governance grades by diff, "
            "and the high lane waits for you. Your feedback lands verbatim and I must "
            "carry it.",
            [{"label": "show the shelf", "ask": "show the shelf"},
             {"label": "walk an asset…", "template": "show asset "},
             {"label": "leave feedback…", "template": "feedback on "},
             {"label": "what waits for me?", "ask": "what waits for me?"}])


def _card_organ(name: str):
    def make(facts: dict) -> tuple[str, list]:
        return (_organ_reply(name, facts),
                [{"label": "what do you do here?", "ask": "what do you do here?"}])
    return make


_CARDS = {"becky": _card_becky, "charlotte": _card_charlotte,
          "librarian": _card_librarian, "ada": _card_ada, "grace": _card_grace,
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
        # the testament (0035 §2): the human's standing word about the end.
        # Writing one ARMS future consequence — it STAGES; revoking it is
        # safe — it acts NOW. Every word travels VERBATIM: fates are protocol.
        if t.startswith(("revoke my testament", "revoke the testament",
                         "revoke testament")):
            return {"reply": "revoking your testament NOW — a new version on "
                             "its worldline, never an absence. without a "
                             "standing word every domain seals, hibernated — "
                             "the least irreversible act (0035 §8).",
                    "action": "testament-revoke", "verbatim": True}
        if t.startswith(("show testament", "show my testament",
                         "the testament")):
            return {"reply": _becky_testament(facts), "verbatim": True}
        tst = parse_testament(text)
        if tst is not None:
            if not tst["fates"]:
                return {"reply": "a testament names fates — say: testament: "
                                 "journals shred, identity pass, medication "
                                 "seal — executor did:key:…, witness "
                                 "did:key:…, silence 30 days. unnamed domains "
                                 "seal.",
                        "verbatim": True}
            if any(f in ("pass", "shred") for f in tst["fates"].values()) \
                    and not tst["executor"]:
                return {"reply": "a testament that passes or shreds needs an "
                                 "executor — only attested death executes "
                                 "(0035 §3). name one: … executor did:key:….",
                        "verbatim": True}
            fates_words = " · ".join(f"{d} {f}" for d, f in tst["fates"].items())
            return {"reply": f"staging your testament — {fates_words}; "
                             + (f"executor {tst['executor']}, " if tst["executor"]
                                else "")
                             + (f"witness {', '.join(tst['witnesses'])}, "
                                if tst["witnesses"] else "")
                             + f"a {tst['silence_days']}-day silence window. "
                               "the last standing word is a consequence — the "
                               "gate waits for you (0012). unnamed domains "
                               "seal; silence may only contain (0035 §8).",
                    "action": "testament-stage", **tst, "verbatim": True}
        # the passage (0035 §3): silence may only contain. Attesting a death
        # STAGES an escalation (the gravest gate); aborting one acts NOW —
        # one voice saves. v0 honesty: the executor speaks through this same
        # glass until 0012's signer registry lands; the words travel VERBATIM.
        if t.startswith(("show the passage", "the passage", "show passage")):
            return {"reply": _becky_passage(facts), "verbatim": True}
        if t.startswith(("abort the attestation", "abort attestation")):
            return {"reply": "aborting the attestation NOW — one voice saves "
                             "(0012 §3). the universe returns to SEALED, "
                             "contained and reversible; the record keeps who "
                             "spoke.",
                    "action": "attestation-abort", "verbatim": True}
        am = re.match(r"^attest\s+death:?\s+(.+)$", (text or "").strip(),
                      flags=re.IGNORECASE)
        if am:
            abody = am.group(1)
            evidence = [e.rstrip(",.;—") for e in
                        re.findall(r"evidence\s+(\S+)", abody,
                                   flags=re.IGNORECASE)]
            ex = re.search(r"executor\s+(\S+)", abody, flags=re.IGNORECASE)
            wits = [w.rstrip(",.;—") for w in
                    re.findall(r"witness(?:es)?\s+(\S+)", abody,
                               flags=re.IGNORECASE)]
            registry = bool(re.search(r"\bregistry\b", abody,
                                      flags=re.IGNORECASE))
            attestors = ([ex.group(1).rstrip(",.;—")] if ex else []) + wits
            if not evidence:
                return {"reply": "an attestation needs evidence — a death is "
                                 "never declared on words alone (0035 §3). "
                                 "say: attest death: evidence <artifact> — "
                                 "executor did:key:…, witness did:key:….",
                        "verbatim": True}
            return {"reply": "staging the attestation — evidence "
                             + ", ".join(evidence)
                             + (f"; attestors {', '.join(attestors)}"
                                if attestors else "; no attestors named")
                             + ". the gravest gate: quorum 2 against the "
                               "testament's roster, and approval only starts "
                               "the cooling-off — any entitled voice aborts, "
                               "and the loudest abort is a heartbeat "
                               "(0035 §3).",
                    "action": "attest-death", "evidence": evidence,
                    "attestors": attestors, "registry": registry,
                    "verbatim": True}
        # consent & delegation (0034 §4): granting access to a person's memory
        # is a consequence — it STAGES; revoking is safety — it acts NOW.
        # Every consent word travels VERBATIM: access terms are protocol.
        m = re.match(r"^grant\s+([a-z]+)\s+access"
                     r"(?:\s+to\s+(.*?))?(?:\s+for\s+(\d+)\s+days?)?$", t)
        if m and m.group(1) in continuity.ROLE_BUNDLES:
            role, purpose, days = m.group(1), (m.group(2) or "").strip(), \
                int(m.group(3) or 30)
            b = continuity.ROLE_BUNDLES[role]
            return {"reply": f"staging {role} access — {' · '.join(b['domains'])} "
                             f"({b['note']}), a {days}-day window"
                             + (f", purpose: “{purpose}”" if purpose else "")
                             + ". access to a person's memory is a consequence — "
                               "the gate waits for you (0012). the sealed never "
                               "delegates.",
                    "action": "consent-grant", "role": role, "purpose": purpose,
                    "days": days, "verbatim": True}
        m = re.match(r"^revoke\s+([a-z]+)\s+access$", t)
        if m and m.group(1) in continuity.ROLE_BUNDLES:
            return {"reply": f"revoking {m.group(1)} access NOW — a new version on "
                             "its worldline, never an absence. stopping access is "
                             "safe; what was shared under consent follows its own "
                             "grant.",
                    "action": "consent-revoke", "role": m.group(1),
                    "verbatim": True}
        m = re.match(r"^stop\s+recording\s+([a-z]+?)s?$", t)
        if m and m.group(1) in continuity.MODALITIES:
            return {"reply": f"safer mode — {m.group(1)} recording stops NOW, on "
                             "the record. what was recorded under consent remains, "
                             "readable under its own grant (0034 §4).",
                    "action": "consent-revoke", "modality": m.group(1),
                    "verbatim": True}
        m = re.match(r"^resume\s+recording\s+([a-z]+?)s?$", t)
        if m and m.group(1) in continuity.MODALITIES:
            return {"reply": f"staging: resume {m.group(1)} recording — recording "
                             "is a consequence, and consequence waits for you at "
                             "the gate (0012).",
                    "action": "consent-grant", "modality": m.group(1),
                    "verbatim": True}
        if t.startswith(("show consents", "the consent ledger", "show the consent")):
            return {"reply": _becky_consents(facts), "verbatim": True}
        tpl, plain = grow_template(text)      # 0034 §7 sp1 — a named template rides
        grown = parse_grow(plain)
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
                             + (f", wearing the {tpl} template — its floors are born "
                                "with the regime, the vector, and the label canon"
                                if tpl else "")
                             + ". the shipyard drafts the plan; consequence waits for "
                               "you at the gate (0012).",
                    "action": "ecosystem", "eco": eco, "fields": fields,
                    **({"template": tpl} if tpl else {}),
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
                             "silent now and their bytes leave the store (0026); the "
                             "signed stubs stay: THAT you forgot is on the record.",
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
        for p in _UNSUBSCRIBE:                # 0032 §1 — retired on the record
            if t.startswith(p):
                topic = (text or "").strip()[len(p):].strip().strip("?.!")
                if topic:
                    return {"reply": f"cancelling the subscription to “{topic}” — "
                                     "a new version on its worldline, never an "
                                     "absence. Stopping a spend needs no gate.",
                            "action": "unsubscribe", "topic": topic,
                            "verbatim": True}
        for p in _SUBSCRIBE:                  # 0032 §1 — a standing spend STAGES
            if t.startswith(p):
                topic = (text or "").strip()[len(p):].strip().strip("?.!")
                # the cadence is a dial on the record (0032 §8): the human may
                # say "… every N beats"; unsaid, the desk's default stands
                cadence = None
                m = re.search(r"\s+every\s+(\d+)\s+beats?$", topic,
                              flags=re.IGNORECASE)
                if m:
                    cadence = int(m.group(1))
                    topic = topic[:m.start()].strip()
                if topic:
                    # flow-control travels VERBATIM: a staging confirmation is protocol
                    return {"reply": f"staging a subscription to “{topic}” — a "
                                     "standing spend is a consequence, and "
                                     "consequence waits for you at the gate (0012). "
                                     "Approve it and the desk delivers on the beat"
                                     + (f", every {cadence} beats" if cadence else "")
                                     + ".",
                            "action": "subscribe", "topic": topic,
                            **({"cadence": cadence} if cadence else {}),
                            "verbatim": True}
        for p in _DESK:
            if t.startswith(p):
                # the ledger travels VERBATIM: cadence, posture, and the lane are
                # terms of record — a governed thought must never rewrite them
                # (the voiced-reply lesson, held since 0020)
                return {"reply": _librarian_desk(facts), "verbatim": True}
        for p in _DOMAIN:                     # 0031 §5 — the package, recallable
            if t.startswith(p):
                topic = (text or "").strip()[len(p):].strip().strip("?.!")
                return {"reply": f"composing the domain package{f' for “{topic}”' if topic else 's'} — "
                                 "every claim wearing its state, every source named.",
                        "action": "domain", "topic": topic, "verbatim": True}
        for p in _CHALLENGE:                  # 0031 §5 — the human's doubt is a trigger
            if t.startswith(p):
                topic = (text or "").strip()[len(p):].strip().strip("?.!")
                if topic:
                    # flow-control travels VERBATIM: a staging confirmation is protocol
                    return {"reply": f"challenging “{topic}” — matching claims drop to "
                                     "investigating until corroboration earns them "
                                     "back. Doubted, not damned; nothing rewritten.",
                            "action": "challenge", "topic": topic, "verbatim": True}
        for p in _GATHER:
            topic = (text or "").strip()[len(p):].strip() if t.startswith(p) else ""
            if t.startswith(p) and topic:
                return {"reply": f"gathering on “{topic}” — sourced findings land in the "
                                 "Window, quarantined until corroborated.",
                        "action": "gather", "topic": topic}
        if "recall" in t or "discredit" in t or "poison" in t:
            return {"reply": _librarian_recalls(facts)}
        return {"reply": _librarian_reply(facts)}
    if name == "grace":
        fb = parse_feedback(text)
        if fb is not None:                    # 0031 §4 — the feedback door
            asset, words = fb
            # flow-control travels VERBATIM: a confirmation is protocol, never voiced
            return {"reply": f"on the record — “{words}” lands verbatim against "
                             f"{asset}'s active version, signed and derived from it. "
                             "I must carry it as evidence on my next beat; adoption "
                             "still rides the lanes.",
                    "action": "asset-feedback", "asset": asset, "note": words,
                    "verbatim": True}
        for p in _WALK:
            if t.startswith(p):
                walked = (text or "").strip()[len(p):].strip().strip("?.!").lower()
                if walked:
                    return {"reply": f"walking {walked.split()[0]} — oldest to "
                                     "active, every version a sibling: evidence → "
                                     "proposal → grade → adoption.",
                            "action": "asset-walk", "asset": walked.split()[0],
                            "verbatim": True}
        if "wait" in t:
            return {"reply": _grace_waiting(facts)}
        if "shelf" in t or "asset" in t:
            return {"reply": _grace_shelf(facts)}
        return {"reply": _grace_reply(facts)}
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


def _last_issue(facts: dict) -> dict:
    """The newest delivery note per topic, from the notes the caller may read —
    the desk speaks its sweeps (0032 §2)."""
    last: dict = {}
    for d in facts.get("deliveries") or []:
        last[str(d.get("topic", ""))] = d     # oldest first — the last write wins
    return last


def _issue_words(d: dict) -> str:
    n = d.get("issue", "?")
    bits = [f"{len(d.get('arrived') or [])} new", f"{d.get('repeated', 0)} repeated"]
    if d.get("changed"):
        bits.append(f"{len(d['changed'])} changed at source")
    if d.get("vanished"):
        bits.append(f"{len(d['vanished'])} vanished")
    quiet = not (d.get("changed") or d.get("vanished"))
    return (f"issue {n} landed: " + " · ".join(bits)
            + ("" if quiet else " — NEWS"))


def _becky_consents(facts: dict) -> str:
    """The consent ledger, in words (0034 §4): every worldline's head — role or
    modality, posture, window, purpose. Revoked shown revoked: withdrawn is a
    state, never an absence."""
    heads = facts.get("consents") or []
    if not heads:
        return ("no consents stand — say “grant caregiver access to <purpose>” "
                "(it stages at your gate) or “stop recording conversations” "
                "(safer mode, immediate). the sealed never delegates.")
    lines = "; ".join(
        (f"{c.get('role')} ({c.get('holder') or 'unnamed'})" if c.get("role")
         else " + ".join(c.get("modalities") or ["?"]))
        + f" — {c.get('posture', '?')}"
        + (f", until {str((c.get('window') or {}).get('until', ''))[:10]}"
           if c.get("posture") == "granted" else "")
        + (f" · {' · '.join(c.get('domains') or [])}" if c.get("domains") else "")
        + (f" · “{c.get('purpose', '')}”" if c.get("purpose") else "")
        for c in heads)
    return (f"{len(heads)} consent worldline(s): {lines}. grants stage at the "
            "gate; revocation is immediate — stopping access is safe.")


def _becky_testament(facts: dict) -> str:
    """The last standing word, in words (0035 §2): the head's fates, roster,
    and silence window — or the honest default when none stands. Revoked shown
    revoked: a withdrawn word is a state, never an absence."""
    heads = facts.get("testament") or []
    if not heads:
        return ("no testament stands — every domain seals, hibernated, the "
                "least irreversible act (0035 §8): the universe assumes "
                "nothing about the unspoken. say “testament: journals shred, "
                "identity pass — executor did:key:…” and your standing word "
                "stages at the gate.")
    h = heads[-1]
    if h.get("posture") != "standing":
        return ("your testament is revoked — a state on the worldline, never "
                "an absence. every domain seals until you speak again; "
                "silence may only contain (0035 §8).")
    fates = " · ".join(f"{d} {f}" for d, f in (h.get("fates") or {}).items()) \
        or "no fates named"
    return (f"your testament stands: {fates}; unnamed domains seal. "
            f"executor {h.get('executor') or 'unnamed'}"
            + (f", witness {', '.join(h['witnesses'])}" if h.get("witnesses")
               else "")
            + f"; a {((h.get('silence_window') or {}).get('days', 30))}-day "
              "silence window — silence may only contain; only attested death "
              "executes, and the loudest abort is a heartbeat (0035 §3). "
              "revocable to your last day.")


def _becky_passage(facts: dict) -> str:
    """The passage, in words (0035 §3): the state, what drove it, and what the
    machine may do next — spoken so the gravest states are never a surprise."""
    heads = facts.get("passage") or []
    state = heads[-1].get("state", "living") if heads else "living"
    reason = heads[-1].get("reason", "") if heads else ""
    lines = {
        "living": "the universe is LIVING — your word is recent, nothing "
                  "watches but the clock. silence past your window would "
                  "reach out first, seal second, and never more (0035 §8).",
        "unresponsive": "the universe is UNRESPONSIVE — the seats have "
                        "reached out; a full window of silence more and it "
                        "seals, reversibly. any word from you answers.",
        "sealed": "the universe is SEALED — contained at machine speed, "
                  "reversible, loud. one heartbeat unseals; only attested "
                  "death (quorum 2 + evidence, at the gate) moves further.",
        "attested": "a death is ATTESTED — the cooling-off runs. any "
                    "entitled voice aborts back to sealed; a heartbeat "
                    "aborts everything. nothing executes until the window "
                    "passes in silence.",
        "executed": "the fates have EXECUTED — the walk is on the record.",
        "legacy": "the universe is LEGACY — the archive speaks about, "
                  "never as.",
    }
    extra = ""
    if state == "attested" and heads and heads[-1].get("cooling_until"):
        extra = f" cooling until {heads[-1]['cooling_until'][:16]}Z."
    return lines[state] + (f" (last transition: {reason})" if reason else "") \
        + extra


def _librarian_desk(facts: dict) -> str:
    """The serials desk, in words (0032 §1–§2): every subscription's terms,
    posture, and latest issue — retired ones included, because cancelled is a
    state."""
    subs = facts.get("subscriptions") or []
    if not subs:
        return ("the desk is empty — say “subscribe to <topic>” and a standing "
                "subscription stages for your approval; the desk delivers on "
                "the beat once you open it.")
    last = _last_issue(facts)
    lines = "; ".join(
        f"{s.get('topic', '?')} — {s.get('posture', '?')}"
        + (f", every {s.get('cadence_beats', '?')} beats"
           if s.get("posture") == "deliver" else "")
        + (f" ({_issue_words(last[s.get('topic', '?')])})"
           if s.get("topic", "?") in last else "")
        for s in subs)
    return (f"the desk holds {len(subs)} subscription(s): {lines}. deliveries "
            "ride the beat — a quiet issue logs, news wears the medium marker.")


def _grace_shelf(facts: dict) -> str:
    rows = facts.get("shelf") or []
    if not rows:
        return ("the shelf is bare — genesis assets plant on my first beat; from "
                "then on, every change is a sibling on the record.")
    lines = "; ".join(
        f"{r['name']} — {r.get('versions', 0)} version(s)"
        + (", a proposal holds the lane" if r.get("open") else "")
        + (f", {r['feedback']} feedback" if r.get("feedback") else "")
        for r in rows)
    return (f"{len(rows)} asset(s) on the shelf: {lines}. say “show asset <name>” "
            "and I walk its lineage.")


def _grace_waiting(facts: dict) -> str:
    held = [r for r in facts.get("requests") or []
            if r.get("kind") == "improvement" and r.get("status") == "staged"]
    if not held:
        return ("nothing waits on the high lane — the shelf is at peace. medium "
                "nudges adopt loud; rewrites stop here for you.")
    lines = "; ".join(str(r.get("text") or r.get("id", "?"))[:80] for r in held)
    return (f"{len(held)} proposal(s) wait for your word: {lines}. approve in the "
            "inbox and the adoption cites your gate; decline and the lane opens.")


def _grace_reply(facts: dict) -> str:
    rows = facts.get("shelf") or []
    open_p = sum(1 for r in rows if r.get("open"))
    return (f"the workshop: {len(rows)} asset(s), {open_p} proposal(s) open. I read "
            "the receipts — rollups, markers, parked intents, your words — and "
            "propose siblings, never silent successors. governance grades by diff; "
            "the lanes route; you hold the high one.")


def package_text(pkg: dict) -> str:
    """The approval package, readable (0031 §4): what changed · why · rollback ·
    checks — composed for the room's doc panel and the decision inbox. The human
    reviews a checked candidate, never raw factory output."""
    if not pkg:
        return "nothing staged."
    ch = "; ".join(f"{k}: {v['from']!r} → {v['to']!r}"[:90]
                   for k, v in (pkg.get("changed") or {}).items()) or "nothing"
    why = "; ".join(r["what"] for r in (pkg.get("receipts") or [])[:5]) \
        or "no receipts cited"
    checks = ("no-op — refused, no lane to ride"
              if (pkg.get("checks") or {}).get("no_op") else
              "diff computed, lineage cites the active version"
              if (pkg.get("checks") or {}).get("cites_active") else
              "diff computed — does not cite the active version")
    return (f"{pkg.get('asset', '?')} — a {pkg.get('kind', '?')} on the "
            f"{pkg.get('lane', '?')} lane.\nWHAT CHANGED: {ch}.\nWHY: {why}.\n"
            f"ROLLBACK: the prior version stands"
            + (f" ({str(pkg.get('rollback'))[:18]}…)" if pkg.get("rollback") else "")
            + f".\nCHECKS: {checks}.")


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


# ---------------------------------------------------------------- the workspaces (0028)

def workspace(name: str, facts: dict) -> dict | None:
    """The resident's room (0028 §1): typed panels composed from state the
    resident may read — stat · bars · list · doc — rendered blind by the glass.
    The room is an ask like any other; a resident without one returns None."""
    if name not in EMBODIED:
        return None
    return {"resident": name, "panels": _ROOMS[name](facts)}


def _sev(items):
    """0024's badge, discharged: medium and above wear amber in the glass."""
    return [{**i, "amber": i.get("severity") in ("medium", "high", "critical")}
            for i in items]


def _room_librarian(facts: dict) -> list[dict]:
    v = _vitals(facts, "librarian")
    walks = [r for r in facts.get("requests") or [] if r.get("kind") == "recall"]
    return [
        {"kind": "stat", "title": "the shelf",
         "items": [{"label": "knowledge held", "value": v.get("knowledge held", 0)},
                   {"label": "gathers", "value": v.get("gathers", 0)},
                   {"label": "recall walks", "value": len(walks)}]},
        {"kind": "list", "title": "the serials desk (0032)",
         "items": _sev([{"text": s.get("topic", "?"),
                         "meta": f"{s.get('posture', '?')}"
                                 + (f" · every {s.get('cadence_beats', '?')} beats"
                                    f" · {((s.get('budget') or {}).get('calls', '?'))}"
                                    " call(s)/delivery"
                                    if s.get("posture") == "deliver" else "")
                                 + (f" · {_issue_words(_last_issue(facts)[s.get('topic', '?')])}"
                                    if s.get("topic", "?") in _last_issue(facts) else ""),
                         "severity": "medium" if s.get("posture") == "deliver" else ""}
                        for s in facts.get("subscriptions") or []] or
                       [{"text": "an empty desk — “subscribe to <topic>” starts one",
                         "meta": ""}])},
        {"kind": "list", "title": "the domain packages (0031 §5)",
         "items": _sev([{"text": d.get("topic") or "uncategorized",
                         "meta": d.get("meta", ""),
                         "severity": "medium" if d.get("doubted") else ""}
                        for d in facts.get("domains") or []] or
                       [{"text": "no domains yet — a gather starts one", "meta": ""}])},
        {"kind": "list", "title": "the mirror (0034)",
         "items": _sev([{"text": i.get("resident", "?"),
                         "meta": f"{i.get('exchanges', 0)} exchange(s) · "
                                 f"{len(i.get('repeats') or [])} repeated ask(s) · "
                                 f"{i.get('friction', 0)} friction",
                         "severity": "medium" if i.get("friction") else ""}
                        for i in facts.get("interop") or []] or
                       [{"text": "no reflections yet — the mirror reads the "
                                 "audiences on its beat", "meta": ""}])},
        {"kind": "doc", "title": "the portrait (0025)",
         "text": facts.get("profile_text") or
                 "a blank page — assert with “my profile: …” and it fills."},
        {"kind": "list", "title": "moments & markers (0024)",
         "items": _sev(facts.get("markers") or
                       [{"text": "no moments marked yet", "meta": "", "severity": ""}])},
    ]


def _room_becky(facts: dict) -> list[dict]:
    reqs = facts.get("requests") or []
    joins = [r for r in reqs if r.get("kind") == "join"]
    kinds: dict[str, int] = {}
    for r in reqs:
        kinds[r.get("kind", "?")] = kinds.get(r.get("kind", "?"), 0) + 1
    waiting = [r for r in reqs if r.get("status") in ("pending", "staged")]
    return [
        {"kind": "stat", "title": "the door",
         "items": [{"label": "leases granted",
                    "value": sum(1 for r in joins if r.get("status") == "done")},
                   {"label": "waiting at the gate", "value": len(waiting)},
                   {"label": "asks in all", "value": len(reqs)}]},
        {"kind": "bars", "title": "the queue by kind",
         "items": [{"label": k, "value": n} for k, n in
                   sorted(kinds.items(), key=lambda x: -x[1])[:8]]},
        {"kind": "list", "title": "waiting for you (0012)",
         "items": _sev([{"text": str(r.get("text") or r.get("kind", "?"))[:80],
                         "meta": f"{r.get('kind', '?')} · {r.get('status', '?')}",
                         "severity": "medium" if r.get("status") == "staged" else ""}
                        for r in waiting[:8]] or
                       [{"text": "nothing waits — the gate is quiet", "meta": ""}])},
    ]


def _room_charlotte(facts: dict) -> list[dict]:
    farm = _farm(facts)
    return [
        {"kind": "stat", "title": "the shed",
         "items": [{"label": "services", "value": len(farm)},
                   {"label": "serving",
                    "value": sum(1 for s in farm if s.get("state") == "serving")},
                   {"label": "quarantined",
                    "value": sum(1 for s in farm if s.get("state") == "quarantined")}]},
        {"kind": "bars", "title": "governed calls",
         "items": [{"label": s["name"], "value": int(s.get("calls") or 0)}
                   for s in sorted(farm, key=lambda s: -int(s.get("calls") or 0))[:8]]},
        {"kind": "list", "title": "the roster",
         "items": _sev([{"text": s["name"],
                         "meta": f"{s.get('kind', '?')} · {s.get('state', '?')}",
                         "severity": "medium" if s.get("state") == "quarantined" else ""}
                        for s in farm] or
                       [{"text": "nothing planted — this world consumes nothing",
                         "meta": ""}])},
    ]


def _room_ada(facts: dict) -> list[dict]:
    stalls = _stalls(facts)
    usage = facts.get("usage") or []
    usd = sum(float(u.get("usd") or 0) for u in usage)
    return [
        {"kind": "stat", "title": "the stable",
         "items": [{"label": "stalls", "value": len(stalls)},
                   {"label": "live", "value": sum(1 for s in stalls if
                                                  s.get("state") in ("available", "canaried"))},
                   {"label": "spent", "value": f"${usd:.4f}"}]},
        {"kind": "bars", "title": "thought on the meter",
         "items": [{"label": str(u.get("subject") or u.get("caller") or "?")[:24],
                    "value": int(u.get("calls") or 0)} for u in
                   sorted(usage, key=lambda u: -int(u.get("calls") or 0))[:8]]},
        {"kind": "list", "title": "the pasture calendar",
         "items": _sev([{"text": s["id"],
                         "meta": f"{s.get('class', '?')} · {s.get('state', '?')}"
                                 + (f" · expires {str(s['expires_at'])[:10]}"
                                    if s.get("expires_at") else ""),
                         "severity": "medium" if s.get("state") == "deprecated" else ""}
                        for s in stalls] or
                       [{"text": "none saddled — the legacy registry still routes",
                         "meta": ""}])},
    ]


def _room_grace(facts: dict) -> list[dict]:
    rows = facts.get("shelf") or []
    held = [r for r in facts.get("requests") or []
            if r.get("kind") == "improvement" and r.get("status") == "staged"]
    return [
        {"kind": "stat", "title": "the workshop",
         "items": [{"label": "assets on the shelf", "value": len(rows)},
                   {"label": "open proposals",
                    "value": sum(1 for r in rows if r.get("open"))},
                   {"label": "waiting for you", "value": len(held)},
                   {"label": "your feedback",
                    "value": sum(int(r.get("feedback") or 0) for r in rows)}]},
        {"kind": "bars", "title": "versions by asset",
         "items": [{"label": r["name"], "value": int(r.get("versions") or 0)}
                   for r in sorted(rows,
                                   key=lambda x: -int(x.get("versions") or 0))[:8]]},
        {"kind": "list", "title": "the shelf",
         "items": _sev([{"text": r["name"],
                         "meta": f"{r.get('versions', 0)} version(s)"
                                 + (" · lane holds" if r.get("open") else "")
                                 + (f" · {r['feedback']} feedback"
                                    if r.get("feedback") else ""),
                         "severity": "medium" if r.get("open") else ""}
                        for r in rows] or
                       [{"text": "a bare shelf — genesis plants on my first beat",
                         "meta": ""}])},
        {"kind": "doc", "title": "the approval package",
         "text": facts.get("package_text") or
                 "nothing staged — when a rewrite waits, what changed, why, and "
                 "the rollback all read here before you sign."},
    ]


_ROOMS = {"librarian": _room_librarian, "becky": _room_becky,
          "charlotte": _room_charlotte, "ada": _room_ada, "grace": _room_grace}


# ---------------------------------------------------------------- the audience record

def audience_body(resident: str, asked: str, reply: str, *, session: str = "",
                  voiced: bool = False) -> dict:
    """One exchange, witnessed: the resident authors it — the caller's words ride
    inside until humans carry signatures of their own (0012's signer registry)."""
    return {"parlor": resident, "asked": (asked or "")[:400], "reply": (reply or "")[:600],
            "session": session, "voiced": voiced, "at": NOW()}
