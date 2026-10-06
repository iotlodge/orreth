# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp2, THE SHELF WIDENED: the craft kinds · the wear table · the draft shelf · the hull's edges · 2026-10-05
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 sp3 THE WORKSHOP v0: the graph declaration BRANCHES (an edge wears `when`: the hull's edge · the ask's words · the last reply), per-node refs typed, the default line and the run-time pick · 2026-10-06
"""THE SHELF WIDENED (canon 0010 lock 3 · lock 6 · 0004 AG-9 · 0005 Phase 8 sp2).

JB's laws: *every Agent is a sum of its versioned components; an Agent cannot
exist outside versioned components; a versioned component knows whether it is
in use and by how many agents.*

THE CRAFT KINDS. The one services shelf (`services.py` — one ladder, one pin,
one version history, one door family) gains the kinds a body is MADE of:
`template · prompt · skill · policy · graph · binding · golden`. A craft is
addressed by its NAME and its HASH and mints NO DID of its own (Orreth Law 1: a
human approves every new DID — a component is not a self). On the shelf a craft
wears the name `<name>.<kind>` (`librarian.template` · `crew.binding` ·
`mind.v0.graph`), so a name wears one kind as the ladder demands, and its
`did` column carries the plain ADDRESS `craft:<name>.<kind>` — never a DID.
`source` (already a kind) gains its second form: a repo'd origin —
`{repo, commit, entry}` — beside the locator form.

THE WEAR TABLE (`spine_wear`). Which body wears which component at which
version: written in the body's join transaction (one row per component it is
made of — its template, its binding, its policy, its graph, its golden set),
the previous life's rows closed; closed at decom (a later spoonful). It IS
"in use by N", the blast radius, the decom refusal, and the repo-to-running
correlation for forensics.

THE DRAFT SHELF (`spine_drafts`). A draft lives in the ground UNDER THE PERSON
— beside the profile, never on the shelf, never in any inventory or recall
(AG-9); only its author's seat reads it; it survives a closed browser; no other
person's session can pull it. Saving a draft is ROUTINE (L1) — no fact, no
marker: an unversioned draft is private state. THE CUT is the gate: a held act
of the kernel's (`craft.cut`), its demand by the craft's class — firmware is
cut only in a dev universe (prod by release); a resident's template at L3; an
agent's template only through the Experiment (spoonful 4); every other craft
at L2 — and on the human's deliberate yes the draft lands on the shelf as a
registered craft or the next version of one (the ladder's own facts, the
person on the chain), the draft spent.

THE HULL (lock 6). The body's fixed graph becomes hear → recall → ROUTE → one
of three edges — CHAT (a human's ask) · WORK (an objective under an intention,
a duty's occurrence) · EVENT (a marker dispatched by interest) — into the WORK
NODE, which runs the template's `graph` component from the shelf, finally
read (`mind.v0` = today's think; `echo.v0` = the echo). The edge is read off
the ask's marker: a thought is chat; a root is chat; a parent of a structural
kind is work; any other parent kind is an event. The kernel's laws (the seat
words, the covenant slice, the metered gateway, the checkpoint per hop, the
stop at a safe boundary) live in the hull, never in the agent's graph.

THE GRAPH DECLARATION v0 (0004's open "template schema v0", answered here):
declaration first, canvas as the view — `{format: orreth-graph/1, name,
entry, nodes: [{id, kind: think | echo, prompt?, skill?, tools?, mind?}],
edges: [{from, to, when?}]}`. Spoonful 3 (THE WORKSHOP v0) lets it BRANCH:
an edge may wear `when` — exactly one of `{"edge": chat | work | event}` (the
hull's edge this ask took), `{"ask": "<pattern>"}` (the ask's words) or
`{"reply": "<pattern>"}` (the last node's reply) — and a node may have several
ways out when at most ONE of them wears no `when` (the default, "otherwise").
The run picks the first `when` that holds, in declaration order, else the
default, else the line ends there. The graph runs FORWARD only (a loop
refuses). A node's refs are executed by the hull: `prompt` and `skill` join
the system words, `tools` narrows the door to those the template declares,
`mind` pins the stall. `path(g)` is the DEFAULT LINE (the edges without a
`when`, from the entry); `branches(g)` names the nodes that branch. The pure
laws here are the fixture's (`crafts-v0.json`).
"""
from __future__ import annotations

import json
import re
import secrets
from pathlib import Path

from . import envelope as ev

SPINE = Path(__file__).resolve().parents[1]

