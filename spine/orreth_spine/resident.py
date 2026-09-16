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


class PolicyRefused(RuntimeError):
    """No policy loaded, no join — ever."""


class _State(TypedDict):
    text: str
    reply: str
    steps: list


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
            " reply text, served_by text,"
            " asked_at timestamptz NOT NULL DEFAULT now(),"
            " replied_at timestamptz)")


class Resident:
    def __init__(self, template_path: str | os.PathLike,
                 *, home: str | os.PathLike | None = None):
        raw = Path(template_path).read_bytes()
        self.template = json.loads(raw)
        if self.template.get("format") != "orreth-resident-template/1":
            raise ValueError("not a resident template: "
                             f"{self.template.get('format')!r}")
        self.template_hash = ev.content_hash(self.template)
        self.name = self.template["name"]
        self.identity = Identity.load(self.name, home)
        self.policy: dict | None = None
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

        def think(s: _State) -> dict:
            reply = (f"I am {self.name} — {self.template['persona']}. "
                     f"You asked: \"{s['text']}\" — and that is every word "
                     f"of it, back to you, none summarized away.")
            return {"reply": reply,
                    "steps": s["steps"] + ["thought it through"]}

        g = StateGraph(_State)
        g.add_node("hear", hear)
        g.add_node("think", think)
        g.add_edge(START, "hear")
        g.add_edge("hear", "think")
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
        out = self._graph.invoke({"text": text, "reply": "", "steps": []})
        seq = 1                                   # ask.received wore seq 1
        full_chain = list(chain) if chain else [person]
        if self.identity.did not in full_chain:
            full_chain.append(self.identity.did)
        for step in out["steps"]:
            seq += 1
            j = ev.make_envelope(
                kind="event", type=JOURNEY, universe_id="u:dev",
                scope_path="u:dev",
                payload={"ref": ask_id, "hash": "sha256:-",
                         "note": f"{self.name}: {step}"},
                correlation_id=ask_id, authority_chain=full_chain,
                aggregate={"type": "ask", "id": ask_id, "sequence": seq})
            outbox.add_row(cur, ev.encode(j), j["message_id"])
        cur.execute(
            "UPDATE spine_asks SET status = 'replied', reply = %s,"
            " served_by = %s, replied_at = now() WHERE ask_id = %s",
            (out["reply"], self.identity.did, ask_id))
        seq += 1
        r = ev.make_envelope(
            kind="event", type=REPLY, universe_id="u:dev", scope_path="u:dev",
            payload={"ref": ask_id, "hash": ev.content_hash(out["reply"])},
            correlation_id=ask_id, authority_chain=full_chain,
            aggregate={"type": "ask", "id": ask_id, "sequence": seq})
        outbox.add_row(cur, ev.encode(r), r["message_id"])

    def serve_once(self, conn, *, rabbit_url: str | None = None,
                   idle_s: float = 5.0, max_commands: int = 50) -> dict:
        """Consume the invocation rail: effect + events in one
        transaction through the durable inbox, ACK only after commit."""
        ensure_schema(conn)
        inbox.ensure_schema(conn)
        outbox.ensure_schema(conn)
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
                outcome = inbox.apply_once(
                    conn, f"resident:{self.name}", env["message_id"],
                    lambda cur: self._serve_ask(cur, ask_id, chain))
                tally["served" if outcome == "applied" else "absorbed"] += 1
                ch.basic_ack(method.delivery_tag)   # only AFTER the commit
        finally:
            rc.close()
        return tally
