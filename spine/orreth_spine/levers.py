# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c, THE REMEDIATION RAIL · 2026-09-27
"""The remediation rail (canon 0005, P7 sp8 row 3c): the half of the
Resiliency loop that ACTS.

The finding (walk day, 2026-09-27): the SENSING half is a rail — a red
watch wakes the intention, a turn opens, the planner is asked, its reply
is filed, every hop recorded — and the REMEDIATION half was a
conversation: the planner was told a marker id and nothing else, so it
invented; nobody was told what levers exist, so a plan was a sentence and
the job landed on a reader; green was never attributed, so the loop could
neither learn nor stop churning (W72). Four cures, in the kernel's own
shapes:

(a) THE FORENSIC TURN — before anyone thinks, the kernel assembles a
    DOSSIER from the ground (`forensic`): the watch, its last readings,
    who it names and their state, the last acts on them, what happened
    the last time it went red, what was tried this time. A pure kernel
    read, no mind; handed to the planner in plain words (`dossier_words`)
    in place of a marker id.
(b) THE LEVER CATALOGUE — every governed act the kernel can pull is
    DECLARED as data in `spine/levers.v0.json` beside `tools.v0.json`
    (`catalogue`); the planner is shown the levers this door serves for
    the watch's metric (`remedies` · `lever_words`) and answers IN the
    catalogue (`read_lever`): "LEVER: body.restart name=echo — BECAUSE:
    …", or "LEVER: none — BECAUSE: …".
(c) THE KERNEL IS THE REMEDIATION RUNNER — a resident plans and reports;
    the kernel pulls the lever (`pull`) through the same doors a person
    would, under the intention's authority, as a recorded hop in the
    intention's own session: a routine lever runs at once, a
    consequential one holds at the interlock for a person's click (the
    guide's law: the kernel never lowers the ladder because it runs on
    its own), a grave one is never pulled. A resident never again
    receives a job it cannot do.
(d) THE ATTRIBUTED OUTCOME — after a lever the kernel re-reads the watch
    (`attribute`): green after our act = a recorded improvement WITH its
    cause; green with no act = recorded as self-healed, the turn closed
    without pretending; red after the lever = one more plan with what was
    tried, then the human with the dossier attached. The drift harness
    grades it (`harness.reds_answered`): every red is answered and every
    green attributed.

Every word here aimed at a human is plain (rule 13)."""
from __future__ import annotations

import json
import re
import secrets
from pathlib import Path

from . import envelope as ev, outbox

FORMAT = "orreth-levers/1"
CATALOGUE = Path(__file__).resolve().parents[1] / "levers.v0.json"      # beside tools.v0.json
DECLARED_KEYS = ("name", "description", "needs", "consequence", "for", "doors", "settles_s")
CLASSES = ("routine", "consequential", "grave")
DOOR = "python"                                        # the reference's door; the Rust kernel's is "rust"
KERNEL = "the kernel"
TRIES = 2                                              # levers per red episode before the human is told
NONE = "none"
OUTCOMES = ("cured", "self-healed", "still-red", "cancelled")

# ---- the catalogue: data both kernels read (b) ----------------------------------------

def catalogue(path: str | Path | None = None) -> list[dict]:
    """The levers' declarations, read from the one file beside the tools'
    (`spine/levers.v0.json`) — the SAME file the Rust kernel reads. Refuses
    in words: a wrong format, a lever missing a key, an unknown class, a
    name declared twice."""
    p = Path(path) if path is not None else CATALOGUE
    doc = json.loads(p.read_text("utf-8"))
    if doc.get("format") != FORMAT:
        raise ValueError(f"not a lever catalogue ({p}): format {doc.get('format')!r}, expected {FORMAT!r}")
    out, seen = [], set()
    for d in doc.get("levers") or []:
        missing = [k for k in DECLARED_KEYS if k not in d]
        if missing:
            raise ValueError(f"the lever declaration {d.get('name', '?')!r} lacks {', '.join(missing)}")
        if d["consequence"] not in CLASSES:
            raise ValueError(f"the {d['name']!r} lever declares an unknown class {d['consequence']!r} — "
                             f"the classes: {', '.join(CLASSES)}")
        if d["name"] in seen:
            raise ValueError(f"the lever {d['name']!r} is declared twice")
        seen.add(d["name"])
        out.append(d)
    return out