CRAFT_KINDS = ("template", "prompt", "skill", "policy", "graph", "binding", "golden")
FORMATS = {
    "template": "orreth-resident-template/1",
    "binding": "orreth-workspace-binding/1",
    "policy": "orreth-covenant-policy/1",
    "graph": "orreth-graph/1",
    "golden": "orreth-golden/1",
    "prompt": "orreth-prompt/1",
    "skill": "orreth-skill/1",
}
NODE_KINDS = ("think", "echo")                       # v0: the metered mind · the words back
WHEN_KEYS = ("edge", "ask", "reply")                 # sp3: what a way out may be conditioned on
EDGES = ("chat", "work", "event")                    # the hull's three edges = the three modes of agent interoperability
STRUCTURAL = ("objective", "intention", "thought", "action", "observation")   # markers.SEED's structural group
TEMPLATE_KINDS = ("resident", "firmware", "agent")   # the three selves (0010 lock 4)
ADDRESS = "craft:"                                   # what a craft's `did` column carries — an address, never a DID
CUT_TOOL = "craft.cut"                               # the kernel's own held act
CUT_CLASS = "consequential"
KERNEL = "the kernel"
NAME_RX = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_HEX = re.compile(r"^[0-9a-f]{7,64}$")

FOLDERS = {"template": "templates", "binding": "bindings", "policy": "policy", "graph": "graphs",
           "golden": "golden", "prompt": "prompts", "skill": "skills"}


class CraftRefused(ValueError):
    """The shelf's refusal for a craft — the reason in plain words."""


# ---- the pure laws (fixture crafts-v0) -------------------------------------------------------------

def craft_name(name: str, kind: str) -> str:
    """The shelf name a craft wears: `<name>.<kind>` — one name, one kind, the ladder's law kept
    (`librarian.template` · `librarian.golden` · `mind.v0.graph`)."""
    if kind not in CRAFT_KINDS:
        raise CraftRefused(f"a craft kind is one of {', '.join(CRAFT_KINDS)} — not {kind!r}")
    n = str(name or "").strip()
    if not NAME_RX.match(n) or n.endswith("." + kind):
        raise CraftRefused("a craft name is a short lowercase name: letters, digits, dashes, dots, underscores")
    return f"{n}.{kind}"


def split_name(shelf_name: str) -> tuple[str, str] | None:
    """`librarian.template` → ("librarian", "template"); None for a service that is no craft."""
    s = str(shelf_name or "")
    for k in CRAFT_KINDS:
        if s.endswith("." + k) and len(s) > len(k) + 1:
            return s[: -len(k) - 1], k
    return None


def address(name: str, kind: str) -> str:
    """What a craft's `did` column carries: `craft:<name>.<kind>` — a plain address; a craft is
    not a self and mints no DID."""
    return ADDRESS + craft_name(name, kind)


def is_craft(kind: str) -> bool:
    return kind in CRAFT_KINDS


def plain(name: str, kind: str) -> str:
    """A service in the human's words (rule 13): `greeting prompt` for a craft (the shelf name
    already wears its kind), `weather tool` for an identity — W100 (walk SPEC-SHELF-01)."""
    sp = split_name(name)
    if sp and sp[1] == kind:
        return f"{sp[0]} {kind}"
    return f"{name} {kind}"


def validate(kind: str, manifest) -> dict:
    """The declaration reads whole, or the reason why not — `{ok, reason}`; one law per kind."""
    if kind not in CRAFT_KINDS:
        return {"ok": False, "reason": f"a craft kind is one of {', '.join(CRAFT_KINDS)} — not {kind!r}"}
    if not isinstance(manifest, dict) or not manifest:
        return {"ok": False, "reason": f"a {kind} is a non-empty object — its declaration"}
    want = FORMATS[kind]
    if manifest.get("format") != want:
        return {"ok": False, "reason": f"a {kind} declares format {want!r} — got {manifest.get('format')!r}"}
    if kind == "template":
        if not str(manifest.get("name") or "").strip():
            return {"ok": False, "reason": "a template names its body (`name`)"}
        if not str(manifest.get("graph") or "").strip():
            return {"ok": False, "reason": "a template names its graph component (`graph`) — the hull's work node"}
        tk = manifest.get("kind", "resident")
        if tk not in TEMPLATE_KINDS:
            return {"ok": False, "reason": f"a template's kind is one of {', '.join(TEMPLATE_KINDS)} — got {tk!r}"}
        return {"ok": True, "reason": None}
    if kind == "binding":
        for k in ("pull", "name"):
            if not str(manifest.get(k) or "").strip():
                return {"ok": False, "reason": f"a binding names its {k}"}
        return {"ok": True, "reason": None}
    if kind == "policy":
        rules = manifest.get("rules")
        if not str(manifest.get("version") or "").strip():
            return {"ok": False, "reason": "a policy wears a version"}
        if not isinstance(rules, list) or not rules or not all(isinstance(r, str) and r.strip() for r in rules):
            return {"ok": False, "reason": "a policy is its rules — a non-empty list of plain sentences"}
        return {"ok": True, "reason": None}
    if kind == "golden":
        if not str(manifest.get("template") or "").strip():
            return {"ok": False, "reason": "a golden set names the template it proves (`template`)"}
        cases = manifest.get("cases")
        if not isinstance(cases, list) or not cases:
            return {"ok": False, "reason": "a golden set is its cases — a non-empty list of {ask, expect}"}
        for i, c in enumerate(cases):
            if not isinstance(c, dict) or not str(c.get("ask") or "").strip():
                return {"ok": False, "reason": f"case {i + 1} asks something (`ask`)"}
            exp = c.get("expect")
            if not isinstance(exp, list) or not exp or not all(isinstance(x, str) and x for x in exp):
                return {"ok": False, "reason": f"case {i + 1} expects words (`expect`, a non-empty list)"}
        return {"ok": True, "reason": None}
    if kind == "prompt":
        if not str(manifest.get("text") or "").strip():
            return {"ok": False, "reason": "a prompt is its text (`text`)"}
        return {"ok": True, "reason": None}
    if kind == "skill":
        for k in ("name", "words"):
            if not str(manifest.get(k) or "").strip():
                return {"ok": False, "reason": f"a skill has a {k}" + (" — what it is, in one line" if k == "words" else "")}
        if not str(manifest.get("text") or "").strip():
            return {"ok": False, "reason": "a skill is its text (`text`) — the words a body follows"}
        return {"ok": True, "reason": None}
    return validate_graph(manifest)                  # graph


