# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp6, THE TWO CHIPS · 2026-10-09
"""THE TWO CHIPS (canon 0010 §8, lock 8 · 0005 Phase 8 sp6): identity and security v0.

Two firmware bodies of the third kind join the crew (`templates/firmware-identity.v0.json` ·
`templates/firmware-security.v0.json`) and the Experiment's gate closes WHOLE — the two honest
empty slots on the card since spoonful 4 are reviewers now, each asked by the kernel under the
experiment's marker (the hull's EVENT edge) and each writing a SIGNED VERDICT under its own DID
(rule 2: the evidence is the kernel's record, never the reviewer's own words):

- **identity** reviews THE TRIAL LIFE'S CLAIMS — WHO it joined as (the agent's own DID, the
  same self as the standing life: a new DID per life is a defect, rule 1), WHAT it said it is
  (the template hash it joined with against the candidate's hash), WHERE it stood (the
  experiment room, not the agent's seat) and that it LEFT (its wear closed when it stopped);
  the kernel checks the record, the chip judges and signs: `identity: kept | broken — <line>`.
  The chip also HOLDS THE CEREMONY AND THE SEATS in its recall (the people seated, the bodies
  seated, the key-checks of the day) and runs THE KEY-CHECK CADENCE (below).
- **security** reviews THE CANDIDATE'S DIFF against the standing version — the capabilities
  WIDENED or narrowed (a tool it may call, a binding it may wear), the graph, the mind and the
  policy it would run under — and reads THE REFUSALS GROUND (`spine_refusals`: a body turned
  away at the join for stepping outside its placement) for the agent under review:
  `security: clear | concern — <line>`. A widened capability is never a verdict by itself; the
  chip weighs it and says why.

THE KEY-CHECK (JB's pin of 2026-09-26, lifted here): the kernel asks every seated body, on a
cadence (`SPINE_KEYCHECK_S`, 300 s; `0` turns it off), to prove it is WHO and WHAT it says —
the join desk's challenge repeated: a fresh nonce the kernel issued itself, which the body
signs with the key behind its DID (`desk.challenge_payload`, the same bytes as the knock) and
answers with its public key and the template hash it stands on; the kernel verifies (the key
derives the DID; the signature stands over the kernel's own nonce; the hash is the one it
joined as — `desk.prove`) and records the verdict. The body NEVER marks itself proven. A body
silent past the desk's two minutes, a signature that does not stand or a hash that is not the
join's is a FAILED check — a fact, a watch metric (`key_checks_failed`) and the kernel's
SEVENTH watch at light, red while a seated body cannot prove itself.

Law for law with the Rust kernel (`chips.rs` · `chips_live.rs`, fixture `chips-v0.json`).
"""
from __future__ import annotations

import json
import os
import re
import secrets

from . import desk
from . import envelope as ev
from . import outbox

KERNEL = "the kernel"
IDENTITY, SECURITY = "identity", "security"
CHIPS = (IDENTITY, SECURITY)
FUNCTIONS = {"identify": IDENTITY, "secure": SECURITY}        # a template's `function` → the reviewer it is
IDENTITY_WORDS = ("kept", "broken")
SECURITY_WORDS = ("clear", "concern")

KEYCHECK_CMD = "orreth.resident.keycheck.v1"                 # the kernel's command to a body: prove yourself
KEYCHECK_ASKED = "orreth.keycheck.asked.v1"                  # the challenge issued (the nonce is the kernel's)
KEYCHECK_VERDICT = "orreth.keycheck.v1"                      # the kernel's verdict on the proof — passed · failed
CADENCE_DIAL, CADENCE_DEFAULT = "SPINE_KEYCHECK_S", 300      # how often a seated body is asked; 0 = off
WAIT_S = desk.NONCE_S                                        # the desk's two minutes: silent past it is a failed check
KEYCHECK_WATCH = "key_checks_failed"                         # the kernel's seventh watch at light
KEYCHECK_WINDOW_H = 24                                       # the metric's window: the checks of the last day

CLAIMS = ("who", "what", "where", "left")


# ---- the law (pure; mirrored in chips.rs) ------------------------------------------------------