def lever_manifest(decl: dict) -> dict:
    """What a lever DECLARES, as the conformance pins it: name · words ·
    needs · class · the metrics it remedies · the doors that serve it."""
    return {"name": decl["name"], "description": decl["description"], "needs": decl["needs"],
            "consequence": decl["consequence"], "for": list(decl["for"]),
            "doors": list(decl["doors"]), "settles_s": int(decl["settles_s"])}


def declared(levers: list[dict], name: str) -> dict | None:
    return next((d for d in levers if d["name"] == name), None)


def remedies(levers: list[dict], metric: str, door: str = DOOR) -> list[dict]:
    """The levers this door serves that can remedy a watch on `metric`
    (conformance `lever_remedies`): declared for the metric (or for any,
    '*'), served by the door, never grave — the kernel never pulls a
    grave act as a remedy."""
    return [d for d in levers
            if door in d["doors"] and d["consequence"] != "grave"
            and (metric in d["for"] or "*" in d["for"])]


def lever_words(levers: list[dict]) -> str:
    """The catalogue as the planner reads it (conformance `lever_words`):
    one line per lever — its name with what it needs, then what it does
    and whether it holds for a person's yes."""
    if not levers:
        return "LEVERS this kernel can pull for this watch: none."
    lines = ["LEVERS this kernel can pull for this watch (name and what it needs · what it does):"]
    for d in levers:
        needs = " ".join(f"{k}=<{v}>" for k, v in d["needs"].items())
        hold = (" Holds for a person's yes before it runs."
                if d["consequence"] == "consequential" else " Runs at once.")
        lines.append(f"- {d['name']}{(' ' + needs) if needs else ''} · {d['description']}{hold}")
    return "\n".join(lines)


ANSWER_SHAPE = ("Reply on ONE line, in this shape and nothing else:\n"
                "LEVER: <name> <what it needs>=<value> — BECAUSE: <one plain sentence, from the dossier>\n"
                "or, when no lever fits: LEVER: none — BECAUSE: <one plain sentence>")


def remedy_words(serves: str, words: str, dossier_text: str, levers_text: str) -> str:
    """What the kernel asks the planner under a RED WATCH (conformance
    `remedy_words`): the intention, the dossier in plain words, the levers
    this door serves, and the one shape to answer in."""
    return (f"INTENTION (serves {serves}): {words}\n"
            f"THE DOSSIER — what the kernel read on the ground, no guessing needed:\n{dossier_text}\n"
            f"{levers_text}\n{ANSWER_SHAPE}")


_MARKS = "*#-> \"“'`"
_LEVER_RE = re.compile(
    r"^lever\s*:[\s*_`]*(none|[a-z][a-z0-9_.-]*)"
    r"((?:\s+[a-z_][a-z0-9_]*\s*=\s*(?:\"[^\"]*\"|“[^”]*”|'[^']*'|[^\s,;]+))*)"
    r"\s*[\s—–\-:,;.]*\s*(?:because\s*:?\s*)?(.*)$", re.I | re.S)
_ARG_RE = re.compile(r"([a-z_][a-z0-9_]*)\s*=\s*(\"[^\"]*\"|“[^”]*”|'[^']*'|[^\s,;]+)", re.I)