def validate_graph(g) -> dict:
    """The graph declaration v0, branching since sp3: an entry; nodes with unique ids, a known
    kind and typed refs (`prompt` · `skill` · `mind` a name; `tools` a list of names); edges that
    name nodes, each wearing at most one `when` (edge · ask · reply); at most ONE way out of a
    node without a `when` (the default); forward only — a loop refuses."""
    if not isinstance(g, dict) or g.get("format") != FORMATS["graph"]:
        return {"ok": False, "reason": f"a graph declares format {FORMATS['graph']!r}"}
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return {"ok": False, "reason": "a graph has nodes — a non-empty list of {id, kind}"}
    ids = []
    for i, n in enumerate(nodes):
        if not isinstance(n, dict) or not str(n.get("id") or "").strip():
            return {"ok": False, "reason": f"node {i + 1} has an id"}
        if n["id"] in ids:
            return {"ok": False, "reason": f"node ids are unique — {n['id']!r} appears twice"}
        if n.get("kind") not in NODE_KINDS:
            return {"ok": False, "reason": f"node {n['id']!r}: a node's kind is one of {', '.join(NODE_KINDS)} — got {n.get('kind')!r}"}
        for ref in ("prompt", "skill", "mind"):
            if ref in n and n[ref] is not None and (not isinstance(n[ref], str) or not n[ref].strip()):
                return {"ok": False, "reason": f"node {n['id']!r}: `{ref}` names a {ref if ref != 'mind' else 'stall'} by name"}
        if "tools" in n and n["tools"] is not None and (
                not isinstance(n["tools"], list) or not all(isinstance(t, str) and t.strip() for t in n["tools"])):
            return {"ok": False, "reason": f"node {n['id']!r}: `tools` is a list of tool names"}
        ids.append(n["id"])
    entry = g.get("entry")
    if entry not in ids:
        return {"ok": False, "reason": f"a graph names its entry node — {entry!r} is not a node"}
    edges = g.get("edges", [])
    if not isinstance(edges, list):
        return {"ok": False, "reason": "edges is a list of {from, to}"}
    defaults: set[str] = set()
    for e in edges:
        if not isinstance(e, dict) or e.get("from") not in ids or e.get("to") not in ids:
            fr, to = (e.get("from"), e.get("to")) if isinstance(e, dict) else (None, None)
            return {"ok": False, "reason": f"an edge names two nodes — {fr!r} → {to!r} does not"}
        w = e.get("when")
        if w is None:
            if e["from"] in defaults:
                return {"ok": False, "reason": f"node {e['from']!r} has two ways out and neither says when — one way out may be the default; every other wears a `when` (edge · ask · reply)"}
            defaults.add(e["from"])
            continue
        if not isinstance(w, dict) or len(w) != 1 or next(iter(w)) not in WHEN_KEYS:
            return {"ok": False, "reason": f"the way out of {e['from']!r} to {e['to']!r}: `when` is one of {{edge}}, {{ask}} or {{reply}}"}
        k, v = next(iter(w.items()))
        if k == "edge" and v not in EDGES:
            return {"ok": False, "reason": f"the way out of {e['from']!r} to {e['to']!r}: `when.edge` is one of {', '.join(EDGES)} — got {v!r}"}
        if k != "edge" and (not isinstance(v, str) or not v.strip()):
            return {"ok": False, "reason": f"the way out of {e['from']!r} to {e['to']!r}: `when.{k}` is a pattern — the words to look for"}
    loop = _loops_at(g, ids)
    if loop is not None:
        return {"ok": False, "reason": f"the graph loops at {loop!r} — v0 runs forward only"}
    return {"ok": True, "reason": None}


def _loops_at(g: dict, ids: list[str]) -> str | None:
    """The first node (in declaration order) that can reach itself along ANY edges — None when
    the graph runs forward only."""
    outs: dict[str, list[str]] = {i: [] for i in ids}
    for e in g.get("edges", []):
        if isinstance(e, dict) and e.get("from") in outs:
            outs[e["from"]].append(e.get("to"))
    for start in ids:
        seen, stack = set(), list(outs[start])
        while stack:
            cur = stack.pop()
            if cur == start:
                return start
            if cur in seen or cur not in outs:
                continue
            seen.add(cur)
            stack.extend(outs[cur])
    return None


