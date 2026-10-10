# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp3, MITL recalls the canon it wears · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement enforced at birth · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W8 · W12 · W16 · W17 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): W21 the duty law + the pack · W23 the interlock's words · W24 echo's bubble · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, W26: an empty reply never lands as replied — asked again once, then said in words · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the harness command served on the bench · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile in the seat words and the clock (W58) · 2026-09-26
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 walk #18, W65: the governed-acts law in every body's seat — a body never performs nor claims the kernel's acts · 2026-09-27
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: lock 4's last poll — a body's JOIN is a fact (orreth.body.joined.v1), so the roster follows the feed · 2026-09-28
# Amended: Claude Fable 5.1 (claude-fable-5-1) — schema 4: an ask's resent_at (W91 THE BENCH SWEEP) · 2026-10-02
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 sp1 THE PATH: a body's own scope path (`scope`), its join and facts wearing it, the crew read within the universe, the seat words naming the level · 2026-10-05
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 sp2 THE SHELF WIDENED: THE HULL — hear → recall → route → chat · work · event → the work node, the template's `graph` component finally read; the wear rows at the join · 2026-10-05
# Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (JB's word 2026-10-08): a body holds a ground line only while it SERVES (`hold_line` · `release_line`), its working memory's line with it; the lease kept on a cadence; the seat budget honoured at the join · 2026-10-08
"""The resident body v0 (canon 0004): one governed body for every mind.

Born from a versioned TEMPLATE artifact; the SAME identity in every life
(covenant rule 1); the covenant policy LOADED before joining or the join
refuses — governance is worn, not remembered (AG-3). It serves commands
from the invocation rail, thinks through a real LangGraph graph, and
lands its reply, its journey, and its events in ONE transaction — then,
and only then, acknowledges the delivery (the ACK law).

The mind here is deliberately small — an echo that proves the FULL-reply
law (every word of the ask comes back verbatim inside the answer). The
LLM arrives in the next spoonful; the body's laws never change.

THE HULL (Phase 8 sp2, canon 0010 lock 6): the body's fixed graph is
hear → recall → ROUTE → one of three edges — CHAT (a human's ask) · WORK
(assigned work under an intention) · EVENT (a marker dispatched by interest)
— into the WORK NODE, which runs the template's `graph` component from the
shelf (`mind.v0` = the metered think · `echo.v0` = the echo), node by node
along its one path. The kernel's laws live in the hull — the seat words, the
covenant slice, the metered gateway, the checkpoint per hop, the stop at a
safe boundary — never in the agent's graph. At its join the body writes what
it WEARS (its template · binding · policy · graph · golden, each by the
shelf's own pin) into the wear table: "in use by N", the blast radius.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

import pika
from langgraph.graph import END, START, StateGraph

from . import envelope as ev
from . import levels as _levels
from . import inbox, outbox, placement as _placement
from .identity import Identity
from .rails import COMMAND_EXCHANGE, RABBIT_URL

SERVE_QUEUE = "resident.serve.00"
SERVE_KEY = "cmd.dev.00.resident.serve"


def serve_queue(name: str | None = None) -> str:
    """Queue names wear the SPINE_QUEUE_NS namespace when one is set —
    a test session lives on its own benches and can never race a live
    rig on the same broker (found live: the running Bridge's librarian
    answered a test's ask, with yesterday's weather in her recall)."""
    ns = os.environ.get("SPINE_QUEUE_NS", "")
    base = SERVE_QUEUE + (f".{ns}" if ns else "")
    return f"{base}.{name}" if name else base


def serve_key(name: str | None = None) -> str:
    ns = os.environ.get("SPINE_QUEUE_NS", "")
    base = SERVE_KEY + (f".{ns}" if ns else "")
    return f"{base}.{name}" if name else base
ASK_RECEIVED = "orreth.ask.received.v1"
JOURNEY = "orreth.journey.v1"
REPLY = "orreth.reply.v1"
CONFIRM_NEEDED = "orreth.confirm.needed.v1"
CONFIRM_CMD = "orreth.resident.confirm.v1"
HARNESS_CMD = "orreth.resident.harness.v1"   # P7 sp6: the kernel asks a body to run its golden cases
KEYCHECK_CMD = "orreth.resident.keycheck.v1"  # Phase 8 sp6: the kernel asks a body to prove who and what it is (chips.KEYCHECK_CMD)
_CHIP_FUNCTIONS = {"identify": "identity", "secure": "security"}   # Phase 8 sp6: a chip's template function → the reviewer it is


# W26 (P7 sp4): a mind that returns no words is asked again ONCE; a second
# silence lands as these words with status `replied` — never an empty bubble
W26_WORDS = "the mind returned nothing; asked again, nothing"
W26_STEP = "the mind returned no words — asked again, once (W26)"
HUMAN_ZONE_DIAL = "SPINE_HUMAN_ZONE"          # W12: the ground's default human zone
HUMAN_ZONE_DEFAULT = "America/Denver"          # JB is relocating to Colorado

# W12 (JB's law, 2026-09-21): every body wears the ontology's slice for its
# seat — the covenant's rules 2 · 4 · 5 · 8 · 11 in one paragraph, for all
COVENANT_SLICE = (
    "The covenant you wear (rules 2, 4, 5, 8, 11): nothing grades its own yardstick — "
    "never attest your own outcome; refusal wears one face — a refusal never teaches a "
    "prober which check failed; the plane authorizes and meters and never sees the "
    "prompt — every thought of yours goes through the metered gateway, none around it; "
    "lived time is monotone — never backdate a memory or a fact; the human can always "
    "stop what the machine manages — a stop is recorded, never a deletion, and you say "
    "what you left undone.")

# W21 (walk #8, the reasoning wound): a standing duty is served, never refused
DUTY_LAW = (
    "A duty is served, never refused. An ask framed as your duty — with its cadence and its "
    "window — is the kernel keeping your own standing intention, never a human repeating a "
    "question; your earlier notes are yours to build on. When nothing is new since your last "
    "run, answer in ONE line: \"nothing new since <time>\".")

# W65 (walk #18, 2026-09-27, the truth wound): quinn typed "stopping the kernel's
# intention"; the words missed the kernel's grammar and reached the librarian, who
# answered "I'm stopping it now. That stop is recorded here" — a governed act it holds
# no tool for and never performed. A body never claims the kernel's acts.
GOVERNED_ACTS_LAW = (
    "You never perform, and never claim to have performed, an act only the kernel does: "
    "stopping, resting or restarting an intention (the kernel's or a person's), retiring or "
    "restoring a service, enrolling a person, admitting a body. You hold no tool for these "
    "and nothing you say changes them. When the human asks you for one, answer in ONE line: "
    "that only the kernel does this, and the exact words it hears — for example "
    "\"stop the kernel's Resiliency intention\" or \"stop my time intention\" — and add nothing "
    "about having done it.")

# the laws every body lives by at the serve (W8 · W16 · W8-loop · W65), one block
COMMON_LAWS = (
    "Never answer in another body's words: a note marked ANOTHER BODY'S WORDS is theirs — "
    "cite it by their name if it bears on the ask, never repeat it as your own reply. When "
    "the ask is addressed to another body by name, say so and answer only your own part. "
    "A new ask is always thought anew: your earlier replies in the notes are context, "
    "never the answer — never hand back an earlier reply. If the ask is an objective you "
    "cannot act on because you lack the tools, open your reply with the exact words "
    "'CANNOT ACT:' and name what body or tool would be needed. When the human asks you "
    "to propose, add or create something you hold a tool for, CALL the tool — never "
    "describe what you would do instead. " + DUTY_LAW + " " + GOVERNED_ACTS_LAW)


def interlock_words(tool: str) -> str:
    """The L2 interlock's words (W23, covenant rule 11): a consequential
    act is RECORDED and the human can rest it later — never "cannot be
    undone". Cancel is the default; a deliberate click confirms."""
    return (f"Are you sure? The {tool} act is consequential — it is recorded, and you "
            "can rest it later. Cancel is the default; a deliberate click confirms.")


_QUESTION = re.compile(r"(\?\s*$|^(who|what|what's|whats|when|where|why|how|is|are|does|do|can"
                       r"|could|would|should|which|did|tell me)\b)", re.I)
_DATE_ASK = re.compile(r"\b(date|time|clock|year|month|what day|which day|day is it|day it is|day of the week)\b", re.I)


def echo_reply(name: str, text: str) -> str:
    """W24 (conformance `echo_reply`): the echoed words alone — "hello" is
    "hello". A QUESTION the body cannot answer by nature adds one plain
    line: "echo repeats; ask the librarian for the date" (a date or time
    ask) — or "… for an answer" (anything else)."""
    words = " ".join((text or "").split())
    if not _QUESTION.search(words):
        return words
    want = "the date" if _DATE_ASK.search(words) else "an answer"
    return f"{words}\n{name} repeats; ask the librarian for {want}"


def human_zone(conn, ask_id: str | None) -> str:
    """The human's zone for this ask (W12): the ask's own, else its
    session's, else the one their PROFILE knows (P7 sp8 — told, or the
    clock of the place they told; a routed ask carries it), else the
    ground's dial, else America/Denver."""
    if conn is not None and ask_id:
        cur = conn.cursor()
        cur.execute("SELECT a.zone, s.zone, a.person FROM spine_asks a"
                    " LEFT JOIN spine_sessions s ON s.session_id = a.session"
                    " WHERE a.ask_id = %s", (ask_id,))
        row = cur.fetchone()
        if row:
            for z in row[:2]:
                if z:
                    return z
            from . import profile
            rode = profile.carried(conn, ask_id)
            if rode and rode.get("zone"):
                return rode["zone"]
            z = profile.zone_of(conn, row[2]) if row[2] else None
            if z:
                return z
    return os.environ.get(HUMAN_ZONE_DIAL) or HUMAN_ZONE_DEFAULT