def read_lever(reply: str | None) -> dict | None:
    """The planner's answer read IN the catalogue (conformance
    `read_lever`): `{"lever": name | None, "args": {…}, "because": words}`
    — `None` for the name means "no lever fits"; the whole read is `None`
    when the reply is not in the shape at all (a sentence: the crew's
    road, as before). Marks and one short preface ending in a colon are
    forgiven; the name is folded to lower case; the because is one line
    of plain words, the trailing stop dropped."""
    head = " ".join((reply or "").split()).lstrip(_MARKS)
    m = _LEVER_RE.match(head)
    if not m:
        p = re.match(r"^[^:.]{0,60}:\s*", head)          # one short preface, then the shape
        if not p or p.group(0).strip().lower().startswith("lever"):
            return None
        m = _LEVER_RE.match(head[p.end():].lstrip(_MARKS))
        if not m:
            return None
    name = m.group(1).lower()
    args = {k.lower(): v.strip("\"'“”") for k, v in _ARG_RE.findall(m.group(2) or "")}
    because = " ".join(m.group(3).split()).strip(_MARKS + "”").rstrip(".")
    return {"lever": None if name == NONE else name, "args": args, "because": because}


# ---- the dossier in words (a) -----------------------------------------------------------

def _hms(iso: str | None) -> str:
    """`2026-09-27T20:11:03.120+00:00` → `20:11:03`; anything else as given."""
    if not iso:
        return "?"
    t = iso[11:19] if len(iso) >= 19 and iso[10] == "T" else iso
    return t


def ago_words(s: float | int | None) -> str:
    """`40` → `40 seconds ago`; `130` → `2 minutes ago`; `7300` → `2 hours ago`."""
    if s is None:
        return "just now"
    s = int(s)
    if s < 60:
        return f"{s} second{'' if s == 1 else 's'} ago"
    if s < 3600:
        m = s // 60
        return f"{m} minute{'' if m == 1 else 's'} ago"
    h = s // 3600
    return f"{h} hour{'' if h == 1 else 's'} ago"


def _args_words(args: dict | None) -> str:
    return " ".join(f"{k}={v}" for k, v in (args or {}).items())


def dossier_words(d: dict) -> str:
    """The dossier as the planner (and the human) reads it (conformance
    `dossier_words`): six lines, each a plain sentence — the watch, what
    it saw lately, who it names, the last acts on them, the last time it
    went red, what was tried this time. Pure: every clock and every
    'ago' is already in the dict."""
    w = d["watch"]
    since = f", since {_hms(w.get('since'))} ({ago_words(w.get('since_s'))})" if w.get("since") else ""
    out = [f"THE WATCH: {w['name']!r} is {w['state']} — red when {w['metric']} {w['op']} {w['threshold']}, "
           f"now {w['value']}{since}."]
    r = d.get("readings") or []
    out.append("WHAT IT SAW LATELY: " + (" · ".join(f"{x['to']} at {_hms(x['at'])} (value {x['value']})" for x in r)
                                         if r else "nothing before this") + ".")
    s = d.get("subjects") or []
    out.append("WHO IT NAMES: " + ("; ".join(f"{x['name']} ({x['kind']}) — {x['state']}" for x in s)
                                   if s else "no one by name — the metric is the world's") + ".")
    a = d.get("acts") or []
    out.append("THE LAST ACTS ON THEM: " + (" · ".join(f"{_hms(x['at'])} {x['words']}" for x in a)
                                            if a else "none recorded") + ".")
    last = d.get("last_red")
    if last:
        pulled = (f"the kernel pulled {last['lever']} {_args_words(last.get('args'))}".rstrip()
                  if last.get("lever") and last["lever"] != NONE else "no lever was pulled")
        out.append(f"THE LAST TIME IT WENT RED: {_hms(last['at'])} — {pulled}; "
                   f"{last.get('outcome') or 'still open'}"
                   + (f" ({last['note']})" if last.get("note") else "") + ".")
    else:
        out.append("THE LAST TIME IT WENT RED: never before.")
    t = d.get("tried") or []
    out.append("TRIED THIS TIME: " + (" · ".join(f"{x['lever']} {_args_words(x.get('args'))}".rstrip()
                                                 + f" → {x.get('outcome') or 'no change yet'}" for x in t)
                                      if t else "nothing yet") + ".")
    return "\n".join(out)


# ---- the outcome's words (d) ----------------------------------------------------------------