def path(g: dict) -> list[str]:
    """THE DEFAULT LINE: the nodes a run visits from the entry along the edges that wear no
    `when` (the "otherwise" of every node), in order — what the canvas draws as the spine of the
    graph and the probe says; a loop refuses. A node whose every way out is conditioned ends
    the line."""
    outs = {e["from"]: e["to"] for e in g.get("edges", []) if isinstance(e, dict) and e.get("when") is None}
    seen, cur = [], g.get("entry")
    while cur is not None:
        if cur in seen:
            raise CraftRefused(f"the graph loops at {cur!r} — v0 runs forward only")
        seen.append(cur)
        cur = outs.get(cur)
    return seen


def branches(g: dict) -> list[str]:
    """The nodes with more than one way out, in declaration order."""
    counts: dict[str, int] = {}
    for e in g.get("edges", []):
        if isinstance(e, dict):
            counts[e.get("from")] = counts.get(e.get("from"), 0) + 1
    return [n["id"] for n in g.get("nodes", []) if counts.get(n.get("id"), 0) > 1]


def when_words(e: dict) -> str:
    """A way out, in words (rule 13): `when the ask took the chat edge` · `when the ask says
    /weather/` · `when the reply says /HOLD/` · `otherwise`."""
    w = e.get("when") if isinstance(e, dict) else None
    if not w:
        return "otherwise"
    k, v = next(iter(w.items()))
    if k == "edge":
        return f"when the ask took the {v} edge"
    return f"when the {'ask' if k == 'ask' else 'reply'} says /{v}/"


def next_node(g: dict, node_id: str, ctx: dict) -> tuple[str | None, str | None]:
    """THE RUN-TIME PICK (the hull's, Python only — the Rust kernel runs no graph): the first
    way out of `node_id` whose `when` holds, in declaration order — `edge` against the hull's
    edge, `ask` and `reply` as patterns searched (case-blind) in the ask's words and the last
    reply — else the default, else None (the line ends). Returns the next node and the journey's
    words; a pattern that does not compile is said and never matches."""
    ways = [e for e in g.get("edges", []) if isinstance(e, dict) and e.get("from") == node_id]
    if not ways:
        return None, None
    default = next((e for e in ways if e.get("when") is None), None)
    said = []
    for e in ways:
        w = e.get("when")
        if not w:
            continue
        k, v = next(iter(w.items()))
        if k == "edge":
            hit = (ctx.get("edge") or "chat") == v
        else:
            text = str(ctx.get("ask" if k == "ask" else "reply") or "")
            try:
                hit = re.search(str(v), text, re.I) is not None
            except re.error as x:
                said.append(f"the way out to {e['to']!r} has a pattern that does not read ({x}) — skipped")
                hit = False
        if hit:
            words = f"took the way out to {e['to']!r} — {when_words(e)}"
            return e["to"], " · ".join(said + [words]) if said else words
    if default is not None:
        words = (f"took the default way out to {default['to']!r} — no `when` held" if len(ways) > 1
                 else None)
        return default["to"], " · ".join(said + [words]) if (said and words) else (words or (" · ".join(said) or None))
    words = f"no way out of {node_id!r} held — the line ends here"
    return None, " · ".join(said + [words])


def node(g: dict, node_id: str) -> dict:
    for n in g.get("nodes", []):
        if n.get("id") == node_id:
            return n
    raise CraftRefused(f"no node {node_id!r} in the graph")


def hull_edge(marker_kind: str | None, parent_kind: str | None) -> str:
    """Which of the hull's three edges an ask takes, read off its marker: a THOUGHT (an include
    asked in the chat) is chat; a ROOT (no parent) is chat — a human's own ask; a parent of a
    STRUCTURAL kind (an intention's occurrence, an objective's child) is work; any other parent
    (improvement · watch-red · any declared kind a body is interested in) is an event."""
    if marker_kind == "thought":
        return "chat"
    if not parent_kind:
        return "chat"
    if parent_kind in STRUCTURAL:
        return "work"
    return "event"


def edge_words(edge: str, parent_kind: str | None = None) -> str:
    """The journey's line for the route — plain (rule 13)."""
    if edge == "chat":
        return "routed to the chat edge — a human's ask"
    if edge == "work":
        return "routed to the work edge — assigned work under an intention"
    return f"routed to the event edge — a marker of kind {parent_kind or 'unknown'} asked for a response"


def source_form(manifest) -> dict:
    """A source's two forms: `{locator}` (reachable by NAME) or a repo'd origin `{repo, commit,
    entry}` — `{ok, form, reason}`."""
    if not isinstance(manifest, dict) or not manifest:
        return {"ok": False, "form": None, "reason": "a source is a non-empty object"}
    if manifest.get("locator"):
        return {"ok": True, "form": "locator", "reason": None}
    repo, commit, entry = (str(manifest.get(k) or "").strip() for k in ("repo", "commit", "entry"))
    if not repo:
        return {"ok": False, "form": None, "reason": "a source names a locator by NAME, or a repo with its commit and entry point"}
    if not _HEX.match(commit.lower()):
        return {"ok": False, "form": "repo", "reason": "a repo'd source pins a commit — 7 to 64 hex characters"}
    if not entry:
        return {"ok": False, "form": "repo", "reason": "a repo'd source names its entry point (`entry`: the module or file the graph is built from)"}
    return {"ok": True, "form": "repo", "reason": None}