def _h8(h: str | None) -> str:
    """Eight characters of a declaration hash AFTER its `sha256:` prefix (W113: `sha256:0` said nothing)."""
    h = str(h or "")
    h = h[7:] if h.startswith("sha256:") else h
    return h[:8] if h else "?"


def lease_claims(exp: dict, trial: dict | None, standing_did: str | None) -> list[dict]:
    """THE TRIAL LIFE'S CLAIMS against the kernel's record — four claims, each `{claim, kept, said}`.
    `trial` is the trial life's join as the ground holds it (`did · life · template_hash · scope ·
    wear_open`), None when no life joined the room. `standing_did` is the agent's standing self
    (its latest join outside the room), None on a first cut."""
    if trial is None:
        return [{"claim": c, "kept": False, "said": "no trial life joined the experiment room — the candidate never stood"}
                for c in CLAIMS]
    out = []
    if standing_did is None:
        out.append({"claim": "who", "kept": True,
                    "said": f"joined as {trial.get('did')} — the first life of this self; no standing life to compare"})
    elif trial.get("did") == standing_did:
        out.append({"claim": "who", "kept": True,
                    "said": f"joined as {trial['did']} — the same self as the standing life (life {trial.get('life')})"})
    else:
        out.append({"claim": "who", "kept": False,
                    "said": f"joined as {trial.get('did')} but the standing life is {standing_did} — another self (rule 1)"})
    want = exp.get("candidate_hash")
    if trial.get("template_hash") == want:
        out.append({"claim": "what", "kept": True, "said": f"stood on the candidate's declaration ({_h8(want)})"})
    else:
        out.append({"claim": "what", "kept": False,
                    "said": f"said it was {_h8(trial.get('template_hash'))} but the candidate is {_h8(want)}"})
    if trial.get("scope") == exp.get("room"):
        out.append({"claim": "where", "kept": True, "said": "stood in the experiment room, nowhere else"})
    else:
        out.append({"claim": "where", "kept": False,
                    "said": f"stood at {trial.get('scope')} — not the experiment room {exp.get('room')}"})
    if trial.get("wear_open"):
        out.append({"claim": "left", "kept": False, "said": "its wear is still open — the trial life did not stop whole"})
    else:
        out.append({"claim": "left", "kept": True, "said": "left the room — its wear closed when it stopped"})
    return out


def claims_words(claims: list[dict]) -> str:
    """The claims in one line for the ask and the recall."""
    broken = [c for c in claims if not c["kept"]]
    head = "every claim kept" if not broken else f"{len(broken)} of {len(claims)} claims broken"
    return head + ": " + "; ".join(f"{c['claim']} — {c['said']}" for c in claims)


def _caps(m: dict | None) -> set[str]:
    return set(str(c) for c in ((m or {}).get("capabilities") or []))


def _mind_of(m: dict | None) -> str | None:
    mind = (m or {}).get("mind") or {}
    return mind.get("pin") or mind.get("model")


def capability_diff(current: dict | None, candidate: dict) -> dict:
    """THE CANDIDATE'S DIFF against the standing version's manifest: the capabilities widened and
    narrowed, the graph, the mind, the policy, the binding, the summon word — `first` when no
    version stands (everything the candidate declares is new)."""
    cur_caps, cand_caps = _caps(current), _caps(candidate)
    d = {"first": current is None,
         "widened": sorted(cand_caps - cur_caps), "narrowed": sorted(cur_caps - cand_caps),
         "graph": None, "mind": None, "policy": None, "binding": None, "summonable": None}
    for key in ("graph", "policy", "binding"):
        a, b = (current or {}).get(key), candidate.get(key)
        if a != b:
            d[key] = [a, b]
    a, b = _mind_of(current), _mind_of(candidate)
    if a != b:
        d["mind"] = [a, b]
    a, b = bool((current or {}).get("summonable")), bool(candidate.get("summonable"))
    if a != b:
        d["summonable"] = [a, b]
    return d


