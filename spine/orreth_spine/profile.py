# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile (W58, the Mirror's first row carried) · 2026-09-26
"""THE HUMAN PROFILE (canon 0003 "packing the mind" slot 1 · "who remembers
what" · 0001 P22 the human's profile · the old world's 0025 + 0070 carried —
W58, walk #15: cell two's librarian answered the weather for the WRONG
PLACE because no ground knew where JB was).

What a person tells this ground about themselves, in their own words,
provenance-labeled exactly as the Mirror had it:

    you told me         — the person said it (`asserted_by: human`, TRUSTED —
                          self-sovereignty: nothing outranks a person's own
                          word about themselves)
    I observed          — the kernel found it out (`asserted_by: kernel`: the
                          coordinates and the clock of a told place, from the
                          geocoder — always beside the told words, never
                          instead of them)
    the mirror noticed  — reserved (`asserted_by: mirror`): the Mirror's own
                          inferences from conversation are NOT built on this
                          kernel; the label is kept so the ladder is whole

Four fields — `name` · `place` · `zone` · `claim` (a free sentence: "remember
about me: I take my coffee black"). The newest word wins per named field;
claims accumulate. A correction is a new claim (append-only); FORGETTING is
a recorded withdrawal (`forget about me: my place`) — the row stays, marked
withdrawn, and never reads again (rule 11: a recorded act, never a
deletion; 0003: forgetting is governed, never silent). Every change is a
FACT through the outbox with the chain (`[person, the kernel]` for a told
word; `[the kernel]` for an observation) and a marker (an ACTION under the
ask that carried the words, else an OBSERVATION under the person's one
profile root).

WHO READS IT: every body, at every voiced answer — `resident.seat_words`
reads `seat_words()` FIRST (slot 1 of the pack: "who is this human"); the
weather tool reads `place_for_ask()` as its default; the human's zone reads
`zone_of()` ahead of the ground's dial. A routed ask CARRIES the slice
over the seam (`carry()` → `spine_asks.carried_profile`), so the far cell
answers for the person's place and stores nothing about them — the privacy
floor stands: the slice is injected structurally, never into a projection
or a record of the far ground.

The pure laws here (`read_words` · `slice_words` · `label_of` ·
`place_default`) are the REFERENCE for the fixture `spine/conformance/
profile-v0.json`; the Rust kernel passes it unchanged (0008).
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

from . import envelope as ev, outbox

CONTRACT = "orreth.profile/1"
TOLD = "orreth.profile.told.v1"            # a person's own word about themselves — a fact
OBSERVED = "orreth.profile.observed.v1"    # what the kernel found out beside a told word — a fact
WITHDRAWN = "orreth.profile.withdrawn.v1"  # a word withdrawn on the person's say — a fact, never a deletion

FIELDS = ("name", "place", "zone", "claim")
ASSERTERS = ("human", "kernel", "mirror")
LABELS = {"human": "you told me", "kernel": "I observed", "mirror": "the mirror noticed"}
STATE_OF = {"human": "trusted", "kernel": "trusted", "mirror": "untrusted"}
KERNEL = "the kernel"
PROFILE_REF = "the profile"
SLICE_CAP = 700                            # the pack's budget for slot 1 (0003)
GEOCODER = "https://geocoding-api.open-meteo.com/v1/search"

NOTHING_WORDS = ("those words tell me nothing about you — say \"my name is …\", \"I live in …\", "
                 "\"my time zone is …\", \"remember about me: …\", \"what do you know about me?\" "
                 "or \"forget about me: …\"")
NONE_YET = "nothing yet — you have told this ground nothing about yourself"


class ProfileRefused(Exception):
    """Refused in words — the words are the law."""


# ---- the pure laws (the fixture's) ----------------------------------------------------------

_READ = re.compile(r"^(?:what do you know about me|show (?:me )?my profile|read my profile|my profile|who am i)\s*\??$", re.I)
_NAME = re.compile(r"^(?:my name is|call me|i am|i'm)\s+(?P<v>[^,.;:!?]{1,60}?)\s*[.!]?$", re.I)
_PLACE = re.compile(r"^(?:i live in|i'm in|i am in|my place is|my home is|my town is|i live at|i am living in|i'm living in)\s+(?P<v>[^;:!?]{1,120}?)\s*[.!]?$", re.I)
_ZONE = re.compile(r"^(?:my (?:time ?zone|zone|clock) is|i am on|i'm on)\s+(?P<v>[A-Za-z_]+(?:/[A-Za-z0-9_+\-]+){1,2}|UTC|GMT)\s*[.!]?$", re.I)
_CLAIM = re.compile(r"^(?:remember about me|about me|my profile)\s*:\s*(?P<v>.{1,240}?)\s*$", re.I)
_FORGET_FIELD = re.compile(r"^forget (?:about me:\s*)?my (?P<f>name|place|zone|time ?zone|home|town|clock)\s*[.!]?$", re.I)
_FORGET_TOPIC = re.compile(r"^forget (?:about me:|that|about)\s*(?P<v>.{1,240}?)\s*[.!]?$", re.I)

_FIELD_OF = {"name": "name", "place": "place", "home": "place", "town": "place",
             "zone": "zone", "timezone": "zone", "time zone": "zone", "clock": "zone"}


def read_words(text: str) -> dict:
    """What a sentence says about the person (conformance `profile_words`):
    `act` is `tell` · `read` · `forget` · null; a `tell` names its `field`
    (name · place · zone · claim) and carries the `value` in the person's
    own spelling (trimmed, never rewritten); a `forget` names a `field` or
    a `topic`. Words that say nothing about the person read null — the
    ask goes on to a body untouched."""
    t = " ".join((text or "").split())
    if not t:
        return {"act": None, "field": None, "value": None}
    if _READ.match(t):
        return {"act": "read", "field": None, "value": None}
    m = _CLAIM.match(t)
    if m:
        return {"act": "tell", "field": "claim", "value": m.group("v").strip()}
    m = _FORGET_FIELD.match(t)
    if m:
        return {"act": "forget", "field": _FIELD_OF[m.group("f").lower()], "value": None}
    m = _FORGET_TOPIC.match(t)
    if m:
        return {"act": "forget", "field": None, "value": m.group("v").strip()}
    m = _ZONE.match(t)
    if m:
        return {"act": "tell", "field": "zone", "value": m.group("v").strip()}
    m = _PLACE.match(t)
    if m:
        return {"act": "tell", "field": "place", "value": m.group("v").strip()}
    m = _NAME.match(t)
    if m:
        v = m.group("v").strip()
        # "I am in Boulder" is a place (read above); "I am tired" is not a name — a name is one to four words, no verb-ish tails
        if len(v.split()) <= 4 and not re.search(r"\b(?:not|very|so|here|there|back|going|feeling|tired|happy|sad|busy|ready|done)\b", v, re.I):
            return {"act": "tell", "field": "name", "value": v}
    return {"act": None, "field": None, "value": None}


def label_of(asserted_by: str) -> str:
    """The provenance label a read wears (conformance `profile_label`)."""
    if asserted_by not in LABELS:
        raise ProfileRefused(f"a profile word is asserted by one of {', '.join(ASSERTERS)}, not {asserted_by!r}")
    return LABELS[asserted_by]


def slice_words(claims: list[dict], name_fallback: str | None = None) -> str:
    """The profile as one paragraph for the pack's first slot (conformance
    `profile_slice`): the person's own words first ("you told me: …"),
    then what the kernel observed, then what the mirror noticed — each
    group one label, the rows joined by " · ", the whole capped at
    SLICE_CAP so a decade of claims never crowds the ask. Withdrawn rows
    never appear (the caller hands live rows). Nothing told reads as
    NONE_YET."""
    live = [c for c in claims if not c.get("withdrawn_at")]
    if not live:
        return NONE_YET
    told_place = next((c["value"] for c in live if c["field"] == "place" and c["asserted_by"] == "human"), None)
    groups: dict[str, list[tuple[int, str]]] = {a: [] for a in ASSERTERS}
    seen: set[tuple[str, str]] = set()
    for c in live:                                 # newest first: the newest word per named field wins
        by, field = c["asserted_by"], c["field"]
        if field in ("name", "place", "zone") and by == "human":
            if (by, field) in seen:
                continue
            seen.add((by, field))
        if field == "place" and by == "kernel" and c.get("evidence") != told_place:
            continue                               # an observation reads only beside the told place it explains
        groups.setdefault(by, []).append((FIELDS.index(field) if field in FIELDS else 9, _row_words(c)))
    parts = [f"{LABELS[a]}: " + " · ".join(w for _, w in sorted(groups[a], key=lambda x: x[0]))
             for a in ASSERTERS if groups.get(a)]   # name · place · zone · then the claims
    out = " — ".join(parts)
    if len(out) > SLICE_CAP:
        out = out[:SLICE_CAP - 1].rstrip() + "…"
    return out


def _row_words(c: dict) -> str:
    f, v = c["field"], c["value"]
    if f == "name":
        return f"your name is {v}"
    if f == "place":
        if c["asserted_by"] == "kernel" and c.get("lat") is not None:
            zone = f", its clock {c['zone']}" if c.get("zone") else ""
            return f"{v} is at {float(c['lat']):.2f},{float(c['lon']):.2f}{zone}"
        return f"you live in {v}"
    if f == "zone":
        return f"your clock is {v}"
    return str(v)


def place_default(claims: list[dict]) -> dict | None:
    """The weather tool's default (conformance `place_default`): the newest
    OBSERVED coordinates standing beside a live told place — `{place, lat,
    lon, zone}` — or null when the person has told this ground no place
    (the tool then says so, never a fixed point)."""
    live = [c for c in claims if not c.get("withdrawn_at")]
    told = next((c for c in live if c["field"] == "place" and c["asserted_by"] == "human"), None)
    if told is None:
        return None
    seen = next((c for c in live if c["field"] == "place" and c["asserted_by"] == "kernel"
                 and c.get("lat") is not None and c.get("evidence") == told["value"]), None)
    if seen is None:
        return {"place": told["value"], "lat": None, "lon": None, "zone": None}
    return {"place": told["value"], "lat": float(seen["lat"]), "lon": float(seen["lon"]), "zone": seen.get("zone") or None}


# ---- the record ------------------------------------------------------------------------------

def ensure_schema(conn) -> None:
    if not outbox.once(conn, "profile"):
        return
    from . import resident
    resident.ensure_schema(conn)               # the seam's column rides on spine_asks — the asks' ground first
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_profile ("
            " claim_id bigserial PRIMARY KEY, scope text NOT NULL, person text NOT NULL,"
            " field text NOT NULL, value text NOT NULL, asserted_by text NOT NULL,"
            " state text NOT NULL, quoted text, evidence text, lat double precision, lon double precision,"
            " zone text, by_did text NOT NULL, marker text, ask text,"
            " at timestamptz NOT NULL DEFAULT now(),"
            " withdrawn_at timestamptz, withdrawn_by text, withdrawn_marker text)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_profile_person ON spine_profile (scope, person, at DESC)")
        # the routed ask carries the asker's slice over the seam (P7 sp8): the far cell reads it for
        # that answer only — a column on the ask, never a row of the far ground's profile
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS carried_profile text")


def _rows(cur) -> list[dict]:
    cols = [d[0] for d in cur.description]
    out = []
    for r in cur.fetchall():
        d = dict(zip(cols, r))
        for k in ("at", "withdrawn_at"):
            if d.get(k) is not None:
                d[k] = d[k].isoformat()
        out.append(d)
    return out


def claims(conn, person: str, *, withdrawn: bool = False) -> list[dict]:
    """The person's rows on this ground, newest first — live ones unless
    `withdrawn` asks for the whole record."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT claim_id, person, field, value, asserted_by, state, quoted, evidence, lat, lon, zone,"
                " by_did, marker, ask, at, withdrawn_at, withdrawn_by FROM spine_profile"
                " WHERE scope = %s AND person = %s" + ("" if withdrawn else " AND withdrawn_at IS NULL")
                + " ORDER BY claim_id DESC", (ev.scope(), person))
    return _rows(cur)


