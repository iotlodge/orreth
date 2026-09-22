# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp2, the compliance export · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W19 (the refused ask in the record) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the tool hop reads the service DID · 2026-09-22
"""The compliance export (canon 0005 P6 sp2 · AG-7): the chain, proven to
a stranger.

A bundle (orreth.compliance/1) is every ask, hold, proof offered, reply,
include act, tool call, intention stop and marker set inside ONE scope — a session,
a window, or a marker root (an objective or intention and everything
under it) — in the order it happened, each row wearing what the wire
carried: the authority chain END TO END (the origin human → the residents
whose results were read → the firmware → the kernel), the proof level the
act wore, and its marker lineage (the WHY). Nothing here is reconstructed:
a row's chain is the chain on its envelope in the outbox log, and a hop
whose chain does not run from the origin human to the body that acted is
said to be BROKEN — counted, never hidden.

Integrity is a hash chain over the rows: h0 = sha256(canonical(row0)),
h_i = sha256(ascii(h_{i-1}) || canonical(row_i)) — `envelope.canonical`
bytes, so the Rust plane produces the same digests from the same rows
(0008: the fixture is `conformance/export-v0.json`). `verify` recomputes
it and re-derives every row's chain status from the row's own fields: a
truncated chain changes the bytes, and the bundle fails.

A bundle only ever holds the requester's OWN asks (P11: another person's
words are grave to export — that door is a named seam, not built). An
opt-out session's rows carry no words. The export is a READ: it writes
nothing (rule 11 has nothing to stop).

Signing: when a signer (an `Identity`) is given, the root hash is signed
Ed25519 and the bundle names the key; the glass has no kernel self yet, so
its door exports unsigned — `signed_by: null`, honestly.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re

from . import envelope as ev
from .markers import INCLUDES, MARKER_SET
from .resident import ASK_RECEIVED, CONFIRM_NEEDED, REPLY

CONTRACT = "orreth.compliance/1"
HASHING = ("sha256; h0 = sha256(canonical(row0)); "
           "h_i = sha256(ascii_hex(h_{i-1}) || canonical(row_i)); root_hash = h_last")
WORDS_MAX = 500                                    # the CSV's cut, marked when it cuts
INTENTION_STOPPED = "orreth.intention.stopped.v1"   # intent.py's fact (no import cycle)
PROOF_ATTEMPT = "orreth.proof.attempt.v1"           # proof.py's fact
TOOL_CALLED = "orreth.tool.called.v1"               # tools.py's fact: the tool hop
ASK_REFUSED = "orreth.ask.refused.v1"               # dispatch.py's fact: an ask to a body not here (W19)
KERNEL = "the kernel"

KIND_OF = {ASK_RECEIVED: "ask", CONFIRM_NEEDED: "hold", PROOF_ATTEMPT: "proof",
           REPLY: "reply", INTENTION_STOPPED: "intention.stop", MARKER_SET: "marker.set",
           TOOL_CALLED: "tool", ASK_REFUSED: "refused"}
CSV_COLUMNS = ("at", "kind", "ref", "person", "authority_chain", "chain_status", "proof",
               "marker_kind", "marker_id", "marker_parent", "marker_root", "served_by",
               "tool", "words", "words_truncated", "placement", "target", "marker_words")


# ---- the hash chain (the wire contract; the fixture's law) ---------------------------

def hash_chain(rows: list[dict]) -> list[str]:
    """h0 = sha256(canonical(row0)); h_i = sha256(ascii(h_{i-1}) || canonical(row_i))."""
    out: list[str] = []
    prev = b""
    for row in rows:
        h = hashlib.sha256(prev + ev.canonical(row)).hexdigest()
        out.append(h)
        prev = h.encode("ascii")
    return out


def chain_status(row: dict) -> str:
    """Judged from the row's own fields, never from elsewhere: a chain is
    intact when it exists, begins with the origin human, and — where a
    body acted — ends with that body. A proof offered wears only its
    prover (a master is never the asker), so it is intact when present."""
    chain = row.get("authority_chain") or []
    if not chain:
        return "broken"
    if row.get("kind") == "proof":
        return "intact"
    if chain[0] != row.get("person"):
        return "broken"
    served = row.get("served_by")
    if served and chain[-1] != served:
        return "broken"
    return "intact"


def seal(rows: list[dict], *, scope: dict, world: str, generated_at: str | None = None,
         signer=None) -> dict:
    """Rows → a bundle: statuses re-derived, the summary counted, the hash
    chain drawn, the root signed when a signer is given."""
    rows = [dict(r) for r in rows]
    for r in rows:
        r["chain_status"] = chain_status(r)
    by_kind: dict[str, int] = {}
    by_proof: dict[str, int] = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
        by_proof[r.get("proof") or "-"] = by_proof.get(r.get("proof") or "-", 0) + 1
    chain = hash_chain(rows)
    bundle = {
        "contract": CONTRACT, "scope": scope, "generated_at": generated_at or ev.now_iso(),
        "world": world, "rows": rows,
        "summary": {"rows": len(rows), "by_kind": by_kind, "by_proof": by_proof,
                    "chain_broken": sum(r["chain_status"] == "broken" for r in rows),
                    "words_withheld": sum(1 for r in rows if r.get("words_withheld"))},
        "hashing": HASHING, "hash_chain": chain, "root_hash": chain[-1] if chain else None,
        "signed_by": None, "signer_key": None, "signature": None,
    }
    if signer is not None:
        bundle["signed_by"] = signer.did
        bundle["signer_key"] = signer.verify_key_hex
        bundle["signature"] = signer.sign(_signed_part(bundle))
    return bundle


def _signed_part(bundle: dict) -> dict:
    return {"contract": bundle["contract"], "root_hash": bundle["root_hash"],
            "generated_at": bundle["generated_at"], "world": bundle["world"],
            "rows": len(bundle["rows"])}


def verify(bundle: dict) -> bool:
    """Recompute everything a stranger can: the hash chain and root, every
    row's chain status from its own fields, the summary's counts, and the
    signature when one is worn. Any disagreement → False."""
    try:
        rows = bundle["rows"]
        if bundle.get("contract") != CONTRACT:
            return False
        if any(chain_status(r) != r.get("chain_status") for r in rows):
            return False
        chain = hash_chain(rows)
        if chain != bundle.get("hash_chain") or (chain[-1] if chain else None) != bundle.get("root_hash"):
            return False
        s = bundle.get("summary") or {}
        if s.get("rows") != len(rows) or \
           s.get("chain_broken") != sum(r["chain_status"] == "broken" for r in rows):
            return False
        if bundle.get("signature"):
            from nacl.exceptions import BadSignatureError
            from nacl.signing import VerifyKey
            pub = bytes.fromhex(bundle["signer_key"])
            if "did:orreth:agent:" + hashlib.sha256(pub).hexdigest()[:32] != bundle.get("signed_by"):
                return False
            try:
                VerifyKey(pub).verify(ev.canonical(_signed_part(bundle)),
                                      bytes.fromhex(bundle["signature"]))
            except BadSignatureError:
                return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


# ---- the read (from the ground and the outbox log; never a write) -------------------

def current_session(conn, person: str) -> str | None:
    cur = conn.cursor()
    cur.execute("SELECT session_id FROM spine_sessions WHERE person = %s AND scope = %s"
                " ORDER BY opened_at DESC LIMIT 1", (person, ev.scope()))
    r = cur.fetchone()
    return r[0] if r else None


def build(conn, *, person: str, session: str | None = None,
          window: tuple[str, str] | None = None, marker: str | None = None,
          signer=None) -> dict:
    """The bundle for ONE scope — session · window · marker root — of the
    requester's own asks; none given → the current session."""
    from .resident import ensure_schema as _asks
    from .markers import ensure_schema as _marks
    from .outbox import ensure_schema as _out
    _asks(conn); _marks(conn); _out(conn)
    cur = conn.cursor()
    world = ev.scope()
    if not (session or window or marker):
        session = current_session(conn, person)
    scope: dict = {"person": person}
    where, args = ["a.person = %s", "a.scope = %s"], [person, world]
    if session:
        scope["session"] = session
        where.append("a.session = %s"); args.append(session)
    if window:
        scope["window"] = {"from": window[0], "to": window[1]}
        where.append("a.asked_at BETWEEN %s AND %s"); args += [window[0], window[1]]
    if marker:
        scope["marker"] = marker
        where.append("m.root = %s"); args.append(marker)
    cur.execute(
        "SELECT a.ask_id, a.text, a.reply, a.person, a.served_by, a.target, a.state,"
        " a.proof, a.session, a.marker, a.held, m.root FROM spine_asks a"
        " LEFT JOIN spine_markers m ON m.marker_id = a.marker"
        f" WHERE {' AND '.join(where)} ORDER BY a.asked_at", args)
    asks = {r[0]: {"text": r[1], "reply": r[2], "person": r[3], "served_by": r[4],
                   "target": r[5], "state": r[6] or "in", "proof": r[7] or "L1",
                   "session": r[8], "marker": r[9], "held": json.loads(r[10]) if r[10] else None,
                   "root": r[11]} for r in cur.fetchall()}
    # the intentions in scope: stopped by the requester in the window, rooted
    # at the marker, or held for a stop by an ask of this session (the record
    # names the intention on the held act — never a guess)
    intentions: set[str] = set()
    if _has(conn, "spine_intentions"):
        if window:
            cur.execute("SELECT intention_id FROM spine_intentions WHERE scope = %s AND stopped_by = %s"
                        " AND stopped_at BETWEEN %s AND %s", (world, person, window[0], window[1]))
            intentions |= {r[0] for r in cur.fetchall()}
        if marker:
            cur.execute("SELECT intention_id FROM spine_intentions WHERE scope = %s AND marker = %s"
                        " AND stopped_by = %s", (world, marker, person))
            intentions |= {r[0] for r in cur.fetchall()}
    for a in asks.values():
        h = a["held"] or {}
        if h.get("tool") == "intent.stop" and (h.get("args") or {}).get("intention_id"):
            intentions.add(h["args"]["intention_id"])
    # the markers in scope (marker.set facts under the root)
    marker_ids: set[str] = set()
    if marker:
        cur.execute("SELECT marker_id FROM spine_markers WHERE scope = %s AND root = %s", (world, marker))
        marker_ids = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT did FROM spine_joins WHERE scope = %s AND kind = 'firmware'", (world,))
    firmware = {r[0] for r in cur.fetchall()}
    # P6 sp4: the placement each body was born under (its latest join) —
    # a row for a body's act carries cell · metal from the record
    cur.execute("SELECT DISTINCT ON (did) did, placement FROM spine_joins WHERE scope = %s"
                " ORDER BY did, join_id DESC", (world,))
    stands = {}
    for did, plc in cur.fetchall():
        prof = json.loads(plc) if plc else {"cell": "local", "metal": "any"}
        stands[did] = {"cell": prof["cell"], "metal": prof["metal"]}
    words_by_intention: dict[str, str] = {}
    if intentions:
        cur.execute("SELECT intention_id, words FROM spine_intentions WHERE intention_id = ANY(%s)",
                    (list(intentions),))
        words_by_intention = dict(cur.fetchall())

    needles = list(asks) + sorted(intentions) + sorted(marker_ids)
    rows: list[dict] = []
    if needles:
        # the outbox IS the audit trail (the dev log; every fact lands there
        # with its event) — read by the ids in scope, in commit order
        cur.execute("SELECT outbox_id, body FROM spine_outbox"
                    " WHERE convert_from(body, 'UTF8') LIKE ANY(%s) ORDER BY outbox_id",
                    ([f"%{n}%" for n in needles],))
        for oid, body in cur.fetchall():
            try:
                e = ev.decode(bytes(body))
            except Exception:
                continue
            kind = KIND_OF.get(e.get("type"))
            if kind is None or e.get("scope_path") != world:
                continue
            row = _row(e, kind, oid, asks, intentions, marker_ids, firmware, words_by_intention)
            if row is not None:
                row["placement"] = stands.get(row.get("served_by"))   # a body's act: where it stood
                rows.append(row)
    rows.sort(key=lambda r: (r["at"], r["_order"]))
    served = _marker_words(conn, {(r.get("marker") or {}).get("id") for r in rows})   # W11
    for r in rows:
        r.pop("_order", None)                       # P11: a withheld row borrows no words either
        r["marker_words"] = None if r.get("words_withheld") else served.get((r.get("marker") or {}).get("id"))
    return seal(rows, scope=scope, world=world, signer=signer)