def diff_words(diff: dict) -> str:
    """The diff in plain words — what the candidate may do that the standing version may not."""
    bits = []
    if diff.get("first"):
        bits.append("a first version — every capability it declares is new")
    if diff.get("widened"):
        bits.append("WIDENED: " + ", ".join(diff["widened"]))
    if diff.get("narrowed"):
        bits.append("narrowed: " + ", ".join(diff["narrowed"]))
    for key, word in (("graph", "the graph"), ("mind", "the mind"), ("policy", "the policy"), ("binding", "the binding")):
        v = diff.get(key)
        if v:
            bits.append(f"{word} {v[0] or 'unset'} → {v[1] or 'unset'}")
    if diff.get("summonable"):
        bits.append("summonable " + ("now" if diff["summonable"][1] else "no longer"))
    if not bits:
        return "nothing changes in what the candidate may do — the same capabilities, graph, mind and policy"
    return "; ".join(bits)


def review_form(reviewer: str) -> str:
    """The form a chip's answer takes, appended to the kernel's ask."""
    if reviewer == IDENTITY:
        return ("Judge whether the trial life is WHO and WHAT it says — the claims above are the kernel's record. "
                "End with exactly one line `identity: kept` or `identity: broken` — <one line of reason>.")
    return ("Judge what the candidate may do that the standing version may not, and whether anything on the refusals "
            "ground speaks against it. End with exactly one line `security: clear` or `security: concern` — <one line of reason>.")


_IDENTITY_RX = re.compile(r"^\s*\**\s*identity\s*\**\s*:\s*\**\s*(kept|broken)\b", re.I | re.M)
_SECURITY_RX = re.compile(r"^\s*\**\s*security\s*\**\s*:\s*\**\s*(clear|concern)\b", re.I | re.M)


def _line_after(text: str, head: str) -> str | None:
    for ln in (text or "").splitlines():
        if ln.lower().lstrip("* ").startswith(head + ":") and "—" in ln:
            return ln.split("—", 1)[1].strip().rstrip("*").strip() or None
    return None


def identity_of(text: str | None) -> dict:
    """The identity chip's verdict read off its words by the form; None where the form was not kept."""
    m = _IDENTITY_RX.search(text or "")
    return {"identity": m.group(1).lower() if m else None, "line": _line_after(text or "", "identity") if m else None}


def security_of(text: str | None) -> dict:
    m = _SECURITY_RX.search(text or "")
    return {"security": m.group(1).lower() if m else None, "line": _line_after(text or "", "security") if m else None}


def verdict_of(reviewer: str, text: str | None) -> tuple[dict, bool]:
    """A chip's verdict and whether the form was kept (a verdict not in the form is said, never guessed)."""
    if reviewer == IDENTITY:
        v = identity_of(text)
        return v, v["identity"] is not None
    v = security_of(text)
    return v, v["security"] is not None


def slot_words(reviewer: str, slot: dict | None) -> str:
    """One chip's line on the proposal card."""
    s = slot or {}
    if reviewer == IDENTITY:
        if s.get("identity"):
            w = f"the identity chip finds the trial life's claims {s['identity']}"
            return w + (f": {s['line']}" if s.get("line") else "")
        return f"the identity chip: {s.get('missing') or 'no verdict yet'}"
    if s.get("security"):
        w = f"the security chip reads the candidate as {s['security']}"
        return w + (f": {s['line']}" if s.get("line") else "")
    return f"the security chip: {s.get('missing') or 'no review yet'}"


def chip_holds(reviewers: dict) -> list[str]:
    """What the chips say that HOLDS a promotion: broken claims, a security concern."""
    out = []
    if ((reviewers or {}).get(IDENTITY) or {}).get("identity") == "broken":
        out.append("the identity chip finds the trial life's claims broken")
    if ((reviewers or {}).get(SECURITY) or {}).get("security") == "concern":
        out.append("the security chip reads a concern")
    return out


# ---- the key-check law -------------------------------------------------------------------------

def cadence_s() -> int:
    """The dial: how often a seated body is asked to prove itself; 0 turns the cadence off."""
    try:
        return max(0, int(os.environ.get(CADENCE_DIAL, CADENCE_DEFAULT)))
    except ValueError:
        return CADENCE_DEFAULT


def keycheck_due(last_asked_s_ago: float | None, cadence: int) -> bool:
    """Is a body due its check? Never with the cadence off; at once when never asked; else past the cadence."""
    if cadence <= 0:
        return False
    return last_asked_s_ago is None or float(last_asked_s_ago) >= float(cadence)


def keycheck_payload(did: str, nonce: str) -> dict:
    """The bytes the body signs — the join desk's challenge, repeated (one act, one shape)."""
    return desk.challenge_payload(did, nonce)