def profile_root(conn, person: str) -> str:
    """ONE origin per person for their profile (P25's Analyzer reads
    roots): "jb keeps their own profile" — every told word hangs under it."""
    from . import markers
    markers.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT marker_id FROM spine_markers WHERE scope = %s AND parent IS NULL"
                " AND kind = 'observation' AND ref = %s AND by_did = %s ORDER BY at LIMIT 1",
                (ev.scope(), f"{PROFILE_REF}:{person}", person))
    r = cur.fetchone()
    if r:
        return r[0]
    mid = markers.new_id()
    with conn.transaction():
        markers.insert(conn.cursor(), mid, "observation", None, f"{PROFILE_REF}:{person}", person,
                       f"{short(person)} keeps their own profile — every word theirs, provenance-labeled")
    return mid


def short(person: str) -> str:
    """`did:orreth:person:jb` → `jb`; a bare name stays itself."""
    return person.rsplit(":", 1)[-1] if ":" in person else person


def _fact(conn, type_: str, person: str, by: str, payload: dict, *, ask: str | None,
          parent_marker: str | None, note: str, domain) -> dict:
    """The fact and the domain write in ONE transaction (the outbox law):
    the chain is `[person, the kernel]` when the person spoke, `[the kernel]`
    when the kernel observed; the marker an ACTION under the ask that
    carried the words, else an OBSERVATION under the person's root."""
    from . import markers
    markers.ensure_schema(conn); outbox.ensure_schema(conn)
    mid = markers.new_id()
    kind = "action" if ask else "observation"
    parent = parent_marker or profile_root(conn, person)
    marker = {"kind": kind, "id": mid, "parent": parent, "by": by}
    chain = [KERNEL] if by == KERNEL else [by, KERNEL]
    e = ev.make_envelope(kind="event", type=type_, universe_id=ev.scope(), scope_path=ev.scope(),
                         payload=dict(payload, ref=person, by=by), correlation_id=ask or person,
                         authority_chain=chain, marker=marker)

    def _domain(cur):
        markers.insert(cur, mid, kind, parent, ask or person, by, note)
        domain(cur, mid)

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], _domain)
    return {"marker": mid, "message_id": e["message_id"]}