def _marker_words(conn, ids: set) -> dict[str, str | None]:
    """W11: the WHY in words — for each marker, the words of the objective
    it serves: its parent's when it has one (a thought under an
    objective, an objective under an intention's turn), its own when it
    is a root. Read through `markers.with_words`: an ask's text, an
    intention's words, a schedule's text, else the marker's note."""
    from . import markers
    ids = {i for i in ids if i}
    if not ids:
        return {}
    cur = conn.cursor()
    cur.execute("SELECT marker_id, parent FROM spine_markers WHERE marker_id = ANY(%s)", (list(ids),))
    parent = dict(cur.fetchall())
    want = {parent.get(i) or i for i in ids}
    cur.execute("SELECT marker_id, kind, parent, ref, by_did, note, at, 0 FROM spine_markers"
                " WHERE marker_id = ANY(%s)", (list(want),))
    found = {m["id"]: m for m in markers.with_words(conn, [markers._row(r) for r in cur.fetchall()])}
    # P11: words borrowed from an ask in an opt-out session stay there — withheld here too
    refs = [m["ref"] for m in found.values() if m["ref"].startswith("ask_")]
    if refs:
        cur.execute("SELECT ask_id FROM spine_asks WHERE ask_id = ANY(%s) AND coalesce(state, 'in') <> 'in'", (refs,))
        for (withheld,) in cur.fetchall():
            for m in found.values():
                if m["ref"] == withheld:
                    m["words"] = m["note"] = None
    out = {}
    for i in ids:
        m = found.get(parent.get(i) or i)
        out[i] = (m.get("words") or m.get("note") or None) if m else None
    return out