def cut_demand(kind: str, manifest, mode: str) -> dict:
    """What a cut demands, by the craft's class (0010 lock 4): a firmware template is cut only
    in a dev universe — prod reaches it as a release; a resident's template at L3 (the code);
    an agent's template only through the Experiment (spoonful 4 — refused in words until then);
    every other craft at L2. `{ok, level, reason}`."""
    if kind not in CRAFT_KINDS:
        return {"ok": False, "level": None, "reason": f"a craft kind is one of {', '.join(CRAFT_KINDS)} — not {kind!r}"}
    if kind != "template":
        return {"ok": True, "level": "L2", "reason": None}
    tk = (manifest or {}).get("kind", "resident") if isinstance(manifest, dict) else "resident"
    if tk == "firmware":
        if mode == "prod":
            return {"ok": False, "level": None,
                    "reason": "firmware is cut only in a dev universe — it reaches prod as a release"}
        return {"ok": True, "level": "L2", "reason": None}
    if tk == "agent":
        return {"ok": False, "level": None,
                "reason": "an agent's cut goes through the Experiment — two arms, the grader's verdict, the stamped promotion (spoonful 4)"}
    return {"ok": True, "level": "L3-code", "reason": None}


def wear_of(parts: dict) -> list[dict]:
    """The components a body is made of at its join — `[{component, kind, hash}]` in the order
    worn: template · binding · policy · graph · golden. `parts` names each by `{name, hash}`
    (binding, graph and golden may be absent); the hash is the content hash of the declaration
    — the same pin the shelf keeps, so a worn version is found by hash."""
    out = []
    for kind in ("template", "binding", "policy", "graph", "golden"):
        p = parts.get(kind)
        if not p:
            if kind in ("template", "policy"):
                raise CraftRefused(f"a body wears a {kind} — none named")
            continue
        out.append({"component": craft_name(str(p["name"]), kind), "kind": kind, "hash": str(p["hash"])})
    return out


def golden_document(template: str, cases: list) -> dict:
    """A golden set as a component (the harness's bare list wrapped in its declaration)."""
    return {"format": FORMATS["golden"], "template": template, "cases": list(cases)}


# ---- the shipped crafts, read from the spine home (both kernels read the same files) -----------------------

def _read(p: Path):
    return json.loads(p.read_text("utf-8"))


def shipped(spine: str | Path | None = None) -> list[dict]:
    """Every craft the spine ships — `[{name, kind, shelf_name, manifest}]`: the templates and
    bindings the crew manifest seats, the covenant policy, the graphs, the golden sets, the
    prompts and the skills in their folders. The seed registers them at light."""
    from . import body as _body
    base = Path(spine or SPINE)
    out, seen = [], set()

    def one(kind, doc, name=None):
        if not isinstance(doc, dict):
            return
        n = name or doc.get("name")
        if not n:
            return
        sn = craft_name(str(n), kind)
        if sn in seen:
            return
        seen.add(sn)
        out.append({"name": str(n), "kind": kind, "shelf_name": sn, "manifest": doc})

    try:
        for seat in _body.crew(base):
            one("template", _read(seat["template"]))
            if seat["binding"]:
                one("binding", _read(seat["binding"]))
    except (OSError, ValueError, KeyError):
        pass
    for p in sorted((base / FOLDERS["template"]).glob("*.json")):
        one("template", _read(p))
    for p in sorted((base / FOLDERS["binding"]).glob("*.json")):
        one("binding", _read(p))
    pol = base / FOLDERS["policy"] / "covenant-policy.v1.json"
    if pol.exists():
        doc = _read(pol)
        one("policy", doc, doc.get("name") or "covenant-policy")
    for p in sorted((base / FOLDERS["graph"]).glob("*.json")):
        one("graph", _read(p))
    for p in sorted((base / FOLDERS["golden"]).glob("*.json")):
        doc = _read(p)
        if isinstance(doc, list):                    # the harness's bare list, wrapped
            doc = golden_document(p.name.split(".")[0], doc)
        one("golden", doc, doc.get("template"))
    for kind in ("prompt", "skill"):
        folder = base / FOLDERS[kind]
        if folder.exists():
            for p in sorted(folder.glob("*.json")):
                one(kind, _read(p))
    return out


def shipped_graph(name: str, spine: str | Path | None = None) -> dict | None:
    """A graph declaration by its name from the spine's folder (`graphs/<name>.json`) — the
    fallback when no ground is at hand (a pure-graph test); the shelf is read first."""
    p = Path(spine or SPINE) / FOLDERS["graph"] / f"{name}.json"
    return _read(p) if p.exists() else None