def geocode(place: str, *, timeout: float = 6.0) -> dict | None:
    """Open-Meteo's geocoder, no key: the first match for a told place —
    `{lat, lon, zone, label}` — or None when nothing matched or the road
    was dark (the told words stand either way; the tool says it has no
    coordinates yet)."""
    q = urllib.parse.urlencode({"name": place, "count": 1, "language": "en", "format": "json"})
    try:
        with urllib.request.urlopen(f"{GEOCODER}?{q}", timeout=timeout) as r:
            doc = json.loads(r.read())
    except Exception:
        return None
    hit = (doc.get("results") or [None])[0]
    if not hit or hit.get("latitude") is None:
        return None
    label = ", ".join(x for x in (hit.get("name"), hit.get("admin1"), hit.get("country")) if x)
    return {"lat": float(hit["latitude"]), "lon": float(hit["longitude"]),
            "zone": hit.get("timezone") or None, "label": label}


def tell(conn, person: str, field: str, value: str, *, ask: str | None = None,
         parent_marker: str | None = None, quoted: str | None = None, geocoder=geocode) -> dict:
    """A person's own word lands TRUSTED as a fact; a told PLACE is geocoded
    once and the coordinates land beside it as an OBSERVED row + fact in
    the same motion (`geocoder=None` skips the road). Returns the told row,
    the observed row (or None), and the words the glass says."""
    ensure_schema(conn)
    if field not in FIELDS:
        raise ProfileRefused(f"a profile word is one of {', '.join(FIELDS)}, not {field!r}")
    value = " ".join(str(value or "").split())
    if not value:
        raise ProfileRefused("an empty word says nothing about you")
    if field == "zone":
        from zoneinfo import ZoneInfo
        try:
            ZoneInfo(value)
        except Exception:
            raise ProfileRefused(f"{value!r} is not a clock I know — a time zone reads like America/Denver")
    seen = geocoder(value) if (field == "place" and geocoder is not None) else None
    told: dict = {}
    obs: dict | None = None

    def _domain(cur, mid):
        cur.execute("INSERT INTO spine_profile (scope, person, field, value, asserted_by, state, quoted, by_did, marker, ask)"
                    " VALUES (%s, %s, %s, %s, 'human', 'trusted', %s, %s, %s, %s) RETURNING claim_id",
                    (ev.scope(), person, field, value, quoted or value, person, mid, ask))
        told["claim_id"] = cur.fetchone()[0]
        if seen is not None:
            omid = _observe(cur, person, value, seen, ask=ask, parent=mid)
            obs.update({"marker": omid})

    if seen is not None:
        obs = {"lat": seen["lat"], "lon": seen["lon"], "zone": seen.get("zone"), "label": seen.get("label")}
    fact = _fact(conn, TOLD, person, person,
                 {"hash": ev.content_hash({"field": field, "value": value}), "field": field,
                  "value": value, "asserted_by": "human", "state": "trusted"},
                 ask=ask, parent_marker=parent_marker,
                 note=f"{short(person)} told the ground their {field}: {value}", domain=_domain)
    told.update({"field": field, "value": value, "asserted_by": "human", "state": "trusted", "marker": fact["marker"]})
    words = f"Noted, in your own words — {_row_words(dict(told))}."
    if field == "place":
        words += (f" I observed: {seen['label']} is at {seen['lat']:.2f},{seen['lon']:.2f}"
                  + (f", its clock {seen['zone']}" if seen.get("zone") else "") + "." if seen
                  else " I could not find its coordinates just now — the weather tool will say so until it can.")
    return {"told": told, "observed": obs, "words": words}


