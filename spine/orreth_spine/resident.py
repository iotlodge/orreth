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


def ensure_schema(conn) -> None:
    with conn.transaction():
        cur = conn.cursor()
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


def _next_seq(cur, ask_id: str) -> int:
    """The ask's own event counter — monotone per aggregate, durable on
    the row, so a conversation that pauses at an interlock continues its
    sequence honestly."""
    cur.execute("UPDATE spine_asks SET seq = seq + 1 WHERE ask_id = %s"
                " RETURNING seq", (ask_id,))
    return cur.fetchone()[0]


class Resident:
    def __init__(self, template_path: str | os.PathLike,
                 *, home: str | os.PathLike | None = None, gateway=None):
        raw = Path(template_path).read_bytes()
        self.template = json.loads(raw)
        if self.template.get("format") != "orreth-resident-template/1":
            raise ValueError("not a resident template: "
                             f"{self.template.get('format')!r}")
        self.template_hash = ev.content_hash(self.template)
        self.name = self.template["name"]
        self.identity = Identity.load(self.name, home)
        self.policy: dict | None = None
        # the mind: a template that declares one thinks through the
        # gateway (metered, always); without a gateway the body falls
        # back to its deterministic graph — there is no unmetered door
        self.gateway = gateway if self.template.get("mind") else None
        self._serve_conn = None
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
                " policy_version, policy_hash, sig)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (self.identity.did, self.name, life, self.template_hash,
                 self.policy["version"], self.policy["hash"], sig))
        return {"did": self.identity.did, "life": life,
                "policy_version": self.policy["version"]}

    # ---- the mind (small, real) ----------------------------------------------

    def _build_graph(self):
        def hear(s: _State) -> dict:
            return {"steps": s["steps"] + ["heard the ask, every word"]}

        def recall(s: _State) -> dict:
            """Pack the mind (canon 0003): my own worldline (recent
            replies) and my memories that match the ask — packed as
            notes the think node reads. Without a serving connection
            (pure-graph tests) the recall is honestly empty."""
            notes: list[str] = []
            conn = self._serve_conn
            if conn is not None:
                from .store import OrrethStore
                cur = conn.cursor()
                cur.execute(
                    "SELECT text, reply FROM spine_asks"
                    " WHERE served_by = %s AND status = 'replied'"
                    " ORDER BY replied_at DESC LIMIT 3",
                    (self.identity.did,))
                for t, rp in cur.fetchall():
                    notes.append(f"earlier, asked: {t!r} — I replied: {rp!r}")
                st = OrrethStore(conn, by_did=self.identity.did)
                for m in st.search(self.name, s["text"][:60], limit=3):
                    notes.append(f"I remember [{m['key']}]: {m['body']}")
            step = (f"recalled {len(notes)} notes" if notes
                    else "recalled nothing yet — a young memory")
            return {"notes": notes, "steps": s["steps"] + [step]}

        def think(s: _State) -> dict:
            if self.gateway is not None and self._serve_conn is not None:
                from .tools import ConsequentialHold, ToolDoor
                mind = self.template.get("mind") or {}
                system = (
                    f"You are {self.name}, a resident of Orreth — "
                    f"{self.template['persona']}. Laws you live by: answer "
                    "in plain, friendly words anyone can understand; answer "
                    "COMPLETELY — the full reply, never a teaser; when your "
                    "recalled notes bear on the ask, use them and say so "
                    "plainly; never invent a memory you were not handed; "
                    "use your tools when the ask needs the real world.")
                prompt = ""
                if s["notes"]:
                    prompt += ("Your recalled notes:\n- "
                               + "\n- ".join(s["notes"]) + "\n\n")
                prompt += f"The ask: {s['text']}"
                door = ToolDoor(self._serve_conn, did=self.identity.did,
                                capabilities=self.template.get(
                                    "capabilities", []))
                try:
                    if hasattr(self.gateway, "think_acting") and \
                            door.schemas():
                        reply, acts = self.gateway.think_acting(
                            self._serve_conn, did=self.identity.did,
                            system=system, prompt=prompt, door=door,
                            model=mind.get("model"))
                        return {"reply": reply,
                                "steps": s["steps"] + acts
                                + ["thought it through the metered gateway"]}
                    reply = self.gateway.think(
                        self._serve_conn, did=self.identity.did,
                        system=system, prompt=prompt,
                        model=mind.get("model"))
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
        return g.compile()

    # ---- service --------------------------------------------------------------

    def _serve_ask(self, cur, ask_id: str, chain: list[str]) -> None:
        """The one-transaction heart: read the ask, run the graph, land
        journey + reply rows AND their events together."""
        cur.execute("SELECT text, person FROM spine_asks"
                    " WHERE ask_id = %s FOR UPDATE", (ask_id,))
        row = cur.fetchone()
        if row is None:
            # a stale command (the ask is not on THIS ground) is TERMINAL,
            # never a retry loop (0002's failure table): the refusal lands
            # as a visible journey event and the footprint stands
            j = ev.make_envelope(
                kind="event", type=JOURNEY, universe_id="u:dev",
                scope_path="u:dev",
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: refused a stale command — "
                                 f"this ask is not on my ground"},
                correlation_id=ask_id, authority_chain=chain or None)
            outbox.add_row(cur, ev.encode(j), j["message_id"])
            return
        text, person = row
        out = self._graph.invoke({"text": text, "reply": "", "steps": [],
                                  "notes": [], "hold": None})
        full_chain = list(chain) if chain else [person]
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
                kind="event", type=CONFIRM_NEEDED, universe_id="u:dev",
                scope_path="u:dev",
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
                kind="event", type=JOURNEY, universe_id="u:dev",
                scope_path="u:dev",
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: {step}"},
                correlation_id=ask_id, authority_chain=chain,
                aggregate={"type": "ask", "id": ask_id,
                           "sequence": _next_seq(cur, ask_id)})
            outbox.add_row(cur, ev.encode(j), j["message_id"])

    def _land_reply(self, cur, ask_id: str, reply: str, chain: list,
                    status: str = "replied") -> None:
        cur.execute(
            "UPDATE spine_asks SET status = %s, reply = %s,"
            " served_by = %s, replied_at = now() WHERE ask_id = %s",
            (status, reply, self.identity.did, ask_id))
        r = ev.make_envelope(
            kind="event", type=REPLY, universe_id="u:dev", scope_path="u:dev",
            payload={"ref": ask_id, "hash": ev.content_hash(reply)},
            correlation_id=ask_id, authority_chain=chain,
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
                                "capabilities", []))
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
        self._serve_conn = conn        # the graph's doors ride this life
        rc = pika.BlockingConnection(
            pika.URLParameters(rabbit_url or RABBIT_URL))
        tally = {"served": 0, "absorbed": 0}
        try:
            ch = rc.channel()
            ch.exchange_declare(COMMAND_EXCHANGE, exchange_type="topic",
                                durable=True)
            ch.queue_declare(SERVE_QUEUE, durable=True)
            ch.queue_bind(SERVE_QUEUE, COMMAND_EXCHANGE, SERVE_KEY)
            deadline = time.monotonic() + idle_s
            while time.monotonic() < deadline and \
                    tally["served"] + tally["absorbed"] < max_commands:
                method, _props, body = ch.basic_get(SERVE_QUEUE)
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