def keycheck_answer(identity, nonce: str, template_hash: str) -> dict:
    """The body's answer: its proof over the kernel's nonce, the key behind its DID beside it (a DID
    is a hash, so the key rides along), and WHAT it stands on. The body never marks itself proven."""
    return {"sig": desk.proof_of(identity, nonce), "public_key": identity.verify_key_hex, "what": template_hash}


def keycheck_verdict(did: str, nonce: str, answer: dict | None, joined_as: str | None, waited_s: float) -> dict:
    """The kernel's verdict on a check — `{ok, words}`: a body silent past the desk's two minutes,
    a key that does not derive the DID or a signature not over the kernel's nonce, a hash that is
    not the one it joined as — each failed in words; else proven."""
    if not answer:
        if waited_s >= WAIT_S:
            return {"ok": False, "words": f"silent — no proof within {WAIT_S // 60} minutes of the kernel's challenge"}
        return {"ok": None, "words": "waiting for the body's proof"}
    pk, sig, what = str(answer.get("public_key") or ""), answer.get("sig"), str(answer.get("what") or "")
    if not desk.prove(did, pk, nonce, sig):
        return {"ok": False, "words": "the signature does not stand over the kernel's nonce under the key behind this DID — not WHO it says"}
    if joined_as is not None and what != joined_as:
        return {"ok": False, "words": f"it says it stands on {_h8(what)} but joined as {_h8(joined_as)} — not WHAT it says"}
    return {"ok": True, "words": f"proven — who it says ({did[-8:]}) and what it says ({_h8(what)})"}


def keycheck_watch(failed: int | None) -> dict:
    """The kernel's seventh watch at light: `key_checks_failed > 0` is red — a seated body could
    not prove it is who and what it says (the identity chip's cadence)."""
    return {"metric": KEYCHECK_WATCH, "op": ">", "threshold": 0, "severity": "red",
            "state": ("unknown" if failed is None else ("red" if int(failed) > 0 else "green")),
            "words": (f"{failed} key-check{'s' if failed != 1 else ''} failed in the last day — a seated body could not prove itself"
                      if failed else "every seated body proved itself on the cadence")}


def keycheck_words(checked: int, failed: int, pending: int, cadence: int) -> str:
    """The glass's line on the key-check."""
    if cadence <= 0:
        return "the key-check cadence is off (SPINE_KEYCHECK_S=0) — no body is asked to prove itself"
    if checked == 0 and pending == 0:
        return f"no body has been asked to prove itself yet — every {cadence} s once one is seated"
    tail = f"{pending} waiting" if pending else "none waiting"
    return (f"{checked} key-check{'s' if checked != 1 else ''} in the last day, {failed} failed, {tail} — "
            f"every seated body is asked every {cadence} s to prove who and what it is")


# ---- the record ----------------------------------------------------------------------------------

DDL = (
    "CREATE TABLE IF NOT EXISTS spine_keychecks ("
    " check_id text PRIMARY KEY, scope text NOT NULL, did text NOT NULL, name text NOT NULL,"
    " nonce text NOT NULL, joined_as text,"
    " asked_at timestamptz NOT NULL DEFAULT now(), answered_at timestamptz,"
    " public_key text, sig text, what text,"
    " ok boolean, words text, verified_at timestamptz)",
    "CREATE INDEX IF NOT EXISTS spine_keychecks_scope_did ON spine_keychecks (scope, did, asked_at DESC)",
    "CREATE INDEX IF NOT EXISTS spine_keychecks_open ON spine_keychecks (scope, verified_at) WHERE verified_at IS NULL",
    # the chips' evidence rides the experiment's row: the trial life's claims and the candidate's diff as the beat read them
    "ALTER TABLE spine_experiments ADD COLUMN IF NOT EXISTS claims text",
    "ALTER TABLE spine_experiments ADD COLUMN IF NOT EXISTS diff text",
)


