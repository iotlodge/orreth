# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
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
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import TypedDict

import pika
from langgraph.graph import END, START, StateGraph

from . import envelope as ev
from . import inbox, outbox
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


class PolicyRefused(RuntimeError):
    """No policy loaded, no join — ever."""


class _State(TypedDict):
    text: str
    reply: str
    steps: list
    notes: list
    hold: dict | None
    read: list          # the DIDs whose results this mind read (the chain)


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
                 binding: str | os.PathLike | None = None):
        raw = Path(template_path).read_bytes()
        self.template = json.loads(raw)
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
        # a workspace binding (0004): ONE workspace-firmware body, a binding
        # per pull — the binding names the seat and adds its prompt/skills
        self.binding = None
        if binding is not None:
            self.binding = json.loads(Path(binding).read_text())
            self.name = self.binding["name"]
            self.function = f"workspace:{self.binding['pull']}"
            self.charge = f"{self.charge} {self.binding.get('prompt', '')}".strip()
            self.template["capabilities"] = list(dict.fromkeys(
                self.template.get("capabilities", [])
                + self.binding.get("capabilities", [])))   # the seat's tools
        self.identity = Identity.load(self.name, home)
        self.policy: dict | None = None
        # the mind: a template that declares one thinks through the
        # gateway (metered, always); without a gateway the body falls
        # back to its deterministic graph — there is no unmetered door
        self.gateway = gateway if self.template.get("mind") else None
        self._serve_conn = None
        self._current_ask = None
        self._current_marker = None  # the ask's marker: WHY this serve (0006)
        self._state = "in"
        self._ckpt_graph = None      # the checkpointed graph, one per life
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
                       "rules": len(pol.get("rules", []))}
        return self.policy

    def join(self, conn) -> dict:
        """The dev gate v0 (the governed becky gate arrives with kernel
        integration): the join is recorded wearing the policy version —
        an agent without the covenant loaded never joins."""
        if self.policy is None:
            raise PolicyRefused(
                "this body wears no covenant policy — load it, or it never "
                "joins (canon 0004: governance is worn, not remembered)")
        ensure_schema(conn)
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
                " interests) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (self.identity.did, self.name, life, self.template_hash,
                 self.policy["version"], self.policy["hash"], sig,
                 ev.scope(), self.kind,        # joined THIS world, as my kind,
                 json.dumps(self.template.get("capabilities", [])),   # declared
                 json.dumps(self.template.get("interests", []))))     # + interests
        from . import scheduler                  # the role schedules the
        for sch in self.template.get("schedules", []):   # template declares are
            scheduler.declared(conn, self.name, "role", sch["text"],   # registered
                               int(sch["every_s"]), self.identity.did)   # at every join
        return {"did": self.identity.did, "life": life,
                "policy_version": self.policy["version"]}

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
                        notes.append(         # never material for my grade
                            f"earlier in this session, asked: {t!r} — "
                            f"{'I' if mine else who} replied: {rp!r}")
                        if not mine and by and by not in read:
                            read.append(by)   # the chain will name them
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
                elif (self.function or "").startswith("workspace:"):
                    # a workspace agent reads ITS workspace's facts (the
                    # binding names which); the crew: every body here
                    cur.execute(
                        "SELECT DISTINCT ON (name) name, kind, life, policy_version,"
                        " capabilities, did FROM spine_joins WHERE scope = %s"
                        " ORDER BY name, join_id DESC", (ev.scope(),))
                    for n, k, life, pv, caps, did in cur.fetchall():
                        notes.append(f"crew card — {n}: {k}, life {life}, wearing "
                                     f"covenant policy v{pv}, capabilities "
                                     f"{', '.join(json.loads(caps or '[]')) or 'none declared'}, "
                                     f"self {did[-8:]}")
                st = OrrethStore(conn, by_did=self.identity.did, state=state)
                if window and window.get("from") and window.get("to"):
                    # MEM-1 by timeframe (P6): the window the human typed is
                    # a lens over ALL their worldlines in this world — every
                    # ask they made and every word I acquired between X and Y
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
                    for t, rp, at, who in cur.fetchall():
                        notes.append(f"in the window, at {at.strftime('%a %b %d %H:%M')}, "
                                     f"asked: {t!r} — {who} replied: {rp!r}")
                    for m in st.within(self.name, window["from"], window["to"]):
                        notes.append(f"in the window I acquired [{m['key']}] at "
                                     f"{m['landed_at'][:16]}: {m['body']}")
                if window and window.get("to"):
                    # MEM-4 in the chat: inside a window the memories read
                    # as they stood at the window's END — what we knew then
                    for m in st.search(self.name, s["text"][:60], limit=3,
                                       at=window["to"]):
                        notes.append(f"as of {window['to'][:16]} I remembered "
                                     f"[{m['key']}]: {m['body']}")
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
                             + ", ".join(names.get(d, d[-8:]) for d in read))
            return {"notes": notes, "steps": steps, "read": read}

        def think(s: _State) -> dict:
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
                if self.kind == "firmware":
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
                        "use your tools when the ask needs the real world.")
                if "tools:mark" in self.template.get("capabilities", []):
                    system += (" If you observe an IMPROVEMENT to what you "
                               "are executing, mark it: call the mark tool "
                               "with kind 'improvement' and a short note — "
                               "other bodies act on marks.")   # 0006's policy line
                prompt = ""
                if s["notes"]:
                    prompt += ("Your recalled notes:\n- "
                               + "\n- ".join(s["notes"]) + "\n\n")
                prompt += f"The ask: {s['text']}"
                door = ToolDoor(self._serve_conn, did=self.identity.did,
                                capabilities=self.template.get(
                                    "capabilities", []), name=self.name,
                                marker=(self._current_marker or {}).get("id"))
                deltas = None
                if self.on_delta is not None and self._current_ask:
                    aid = self._current_ask
                    deltas = lambda t, a=aid: self.on_delta(a, t)  # noqa: E731
                try:
                    if hasattr(self.gateway, "think_acting") and \
                            door.schemas():
                        reply, acts = self.gateway.think_acting(
                            self._serve_conn, did=self.identity.did,
                            system=system, prompt=prompt, door=door,
                            model=mind.get("model"), on_delta=deltas)
                        return {"reply": reply,
                                "steps": s["steps"] + acts
                                + ["thought it through the metered gateway"]}
                    reply = self.gateway.think(
                        self._serve_conn, did=self.identity.did,
                        system=system, prompt=prompt,
                        model=mind.get("model"), on_delta=deltas)
                except ConsequentialHold as h:
                    return {"hold": {"tool": h.tool, "args": h.tool_args},
                            "steps": s["steps"]
                            + [f"the {h.tool} act is consequential — "
                               "held at the interlock for the human"]}
                return {"reply": reply,
                        "steps": s["steps"] + ["thought it through the "
                                               "metered gateway"]}
            reply = (f"I am {self.name} — {self.template['persona']}. "
                     f"You asked: \"{s['text']}\" — and that is every word "
                     f"of it, back to you, none summarized away.")
            return {"reply": reply,
                    "steps": s["steps"] + ["thought it through"]}

        g = StateGraph(_State)
        g.add_node("hear", hear)
        g.add_node("recall", recall)
        g.add_node("think", think)
        g.add_edge(START, "hear")
        g.add_edge("hear", "recall")
        g.add_edge("recall", "think")
        g.add_edge("think", END)
        return g.compile(checkpointer=checkpointer)

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
        own = psycopg.connect(conn.info.dsn, password=conn.info.password,
                              autocommit=True)
        saver = PostgresSaver(own)
        own.execute("SELECT pg_advisory_lock(742199)")      # the DDL guard, session-
        try:                                                # scoped: the saver's
            saver.setup()                                   # migrations commit on
        finally:                                            # their own
            own.execute("SELECT pg_advisory_unlock(742199)")
        self._ckpt_graph = self._build_graph(saver)

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
                kind="event", type=JOURNEY, universe_id=ev.scope(),
                scope_path=ev.scope(),
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: refused a stale command — "
                                 f"this ask is not on my ground"},
                correlation_id=ask_id, authority_chain=chain or None)
            outbox.add_row(cur, ev.encode(j), j["message_id"])
            return
        text, person, _status = row
        self._current_ask = ask_id
        from . import markers as _mk
        cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ask_id,))
        _mrow = cur.fetchone()
        self._current_marker = _mk.as_env(self._serve_conn, _mrow[0]) if _mrow and _mrow[0] else None
        initial = {"text": text, "reply": "", "steps": [], "notes": [],
                   "hold": None, "read": []}
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
        full_chain = list(chain) if chain else [person]
        for by in out.get("read") or []:    # AG-8: H → the residents whose
            if by not in full_chain:        # results I read → me
                full_chain.append(by)
        if self.identity.did not in full_chain:
            full_chain.append(self.identity.did)
        self._journey(cur, ask_id, out["steps"], full_chain)
        if out.get("hold"):
            held = out["hold"]
            question = (
                f"Are you sure? The {held['tool']} act is consequential "
                "and cannot be undone. Confirming takes a deliberate yes — "
                "cancel is the default, and doing nothing cancels.")
            cur.execute(
                "UPDATE spine_asks SET status = 'awaiting-confirm',"
                " reply = %s, served_by = %s, held = %s WHERE ask_id = %s",
                (question, self.identity.did, json.dumps(held), ask_id))
            n = ev.make_envelope(
                kind="event", type=CONFIRM_NEEDED, universe_id=ev.scope(),
                scope_path=ev.scope(),
                payload={"ref": ask_id, "hash": "sha256:-",
                         "tool": held["tool"]},
                correlation_id=ask_id, authority_chain=full_chain,
                aggregate={"type": "ask", "id": ask_id,
                           "sequence": _next_seq(cur, ask_id)})
            outbox.add_row(cur, ev.encode(n), n["message_id"])
            return
        self._land_reply(cur, ask_id, out["reply"], full_chain)

    def _journey(self, cur, ask_id: str, steps: list, chain: list) -> None:
        for step in steps:
            j = ev.make_envelope(
                kind="event", type=JOURNEY, universe_id=ev.scope(),
                scope_path=ev.scope(),
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: {step}"},
                correlation_id=ask_id, authority_chain=chain,
                aggregate={"type": "ask", "id": ask_id,
                           "sequence": _next_seq(cur, ask_id)},
                marker=self._current_marker)       # every hop says WHY
            outbox.add_row(cur, ev.encode(j), j["message_id"])

    def _land_reply(self, cur, ask_id: str, reply: str, chain: list,
                    status: str = "replied") -> None:
        cur.execute(
            "UPDATE spine_asks SET status = %s, reply = %s,"
            " served_by = %s, replied_at = now() WHERE ask_id = %s",
            (status, reply, self.identity.did, ask_id))
        r = ev.make_envelope(
            kind="event", type=REPLY, universe_id=ev.scope(), scope_path=ev.scope(),
            payload={"ref": ask_id, "hash": ev.content_hash(reply)},
            correlation_id=ask_id, authority_chain=chain, marker=self._current_marker,
            aggregate={"type": "ask", "id": ask_id,
                       "sequence": _next_seq(cur, ask_id)})
        outbox.add_row(cur, ev.encode(r), r["message_id"])

    def _confirm_ask(self, cur, ask_id: str, approved: bool,
                     chain: list[str]) -> None:
        """The human's word arrives (canon 0001 L2): a deliberate yes
        releases the held act through the door; anything else cancels —
        cancel is the default, and a cancelled act NEVER ran."""
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
        if approved:
            door = ToolDoor(self._serve_conn, did=self.identity.did,
                            capabilities=self.template.get(
                                "capabilities", []), name=self.name,
                            marker=(self._current_marker or {}).get("id"))
            result = door.call(held["tool"], held["args"], confirmed=True)
            self._journey(cur, ask_id,
                          [f"the human said yes — the {held['tool']} act "
                           "ran through the door"], full_chain)
            self._land_reply(cur, ask_id, f"Done, on your word: {result}",
                             full_chain)
        else:
            self._journey(cur, ask_id,
                          [f"the human cancelled — the {held['tool']} act "
                           "never ran (cancel is always the default)"],
                          full_chain)
            self._land_reply(
                cur, ask_id,
                "Cancelled — nothing was done. Cancel is always the "
                "default here.", full_chain, status="cancelled")

    def serve_once(self, conn, *, rabbit_url: str | None = None,
                   idle_s: float = 5.0, max_commands: int = 50) -> dict:
        """Consume the invocation rail: effect + events in one
        transaction through the durable inbox, ACK only after commit."""
        ensure_schema(conn)
        inbox.ensure_schema(conn)
        outbox.ensure_schema(conn)
        from . import gateway as _gw, tools as _tl
        from . import store as _st
        _gw.ensure_schema(conn)     # pre-flagged: the serving transaction
        _tl.ensure_schema(conn)     # never runs DDL, never takes the lock
        _st.ensure_schema(conn)
        self._serve_conn = conn        # the graph's doors ride this life
        try:
            self.prepare(conn)         # MEM-2: working memory on the ground
        except Exception:
            self._ckpt_graph = None    # a ground without it still serves
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
                env = ev.decode(body)
                ask_id = str((env.get("payload") or {}).get("ref") or "")
                chain = env.get("authority_chain") or []
                if env.get("type") == CONFIRM_CMD:
                    approved = bool((env.get("payload") or {}).get(
                        "approved", False))       # absence = cancel, always
                    effect = (lambda cur, a=ask_id, ap=approved, c=chain:
                              self._confirm_ask(cur, a, ap, c))
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