def _row(e: dict, kind: str, oid: int, asks: dict, intentions: set, marker_ids: set,
         firmware: set, iwords: dict) -> dict | None:
    p = e.get("payload") or {}
    ref = p.get("ref")
    mk = e.get("marker") or None
    a = asks.get(ref)
    if kind == "intention.stop":
        if ref not in intentions:
            return None
        person, served, proof = p.get("by"), None, p.get("proof") or "L1"
        words = {"intention": iwords.get(ref)} if iwords.get(ref) else None
    elif kind == "marker.set":
        if not (a or (mk and mk.get("id") in marker_ids)):
            return None
        # the origin human is the marked ask's person; the setter (a body,
        # or the human by hand) is who the fact's chain must end with
        served = (mk or {}).get("by")
        person = a["person"] if a else (e.get("authority_chain") or [served])[0]
        proof, words = None, None
    else:
        if a is None:
            return None
        person, served = a["person"], None
        if kind == "ask":
            proof, words = a["proof"], {"ask": a["text"]}
        elif kind == "refused":                     # W19: the door's refusal, the reply is its words
            served, proof, words = KERNEL, a["proof"], {"ask": a["text"], "reply": a["reply"]}
        elif kind == "hold":
            served, proof, words = a["served_by"], p.get("level") or "L2", None
        elif kind == "proof":
            proof, words = p.get("level"), None
        elif kind == "tool":                        # the hop: H → body → the tool's service DID
            served = p.get("service") or f"tool:{p.get('tool')}"   # (P6.5 sp1; tool:<name> when unregistered)
            proof, words = a["proof"], None
        else:                                       # reply — an include's when firmware acted
            served, proof = a["served_by"], p.get("proof") or a["proof"]
            words = {"reply": a["reply"]}
            if served in firmware or (a["target"] in INCLUDES):
                kind = "include"
    row = {"at": e["occurred_at"], "kind": kind, "ref": ref, "person": person,
           "authority_chain": list(e.get("authority_chain") or []), "chain_status": None,
           "proof": proof, "target": (a or {}).get("target"),     # W11: "jb → echo (ask)" in a fan-out
           "marker": ({"kind": mk.get("kind"), "id": mk.get("id"), "parent": mk.get("parent"),
                       "root": (a or {}).get("root") or (mk.get("id") if mk.get("parent") is None else None)}
                      if mk else None),
           "words": words, "served_by": served, "message_id": e.get("message_id"),
           "_order": oid}
    if kind == "hold":
        row["tool"] = p.get("tool"); row["class"] = p.get("class")
    if kind == "proof":
        row["ok"] = bool(p.get("ok"))
    if kind == "tool":
        row["tool"] = p.get("tool"); row["ok"] = bool(p.get("ok"))
    if a and a["state"] != "in":                    # P11: an opt-out session's words stay there
        row["words"] = None; row["words_withheld"] = a["state"]
    return row