def _observe(cur, person: str, place: str, seen: dict, *, ask: str | None, parent: str) -> str:
    """The kernel's observation beside a told place: the row and its own
    fact, inside the tell's transaction (one motion, two facts)."""
    from . import markers
    omid = markers.new_id()
    label = seen.get("label") or place
    markers.insert(cur, omid, "observation", parent, ask or person, KERNEL,
                   f"{KERNEL} observed: {label} is at {seen['lat']:.2f},{seen['lon']:.2f}")
    cur.execute("INSERT INTO spine_profile (scope, person, field, value, asserted_by, state, evidence, lat, lon, zone,"
                " by_did, marker, ask) VALUES (%s, %s, 'place', %s, 'kernel', 'trusted', %s, %s, %s, %s, %s, %s, %s)",
                (ev.scope(), person, label, place, seen["lat"], seen["lon"], seen.get("zone"), KERNEL, omid, ask))
    e = ev.make_envelope(kind="event", type=OBSERVED, universe_id=ev.scope(), scope_path=ev.scope(),
                         payload={"ref": person, "hash": ev.content_hash({"place": place, "lat": seen["lat"], "lon": seen["lon"]}),
                                  "field": "place", "value": label, "asserted_by": "kernel", "state": "trusted",
                                  "evidence": place, "lat": seen["lat"], "lon": seen["lon"], "zone": seen.get("zone"),
                                  "by": KERNEL, "source": "open-meteo geocoder"},
                         correlation_id=ask or person, authority_chain=[KERNEL],
                         marker={"kind": "observation", "id": omid, "parent": parent, "by": KERNEL})
    outbox.add_row(cur, ev.encode(e), e["message_id"])
    return omid