# ---- the ground: the wear table and the draft shelf (schema 6) ----------------------------------------------

def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "crafts"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_wear ("
            " wear_id bigserial PRIMARY KEY, scope text NOT NULL, did text NOT NULL, body text NOT NULL,"
            " life int NOT NULL, component text NOT NULL, kind text NOT NULL, hash text NOT NULL,"
            " version int, since timestamptz NOT NULL DEFAULT now(), until timestamptz)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_wear_component ON spine_wear (scope, component, until)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_wear_body ON spine_wear (scope, did, until)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_drafts ("
            " draft_id text PRIMARY KEY, scope text NOT NULL, person text NOT NULL, kind text NOT NULL,"
            " name text NOT NULL, body text NOT NULL, words text, from_marker text,"
            " at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now())")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_drafts_person ON spine_drafts (scope, person, updated_at DESC)")


# ---- the shelf's craft face -----------------------------------------------------------------------------------

def get(conn, name: str, kind: str) -> dict | None:
    """A craft by its bare name and kind — the shelf's row (`services.get`), or None."""
    from . import services
    return services.get(conn, craft_name(name, kind))


def graph_for(conn, template: dict) -> dict | None:
    """The template's `graph` component — the shelf first (a registered, unretired graph), the
    spine's folder as the fallback; None when neither has it (the hull says so in words)."""
    name = str(template.get("graph") or "").strip()
    if not name:
        return None
    if conn is not None:
        try:
            row = get(conn, name, "graph")
        except Exception:                            # noqa: BLE001 — a ground without the shelf yet
            row = None
        if row and row["state"] != "retired" and validate_graph(row["manifest"])["ok"]:
            return row["manifest"]
    return shipped_graph(name)


def golden_for(conn, template: str) -> list[dict]:
    """A template's golden cases — the shelf's component first, the harness's file as fallback."""
    if conn is not None:
        try:
            row = get(conn, template, "golden")
        except Exception:                            # noqa: BLE001
            row = None
        if row and row["state"] != "retired":
            return list(row["manifest"].get("cases") or [])
    p = SPINE / FOLDERS["golden"] / f"{template}.v0.json"
    if p.exists():
        doc = _read(p)
        return list(doc if isinstance(doc, list) else doc.get("cases") or [])
    return []


def probe(conn, row: dict) -> tuple[bool | None, str]:
    """A craft's honest health: its declaration reads whole; a template's graph stands on the
    shelf; a golden set's template stands on the shelf."""
    kind, m = row["kind"], row["manifest"]
    v = validate(kind, m)
    if not v["ok"]:
        return False, f"the declaration does not read whole: {v['reason']}"
    if kind == "template":
        g = get(conn, str(m.get("graph")), "graph")
        if g is None or g["state"] == "retired":
            return False, f"names graph {m.get('graph')!r}, which is not on the shelf — register it, or restore it"
        return True, f"the declaration reads whole; its graph {m.get('graph')} stands on the shelf"
    if kind == "golden":
        t = get(conn, str(m.get("template")), "template")
        if t is None:
            return True, f"the declaration reads whole ({len(m.get('cases') or [])} cases); its template {m.get('template')} is not on the shelf yet"
        return True, f"the declaration reads whole ({len(m.get('cases') or [])} cases) for the {m.get('template')} template"
    if kind == "graph":
        br = branches(m)
        return True, (f"the declaration reads whole — {len(m.get('nodes') or [])} node(s): " + " → ".join(path(m))
                      + (f" · branches at {', '.join(br)}" if br else ""))
    return True, "the declaration reads whole"


def seed(conn, *, spine: str | Path | None = None, by: str = KERNEL) -> dict:
    """At light the kernel registers every craft the spine ships (the same self every boot; a
    changed declaration re-pins — a fact, never unhealthy). `{registered, versioned, refused}`."""
    from . import services
    made, versioned, refused = [], [], []
    for c in shipped(spine):
        v = validate(c["kind"], c["manifest"])
        if not v["ok"]:
            refused.append(f"{c['shelf_name']}: {v['reason']}")
            continue
        try:
            before = services.get(conn, c["shelf_name"])
            if before is not None and before["kind"] == c["kind"] and before["state"] != "retired" \
                    and before["manifest_hash"] != services.pin(c["manifest"]):
                services.version(conn, c["shelf_name"], c["manifest"], by=by)
                versioned.append(c["shelf_name"])
                continue
            services.register(conn, c["shelf_name"], c["kind"], c["manifest"], by=by)
            if before is None:
                made.append(c["shelf_name"])
        except services.ServiceRefused as e:
            refused.append(f"{c['shelf_name']}: {e}")
    return {"registered": made, "versioned": versioned, "refused": refused}


# ---- the wear table ----------------------------------------------------------------------------------------------