def time_words(zone: str, now: datetime | None = None) -> str:
    """The clock every body carries (W12, JB's law: a body that cannot say
    the date cannot reason about origin): now in UTC to the second, the
    same instant in the human's zone, today's date there, and the plain
    sentence. An unknown zone is said, never guessed."""
    from zoneinfo import ZoneInfo
    now = now or datetime.now(timezone.utc)
    utc = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        local = now.astimezone(ZoneInfo(zone))
        where = (f"The human's zone is {zone}, where it is "
                 f"{local.strftime('%A %Y-%m-%d %H:%M:%S %Z')}; today's date there is "
                 f"{local.strftime('%Y-%m-%d')}.")
    except Exception:
        where = (f"The human's zone was given as {zone!r}, which this ground does not know — "
                 f"today's date in UTC is {now.strftime('%Y-%m-%d')}; ask the human their zone.")
    return f"NOW is {utc} (UTC). {where} Convert times for humans into their zone, and say the zone."


class PolicyRefused(RuntimeError):
    """No policy loaded, no join — ever."""


PlacementRefused = _placement.PlacementRefused   # P6 sp4: the ground cannot seat this body


class _State(TypedDict):
    text: str
    reply: str
    steps: list
    notes: list
    hold: dict | None
    read: list          # the DIDs whose results this mind read (the chain)
    edge: str           # Phase 8 sp2: which of the hull's edges this ask took — chat · work · event


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "resident"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_joins ("
            " join_id bigserial PRIMARY KEY,"
            " did text NOT NULL, name text NOT NULL, life int NOT NULL,"
            " template_hash text NOT NULL,"
            " policy_version text NOT NULL, policy_hash text NOT NULL,"
            " sig text NOT NULL, joined_at timestamptz NOT NULL DEFAULT now())")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_asks ("
            " ask_id text PRIMARY KEY, text text NOT NULL,"
            " person text NOT NULL, status text NOT NULL DEFAULT 'received',"
            " reply text, served_by text, held text,"
            " asked_at timestamptz NOT NULL DEFAULT now(),"
            " replied_at timestamptz)")
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " held text")
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " resent_at timestamptz")        # W91 THE BENCH SWEEP: dispatched again, once
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " seq int NOT NULL DEFAULT 1")
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " target text")
        # the ground wears its world (canon 0002's isolation law, felt by
        # the Playwright: the band and the roster showed EVERY world's
        # rows) — every ask and every join carries the scope it was
        # made in, and a glass's doors serve only their own world's
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " scope text")
        cur.execute("ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS"
                    " scope text")
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " time_window text")   # the time scope the ask was set
        # sessions (0003 · P20): the human's worldlines — an ask belongs to
        # the session it was asked in; a session rolls, never spills
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " session text")
        cur.execute("ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS"
                    " kind text NOT NULL DEFAULT 'resident'")  # the third kind
        cur.execute("ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS"
                    " capabilities text")   # what the body DECLARED at its join
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_sessions ("
            " session_id text PRIMARY KEY, person text NOT NULL,"
            " scope text NOT NULL, title text,"
            " opened_at timestamptz NOT NULL DEFAULT now())")
        cur.execute("ALTER TABLE spine_sessions ADD COLUMN IF NOT EXISTS"
                    " state text NOT NULL DEFAULT 'in'")    # P11: Opt Out is a
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"       # state
                    " state text NOT NULL DEFAULT 'in'")
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " marker text")                 # the ask's marker (0006)
        cur.execute("ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS"
                    " interests text")              # the kinds a body cares about
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " fanout text")
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " proof text NOT NULL DEFAULT 'L1'")   # P6 sp1: the proof the
        # act's record wears — L1 · L2 · L3-code · L3-master; the export reads it
        cur.execute("ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS"
                    " placement text")     # P6 sp4: the placement the body was born under
        cur.execute("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS"
                    " zone text")          # W12: the human's zone, when the ask names it
        cur.execute("ALTER TABLE spine_sessions ADD COLUMN IF NOT EXISTS"
                    " zone text")
        cur.execute("ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS"
                    " nature text")        # W7: what the body IS, in one line
        # schema 2 (the perf cure): the crew's read, the served count, a session's latest ask, the counts by status
        cur.execute("CREATE INDEX IF NOT EXISTS spine_joins_scope_name ON spine_joins (scope, name, join_id DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_asks_scope_served ON spine_asks (scope, served_by)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_asks_session ON spine_asks (session, asked_at DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_asks_scope_status ON spine_asks (scope, status)")


def _next_seq(cur, ask_id: str) -> int:
    """The ask's own event counter — monotone per aggregate, durable on
    the row, so a conversation that pauses at an interlock continues its
    sequence honestly."""
    cur.execute("UPDATE spine_asks SET seq = seq + 1 WHERE ask_id = %s"
                " RETURNING seq", (ask_id,))
    return cur.fetchone()[0]