def withdraw(conn, person: str, *, field: str | None = None, topic: str | None = None,
             ask: str | None = None, parent_marker: str | None = None) -> dict:
    """"Forget about me: …" — the matching live rows are marked withdrawn
    on the person's say (a fact with the chain), never deleted; nothing
    matching refuses in words so a silent no-op never passes for a
    forgetting. A withdrawn place takes its observed coordinates with it."""
    ensure_schema(conn)
    live = claims(conn, person)
    if field:
        hit = [c for c in live if c["field"] == field]
    elif topic:
        t = topic.lower()
        hit = [c for c in live if t in str(c["value"]).lower() or t in str(c.get("evidence") or "").lower()]
    else:
        raise ProfileRefused("say what to forget — 'forget about me: my place' or 'forget that I take my coffee black'")
    if not hit:
        raise ProfileRefused(f"nothing in your profile says {(field or topic)!r} — nothing to forget")
    ids = [c["claim_id"] for c in hit]
    what = field or topic

    def _domain(cur, mid):
        cur.execute("UPDATE spine_profile SET withdrawn_at = now(), withdrawn_by = %s, withdrawn_marker = %s"
                    " WHERE claim_id = ANY(%s)", (person, mid, ids))

    fact = _fact(conn, WITHDRAWN, person, person,
                 {"hash": ev.content_hash({"withdrawn": ids}), "withdrawn": ids, "what": what},
                 ask=ask, parent_marker=parent_marker,
                 note=f"{short(person)} withdrew {len(ids)} word(s) about themselves: {what}", domain=_domain)
    return {"withdrawn": ids, "what": what, "marker": fact["marker"],
            "words": f"Forgotten on your word — {len(ids)} thing(s) about {what} no longer read; the record keeps that you said them once."}