def cured_note(watch: str, lever: str, args: dict | None, because: str) -> str:
    """The improvement's note when the watch went green after the kernel's lever."""
    return (f"watch {watch!r} went green after the kernel pulled {lever} {_args_words(args)}".rstrip()
            + f" — the planner's reason: {because}")


def self_healed_note(watch: str) -> str:
    return f"watch {watch!r} went green on its own — the kernel pulled no lever; recorded as self-healed"


def still_red_note(watch: str, lever: str, args: dict | None, settles_s: int) -> str:
    return (f"watch {watch!r} is still red {settles_s} seconds after the kernel pulled {lever} "
            f"{_args_words(args)}".rstrip())


def cancelled_note(watch: str, lever: str, args: dict | None, why: str) -> str:
    return f"the {lever} {_args_words(args)}".rstrip() + f" lever for watch {watch!r} never ran — {why}"


def no_lever_note(watch: str, because: str) -> str:
    return f"no lever fits watch {watch!r} — the planner's reason: {because}"


def unserved_note(watch: str, lever: str) -> str:
    return f"the planner named {lever} for watch {watch!r} — a lever this door does not serve"


def pulled_words(lever: str, args: dict | None, because: str, result: str) -> str:
    """What the kernel's own row says after a routine lever ran (or refused)."""
    return (f"On the intention's authority the kernel pulled {lever} {_args_words(args)}".rstrip()
            + f": {result} Because {because}.")


def handed_words(watch: str, tried: list[dict], dossier_text: str) -> str:
    """The human is told, with the dossier attached, when the levers did not cure the red."""
    what = " · ".join(f"{t['lever']} {_args_words(t.get('args'))}".rstrip() for t in tried) or "no lever"
    return (f"Watch {watch!r} is still red after the kernel tried {what}. The kernel has no other lever "
            f"for it — this one is yours. What the kernel read on the ground:\n{dossier_text}")


def notice_words(watch: str, because: str, dossier_text: str) -> str:
    return (f"Watch {watch!r} is red and no lever the kernel holds fits it — the planner's reason: "
            f"{because}. This one is yours. What the kernel read on the ground:\n{dossier_text}")


# ---- the forensic turn: the dossier from the ground (a) --------------------------------------

def _events(conn, like: str, type_: str, limit: int = 6) -> list[dict]:
    cur = conn.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s"
                " AND convert_from(body, 'UTF8') LIKE %s ORDER BY outbox_id DESC LIMIT %s",
                (f"%{like}%", f"%{type_}%", limit))
    out = []
    for (b,) in cur.fetchall():
        try:
            e = ev.decode(bytes(b))
        except Exception:                             # noqa: BLE001 — a stray row never breaks the dossier
            continue
        if e.get("type") == type_:
            out.append(e)
    return out


def _secs_between(later, earlier) -> float | None:
    try:
        return max(0.0, (later - earlier).total_seconds())
    except Exception:                                 # noqa: BLE001
        return None