def ensure_schema(conn) -> None:
    if not outbox.once(conn, "chips"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")
        for stmt in DDL:
            cur.execute(stmt)


def _fact(cur, type_: str, ref: str, payload: dict, by: list[str], scope: str | None = None) -> None:
    e = ev.make_envelope(kind="event", type=type_, universe_id=ev.universe(), scope_path=scope or ev.universe(),
                         payload={"ref": ref, "hash": ev.content_hash(payload), **payload},
                         correlation_id=ref, authority_chain=by)
    outbox.add_row(cur, ev.encode(e), e["message_id"])


# ---- the evidence the chips read (the kernel's record, packed into the ask and the recall) ---------

def trial_life(conn, exp: dict) -> dict | None:
    """The trial life's join in the experiment room as the ground holds it, with whether its wear is
    still open — None when no life of the agent joined the room."""
    cur = conn.cursor()
    cur.execute("SELECT did, life, template_hash, scope FROM spine_joins WHERE name = %s AND scope = %s"
                " ORDER BY join_id DESC LIMIT 1", (exp["agent"], exp["room"]))
    r = cur.fetchone()
    if r is None:
        return None
    cur.execute("SELECT count(*) FROM spine_wear WHERE did = %s AND life = %s AND until IS NULL", (r[0], r[1]))
    return {"did": r[0], "life": int(r[1]), "template_hash": r[2], "scope": r[3], "wear_open": int(cur.fetchone()[0]) > 0}


def standing_did(conn, exp: dict) -> str | None:
    """The agent's standing self — its latest join OUTSIDE the experiment room, in this universe."""
    cur = conn.cursor()
    cur.execute(f"SELECT did FROM spine_joins WHERE name = %s AND scope <> %s AND {ev.WITHIN} ORDER BY join_id DESC LIMIT 1",
                (exp["agent"], exp["room"], *ev.within_params(ev.universe())))
    r = cur.fetchone()
    return r[0] if r else None


def claims_for(conn, exp: dict) -> list[dict]:
    return lease_claims(exp, trial_life(conn, exp), standing_did(conn, exp))


def diff_for(conn, exp: dict) -> dict:
    """The candidate's diff against the standing version's manifest on the shelf."""
    from . import services
    current = None
    if exp.get("current_version"):
        row = services.get(conn, f"{exp['agent']}.template")
        current = (row or {}).get("manifest")
    return capability_diff(current, exp.get("candidate") or {})


def refusals_for(conn, name: str | None = None, hours: int = 24) -> list[dict]:
    """THE REFUSALS GROUND: the bodies turned away in this universe over the window — at the join
    (`spine_refusals`: a placement or the seats refused) and at the desk (`spine_desk` denied: a bad
    proof, a no, a hold nobody answered) — one body's when named. The security chip reads it; a body
    that keeps knocking where it may not stand is what it looks for. At v0 the ground holds the
    doors' refusals; a held act a seat was refused is the proof door's record, not read here (said)."""
    cur = conn.cursor()
    w, p = ev.WITHIN, ev.within_params(ev.universe())
    q = (f"SELECT name, did, kind, reasons, refused_at, 'the join' FROM spine_refusals WHERE {w}"
         f" AND refused_at > now() - make_interval(hours => %s)")
    args: list = [*p, hours]
    if name:
        q += " AND name = %s"
        args.append(name)
    cur.execute(q + " ORDER BY refusal_id DESC LIMIT 20", args)
    rows = list(cur.fetchall())
    cur.execute("SELECT to_regclass('spine_desk')")
    if cur.fetchone()[0] is not None:
        q = (f"SELECT name, did, kind, '[\"denied at the desk\"]', updated_at, 'the desk' FROM spine_desk WHERE {w}"
             f" AND status = 'denied' AND updated_at > now() - make_interval(hours => %s)")
        args = [*p, hours]
        if name:
            q += " AND name = %s"
            args.append(name)
        cur.execute(q + " ORDER BY updated_at DESC LIMIT 20", args)
        rows += list(cur.fetchall())
    out = []
    for r in sorted(rows, key=lambda r: r[4], reverse=True)[:20]:
        reasons = r[3]
        try:
            reasons = json.loads(reasons) if isinstance(reasons, str) else reasons
        except ValueError:
            reasons = [str(reasons)]
        out.append({"name": r[0], "did": r[1], "kind": r[2], "reasons": reasons, "at": r[4].isoformat(), "door": r[5]})
    return out


def refusals_words(rows: list[dict], name: str | None = None) -> str:
    who = f"for {name}" if name else "in this universe"
    if not rows:
        return f"THE REFUSALS GROUND {who}: nothing in the last day — no body was turned away at the join or the desk"
    return (f"THE REFUSALS GROUND {who}: {len(rows)} refusal{'s' if len(rows) != 1 else ''} in the last day — "
            + "; ".join(f"{r['name']} ({r['kind']}) turned away at {r.get('door', 'the join')} {r['at'][:19]}: "
                        f"{', '.join(map(str, r['reasons']))[:160]}" for r in rows))


def seats_held(conn) -> dict:
    """THE CEREMONY AND THE SEATS as the identity chip holds them: the people seated now (by role),
    the bodies alive, and the key-checks of the day."""
    cur = conn.cursor()
    cur.execute(f"SELECT role, count(*) FROM spine_seats WHERE left_at IS NULL AND expiry > now() AND role <> 'body' AND {ev.WITHIN} GROUP BY role",
                ev.within_params(ev.universe()))      # W113: a body's lease is a seat with the role `body` — the bodies are counted below, never as people
    people = {r[0]: int(r[1]) for r in cur.fetchall()}
    cur.execute(f"SELECT count(*) FROM spine_leases WHERE until > now() AND {ev.WITHIN}", ev.within_params(ev.universe()))
    bodies = int(cur.fetchone()[0])
    return {"people": people, "bodies": bodies, "keychecks": keycheck_tally(conn)}


def seats_words(s: dict) -> str:
    ppl = ", ".join(f"{n} {role}" for role, n in sorted((s.get("people") or {}).items())) or "nobody"
    k = s.get("keychecks") or {}
    return (f"THE SEATS: {ppl} seated by the ceremony; {s.get('bodies', 0)} bod{'ies' if s.get('bodies', 0) != 1 else 'y'} alive on a lease; "
            + keycheck_words(int(k.get("checked") or 0), int(k.get("failed") or 0), int(k.get("pending") or 0), int(k.get("cadence") or 0)))


# ---- the key-check on the ground ------------------------------------------------------------------

def keycheck_tally(conn, hours: int = KEYCHECK_WINDOW_H) -> dict:
    """The checks of the window: verified · failed · pending, the latest, the cadence."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT count(*) FILTER (WHERE verified_at IS NOT NULL), count(*) FILTER (WHERE ok IS FALSE),"
                f" count(*) FILTER (WHERE verified_at IS NULL), max(verified_at) FROM spine_keychecks"
                f" WHERE {ev.WITHIN} AND asked_at > now() - make_interval(hours => %s)",
                (*ev.within_params(ev.universe()), hours))
    r = cur.fetchone()
    return {"checked": int(r[0] or 0), "failed": int(r[1] or 0), "pending": int(r[2] or 0),
            "last": r[3].isoformat() if r[3] else None, "cadence": cadence_s()}


def key_checks_failed(conn) -> int:
    """The watch metric: the failed checks of the last day in this universe."""
    return keycheck_tally(conn)["failed"]


def listing(conn, limit: int = 50) -> list[dict]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT check_id, name, did, asked_at, answered_at, ok, words, verified_at FROM spine_keychecks"
                f" WHERE {ev.WITHIN} ORDER BY asked_at DESC LIMIT %s", (*ev.within_params(ev.universe()), limit))
    return [{"check_id": r[0], "name": r[1], "did": r[2], "asked_at": r[3].isoformat(),
             "answered_at": r[4].isoformat() if r[4] else None, "ok": r[5], "words": r[6],
             "verified_at": r[7].isoformat() if r[7] else None} for r in cur.fetchall()]


def command_for(check_id: str, did: str, name: str, nonce: str) -> dict:
    """The kernel's command to one body: prove yourself — the nonce rides the command; the body
    answers on the ground (`answer`)."""
    u = ev.universe()
    payload = {"ref": check_id, "hash": ev.content_hash({"did": did, "nonce": nonce}), "target": name, "did": did, "nonce": nonce}
    return ev.make_envelope(kind="command", type=KEYCHECK_CMD, universe_id=u, scope_path=u, payload=payload,
                            correlation_id=check_id, authority_chain=[KERNEL])


def answer(conn, body, env: dict) -> None:
    """THE BODY'S SIDE: a key-check command landed — sign the kernel's nonce with the key behind my
    DID and write my proof on the row; the verdict is the kernel's, never mine. A check not mine
    (another DID's) is left alone, said in nothing."""
    pl = env.get("payload") or {}
    if str(pl.get("did") or "") != body.identity.did:
        return
    a = keycheck_answer(body.identity, str(pl.get("nonce") or ""), body.template_hash)
    conn.cursor().execute(
        "UPDATE spine_keychecks SET answered_at = clock_timestamp(), public_key = %s, sig = %s, what = %s"
        " WHERE check_id = %s AND did = %s AND answered_at IS NULL",
        (a["public_key"], json.dumps(a["sig"]), a["what"], str(pl.get("ref") or ""), body.identity.did))


def beat(conn, publish=None, *, cadence: int | None = None, now_s: float | None = None) -> list[str]:
    """THE KEY-CHECK BEAT (one kernel, under the beat lock): (1) verify every answered check and
    fail the silent ones past the desk's wait — the verdict a fact; (2) challenge every seated body
    whose last challenge is older than the cadence — a row, a fact, a command over the rail to the
    body's own queue. `publish` None (the reference's tests) records the challenge without the rail."""
    ensure_schema(conn)
    cad = cadence_s() if cadence is None else int(cadence)
    moved: list[str] = []
    if cad <= 0:
        return moved
    u = ev.universe()
    cur = conn.cursor()
    # 1. the verdicts
    cur.execute(f"SELECT check_id, did, name, nonce, joined_as, public_key, sig, what, answered_at IS NOT NULL,"
                f" extract(epoch FROM (now() - asked_at)) FROM spine_keychecks WHERE verified_at IS NULL AND {ev.WITHIN}",
                ev.within_params(u))
    for row in cur.fetchall():
        cid, did, name, nonce, joined_as, pk, sig, what, answered, waited = row
        ans = None
        if answered:
            try:
                sig_obj = json.loads(sig) if isinstance(sig, str) else sig
            except ValueError:
                sig_obj = None
            ans = {"public_key": pk, "sig": sig_obj, "what": what}
        v = keycheck_verdict(did, nonce, ans, joined_as, float(waited or 0))
        if v["ok"] is None:
            continue
        with conn.transaction():
            c2 = conn.cursor()
            c2.execute("UPDATE spine_keychecks SET ok = %s, words = %s, verified_at = clock_timestamp() WHERE check_id = %s",
                       (v["ok"], v["words"], cid))
            _fact(c2, KEYCHECK_VERDICT, cid, {"did": did, "name": name, "ok": v["ok"], "words": v["words"]}, [KERNEL])
        moved.append(f"{name}: {v['words']}" if v["ok"] else f"{name}: FAILED — {v['words']}")
    # 2. the challenges
    cur.execute(f"SELECT l.did, l.name, extract(epoch FROM (now() - k.asked_at)) FROM spine_leases l"
                f" LEFT JOIN LATERAL (SELECT asked_at FROM spine_keychecks WHERE did = l.did ORDER BY asked_at DESC LIMIT 1) k ON true"
                f" WHERE l.until > now() AND {ev.WITHIN.replace('scope', 'l.scope')}", ev.within_params(u))
    for did, name, ago in cur.fetchall():
        if not keycheck_due(None if ago is None else float(ago), cad):
            continue
        cur.execute("SELECT template_hash FROM spine_joins WHERE did = %s ORDER BY join_id DESC LIMIT 1", (did,))
        j = cur.fetchone()
        joined_as = j[0] if j else None
        cid, nonce = "kc_" + secrets.token_hex(6), secrets.token_hex(16)
        with conn.transaction():
            c2 = conn.cursor()
            c2.execute("INSERT INTO spine_keychecks (check_id, scope, did, name, nonce, joined_as) VALUES (%s, %s, %s, %s, %s, %s)",
                       (cid, u, did, name, nonce, joined_as))
            _fact(c2, KEYCHECK_ASKED, cid, {"did": did, "name": name}, [KERNEL])
        if publish is not None:                       # the command rides the rail to the body's own queue, after the row stands
            publish(command_for(cid, did, name, nonce))
        moved.append(f"{name}: challenged to prove who and what it is")
    return moved