def say(conn, person: str, text: str, *, ask: str | None = None, parent_marker: str | None = None,
        geocoder=geocode) -> dict:
    """The door's one verb: the words are read by the law and land as a
    tell, a forgetting, or a read; words that say nothing refuse in words."""
    rw = read_words(text)
    if rw["act"] == "tell":
        made = tell(conn, person, rw["field"], rw["value"], ask=ask, parent_marker=parent_marker,
                    quoted=text.strip(), geocoder=geocoder)
        return dict(made, act="tell", portrait=portrait(conn, person))
    if rw["act"] == "forget":
        made = withdraw(conn, person, field=rw["field"], topic=rw["value"], ask=ask, parent_marker=parent_marker)
        return dict(made, act="forget", portrait=portrait(conn, person))
    if rw["act"] == "read":
        return {"act": "read", "portrait": portrait(conn, person), "words": portrait(conn, person)["words"]}
    raise ProfileRefused(NOTHING_WORDS)


def portrait(conn, person: str) -> dict:
    """What the person sees of themselves — every live row with its label,
    the named fields resolved (newest told wins), the slice the bodies
    read, and the clock this ground would use for them."""
    rows = claims(conn, person)
    named = {}
    for c in rows:
        if c["asserted_by"] == "human" and c["field"] in ("name", "place", "zone") and c["field"] not in named:
            named[c["field"]] = c["value"]
    place = place_default(rows)
    return {"person": person, "name": named.get("name"), "place": named.get("place"),
            "zone": named.get("zone"), "coordinates": place,
            "claims": [dict(c, label=LABELS[c["asserted_by"]], words=_row_words(c)) for c in rows],
            "words": slice_words(rows), "clock": zone_of(conn, person)}


def zone_of(conn, person: str, *, dial: str | None = None) -> str | None:
    """The person's clock as this ground knows it: the zone they TOLD, else
    the clock of the place they told (observed), else None — the caller
    falls back to the ask's own zone or the ground's dial."""
    for c in claims(conn, person):
        if c["field"] == "zone" and c["asserted_by"] == "human":
            return c["value"]
    p = place_default(claims(conn, person))
    if p and p.get("zone"):
        return p["zone"]
    return dial


def carry(conn, person: str) -> dict | None:
    """The slice a routed ask carries over the seam: the words the far
    cell's body reads and the place its weather tool defaults to — nothing
    else, and nothing the far ground keeps."""
    rows = claims(conn, person)
    if not rows:
        return None
    return {"words": slice_words(rows), "place": place_default(rows), "zone": zone_of(conn, person)}


def carried(conn, ask_id: str | None) -> dict | None:
    """What rode in with an ask (the seam's column), if anything."""
    if conn is None or not ask_id:
        return None
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT carried_profile, person FROM spine_asks WHERE ask_id = %s", (ask_id,))
    r = cur.fetchone()
    if not r:
        return None
    if r[0]:
        try:
            return json.loads(r[0])
        except ValueError:
            return None
    return None


def person_of(conn, ask_id: str | None) -> str | None:
    if conn is None or not ask_id:
        return None
    cur = conn.cursor()
    cur.execute("SELECT person FROM spine_asks WHERE ask_id = %s", (ask_id,))
    r = cur.fetchone()
    return r[0] if r else None


def seat_words(conn, ask_id: str | None, person: str | None = None) -> str:
    """Slot 1 of the pack — what every body reads about the human it serves
    at this ask: the carried slice when the ask came over the seam, else
    this ground's profile of the asker. Plain, complete, sovereign."""
    who = person or person_of(conn, ask_id) or "did:orreth:person:unknown"
    rode = carried(conn, ask_id)
    words = rode["words"] if rode and rode.get("words") else (slice_words(claims(conn, who)) if conn is not None else NONE_YET)
    if words == NONE_YET:
        return (f"THE HUMAN you serve is {short(who)}. They have told this ground nothing about themselves yet — "
                "if their place, clock or name matters to the ask, say so plainly and invite them to say "
                "\"I live in …\", \"my name is …\" or \"remember about me: …\".")
    where = " (it rode here with the ask, from their home cell)" if rode else ""
    return (f"THE HUMAN you serve is {short(who)} — their own profile, in their own provenance{where}: {words}. "
            "Sovereign: honor it, never recite it unasked; when the ask turns on their place or clock, use these.")


def place_for_ask(conn, ask_id: str | None) -> dict | None:
    """The weather tool's default: the place that rode with the ask, else
    the asker's told place on this ground — with its observed coordinates,
    or `lat: None` when the geocoder never answered."""
    rode = carried(conn, ask_id)
    if rode and rode.get("place"):
        return rode["place"]
    who = person_of(conn, ask_id)
    if not who or conn is None:
        return None
    return place_default(claims(conn, who))