def forensic(conn, watch_id: str, *, episode: str | None = None, bodies: list[dict] | None = None) -> dict:
    """THE FORENSIC TURN: the dossier for a watch, read off the ground — no
    mind, no guessing. `bodies` is the kernel's own view of the bodies it
    seats as processes (the Rust kernel's; the reference seats none).
    `episode` names this red's first turn, so what was tried this time is
    listed apart from the last time."""
    from datetime import datetime, timezone
    from . import monitor
    from .body import PARKED
    cur = conn.cursor()
    snap = monitor.snapshot(conn, rails=False)
    w = next((x for x in snap["watches"] if x["watch_id"] == watch_id), None)
    if w is None:
        raise KeyError(watch_id)
    now = datetime.now(timezone.utc)
    since_s = None
    if w.get("since"):
        since_s = _secs_between(now, datetime.fromisoformat(w["since"]))
    watch = {"watch_id": watch_id, "name": w["name"], "metric": w["metric"], "op": w["op"],
             "threshold": w["threshold"], "value": w["value"], "state": w["state"],
             "since": w.get("since"), "since_s": since_s}
    readings = [{"at": e["occurred_at"], "to": e["payload"].get("to"), "value": e["payload"].get("value")}
                for e in _events(conn, watch_id, monitor.WATCH_TURNED)]
    subjects, names = [], []
    metric = w["metric"]
    if metric in ("bodies_dormant", "bodies_alive"):
        seated = {b["name"]: b for b in (bodies or [])}
        # W82 (walk #20): ONE read — the roster the snapshot judged is the roster the dossier names; a
        # second read of the leases a moment later once found nobody dormant under a red of value 2
        for b in snap["bodies"]:
            if b["alive"]:
                continue
            name, did, until = b["name"], b["did"], datetime.fromisoformat(b["until"])
            state = f"dormant — its lease lapsed {ago_words(_secs_between(now, until))}"
            b = seated.get(name)
            if b:
                if b.get("state") == "parked":
                    state += f"; PARKED by the kernel: it died {len(b.get('deaths') or [])} times"
                    last = " / ".join(b.get("last_words") or [])
                    if last:
                        state += f" (last words: “{last[:160]}”)"
                elif b.get("state"):
                    state += f"; the kernel's process is {b['state']}"
            else:
                parked = _events(conn, name, PARKED, limit=1)
                if parked and parked[0].get("correlation_id") == name:
                    p = parked[0]["payload"]
                    state += f"; PARKED by the kernel: it died {p.get('deaths')} times"
            subjects.append({"kind": "body", "name": name, "did": did, "state": state})
            names.append(name)
        # the roster's view of the others, so the planner knows who stands
        alive = [b["name"] for b in snap["bodies"] if b["alive"]]
        if alive and subjects:
            subjects.append({"kind": "crew", "name": "alive", "state": ", ".join(alive)})
    elif metric == "asks_received":
        cur.execute("SELECT ask_id, text, target, asked_at FROM spine_asks WHERE scope = %s"
                    " AND status = 'received' ORDER BY asked_at LIMIT 6", (ev.scope(),))
        for aid, text, target, at in cur.fetchall():
            subjects.append({"kind": "ask", "name": aid,
                             "state": f"waiting {ago_words(_secs_between(now, at))} — for "
                                      f"{target or 'any body'}: “{' '.join((text or '').split())[:80]}”"})
            names.append(aid)
    elif metric in ("outbox_pending", "oldest_outbox_age_s"):
        lag = snap["outbox"]
        subjects.append({"kind": "outbox", "name": "the outbox",
                         "state": f"{lag['pending']} facts waiting, the oldest {int(lag['oldest_age_s'] or 0)} s"})
    elif metric in ("minds_unhealthy", "minds_standing", "route_failures_1h"):
        from . import services
        for s in services.listing(conn, kind="mind"):
            if s["state"] in ("unhealthy", "retired"):
                subjects.append({"kind": "mind", "name": s["name"],
                                 "state": f"{s['state']} — {s.get('last_detail') or 'no detail'}"})
                names.append(s["name"])
    acts = []
    for name in names[:6]:
        cur.execute("SELECT asked_at, held::json->>'tool', status, person FROM spine_asks WHERE scope = %s"
                    " AND served_by = %s AND held IS NOT NULL AND held::json->'args'->>'name' = %s"
                    " ORDER BY asked_at DESC LIMIT 3", (ev.scope(), KERNEL, name))
        for at, tool, status, person in cur.fetchall():
            acts.append({"at": at.isoformat(), "words": f"{tool} on {name} — {status}, asked by {person}"})
        for e in _events(conn, name, PARKED, limit=2):
            if e.get("correlation_id") == name:
                acts.append({"at": e["occurred_at"],
                             "words": f"the kernel parked {name} after {e['payload'].get('deaths')} deaths"})
        cur.execute("SELECT pulled_at, lever, lever_args, outcome FROM spine_intent_turns"
                    " WHERE lever IS NOT NULL AND lever <> %s AND lever_args LIKE %s AND pulled_at IS NOT NULL"
                    " ORDER BY pulled_at DESC LIMIT 3", (NONE, f"%{name}%"))
        for at, lever, args, outcome in cur.fetchall():
            acts.append({"at": at.isoformat(), "words": f"the kernel pulled {lever} "
                         f"{_args_words(json.loads(args or '{}'))}".rstrip()
                         + (f" → {outcome}" if outcome else "")})
    acts.sort(key=lambda a: a["at"], reverse=True)
    acts = acts[:6]
    cur.execute("SELECT at, lever, lever_args, outcome, outcome_note FROM spine_intent_turns"
                " WHERE watch = %s AND outcome IS NOT NULL AND (%s::text IS NULL OR episode <> %s)"
                " ORDER BY at DESC LIMIT 1", (watch_id, episode, episode))
    r = cur.fetchone()
    last_red = ({"at": r[0].isoformat(), "lever": r[1], "args": json.loads(r[2] or "{}"),
                 "outcome": r[3], "note": r[4]} if r else None)
    tried = []
    if episode:
        cur.execute("SELECT lever, lever_args, outcome FROM spine_intent_turns WHERE episode = %s"
                    " AND lever IS NOT NULL ORDER BY at", (episode,))
        tried = [{"lever": l, "args": json.loads(a or "{}"), "outcome": o} for l, a, o in cur.fetchall()]
    return {"watch": watch, "readings": readings, "subjects": subjects, "acts": acts,
            "last_red": last_red, "tried": tried}