class Resident:
    def __init__(self, template_path: str | os.PathLike,
                 *, home: str | os.PathLike | None = None, gateway=None,
                 binding: str | os.PathLike | None = None, scope: str | None = None):
        raw = b"" if isinstance(template_path, dict) else Path(template_path).read_bytes()
        # Phase 8 sp1, THE PATH: the scope path this body is seated on — a floor's or a room's
        # when the crew manifest says so (the reference seats it in-process; a spawned body
        # reads its own SPINE_SCOPE), else the process's world. What the body writes about
        # itself (its join, its lease, its facts' scope_path) wears it; its universe is
        # `ev.universe()`.
        self.scope = scope or ev.scope()
        # Phase 8 sp4: a template may arrive as the declaration itself — the Experiment's trial life
        # wears the draft's candidate (never a file), a promoted agent wears the shelf's standing version
        self.template = dict(template_path) if isinstance(template_path, dict) else json.loads(raw)
        if self.template.get("format") != "orreth-resident-template/1":
            raise ValueError("not a resident template: "
                             f"{self.template.get('format')!r}")
        self.template_hash = ev.content_hash(self.template)
        self.name = self.template["name"]
        # the third kind (0004): a firmware agent wears no persona and is
        # named by its function; the body of laws is the same
        self.kind = self.template.get("kind", "resident")
        self.function = self.template.get("function")
        self.charge = self.template.get("charge", "")
        # W7 (walk #7): what a body IS, in one line a newcomer reads on its
        # chip and its card — the template's word, a binding's when it seats
        self.nature = str(self.template.get("nature") or "")
        # a workspace binding (0004): ONE workspace-firmware body, a binding
        # per pull — the binding names the seat and adds its prompt/skills
        self.binding = None
        if binding is not None:
            self.binding = json.loads(Path(binding).read_text())
            self.name = self.binding["name"]
            self.function = f"workspace:{self.binding['pull']}"
            self.charge = f"{self.charge} {self.binding.get('prompt', '')}".strip()
            self.nature = str(self.binding.get("nature") or self.nature)
            self.template["capabilities"] = list(dict.fromkeys(
                self.template.get("capabilities", [])
                + self.binding.get("capabilities", [])))   # the seat's tools
        self.identity = Identity.load(self.name, home)
        # P6 sp4: the placement profile the template declares (defaults
        # applied) — enforced at the join, never here; a self is loaded
        # BEFORE the check, so a refusal never mints or loses one (rule 1)
        self.placement = _placement.profile(self.template)
        self.policy: dict | None = None
        # the mind: a template that declares one thinks through the
        # gateway (metered, always); without a gateway the body falls
        # back to its deterministic graph — there is no unmetered door
        self.gateway = gateway if self.template.get("mind") else None
        self._serve_conn = None
        # the cure (2026-10-08): THE LINE — the ground connection this body holds while it serves and
        # for a short idle after, opened when a command lands on its bench, let go by `release_line`;
        # an idle body holds none (the ground's connections follow the SERVES, never the seats)
        self._line = None            # the held psycopg connection, or None
        self._line_dsn = None
        self._line_last = 0.0        # monotonic: when the line last served
        self._lease_at = 0.0         # monotonic: when the lease was last renewed
        self._current_ask = None
        self._current_marker = None  # the ask's marker: WHY this serve (0006)
        self._experiment = None      # Phase 8 sp4: the Experiment this serve reviews, when it does
        self._grading = None         # Phase 8 sp5: the live reply this serve grades, when it does
        self._current_chain = None   # the chain the serve command arrived with (AG-7)
        self._state = "in"
        self._ckpt_graph = None      # the checkpointed graph, one per LINE (the cure: its connection opens and closes with the serve window)
        self._ckpt_conn = None       # the working memory's own connection, closed with the line
        self._ckpt_setup = False     # the saver's migrations run once per life — the rows outlive every line
        # on_delta(ask_id, text): the rig wires this to the glass feed —
        # words stream to the human as they form; glass-bound only, the
        # broker never carries a delta, the door still serves the truth
        self.on_delta = None
        self._graph = self._build_graph()

    # ---- birth ----------------------------------------------------------------

    def load_policy(self, path: str | os.PathLike) -> dict:
        pol = json.loads(Path(path).read_bytes())
        self.policy = {"version": pol["version"],
                       "hash": ev.content_hash(pol),
                       "rules": len(pol.get("rules", [])),
                       "name": str(pol.get("name") or "covenant-policy")}   # Phase 8 sp2: the craft it wears
        return self.policy

    def join(self, conn, *, close_scope: str | None = None) -> dict:
        """The dev gate v0 (the governed becky gate arrives with kernel
        integration): the join is recorded wearing the policy version —
        an agent without the covenant loaded never joins. Phase 8 sp4:
        `close_scope` — a TRIAL life in an experiment room closes only the
        wear rows at its own scope, so the standing life's "in use by N"
        holds while the Experiment runs."""
        if self.policy is None:
            raise PolicyRefused(
                "this body wears no covenant policy — load it, or it never "
                "joins (canon 0004: governance is worn, not remembered)")
        ensure_schema(conn)
        # P6 sp4: placement is policy — the ground declares what it is and
        # a body it cannot seat is REFUSED with the reason, a recorded fact,
        # never started; the same self stands refused (rule 1)
        ground = _placement.ground_declares(conn=conn)
        ok, reasons = _placement.honor(self.placement, ground)
        if ok:
            # the cure (2026-10-08): THE SEAT BUDGET — the ground declares how many bodies may stand on it
            # so that every one could serve at once; the next past that is refused here, in words, never
            # started (the same recorded refusal). This self's own standing lease never counts against it.
            from . import presence as _presence
            ok, reasons = _placement.seat_honor(ground["connections"],
                                                _presence.seated_now(conn, exclude_did=self.identity.did))
        if not ok:
            _placement.refuse(conn, self, self.placement, ground, reasons)
            raise PlacementRefused(self.name, reasons)
        from . import body as _body, crafts
        outbox.ensure_schema(conn)
        crafts.ensure_schema(conn)
        worn = self.worn(conn)                      # Phase 8 sp2: what this life is made of, by the shelf's pins
        with conn.transaction():
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM spine_joins WHERE did = %s",
                        (self.identity.did,))
            life = cur.fetchone()[0] + 1
            sig = self.identity.sign({
                "did": self.identity.did, "life": life,
                "template": self.template_hash,
                "policy": self.policy["hash"]})
            cur.execute(
                "INSERT INTO spine_joins (did, name, life, template_hash,"
                " policy_version, policy_hash, sig, scope, kind, capabilities,"
                " interests, placement, nature)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (self.identity.did, self.name, life, self.template_hash,
                 self.policy["version"], self.policy["hash"], sig,
                 self.scope, self.kind,        # joined THIS world at MY level, as my kind,
                 json.dumps(self.template.get("capabilities", [])),   # declared
                 json.dumps(self.template.get("interests", [])),      # + interests
                 ev.canonical(self.placement).decode("ascii"),        # + where I stand
                 self.nature or None))                                # + what I am (W7)
            # re-base sp1: the join is a FACT in the same transaction (orreth.body.joined.v1) —
            # the roster follows the feed, never a timer (lock 4's last poll)
            e = _body.joined_fact(self.name, self.identity.did, self.kind, life, self.nature, scope=self.scope)
            outbox.add_row(cur, ev.encode(e), e["message_id"])
            # Phase 8 sp2: THE WEAR TABLE — one row per component this life wears, the previous
            # life's rows closed, in the join's own transaction ("in use by N" follows the roster)
            crafts.record_wear(cur, scope=self.scope, did=self.identity.did, body=self.name, life=life, worn=worn,
                               close_scope=close_scope)
        from . import scheduler                  # the role schedules the
        for sch in self.template.get("schedules", []):   # template declares are
            scheduler.declared(conn, self.name, "role", sch["text"],   # registered
                               int(sch["every_s"]), self.identity.did)   # at every join
        return {"did": self.identity.did, "life": life,
                "policy_version": self.policy["version"],
                "placement": dict(self.placement)}

    def worn(self, conn) -> list[dict]:
        """The components this body is made of (Phase 8 sp2): its template, its binding, its
        policy, its graph and its golden set — each named with the content hash the shelf pins,
        so the wear row finds its version by hash (None = worn off the shelf, said honestly)."""
        from . import crafts
        parts = {"template": {"name": self.template["name"], "hash": self.template_hash},
                 "policy": {"name": self.policy["name"], "hash": self.policy["hash"]}}
        if self.binding:
            parts["binding"] = {"name": self.binding["name"], "hash": ev.content_hash(self.binding)}
        g = self.graph_declaration(conn)
        if g:
            parts["graph"] = {"name": g["name"], "hash": ev.content_hash(g)}
        try:
            gold = crafts.get(conn, self.template["name"], "golden")
        except Exception:                           # noqa: BLE001 — a ground without the shelf yet
            gold = None
        if gold and gold["state"] != "retired":
            parts["golden"] = {"name": self.template["name"], "hash": gold["manifest_hash"]}
        return crafts.wear_of(parts)

    def graph_declaration(self, conn=None) -> dict | None:
        """The template's `graph` component — the shelf first, the spine's folder as the fallback
        (Phase 8 sp2: finally read); None when neither has it (the work node says so)."""
        from . import crafts
        return crafts.graph_for(conn if conn is not None else self._serve_conn, self.template)

    # ---- the mind (small, real) ----------------------------------------------

    def _build_graph(self, checkpointer=None):
        def hear(s: _State) -> dict:
            return {"steps": s["steps"] + ["heard the ask, every word"]}

        def recall(s: _State) -> dict:
            """Pack the mind (canon 0003): my own worldline (recent
            replies) and my memories that match the ask — packed as
            notes the think node reads. Without a serving connection
            (pure-graph tests) the recall is honestly empty."""
            notes: list[str] = []
            read: list[str] = []            # whose results I read
            conn = self._serve_conn
            if conn is not None:
                from .store import OrrethStore
                cur = conn.cursor()
                # the session law (P20 · MEM-7): the worldline I read is
                # THIS ask's session — every reply landed in it, by any
                # resident, labeled — never another session's; an ask
                # with no session reads only my own session-less replies
                session, window, person, state = None, None, None, "in"
                if self._current_ask:
                    cur.execute("SELECT session, time_window, person, coalesce(state, 'in')"
                                " FROM spine_asks WHERE ask_id = %s", (self._current_ask,))
                    row = cur.fetchone()
                    if row:
                        session, person, state = row[0], row[2], row[3]
                        window = json.loads(row[1]) if row[1] else None
                self._state = state          # P11: this serve stays in its state
                # Phase 8 sp4: an ask under an EXPERIMENT's marker (the hull's event edge) — the
                # kernel asks a reviewer to judge the arms; the evidence is the kernel's record of
                # the runs, packed here so a grader has another's words to grade (rule 2), never its own
                xm = self._current_marker or {}
                from . import experiments as _xp
                xp = None
                if xm.get("parent"):
                    xid = None
                    cur.execute("SELECT kind, ref FROM spine_markers WHERE marker_id = %s", (xm["parent"],))
                    xr = cur.fetchone()
                    if xr and xr[0] == _xp.MARKER_KIND:
                        xid = xr[1]
                    if xid:
                        xp = _xp.get(conn, xid)
                        if xp:
                            self._experiment = xid
                            for side in _xp.ARMS:
                                a = (xp.get("arms") or {}).get(side)
                                if a and a.get("passed") is not None:
                                    notes.append(f"THE EXPERIMENT'S EVIDENCE — arm {side}: {a['passed']} passed, {a['failed']} failed; "
                                                 + " / ".join(f"asked {d.get('ask')!r} expected {d.get('expect')} replied "
                                                              f"{str(d.get('reply') or '')[:160]!r} ({'passed' if d.get('ok') else 'FAILED'})"
                                                              for d in (a.get("details") or [])))
                            if xp.get("current_version"):
                                notes.append(f"THE EXPERIMENT'S CANDIDATE against version {xp['current_version']}: the candidate's "
                                             f"declaration is {json.dumps(xp.get('candidate'), sort_keys=True)[:1200]}")
                            if _xp.KERNEL not in read:
                                read.append(_xp.KERNEL)   # the evidence is the kernel's record — another's words, never mine
                # Phase 8 sp6: THE TWO CHIPS — the identity chip holds the ceremony and the seats, the security chip
                # the refusals ground; under an experiment each reads its evidence off the kernel's record (the trial
                # life's claims · the candidate's diff), never its own words
                if self.function in _CHIP_FUNCTIONS:
                    from . import chips as _ch
                    chip = _CHIP_FUNCTIONS[self.function]
                    if self._experiment:
                        xp = xp if xp else _xp.get(conn, self._experiment)
                        if chip == "identity":
                            notes.append("THE TRIAL LIFE'S CLAIMS (the kernel's record) — "
                                         + _ch.claims_words(xp.get("claims") or _ch.claims_for(conn, xp)))
                        else:
                            notes.append("THE CANDIDATE'S DIFF against the standing version — "
                                         + _ch.diff_words(xp.get("diff") or _ch.diff_for(conn, xp)))
                            notes.append(_ch.refusals_words(_ch.refusals_for(conn, xp["agent"]), xp["agent"]))
                    elif chip == "identity":
                        notes.append(_ch.seats_words(_ch.seats_held(conn)))
                    else:
                        notes.append(_ch.refusals_words(_ch.refusals_for(conn)))
                    if _xp.KERNEL not in read:
                        read.append(_xp.KERNEL)
                # Phase 8 sp5: THE OPERATING STATE — a live reply handed to the grader by the grade beat: the
                # reply IS the evidence (another body's words, never mine); the grader's verdict feeds Trust
                if self.function == "grade" and self._current_ask:
                    from . import operating as _op
                    gid = _op.graded_ask_of(conn, self._current_ask)
                    if gid:
                        cur.execute("SELECT a.text, a.reply, a.served_by, coalesce(j.name, 'a body') FROM spine_asks a"
                                    " LEFT JOIN LATERAL (SELECT name FROM spine_joins WHERE did = a.served_by ORDER BY join_id DESC LIMIT 1) j ON true"
                                    " WHERE a.ask_id = %s", (gid,))
                        gr = cur.fetchone()
                        if gr:
                            self._grading = gid
                            notes.append(f"THE REPLY TO GRADE — {gr[3]} replied to {gr[0]!r}: {str(gr[1] or '')[:1500]!r} "
                                         "(theirs; grade it against the ask: the right thing, completely, plainly)")
                            fb = _op.feedback_on(conn, gid)
                            if fb:
                                notes.append("THE HUMAN'S THUMBS on this reply (evidence you weigh, never the verdict itself): "
                                             + "; ".join(f"{'up' if f['sign'] >= 0 else 'down'}" + (f" — {f['words']}" if f.get('words') else "") for f in fb))
                            if gr[2] and gr[2] not in read:
                                read.append(gr[2])
                # Phase 8 sp5: the critic asked under an IMPROVEMENT marker — the marked reply, the body that gave it and
                # its template are the evidence; the propose tool lands a draft under that body's owner
                if self.function == "critique" and xm.get("parent"):
                    cur.execute("SELECT kind, ref, note FROM spine_markers WHERE marker_id = %s", (xm["parent"],))
                    pm = cur.fetchone()
                    if pm and pm[0] == "improvement":
                        cur.execute("SELECT a.text, a.reply, a.served_by, coalesce(j.name, '') FROM spine_asks a"
                                    " LEFT JOIN LATERAL (SELECT name FROM spine_joins WHERE did = a.served_by ORDER BY join_id DESC LIMIT 1) j ON true"
                                    " WHERE a.ask_id = %s", (pm[1],))
                        ir = cur.fetchone()
                        who = ir[3] if ir and ir[3] else None
                        notes.append(f"THE IMPROVEMENT MARKED ({xm['parent']}): {pm[2] or 'no note'}"
                                     + (f" — on {who}'s reply to {ir[0]!r}: {str(ir[1] or '')[:800]!r}" if ir and who else ""))
                        if who:
                            from . import services as _sv
                            tpl = _sv.get(conn, f"{who}.template")
                            if tpl:
                                notes.append(f"{who}'S TEMPLATE on the shelf (version {tpl['version']}): "
                                             f"{json.dumps(tpl['manifest'], sort_keys=True)[:1200]}")
                            notes.append(f"If you see ONE concrete change to {who}'s template, prompt, skill or graph that would "
                                         f"cure this, call the propose tool ONCE with for='{who}' and the WHOLE declaration as body — "
                                         "it lands as a draft under that body's owner, who cuts it; never offer to cut.")
                            if ir[2] and ir[2] not in read:
                                read.append(ir[2])
                if person:
                    # the pack's third rung (canon 0003): the SHORT VERSION
                    # first — the digests of this human's earlier sessions,
                    # each naming its session; the verbatim comes after,
                    # and opens on demand through the recall door
                    from .digest import for_person
                    for d in for_person(conn, person, exclude=session,
                                        window=window, state=state):
                        notes.append("the short version of session "
                                     f"{d['session'][4:10]} (digest {d['digest_id'][4:10]},"
                                     f" {len(d['sources'])} sources): "
                                     + d["body"].replace("\n", " / "))
                if session:
                    cur.execute(
                        "SELECT a.text, a.reply, coalesce(j.name, 'a resident'),"
                        " a.served_by"
                        " FROM spine_asks a LEFT JOIN LATERAL ("
                        "  SELECT name FROM spine_joins WHERE did = a.served_by"
                        "  ORDER BY join_id DESC LIMIT 1) j ON true"
                        " WHERE a.session = %s AND a.status = 'replied'"
                        " AND a.ask_id <> %s AND coalesce(a.state, 'in') = %s"
                        " ORDER BY a.replied_at DESC LIMIT 6",
                        (session, self._current_ask, state))
                    for t, rp, who, by in cur.fetchall():
                        mine = by == self.identity.did
                        if mine and self.function == "grade":
                            continue        # scribe-class: my own words are
                        if mine:              # never material for my grade
                            notes.append(f"earlier in this session, asked: {t!r} — "
                                         f"I replied: {rp!r} (context, never the answer)")
                        else:                 # W8: labeled THEIRS, never mine to wear
                            notes.append(f"ANOTHER BODY'S WORDS — {who} replied to {t!r}: "
                                         f"{rp!r} (theirs; cite {who} by name, never repeat "
                                         "it as your own)")
                        if not mine and by and by not in read:
                            read.append(by)   # the chain will name them
                elif (self._current_marker or {}).get("parent"):
                    # W21: an ask filed under an intention's marker (a duty's
                    # occurrence, an objective) — the earlier runs of the SAME
                    # duty are MY OWN NOTES, never a human's repeated question;
                    # a run I declined is named a refusal, never an answer
                    from .harness import refused_words
                    cur.execute(
                        "SELECT a.reply, a.replied_at FROM spine_asks a"
                        " JOIN spine_markers m ON m.marker_id = a.marker"
                        " WHERE m.parent = %s AND a.served_by = %s AND a.status = 'replied'"
                        " AND a.ask_id <> %s ORDER BY a.replied_at DESC LIMIT 3",
                        (self._current_marker["parent"], self.identity.did, self._current_ask))
                    for rp, at in cur.fetchall():
                        when = at.strftime("%H:%M UTC") if at else "earlier"
                        first = " ".join((rp or "").split())[:300]
                        if refused_words(rp):
                            notes.append(f"an earlier run you declined ({when}); do not decline "
                                         f"again — a duty is served: {first!r}")
                        else:
                            notes.append(f"YOUR OWN NOTES from earlier runs of this duty — "
                                         f"{when}: {first!r}")
                else:
                    cur.execute(
                        "SELECT text, reply FROM spine_asks"
                        " WHERE served_by = %s AND status = 'replied'"
                        " AND session IS NULL ORDER BY replied_at DESC LIMIT 3",
                        (self.identity.did,))
                    for t, rp in cur.fetchall():
                        notes.append(f"earlier, asked: {t!r} — I replied: {rp!r}")
                if self.function == "workspace:monitor":
                    from .monitor import snapshot
                    snap = snapshot(conn, rails=False)
                    notes.append("monitor — outbox pending "
                                 f"{snap['values']['outbox_pending']}, oldest "
                                 f"{snap['values']['oldest_outbox_age_s']:.0f} s; "
                                 f"asks {snap['asks']}; bodies alive "
                                 f"{snap['values']['bodies_alive']}, dormant "
                                 f"{snap['values']['bodies_dormant']}")
                    for w in snap["watches"]:
                        notes.append(f"watch — {w['name']}: {w['metric']} "
                                     f"{w['value']} {w['op']} {w['threshold']} → "
                                     f"{'green' if w['ok'] else 'RED'}")
                    if snap["harness"]:
                        h = snap["harness"]
                        notes.append(f"harness — {h['template']} v{h['version']}: "
                                     f"{h['passed']} passed, {h['failed']} failed")
                elif self.function == "workspace:workshop":
                    # Phase 8 sp3: the Workshop's agent reads the SHELF's crafts (what stands,
                    # who wears it) and — on the author's OWN ask only — the one draft the
                    # author has open in the Workshop, named in the ask as [draft <id>]; a
                    # draft is never recalled otherwise (AG-9): the author's seat reads it
                    from . import crafts, services
                    from .crafts import CRAFT_KINDS
                    rows = [r for r in services.listing(conn) if r["kind"] in CRAFT_KINDS]
                    notes.append(f"THE SHELF holds {len(rows)} crafts (name · kind · version · state · worn by): "
                                 + "; ".join(f"{r['name']} · v{r['version']} · {r['state']} · worn by {r.get('worn_by', 0)}"
                                             for r in rows[:80]))
                    for r in rows[:80]:
                        m = r.get("manifest") or {}
                        line = (m.get("words") or m.get("nature") or m.get("charge") or
                                (m.get("text") or "")[:160] or "")
                        if r["kind"] == "graph":
                            line = (f"entry {m.get('entry')} · nodes " + ", ".join(
                                f"{n.get('id')} ({n.get('kind')}" + (f", prompt {n['prompt']}" if n.get('prompt') else "")
                                + (f", skill {n['skill']}" if n.get('skill') else "") + (f", tools {n['tools']}" if n.get('tools') else "")
                                + (f", mind {n['mind']}" if n.get('mind') else "") + ")" for n in m.get("nodes") or [])
                                + " · edges " + ", ".join(f"{e.get('from')}→{e.get('to')}" + (f" {crafts.when_words(e)}" if e.get('when') else "")
                                                          for e in m.get("edges") or []))
                        elif r["kind"] == "template":
                            line = f"a {m.get('kind', 'resident')} body · graph {m.get('graph')} · {m.get('nature') or m.get('charge') or ''}"[:220]
                        notes.append(f"craft {r['name']}: {line}")
                    import re as _re
                    for did_ in _re.findall(r"\[draft (draft_[0-9a-f]+)\]", s["text"]):
                        d = crafts.draft(conn, person, did_) if person else None
                        if d is None:
                            notes.append(f"the ask names draft {did_}, which is not this human's — nothing read")
                            continue
                        v = crafts.validate(d["kind"], d["body"])
                        notes.append(f"THE OPEN DRAFT — the human's own {d['name']} {d['kind']} ({d['draft_id']}), "
                                     f"{'reads whole' if v['ok'] else 'NOT whole yet: ' + str(v['reason'])}. Its declaration: "
                                     f"{json.dumps(d['body'], ensure_ascii=False)}. When the human asks to CHANGE it, call the "
                                     f"`draft` tool ONCE with name {d['name']!r}, kind {d['kind']!r} and the WHOLE edited "
                                     "declaration as `body` — never a fragment, never a description of the change instead. "
                                     "The cut is the human's alone: say “say cut the "
                                     f"{d['name']} draft” and never offer to cut it yourself.")
                elif (self.function or "").startswith("workspace:"):
                    # a workspace agent reads ITS workspace's facts (the
                    # binding names which); the crew: every body here
                    cur.execute(
                        "SELECT DISTINCT ON (name) name, kind, life, policy_version,"
                        f" capabilities, did FROM spine_joins WHERE {ev.WITHIN}"
                        " ORDER BY name, join_id DESC", ev.within_params(ev.universe()))
                    for n, k, life, pv, caps, did in cur.fetchall():
                        notes.append(f"crew card — {n}: {k}, life {life}, wearing "
                                     f"covenant policy v{pv}, capabilities "
                                     f"{', '.join(json.loads(caps or '[]')) or 'none declared'}, "
                                     f"self {did[-8:]}")
                st = OrrethStore(conn, by_did=self.identity.did, state=state)
                if window and window.get("from") and window.get("to"):
                    # MEM-1 by timeframe (P6): the window the human typed is
                    # a lens over ALL their worldlines in this world — every
                    # ask they made and every word I acquired between X and Y.
                    # It goes FIRST, under a header: it IS the answer to a
                    # windowed ask (walk #5: packed deep and unlabeled, the
                    # mind denied having any record of the window)
                    head = [f"THE WINDOW the human asked about: {window['from'][:16]} → "
                            f"{window['to'][:16]}. What was asked and answered inside it "
                            "(this IS the record: open your answer by naming the window "
                            "and what is listed here; an ask not listed here was NOT "
                            "asked in it — name no other; never open with a denial):"]
                    cur.execute(
                        "SELECT a.text, a.reply, a.asked_at, coalesce(j.name, 'a resident')"
                        " FROM spine_asks a LEFT JOIN LATERAL ("
                        "  SELECT name FROM spine_joins WHERE did = a.served_by"
                        "  ORDER BY join_id DESC LIMIT 1) j ON true"
                        " WHERE a.person = %s AND a.scope = %s AND a.status = 'replied'"
                        " AND a.asked_at BETWEEN %s AND %s AND a.ask_id <> %s"
                        " AND coalesce(a.state, 'in') = %s"
                        " ORDER BY a.asked_at LIMIT 12",
                        (person, ev.scope(), window["from"], window["to"],
                         self._current_ask, state))
                    inside = []
                    for t, rp, at, who in cur.fetchall():
                        inside.append(f"in the window, at {at.strftime('%a %b %d %H:%M')}, "
                                      f"asked: {t!r} — {who} replied: {rp!r}")
                    for m in st.within(self.name, window["from"], window["to"]):
                        inside.append(f"in the window I acquired [{m['key']}] at "
                                      f"{m['landed_at'][:16]}: {m['body']}")
                    if not inside:
                        inside = ["nothing was asked or acquired inside this window"]
                    notes[:0] = head + inside              # first, always
                if window and window.get("to"):
                    # MEM-4 in the chat: inside a window the memories read
                    # as they stood at the window's END — what we knew then
                    for m in st.search(self.name, s["text"][:60], limit=3,
                                       at=window["to"]):
                        notes.append(f"as of {window['to'][:16]} I remembered "
                                     f"[{m['key']}]: {m['body']}")
                elif self.function == "impact":
                    # P6 sp3: MITL recalls the CANON it wears — the passages
                    # that match the change (the ask's first line names it),
                    # each named by its source path; the same store, the
                    # same projection, only a wider pack
                    head = s["text"].split("\n", 1)[0]
                    for m in st.search(self.name, head[:240], limit=6):
                        notes.append(f"the canon says [{m['key']}]: {m['body']}")
                else:
                    for m in st.search(self.name, s["text"][:60], limit=3):
                        notes.append(f"I remember [{m['key']}]: {m['body']}")
            step = (f"recalled {len(notes)} notes" if notes
                    else "recalled nothing yet — a young memory")
            steps = s["steps"] + [step]
            if read and conn is not None:
                cur.execute("SELECT DISTINCT ON (did) did, name FROM spine_joins"
                            " WHERE did = ANY(%s) ORDER BY did, join_id DESC",
                            (read,))
                names = {d: n for d, n in cur.fetchall()}
                steps.append("read the session's results by "
                             + ", ".join(names.get(d, d if not d.startswith("did:") else d[-8:]) for d in read))   # W106: "e kernel"
            return {"notes": notes, "steps": steps, "read": read}

        def route(s: _State) -> dict:
            """Phase 8 sp2, THE HULL: which edge this ask takes, read off its marker — a thought
            or a root is CHAT (a human's ask); a parent of a structural kind is WORK (an
            intention's occurrence, an objective); any other parent kind is an EVENT."""
            from . import crafts
            mk = self._current_marker or {}
            parent_kind = None
            if mk.get("parent") and self._serve_conn is not None:
                cur = self._serve_conn.cursor()
                cur.execute("SELECT kind FROM spine_markers WHERE marker_id = %s", (mk["parent"],))
                r = cur.fetchone()
                parent_kind = r[0] if r else None
            edge = crafts.hull_edge(mk.get("kind"), parent_kind)
            return {"edge": edge, "steps": s["steps"] + [crafts.edge_words(edge, parent_kind)]}

        def edge(_s: _State) -> dict:
            return {}                                    # the edge itself is the route's word; the node is the hop

        def work(s: _State) -> dict:
            """THE WORK NODE: the template's graph component, node by node along its one path —
            `think` is the metered mind, `echo` the words back. No declaration, no work — said."""
            from . import crafts
            g = self.graph_declaration()
            if g is None:
                want = self.template.get("graph")
                return {"reply": (f"CANNOT ACT: my template names the graph {want!r}, which is not on the "
                                  "shelf nor shipped with the spine — nothing ran; register it, or restore it."),
                        "steps": s["steps"] + [f"the work node found no graph named {want!r} — nothing ran"]}
            br = crafts.branches(g)                      # Phase 8 sp3: the graph may BRANCH — the way out is
            out: dict = {"steps": list(s["steps"]) + [    # picked as the run goes, each pick said in the journey
                f"the work node runs graph {g['name']}: " + " → ".join(crafts.path(g))
                + (f" · branches at {', '.join(br)} — the way out picked as the run goes" if br else "")]}
            cur_state = dict(s, steps=out["steps"])
            cur, visited = g.get("entry"), 0
            while cur is not None and visited <= len(g.get("nodes", [])):
                visited += 1
                n = crafts.node(g, cur)
                if n["kind"] == "echo":
                    part = {"reply": echo_reply(self.name, cur_state["text"]),
                            "steps": cur_state["steps"] + [f"echoed every word — none summarized away "
                                                            f"({self.template.get('persona') or 'a plain-spoken echo'})"]}
                elif n["kind"] == "import":              # Phase 8 sp5: a repo'd graph run inside the hull (dev universes only)
                    from . import operating as _op
                    reply, said = _op.run_import(self._serve_conn, n, cur_state["text"])
                    part = {"reply": reply, "steps": cur_state["steps"] + [said]}
                else:
                    part = think(cur_state, n)
                cur_state.update(part)
                out.update(part)
                if part.get("hold"):
                    break                                # a held act stops the line at a safe boundary
                cur, why = crafts.next_node(g, cur, {"edge": cur_state.get("edge"), "ask": cur_state["text"],
                                                     "reply": cur_state.get("reply")})
                if why:
                    cur_state["steps"] = cur_state["steps"] + [why]
                    out["steps"] = cur_state["steps"]
            return out

        def think(s: _State, node: dict | None = None) -> dict:
            node = node or {}
            if self.function == "grade" and not s.get("read"):
                # scribe-class (covenant rule 2): with nothing but my own
                # words in view there is nothing I may grade — refused
                # before any thinking, honestly
                return {"reply": ("Nothing here to grade but my own words — "
                                  "I never grade my own yardstick. Bring a "
                                  "resident's answer into this session and "
                                  "ask me again."),
                        "steps": s["steps"] + ["refused to grade my own work "
                                               "— scribe-class"]}
            if self.gateway is not None and self._serve_conn is not None:
                from .tools import ConsequentialHold, ToolDoor
                mind = self.template.get("mind") or {}
                if self.function == "impact":
                    from .mitl import SYSTEM as _mitl_system   # P6 sp3: MITL's own
                    system = _mitl_system                      # words, the same body
                elif self.kind == "firmware":
                    system = (
                        f"You are the {self.name} — a firmware agent of "
                        "Orreth, named by your function, wearing no persona. "
                        f"Your charge: {self.charge}. You "
                        "work over what the residents brought into this "
                        "session — your recalled notes — and nothing else. "
                        "Laws: attribute every point to the resident who said "
                        "it, by name; never present another's words as your "
                        "own; plain words anyone can understand; complete, "
                        "never a teaser.")
                else:
                    system = (
                        f"You are {self.name}, a resident of Orreth — "
                        f"{self.template['persona']}. Laws you live by: answer "
                        "in plain, friendly words anyone can understand; answer "
                        "COMPLETELY — the full reply, never a teaser; when your "
                        "recalled notes bear on the ask, use them and say so "
                        "plainly; never invent a memory you were not handed; "
                        "use your tools when the ask needs the real world. When "
                        "the ask names a time window, the notes under 'THE "
                        "WINDOW' ARE the record of that window — answer from "
                        "them, and never say you have no record while they "
                        "are there.")
                if "tools:mark" in self.template.get("capabilities", []):
                    system += (" If you observe an IMPROVEMENT to what you "
                               "are executing, mark it: call the mark tool "
                               "with kind 'improvement' and a short note — "
                               "other bodies act on marks.")   # 0006's policy line
                if "tools:propose" in self.template.get("capabilities", []):   # Phase 8 sp5: the improvement loop's actor
                    system += (" When your notes carry THE IMPROVEMENT MARKED, call the propose tool ONCE with the whole "
                               "declaration of one concrete change to that body's template, prompt, skill or graph — it lands "
                               "as a draft under the body's owner, who edits and cuts it. A thin mark is not a reason to wait: "
                               "choose the concrete words yourself (a greeting, a line, a node), say in `words` what you chose, "
                               "and let the owner change them in the draft. Never ask the owner back before proposing; never "
                               "offer to cut; never change anything yourself.")   # W115: the critic asked JB back instead of drafting
                worn: list[str] = []                   # Phase 8 sp3: the node's refs, said in the journey
                if node.get("prompt"):                 # Phase 8 sp2: a node's prompt component, from the shelf
                    from . import crafts
                    pr = crafts.get(self._serve_conn, str(node["prompt"]), "prompt")
                    if pr and pr["state"] != "retired":
                        system += "\n\n" + str(pr["manifest"].get("text") or "")
                        worn.append(f"prompt {node['prompt']}")
                    else:
                        worn.append(f"prompt {node['prompt']} (not on the shelf — not read)")
                if node.get("skill"):                  # Phase 8 sp3: a node's skill component — the words a body follows
                    from . import crafts
                    sk = crafts.get(self._serve_conn, str(node["skill"]), "skill")
                    if sk and sk["state"] != "retired":
                        system += "\n\nTHE SKILL you follow here — " + str(sk["manifest"].get("words") or "") + \
                                  ":\n" + str(sk["manifest"].get("text") or "")
                        worn.append(f"skill {node['skill']}")
                    else:
                        worn.append(f"skill {node['skill']} (not on the shelf — not read)")
                system += "\n\n" + self.seat_words(self._serve_conn, self._current_ask)
                prompt = ""
                if s["notes"]:
                    prompt += ("Your recalled notes:\n- "
                               + "\n- ".join(s["notes"]) + "\n\n")
                prompt += f"The ask: {s['text']}"
                caps = list(self.template.get("capabilities", []))
                if node.get("tools") is not None:      # Phase 8 sp3: the node NARROWS the door to the tools it names —
                    asked = {f"tools:{t}" for t in node["tools"]}          # never past what the template declares
                    shut = sorted(t[6:] for t in asked if t not in caps)
                    caps = [c for c in caps if not c.startswith("tools:") or c in asked]
                    worn.append("tools " + (", ".join(node["tools"]) or "none")
                                + (f" ({', '.join(shut)} never declared by the template — the door stays shut)" if shut else ""))
                if node.get("mind"):                   # Phase 8 sp3: the node pins the stall it thinks with
                    mind = dict(mind, pin=str(node["mind"]))
                    worn.append(f"mind pinned to the {node['mind']} stall")
                node_step = [f"node {node.get('id')}: " + " · ".join(worn)] if worn else []
                door = ToolDoor(self._serve_conn, did=self.identity.did,
                                capabilities=caps, name=self.name,
                                marker=(self._current_marker or {}).get("id"),
                                ask=self._current_ask,          # AG-7: the door wears
                                chain=self._full_chain(s.get("read")))   # the chain
                deltas = None
                if self.on_delta is not None and self._current_ask:
                    aid = self._current_ask
                    deltas = lambda t, a=aid: self.on_delta(a, t)  # noqa: E731
                retried = []                       # W26: the mind's silence, said in words
                try:
                    if hasattr(self.gateway, "think_acting") and \
                            door.schemas():
                        reply, acts = self.gateway.think_acting(
                            self._serve_conn, did=self.identity.did,
                            system=system, prompt=prompt, door=door,
                            model=mind.get("model"), on_delta=deltas,
                            subject=self.name, klass=mind.get("class"),
                            pin=mind.get("pin"), ask=self._current_ask)   # P6.5 sp3: the Stable decides the mind · sp5: the meter wears the ask
                        if not (reply or "").strip():          # W26: asked again, once
                            reply, more = self.gateway.think_acting(
                                self._serve_conn, did=self.identity.did,
                                system=system, prompt=prompt, door=door,
                                model=mind.get("model"), on_delta=deltas,
                                subject=self.name, klass=mind.get("class"), pin=mind.get("pin"), ask=self._current_ask)
                            acts, retried = acts + more, [W26_STEP]
                            if not (reply or "").strip():
                                reply = W26_WORDS
                        return {"reply": reply,
                                "steps": s["steps"] + node_step + acts + retried
                                + ["thought it through the metered gateway"]}
                    reply = self.gateway.think(
                        self._serve_conn, did=self.identity.did,
                        system=system, prompt=prompt,
                        model=mind.get("model"), on_delta=deltas,
                        subject=self.name, klass=mind.get("class"), pin=mind.get("pin"), ask=self._current_ask)   # P6.5 sp3 · sp5
                    if not (reply or "").strip():              # W26: asked again, once
                        reply = self.gateway.think(
                            self._serve_conn, did=self.identity.did,
                            system=system, prompt=prompt,
                            model=mind.get("model"), on_delta=deltas,
                            subject=self.name, klass=mind.get("class"), pin=mind.get("pin"), ask=self._current_ask)
                        retried = [W26_STEP]
                        if not (reply or "").strip():
                            reply = W26_WORDS
                except ConsequentialHold as h:
                    return {"hold": {"tool": h.tool, "args": h.tool_args,
                                     "class": h.consequence, "level": h.level},
                            "steps": s["steps"] + node_step
                            + [f"the {h.tool} act is {h.consequence} — "
                               "held at the interlock for the human"
                               + ("" if h.level == "L2" else f" · needs {h.level}")]}
                return {"reply": reply,
                        "steps": s["steps"] + node_step + retried + ["thought it through the "
                                                                     "metered gateway"]}
            if self.kind == "firmware":
                # P6 sp4's side cure (found by sp3): a firmware body without a
                # gateway wears no persona — the echo names it plainly instead
                persona = self.template.get("persona") or f"the {self.name}, a firmware body"
                reply = (f"I am {self.name} — {persona}. "
                         f"You asked: \"{s['text']}\" — and that is every word "
                         f"of it, back to you, none summarized away.")
                return {"reply": reply,
                        "steps": s["steps"] + ["thought it through"]}
            # W24 (walk #8): a body says its nature ONCE, on its chip — the
            # reply is the echoed words alone; the assertion (the body proven
            # before the mind arrives, none summarized away) lives in the
            # journey — the record — never in the bubble. A question it
            # cannot answer by nature earns one plain line more.
            return {"reply": echo_reply(self.name, s["text"]),
                    "steps": s["steps"] + [f"echoed every word — none summarized away "
                                           f"({self.template.get('persona') or 'a plain-spoken echo'})"]}

        g = StateGraph(_State)
        g.add_node("hear", hear)
        g.add_node("recall", recall)
        g.add_node("route", route)                      # Phase 8 sp2: THE HULL
        g.add_node("edge-chat", edge)
        g.add_node("edge-work", edge)
        g.add_node("edge-event", edge)
        g.add_node("work", work)
        g.add_edge(START, "hear")
        g.add_edge("hear", "recall")
        g.add_edge("recall", "route")
        g.add_conditional_edges("route", lambda s: "edge-" + (s.get("edge") or "chat"),
                                {"edge-chat": "edge-chat", "edge-work": "edge-work", "edge-event": "edge-event"})
        for e in ("edge-chat", "edge-work", "edge-event"):
            g.add_edge(e, "work")
        g.add_edge("work", END)
        return g.compile(checkpointer=checkpointer)

    def seat_words(self, conn, ask_id: str | None) -> str:
        """W12 (JB's law): what the kernel hands EVERY body — resident or
        firmware — with its system words: the clock (now in UTC, the
        human's zone, the sentence), the world, THE HUMAN's own profile
        (P7 sp8, W58 — the pack's first slot by 0003), the covenant's slice, the
        slice of the ontology its template names (`ontology: [...]`,
        searched in MITL's acquired corpus — v0: the best passage per
        entry), and the common laws of the serve."""
        from . import profile
        parts = [time_words(human_zone(conn, ask_id)),
                 f"THE WORLD you serve in is {self.scope} ({_levels.words(self.scope) if _levels.ok(self.scope) else 'a world'}); you are {self.name}, "
                 f"a {self.kind} body" + (f" whose function is {self.function}" if self.function else "") + ".",
                 profile.seat_words(conn, ask_id),     # P7 sp8: slot 1 of the pack — who this human is (W58)
                 COVENANT_SLICE]
        for entry in self.template.get("ontology", []) or []:
            try:
                from .mitl import NAME as _mitl
                from .store import OrrethStore
                hits = OrrethStore(conn, by_did=self.identity.did).search(_mitl, str(entry), limit=6) \
                    if conn is not None else []
            except Exception:
                hits = []
            if hits:                       # v0: the passage holding MOST of the entry's words wins
                words = [w.lower() for w in str(entry).split() if len(w) > 2]
                best = max(hits, key=lambda h: sum(w in h["body"].lower() for w in words))
                parts.append(f"The canon on '{entry}' [{best['key']}]: {best['body'][:700]}")
            else:
                parts.append(f"The canon on '{entry}': not acquired on this ground yet — "
                             "say so if asked, never invent it.")
        parts.append(COMMON_LAWS)
        return "\n".join(parts)

    def prepare(self, conn) -> None:
        """Working memory (canon 0003 · MEM-2): the graph checkpointed on
        the ground after every hop — on a connection of its OWN, so a
        serve that rolls back keeps the hops it already made and a life
        that dies mid-graph resumes at its hop, never re-hearing, never
        re-recalling. Called once per life, at the first serve."""
        if self._ckpt_graph is not None:
            return
        import psycopg
        from langgraph.checkpoint.postgres import PostgresSaver
        # the cure (2026-10-08): the saver's line is opened for THIS serve window and closed with
        # the body's line (`release_line`); the checkpoints are rows and outlive every line — only
        # the connection comes and goes. The migrations run once per life.
        own = psycopg.connect(conn.info.dsn, password=conn.info.password,
                              autocommit=True, application_name=f"orreth body {self.name} memory")
        saver = PostgresSaver(own)
        if not self._ckpt_setup:
            own.execute("SELECT pg_advisory_lock(742199)")      # the DDL guard, session-
            try:                                                # scoped: the saver's
                saver.setup()                                   # migrations commit on
            finally:                                            # their own
                own.execute("SELECT pg_advisory_unlock(742199)")
            self._ckpt_setup = True
        self._ckpt_conn = own
        self._ckpt_graph = self._build_graph(saver)

    # ---- the line (the ground connections cure, 2026-10-08) ------------------------------

    def hold_line(self, dsn: str | None = None):
        """The ground connection this body serves on — opened now if it holds none (named on the
        ground as `orreth body <name>`), the same one while it stands. A body holds a line only
        while it serves: the ground's connections follow the SERVES, never the seated crew."""
        import psycopg
        if self._line is not None and not self._line.closed:
            self._line_last = time.monotonic()
            return self._line
        self._line_dsn = dsn or self._line_dsn
        if not self._line_dsn:
            from .rails import PG_DSN
            self._line_dsn = PG_DSN
        self._line = psycopg.connect(self._line_dsn, autocommit=True, application_name=f"orreth body {self.name}")
        self._line_last = time.monotonic()
        return self._line

    def holds_line(self) -> bool:
        return self._line is not None and not self._line.closed

    def release_line(self, idle_s: float = 0.0) -> bool:
        """Let the line go once it has served nothing for `idle_s` (0: now) — and the working
        memory's line with it. True when a line was closed. The next command opens a fresh one."""
        if not self.holds_line():
            return False
        if idle_s > 0 and time.monotonic() - self._line_last < idle_s:
            return False
        for c in (self._ckpt_conn, self._line):
            try:
                if c is not None:
                    c.close()
            except Exception:                              # noqa: BLE001 — a line already gone is gone
                pass
        self._ckpt_conn, self._ckpt_graph = None, None
        self._line = None
        if self._serve_conn is not None and getattr(self._serve_conn, "closed", False):
            self._serve_conn = None
        return True

    def keep_lease(self, dsn: str | None = None, every_s: float | None = None) -> bool:
        """The body's presence, kept on a cadence (M2): renewed every `every_s` (`presence.RENEW_S`)
        — on the held line while the body serves, else on a line opened for the renew and closed
        with it, so an idle body holds nothing between renews. True when renewed now."""
        import psycopg
        from . import presence
        every = presence.RENEW_S if every_s is None else float(every_s)
        now = time.monotonic()
        if now - self._lease_at < every:
            return False
        if self.holds_line():
            presence.renew(self._line, self.identity.did, self.name, self.kind, scope=self.scope)
        else:
            dsn = dsn or self._line_dsn
            if not dsn:
                from .rails import PG_DSN
                dsn = PG_DSN
            self._line_dsn = dsn
            with psycopg.connect(dsn, autocommit=True, application_name=f"orreth body {self.name} lease") as brief:
                presence.renew(brief, self.identity.did, self.name, self.kind, scope=self.scope)
        self._lease_at = now
        return True

    # ---- service --------------------------------------------------------------

    def _serve_ask(self, cur, ask_id: str, chain: list[str]) -> None:
        """The one-transaction heart: read the ask, run the graph, land
        journey + reply rows AND their events together."""
        cur.execute("SELECT text, person, status FROM spine_asks"
                    " WHERE ask_id = %s FOR UPDATE", (ask_id,))
        row = cur.fetchone()
        if row is not None and row[2] != "received":
            # 0002's conditional-transition law: a re-dispatched fact is a
            # NEW command the inbox cannot absorb — the BUSINESS state must
            # refuse. An ask already settled (or held) is never re-served.
            return
        if row is None:
            # a stale command (the ask is not on THIS ground) is TERMINAL,
            # never a retry loop (0002's failure table): the refusal lands
            # as a visible journey event and the footprint stands
            j = ev.make_envelope(
                kind="event", type=JOURNEY, universe_id=ev.universe(),
                scope_path=self.scope,
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: refused a stale command — "
                                 f"this ask is not on my ground"},
                correlation_id=ask_id, authority_chain=chain or None)
            outbox.add_row(cur, ev.encode(j), j["message_id"])
            return
        text, person, _status = row
        self._current_ask = ask_id
        self._current_chain = list(chain) if chain else [person]
        from . import markers as _mk
        cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ask_id,))
        _mrow = cur.fetchone()
        self._current_marker = _mk.as_env(self._serve_conn, _mrow[0]) if _mrow and _mrow[0] else None
        self._experiment = None
        self._grading = None
        initial = {"text": text, "reply": "", "steps": [], "notes": [],
                   "hold": None, "read": [], "edge": ""}
        resumed = None
        if self._ckpt_graph is not None:            # MEM-2: resume at the hop
            config = {"configurable": {"thread_id": ask_id}}
            snap = self._ckpt_graph.get_state(config)
            if snap.next:                            # a life died mid-graph
                resumed = (f"resumed at {snap.next[0]} — the hops before it "
                           "were already mine")
                out = self._ckpt_graph.invoke(None, config)
            else:
                out = self._ckpt_graph.invoke(initial, config)
        else:
            out = self._graph.invoke(initial)
        if resumed:
            out = dict(out, steps=list(out["steps"]) + [resumed])
        full_chain = self._full_chain(out.get("read"))
        self._journey(cur, ask_id, out["steps"], full_chain)
        if out.get("hold"):
            held = dict(out["hold"])
            held.setdefault("class", "consequential"); held.setdefault("level", "L2")
            if held["level"] == "L2":
                from .tools import interlock_words_for
                question = interlock_words_for(held["tool"], held.get("args") or {})   # W23: rule 11's words · W30: the act NAMED
            else:                                # P6 sp1: the demand rises
                from .proof import question_for
                question = question_for(held["level"], f"The {held['tool']} act")
            cur.execute(
                "UPDATE spine_asks SET status = 'awaiting-confirm',"
                " reply = %s, served_by = %s, held = %s WHERE ask_id = %s",
                (question, self.identity.did, json.dumps(held), ask_id))
            n = ev.make_envelope(
                kind="event", type=CONFIRM_NEEDED, universe_id=ev.universe(),
                scope_path=self.scope,
                payload={"ref": ask_id, "hash": "sha256:-",
                         "tool": held["tool"], "class": held["class"],
                         "level": held["level"]},     # the hold wears its level
                correlation_id=ask_id, authority_chain=full_chain,
                aggregate={"type": "ask", "id": ask_id,
                           "sequence": _next_seq(cur, ask_id)})
            outbox.add_row(cur, ev.encode(n), n["message_id"])
            return
        self._land_reply(cur, ask_id, out["reply"], full_chain)
        if self._grading and self.function == "grade":
            # Phase 8 sp5: the grader's SIGNED VERDICT on a LIVE reply — under its own DID, in its reply's
            # transaction (rule 2); Trust reads it; a verdict not in the form is said, never guessed
            from . import experiments as _xp, operating as _op
            v = _op.grade_of_live(out.get("reply") or "")
            if v["grade"]:
                _xp.verdict_in(cur, experiment_id=None, identity=self.identity, by_name=self.name, reviewer="grader",
                               ask_id=ask_id, verdict=v, words=out.get("reply") or "", scope=self.scope, on_ask=self._grading)
                self._journey(cur, ask_id, [f"wrote my signed verdict on {self._grading} under my own name — grade {v['grade']}"], full_chain)
            else:
                self._journey(cur, ask_id, [f"no verdict written on {self._grading} — my reply did not keep the form `grade: <A-F> — …`"], full_chain)
        if self._experiment and (self.function in ("grade", "critique") or self.function in _CHIP_FUNCTIONS):
            # Phase 8 sp4: a reviewer's SIGNED VERDICT on an Experiment — written by the reviewer
            # itself, under its own DID, in its reply's transaction (rule 2: nothing grades its own
            # yardstick; the evidence was the kernel's record of the arms, packed at recall).
            # Phase 8 sp6: the two chips the same — identity: kept|broken · security: clear|concern
            from . import chips as _ch, experiments as _xp
            reply = out.get("reply") or ""
            if self.function == "grade":
                reviewer, verdict = "grader", _xp.grade_of(reply)
                kept = verdict["candidate"] is not None or verdict["verdict"] is not None
            elif self.function == "critique":
                r = _xp.risk_of(reply)
                line = next((ln.split("—", 1)[1].strip() for ln in reply.splitlines() if ln.lower().lstrip("* ").startswith("risk:") and "—" in ln), None)
                reviewer, verdict, kept = "critic", {"risk": r, "line": line}, r is not None
            else:
                reviewer = _CHIP_FUNCTIONS[self.function]
                verdict, kept = _ch.verdict_of(reviewer, reply)
            if kept:
                _xp.verdict_in(cur, experiment_id=self._experiment, identity=self.identity, by_name=self.name,
                               reviewer=reviewer, ask_id=ask_id, verdict=verdict, words=reply, scope=self.scope)
                self._journey(cur, ask_id, [f"wrote my signed verdict on the experiment {self._experiment} under my own name"],
                              full_chain)
            else:
                self._journey(cur, ask_id, [f"no verdict written on the experiment {self._experiment} — my reply did not keep the form"],
                              full_chain)

    def _full_chain(self, read: list | None) -> list[str]:
        """The chain this body wears for the serve in hand (AG-8 · AG-7):
        the command's chain (the origin human first) → the selves whose
        results I read → me. The journey, the reply, the hold and every
        tool call wear the SAME chain."""
        full_chain = list(self._current_chain or [])
        for by in read or []:
            if by not in full_chain:
                full_chain.append(by)
        if self.identity.did not in full_chain:
            full_chain.append(self.identity.did)
        return full_chain

    def _journey(self, cur, ask_id: str, steps: list, chain: list) -> None:
        for step in steps:
            j = ev.make_envelope(
                kind="event", type=JOURNEY, universe_id=ev.universe(),
                scope_path=self.scope,
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: {step}"},
                correlation_id=ask_id, authority_chain=chain,
                aggregate={"type": "ask", "id": ask_id,
                           "sequence": _next_seq(cur, ask_id)},
                marker=self._current_marker)       # every hop says WHY
            outbox.add_row(cur, ev.encode(j), j["message_id"])

    def _land_reply(self, cur, ask_id: str, reply: str, chain: list,
                    status: str = "replied", proof: str = "L1") -> None:
        # P6 sp1: every act's record wears its proof level (L1 · L2 ·
        # L3-code · L3-master) on the row AND on the reply's envelope
        # W17: replied_at is the LANDING on the ground's clock — clock_timestamp(),
        # never now(): inside the serve's one transaction now() is the transaction's
        # START, and a long thought read "completed (0.2 s)" on the glass
        cur.execute(
            "UPDATE spine_asks SET status = %s, reply = %s, proof = %s,"
            " served_by = %s, replied_at = clock_timestamp() WHERE ask_id = %s",
            (status, reply, proof, self.identity.did, ask_id))
        r = ev.make_envelope(
            kind="event", type=REPLY, universe_id=ev.universe(), scope_path=self.scope,
            payload={"ref": ask_id, "hash": ev.content_hash(reply), "proof": proof},
            correlation_id=ask_id, authority_chain=chain, marker=self._current_marker,
            aggregate={"type": "ask", "id": ask_id,
                       "sequence": _next_seq(cur, ask_id)})
        outbox.add_row(cur, ev.encode(r), r["message_id"])

    def _confirm_ask(self, cur, ask_id: str, approved: bool,
                     chain: list[str], *, proof: str | None = None,
                     by: str | None = None, reason: str | None = None) -> None:
        """The human's word arrives (canon 0001 L2 · P6 sp1 L3): a
        deliberate yes — judged at the door for its proof — releases the
        held act through the door; anything else cancels — cancel is the
        default, and a cancelled act NEVER ran. `reason` names a cancel
        the kernel made (three wrong proofs rest the act)."""
        from .tools import ToolDoor
        cur.execute("SELECT status, held, person FROM spine_asks"
                    " WHERE ask_id = %s FOR UPDATE", (ask_id,))
        row = cur.fetchone()
        full_chain = list(chain) if chain else []
        if self.identity.did not in full_chain:
            full_chain.append(self.identity.did)
        if row is None or row[0] != "awaiting-confirm" or not row[1]:
            self._journey(cur, ask_id,
                          ["a confirm arrived for nothing held — refused "
                           "as stale"], full_chain or None)
            return
        held = json.loads(row[1])
        level = proof or held.get("level") or "L2"
        if approved:
            cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ask_id,))
            mrow = cur.fetchone()               # the released act hangs under ITS ask
            door = ToolDoor(self._serve_conn, did=self.identity.did,
                            capabilities=self.template.get(
                                "capabilities", []), name=self.name,
                            marker=(mrow[0] if mrow and mrow[0] else None),
                            ask=ask_id, chain=full_chain)   # AG-7: the same chain
            result = door.call(held["tool"], held["args"], confirmed=True)
            word = {"L3-code": "the code was right",
                    "L3-master": f"{(by or '?').split(':')[-1]} confirmed as master"
                    }.get(level, "the human said yes")
            self._journey(cur, ask_id,
                          [f"{word} — the {held['tool']} act ran through "
                           f"the door · proof {level}"], full_chain)
            self._land_reply(cur, ask_id, f"Done, on your word: {result}",
                             full_chain, proof=level)
        else:
            self._journey(cur, ask_id,
                          [f"{reason or 'the human cancelled'} — the "
                           f"{held['tool']} act never ran (cancel is always "
                           "the default)"], full_chain)
            self._land_reply(
                cur, ask_id,
                ("Rested — three wrong proofs were given, so nothing was "
                 "done. The act is at rest, recorded; ask again when you "
                 "are ready." if reason else
                 "Cancelled — nothing was done. Cancel is always the "
                 "default here."), full_chain, status="cancelled")

    def _stand_on(self, conn) -> None:
        """Every ground ensured on this connection (once per ground, per process — `outbox.once`),
        the serving connection remembered, the working memory prepared on it."""
        ensure_schema(conn)
        inbox.ensure_schema(conn)
        outbox.ensure_schema(conn)
        from . import gateway as _gw, harness as _hz, tools as _tl
        from . import store as _st
        _gw.ensure_schema(conn)     # pre-flagged: the serving transaction
        _tl.ensure_schema(conn)     # never runs DDL, never takes the lock
        _st.ensure_schema(conn)
        _hz.ensure_schema(conn)     # P7 sp6: a harness run may ride the bench
        from . import ground as _ground
        _ground.ensure_all(conn)    # EVERY ground, at birth (found live: the
        self._serve_conn = conn        # markers DDL inside one serve wedged the Bridge)
        try:
            self.prepare(conn)         # MEM-2: working memory on the ground
        except Exception:
            self._ckpt_graph = None    # a ground without it still serves

    def serve_once(self, conn=None, *, rabbit_url: str | None = None,
                   idle_s: float = 5.0, max_commands: int = 50) -> dict:
        """Consume the invocation rail: effect + events in one
        transaction through the durable inbox, ACK only after commit.

        `conn` None (the cure, 2026-10-08): the body polls its bench holding NO
        ground connection and takes its line (`hold_line`) only when a command
        lands — the ground's connections follow the serves. A connection given
        is stood on as before (the reference's tests, the harness)."""
        if conn is not None:
            self._stand_on(conn)
        elif self.holds_line():
            conn = self._line
            self._stand_on(conn)
        rc = pika.BlockingConnection(
            pika.URLParameters(rabbit_url or RABBIT_URL))
        tally = {"served": 0, "absorbed": 0}
        try:
            ch = rc.channel()
            ch.exchange_declare(COMMAND_EXCHANGE, exchange_type="topic",
                                durable=True)
            # two doors: the shared any-resident queue (an untargeted ask)
            # and MY OWN queue (a fan-out names its residents — the same
            # request reaches each selected one, never a lottery)
            shared, mine = serve_queue(), serve_queue(self.name)
            ch.queue_declare(shared, durable=True)
            ch.queue_bind(shared, COMMAND_EXCHANGE, serve_key())
            ch.queue_declare(mine, durable=True)
            ch.queue_bind(mine, COMMAND_EXCHANGE, serve_key(self.name))
            queues = [shared, mine]
            deadline = time.monotonic() + idle_s
            while time.monotonic() < deadline and \
                    tally["served"] + tally["absorbed"] < max_commands:
                method = body = None
                for q in queues:
                    method, _props, body = ch.basic_get(q)
                    if method is not None:
                        break
                if method is None:
                    time.sleep(0.05)
                    continue
                deadline = time.monotonic() + idle_s
                if conn is None:                            # the cure: a command landed — the line is held now
                    conn = self.hold_line()
                    self._stand_on(conn)
                self._line_last = time.monotonic()
                env = ev.decode(body)
                ask_id = str((env.get("payload") or {}).get("ref") or "")
                chain = env.get("authority_chain") or []
                if env.get("type") == CONFIRM_CMD:
                    pl = env.get("payload") or {}
                    approved = bool(pl.get("approved", False))   # absence = cancel, always
                    effect = (lambda cur, a=ask_id, ap=approved, c=chain, p=pl:
                              self._confirm_ask(cur, a, ap, c, proof=p.get("proof"),
                                                by=p.get("by"), reason=p.get("reason")))
                elif env.get("type") == HARNESS_CMD:          # P7 sp6: the kernel's run, through MY graph
                    from . import harness as _hz
                    effect = (lambda cur, e=env: _hz.run_command(conn, self, e))
                elif env.get("type") == KEYCHECK_CMD:         # Phase 8 sp6: THE KEY-CHECK — I sign the kernel's nonce; the verdict is the kernel's
                    from . import chips as _ch
                    effect = (lambda cur, e=env: _ch.answer(conn, self, e))
                else:
                    effect = (lambda cur, a=ask_id, c=chain:
                              self._serve_ask(cur, a, c))
                outcome = inbox.apply_once(
                    conn, f"resident:{self.name}", env["message_id"], effect)
                tally["served" if outcome == "applied" else "absorbed"] += 1
                ch.basic_ack(method.delivery_tag)   # only AFTER the commit
        finally:
            rc.close()
        return tally