def _has(conn, table: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (table,))
    return bool(cur.fetchone()[0])


# ---- the human's CSV ----------------------------------------------------------------

def _plain(text: str) -> str:
    """W10: plain words for a human's table — the markdown marks fall
    away (headings, bold, bullets, code ticks), the first line stays
    whole; the JSON bundle keeps the exact words."""
    t = re.sub(r"^\s{0,3}#{1,6}\s+", "", text or "", flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", t)
    t = re.sub(r"^\s*[-*•]\s+", "· ", t, flags=re.M)
    t = t.replace("`", "")
    return t.strip()


def to_csv(bundle: dict) -> str:
    """One line per row; the chain joined by ' → '; words cut at 500 with
    an ellipsis and the cut marked in its own column; the words column
    in plain words (W10), the why in words (W11)."""
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(CSV_COLUMNS)
    for r in bundle["rows"]:
        m = r.get("marker") or {}
        words = " | ".join(f"{k}: {_plain(v)}" for k, v in (r.get("words") or {}).items() if v)
        if r.get("words_withheld"):
            words = f"(withheld — {r['words_withheld']})"
        cut = len(words) > WORDS_MAX
        if cut:
            words = words[:WORDS_MAX] + "…"
        w.writerow([r["at"], r["kind"], r["ref"], r["person"],
                    " → ".join(r.get("authority_chain") or []), r["chain_status"],
                    r.get("proof") or "", m.get("kind") or "", m.get("id") or "",
                    m.get("parent") or "", m.get("root") or "", r.get("served_by") or "",
                    r.get("tool") or "", words, "yes" if cut else "",
                    (f"{r['placement']['cell']} · {r['placement']['metal']}"
                     if r.get("placement") else ""),
                    r.get("target") or "", _plain(r.get("marker_words") or "")])
    return out.getvalue()