# ---- the kernel as the remediation runner (c) --------------------------------------------------

def kernel_row(conn, *, person: str, session: str | None, text: str, reply: str,
               parent_marker: str | None, note: str | None = None) -> str:
    """A hop the KERNEL itself records in the intention's session: an ask
    row served by the kernel, born replied, its marker under the turn's
    cause, its journey note and its reply on the rail — one transaction.
    The chat that promised the intention shows it."""
    from . import markers
    from .resident import JOURNEY, REPLY, ensure_schema as _asks
    _asks(conn); outbox.ensure_schema(conn); markers.ensure_schema(conn)
    ask_id = "ask_" + secrets.token_hex(8)
    mid = markers.new_id()
    marker = {"kind": "action", "id": mid, "parent": parent_marker, "by": KERNEL}
    chain = [person, KERNEL] if person != KERNEL else [KERNEL]
    j = ev.make_envelope(
        kind="event", type=JOURNEY, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ask_id, "hash": "sha256:-", "note": f"{KERNEL}: {note or text}"},
        correlation_id=ask_id, authority_chain=chain,
        aggregate={"type": "ask", "id": ask_id, "sequence": 1}, marker=marker)
    r = ev.make_envelope(
        kind="event", type=REPLY, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ask_id, "hash": ev.content_hash(reply), "proof": "L1"},
        correlation_id=ask_id, authority_chain=chain,
        aggregate={"type": "ask", "id": ask_id, "sequence": 2}, marker=marker)

    def domain(cur):
        markers.insert(cur, mid, "action", parent_marker, ask_id, KERNEL, (note or text)[:200])
        cur.execute(
            "INSERT INTO spine_asks (ask_id, text, person, status, reply, served_by, scope, session,"
            " marker, seq, proof, replied_at) VALUES (%s, %s, %s, 'replied', %s, %s, %s, %s, %s, 2, 'L1',"
            " clock_timestamp())", (ask_id, text, person, reply, KERNEL, ev.scope(), session, mid))
        outbox.add_row(cur, ev.encode(r), r["message_id"])

    outbox.commit_with_outbox(conn, ev.encode(j), j["message_id"], domain)
    return ask_id