def record_wear(cur, *, scope: str, did: str, body: str, life: int, worn: list[dict]) -> list[dict]:
    """Inside the join's transaction: the previous life's rows closed, one row per component
    this life wears — its version read off the shelf by hash (None when the shelf has no such
    pin: worn off the shelf, said honestly). Returns the rows as written."""
    universe = scope.split("/", 1)[0]
    cur.execute("UPDATE spine_wear SET until = clock_timestamp() WHERE did = %s AND until IS NULL", (did,))
    out = []
    for w in worn:
        cur.execute("SELECT version FROM spine_service_versions WHERE scope = %s AND name = %s AND manifest_hash = %s"
                    " ORDER BY version DESC LIMIT 1", (universe, w["component"], w["hash"]))
        r = cur.fetchone()
        version = int(r[0]) if r else None
        cur.execute(
            "INSERT INTO spine_wear (scope, did, body, life, component, kind, hash, version)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (scope, did, body, int(life), w["component"], w["kind"], w["hash"], version))
        out.append(dict(w, version=version))
    return out


def worn_by(conn, component: str) -> list[dict]:
    """Who wears a component now — `[{body, did, life, version, hash, since}]` (the open rows
    within this universe)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT body, did, life, version, hash, since FROM spine_wear"
                f" WHERE {ev.WITHIN} AND component = %s AND until IS NULL ORDER BY body",
                ev.within_params(ev.universe()) + (component,))
    return [{"body": r[0], "did": r[1], "life": int(r[2]), "version": r[3], "hash": r[4], "since": r[5].isoformat()}
            for r in cur.fetchall()]


def wears(conn, did: str) -> list[dict]:
    """What a body wears now — `[{component, kind, version, hash, since}]`."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT component, kind, version, hash, since FROM spine_wear WHERE did = %s AND until IS NULL"
                " ORDER BY wear_id", (did,))
    return [{"component": r[0], "kind": r[1], "version": r[2], "hash": r[3], "since": r[4].isoformat()}
            for r in cur.fetchall()]


def wear_counts(conn) -> dict[str, int]:
    """Component → how many bodies wear it now (the shelf's "in use by N")."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT component, count(DISTINCT did) FROM spine_wear WHERE {ev.WITHIN} AND until IS NULL"
                " GROUP BY component", ev.within_params(ev.universe()))
    return {r[0]: int(r[1]) for r in cur.fetchall()}


def wear_table(conn) -> list[dict]:
    """The whole table, open rows, within this universe — the door's listing."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT body, did, life, component, kind, version, hash, since, scope FROM spine_wear"
                f" WHERE {ev.WITHIN} AND until IS NULL ORDER BY body, wear_id", ev.within_params(ev.universe()))
    return [{"body": r[0], "did": r[1], "life": int(r[2]), "component": r[3], "kind": r[4], "version": r[5],
             "hash": r[6], "since": r[7].isoformat(), "scope": r[8]} for r in cur.fetchall()]


# ---- the draft shelf, under the person --------------------------------------------------------------------------

def _draft_row(r) -> dict:
    return {"draft_id": r[0], "person": r[1], "kind": r[2], "name": r[3], "body": json.loads(r[4]),
            "words": r[5], "from_marker": r[6], "at": r[7].isoformat(), "updated_at": r[8].isoformat()}


_DRAFT_COLS = "draft_id, person, kind, name, body, words, from_marker, at, updated_at"