def perform(conn, lever: str, args: dict, *, gateway=None, bodies=None) -> str:
    """A ROUTINE lever pulled through the same door a person would use —
    the result in words. A refusal is words too, never a raise: the
    outcome is judged by the watch, not by the lever's mood."""
    from . import services, stable
    name = str(args.get("name") or "").strip().lower()
    try:
        if lever in ("service.check", "mind.check"):
            c = services.check(conn, name, gateway=gateway, by=KERNEL)
            return f"{name} was probed — it reads {c.get('state') or ('healthy' if c.get('ok') else 'unhealthy')}" \
                   f"{(': ' + str(c.get('detail'))) if c.get('detail') else ''}."
        if lever in ("service.restore", "mind.restore"):
            gw = stable.Gateway()
            made = stable.restore_mind(conn, name, by=KERNEL, gw=gw if gw.ready() else None)
            return f"the {made['name']} {made['kind']} stands on the shelf again — a new fact, its rest in the record."
        if lever == "body.restart":
            if bodies is None:
                return "refused — this door seats no bodies as processes; that lever is the Rust kernel's."
            return str(bodies(name))
        return f"refused — {lever} is not a lever this door pulls."
    except (services.ServiceRefused, KeyError, ValueError) as e:
        return f"refused — {e}"


def pull(conn, intention: dict, *, turn_id: str, cause_marker: str | None, lever: dict, args: dict,
         because: str, gateway=None, bodies=None) -> dict:
    """THE KERNEL PULLS A LEVER under the intention's authority, as a hop
    in its session. Routine → performed now, the row born replied.
    Consequential → held at the interlock (`proof.hold_kernel_act`) for
    a person's click, with the planner's reason in the hold's words."""
    from . import proof
    level = proof.level_for(lever["consequence"])
    if lever["consequence"] == "consequential":
        text = (f"{lever['name']} {_args_words(args)}".rstrip()
                + f" — the kernel proposes it for the intention “{intention['words']}” because {because}")
        hid = proof.hold_kernel_act(conn, text=text, person=intention["added_by"], tool=lever["name"],
                                    args=args, level=level, session=intention.get("session"),
                                    cls=lever["consequence"])
        held = True
        ask_id = hid
    else:
        result = perform(conn, lever["name"], args, gateway=gateway, bodies=bodies)
        ask_id = kernel_row(conn, person=intention["added_by"], session=intention.get("session"),
                            text=f"the kernel pulls {lever['name']} {_args_words(args)}".rstrip(),
                            reply=pulled_words(lever["name"], args, because, result),
                            parent_marker=cause_marker,
                            note=f"pulled {lever['name']} {_args_words(args)}".rstrip() + f" — {result}")
        held = False
    with conn.transaction():
        conn.cursor().execute(
            "UPDATE spine_intent_turns SET lever = %s, lever_args = %s, because = %s, lever_ask = %s,"
            " pulled_at = CASE WHEN %s THEN NULL ELSE now() END, objective_ask = '-' WHERE turn_id = %s",
            (lever["name"], json.dumps(args), because, ask_id, held, turn_id))
    return {"turn_id": turn_id, "lever": lever["name"], "args": args, "ask_id": ask_id, "held": held}


def _close(conn, turn_id: str, outcome: str, note: str) -> None:
    with conn.transaction():
        conn.cursor().execute("UPDATE spine_intent_turns SET outcome = %s, outcome_at = now(),"
                              " outcome_note = %s WHERE turn_id = %s", (outcome, note, turn_id))


def attribute(conn, *, levers: list[dict] | None = None, bodies: list[dict] | None = None) -> list[dict]:
    """THE ATTRIBUTED OUTCOME: every open remediation turn re-read against
    its watch (the monitor judged first this beat). Green after our act →
    `cured`, an improvement marked WITH its cause; green with no act →
    `self-healed` (a hold still waiting is withdrawn: the act is not
    needed); red past the lever's settle → one more plan with what was
    tried, then the human with the dossier attached (`still-red`); a hold
    cancelled → `cancelled`. Returns what closed or moved."""
    from datetime import datetime, timezone
    from . import intent, markers, proof
    levers = levers if levers is not None else catalogue()
    cur = conn.cursor()
    cur.execute(
        "SELECT t.turn_id, t.intention_id, t.cause, t.watch, t.lever, t.lever_args, t.because, t.lever_ask,"
        " t.pulled_at, t.tries, t.episode, t.dossier, w.name, w.last_ok, w.metric, a.status, a.reply"
        " FROM spine_intent_turns t JOIN spine_watches w ON w.watch_id = t.watch"
        " LEFT JOIN spine_asks a ON a.ask_id = t.lever_ask"
        " WHERE t.outcome IS NULL AND t.watch IS NOT NULL AND w.scope = %s ORDER BY t.at", (ev.scope(),))
    rows = cur.fetchall()
    now = datetime.now(timezone.utc)
    moved = []
    for (tid, iid, cause, wid, lever, largs, because, lask, pulled_at, tries, episode, dossier,
         wname, last_ok, metric, hstatus, hreply) in rows:
        intention = intent.get(conn, iid)
        if intention is None:
            continue
        args = json.loads(largs or "{}")
        green = bool(last_ok)
        pulled = lever is not None and lever != NONE and pulled_at is not None
        holding = lask is not None and hstatus == "awaiting-confirm"
        if green:
            if holding:                                         # the act is not needed after all
                try:
                    proof.settle_kernel_act(conn, lask, approve=False, by=KERNEL,
                                            reason="withdrawn — the watch went green on its own")
                except proof.NotConfirmed:
                    pass
            if pulled:
                note = cured_note(wname, lever, args, because or "")
                m = markers.set_marker(conn, "improvement", ref=wid, by=KERNEL,
                                       parent=intention["marker"], note=note)
                _close(conn, tid, "cured", note)
                moved.append({"turn_id": tid, "outcome": "cured", "improvement": m["id"]})
            else:
                note = self_healed_note(wname)
                m = markers.set_marker(conn, "improvement", ref=wid, by=KERNEL,
                                       parent=intention["marker"], note=note)
                _close(conn, tid, "self-healed", note)
                moved.append({"turn_id": tid, "outcome": "self-healed", "improvement": m["id"]})
            continue
        # still red
        if lask is not None and hstatus == "cancelled" and not pulled:
            why = " ".join((hreply or "").split())[:160] or "the hold was cancelled"
            note = cancelled_note(wname, lever, args, why)
            markers.set_marker(conn, "observation", ref=wid, by=KERNEL, parent=intention["marker"], note=note)
            _close(conn, tid, "cancelled", note)
            moved.append({"turn_id": tid, "outcome": "cancelled"})
            continue
        if not pulled:
            continue                                            # waiting on the planner, or on a person
        decl = declared(levers, lever) or {"settles_s": 30}
        settles = int(decl.get("settles_s") or 30)
        waited = _secs_between(now, pulled_at) or 0.0
        if waited < settles:
            continue
        note = still_red_note(wname, lever, args, settles)
        markers.set_marker(conn, "observation", ref=wid, by=KERNEL, parent=intention["marker"], note=note)
        _close(conn, tid, "still-red", note)
        d = forensic(conn, wid, episode=episode, bodies=bodies)
        if int(tries or 1) < TRIES:                             # one more plan, with what was tried
            t = intent.plan(conn, intention, cause={"id": f"{cause}#{int(tries or 1) + 1}"},
                            observed=dossier_words(d), dossier=d,
                            levers=remedies(levers, metric, DOOR), parent=cause,
                            watch=wid, episode=episode, tries=int(tries or 1) + 1)
            moved.append({"turn_id": tid, "outcome": "still-red", "again": t.get("turn_id")})
        else:                                                   # the human, with the dossier attached
            words = handed_words(wname, d["tried"], dossier_words(d))
            aid = kernel_row(conn, person=intention["added_by"], session=intention.get("session"),
                             text=f"watch {wname!r} is still red after {TRIES} levers", reply=words,
                             parent_marker=cause, note=f"handed to the human: watch {wname!r} still red")
            moved.append({"turn_id": tid, "outcome": "still-red", "handed": aid})
    return moved