def drafts(conn, person: str) -> list[dict]:
    """This person's drafts, newest first — and ONLY this person's (AG-9)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_DRAFT_COLS} FROM spine_drafts WHERE scope = %s AND person = %s ORDER BY updated_at DESC",
                (ev.universe(), person))
    return [_draft_row(r) for r in cur.fetchall()]


def draft(conn, person: str, draft_id: str) -> dict | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_DRAFT_COLS} FROM spine_drafts WHERE draft_id = %s AND scope = %s AND person = %s",
                (draft_id, ev.universe(), person))
    r = cur.fetchone()
    return _draft_row(r) if r else None


def save_draft(conn, person: str, kind: str, name: str, body: dict, *, words: str | None = None,
               draft_id: str | None = None, from_marker: str | None = None) -> dict:
    """Routine (L1): the draft lands under the person — new, or the same draft updated. No
    fact, no marker: an unversioned draft is private. The kind is checked; the body is kept
    as given (a draft may be unfinished — the cut checks it whole)."""
    if kind not in CRAFT_KINDS:
        raise CraftRefused(f"a draft is of a craft kind — one of {', '.join(CRAFT_KINDS)}, not {kind!r}")
    n = str(name or "").strip()
    if not NAME_RX.match(n):
        raise CraftRefused("a draft's name is a short lowercase name: letters, digits, dashes, dots, underscores")
    if not isinstance(body, dict):
        raise CraftRefused("a draft's body is an object — the declaration as it stands")
    body = dict(body)
    body.setdefault("format", FORMATS[kind])
    if kind in ("template", "binding", "skill", "graph"):
        body.setdefault("name", n)
    ensure_schema(conn)
    did = draft_id or ("draft_" + secrets.token_hex(6))
    with conn.transaction():
        cur = conn.cursor()
        if draft_id:
            cur.execute("SELECT 1 FROM spine_drafts WHERE draft_id = %s AND scope = %s AND person = %s",
                        (draft_id, ev.universe(), person))
            if not cur.fetchone():
                raise CraftRefused("no such draft of yours here")
            cur.execute("UPDATE spine_drafts SET kind = %s, name = %s, body = %s, words = %s,"
                        " updated_at = clock_timestamp() WHERE draft_id = %s",
                        (kind, n, json.dumps(body), words, draft_id))
        else:
            cur.execute("INSERT INTO spine_drafts (draft_id, scope, person, kind, name, body, words, from_marker)"
                        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (did, ev.universe(), person, kind, n, json.dumps(body), words, from_marker))
    return draft(conn, person, did)


def discard_draft(conn, person: str, draft_id: str) -> bool:
    """The author lets a draft go — it was never recorded, so nothing is kept."""
    ensure_schema(conn)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("DELETE FROM spine_drafts WHERE draft_id = %s AND scope = %s AND person = %s",
                    (draft_id, ev.universe(), person))
        return cur.rowcount > 0


def cut_check(conn, person: str, draft_id: str) -> dict:
    """What a cut of this draft would do, or why it refuses — read before the hold: the draft
    read whole, the demand by class, the verb the ladder takes (register, or version n+1)."""
    from . import levels, services
    d = draft(conn, person, draft_id)
    if d is None:
        raise CraftRefused("no such draft of yours here")
    v = validate(d["kind"], d["body"])
    if not v["ok"]:
        raise CraftRefused(f"the draft does not read whole yet: {v['reason']}")
    u = levels.row(conn, ev.universe())
    mode = str((u or {}).get("mode") or levels.MODE_DEFAULT)
    dem = cut_demand(d["kind"], d["body"], mode)
    if not dem["ok"]:
        raise CraftRefused(dem["reason"])
    shelf_name = craft_name(d["name"], d["kind"])
    row = services.get(conn, shelf_name)
    if row is None:
        verb, to_version = "register", 1
    elif row["kind"] != d["kind"]:
        raise CraftRefused(f"{shelf_name} is on the shelf as a {row['kind']} — a name wears one kind")
    elif row["state"] == "retired":
        raise CraftRefused(f"{shelf_name} is retired — restore it first, then cut the next version")
    elif row["manifest_hash"] == services.pin(d["body"]):
        raise CraftRefused(f"{shelf_name} already stands on the shelf with these exact bytes (version {row['version']}) — nothing to cut")
    else:
        verb, to_version = "version", row["version"] + 1
    return {"draft": d, "shelf_name": shelf_name, "verb": verb, "version": to_version,
            "level": dem["level"], "mode": mode}


def cut_words(name: str, kind: str, verb: str, version: int) -> str:
    """The held act's words: what the cut lands."""
    if verb == "register":
        return f"cutting the {name} {kind} — version 1 onto the shelf"
    return f"cutting the {name} {kind} — version {version} onto the shelf"


def hold_cut(conn, person: str, draft_id: str, *, session: str | None = None) -> str:
    """The cut is the gate: held at the interlock as the kernel's own act at the level the
    class demands; the human's deliberate yes settles it (`proof.settle_kernel_act` → `cut`)."""
    from .proof import hold_kernel_act
    c = cut_check(conn, person, draft_id)
    return hold_kernel_act(conn, text=cut_words(c["draft"]["name"], c["draft"]["kind"], c["verb"], c["version"]),
                           person=person, tool=CUT_TOOL, args={"draft_id": draft_id, "person": person},
                           level=c["level"], session=session, cls=CUT_CLASS)


def cut(conn, person: str, draft_id: str, *, by: str | None = None, ask: str | None = None,
        parent_marker: str | None = None, confirmed_by: str | None = None) -> dict:
    """The settled cut: the draft lands on the shelf — registered, or the next version — as the
    ladder's own fact with the person on the chain (`by` the author, `confirmed_by` the one who
    said yes); the draft is spent. Returns the shelf row."""
    from . import services
    c = cut_check(conn, person, draft_id)
    d, sn = c["draft"], c["shelf_name"]
    who = by or person
    if c["verb"] == "register":
        row = services.register(conn, sn, d["kind"], d["body"], by=who)
    else:
        row = services.version(conn, sn, d["body"], by=who)
    with conn.transaction():
        conn.cursor().execute("DELETE FROM spine_drafts WHERE draft_id = %s", (draft_id,))
    ok_, detail = probe(conn, row)                   # walk SPEC-SHELF-01: a cut craft is probed at the cut — never "never probed"
    services.record_health(conn, sn, ok_, detail, by=who)
    return services.get(conn, sn)


def worn_words(component: str, wearers: list[dict]) -> str:
    """"in use by N", in words."""
    if not wearers:
        return f"{component} is worn by no body now"
    names = ", ".join(f"{w['body']} (life {w['life']}" + (f", v{w['version']}" if w.get("version") else ", off the shelf") + ")"
                      for w in wearers)
    n = len(wearers)
    return f"{component} is worn by {n} bod{'y' if n == 1 else 'ies'}: {names}"
