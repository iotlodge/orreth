# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0067 sp1, the act-graph format · 2026-09-09
"""The act-graph format (0067 §3.1) — one way to describe any picture of work.

KCR-0004's payment begins here: one graph language for who did what, in what
order, what each step saw and cost — that every view can draw, and where
clicking any box opens the real record behind it. Firmware-versioned beside
the contracts and EARMARKED for contracts/v1 exactly as 0008 planned
(GraphSpec's reserved slot); the sacred v0 contracts need no change — the
`coordinate` field already rides there.

The four laws, held by `validate`:

1. **Every node is a door.** A box with nothing behind it is refused at
   validation — the 0052 law made structural. A door is
   `{kind: record|room|floor|view, target}`.
2. **The narrative is a bijection.** Every sentence's nodes and edges exist;
   every node is covered by at least one sentence — a graph a human can read
   aloud (0008 §3's discipline, kept).
3. **Edges bind existing nodes**, and their `kinds` list keeps the atlas's
   glow law: an edge lights only from real activity; empty means structural.
4. **A live act's graph is a projection of its signed records** — it grows
   because records land, never because anyone edits a picture (`coordinate`
   is the join; sp4 builds the accretion).

The choreography dialect converts first (§6 sp1): the walk's picture becomes
act-v1 with its narrative verbatim and every seat wearing a real door — a
fingertip opens its outcome record when one stands, and carries the
objective coordinate so the deepest answer (the APERTURE — what rode down,
whole) is one governed fetch away.
"""
from __future__ import annotations

VERSION = "act-v1"

DOOR_KINDS = ("record", "room", "floor", "view")


def validate(g: dict) -> list[str]:
    """The format's law — a list of flaws, empty when the picture is whole."""
    flaws = []
    nodes = g.get("nodes") or []
    ids = [n.get("id") for n in nodes]
    if len(ids) != len(set(ids)):
        flaws.append("node ids must be unique")
    known = set(ids)
    for n in nodes:
        d = n.get("door")
        if not (isinstance(d, dict) and d.get("kind") in DOOR_KINDS
                and d.get("target")):
            flaws.append(f"node «{n.get('id')}» has no door — a box with "
                         "nothing behind it is refused (0052)")
    edge_refs = set()
    for e in g.get("edges") or []:
        if e.get("from") not in known or e.get("to") not in known:
            flaws.append(f"edge {e.get('from')}→{e.get('to')} binds a node "
                         "that does not exist")
        edge_refs.add(f"{e.get('from')}→{e.get('to')}")
    covered = set()
    for s in g.get("narrative") or []:
        for nid in s.get("nodes") or []:
            if nid not in known:
                flaws.append(f"the narrative names an unknown node «{nid}»")
            covered.add(nid)
        for er in s.get("edges") or []:
            if er not in edge_refs:
                flaws.append(f"the narrative names an unknown edge «{er}»")
    uncovered = known - covered
    if g.get("narrative") and uncovered:
        flaws.append("the narrative must cover every node — silent boxes: "
                     + ", ".join(sorted(uncovered)))
    return flaws


def from_choreography(g: dict, *, objective: str | None = None,
                      request: str | None = None) -> dict:
    """The walk's dialect → act-v1, nothing lost: the narrative rides
    verbatim, every field the glass's detail reads survives on the node, and
    every seat gains a REAL door — a fingertip opens its outcome record when
    one stands (its marker behind it), the orchestrator and review open the
    objective's own record or view, the human opens the request. The
    objective coordinate rides the graph root: the aperture — what rode
    down, whole — is one governed fetch away for any seat."""
    nodes = []
    for n in g.get("nodes") or []:
        role = n.get("role", "")
        if role == "fingertip":
            label = ((n.get("altitude") or n["id"]).split("/")[-1]
                     + (f" · {n['status']}" if n.get("status") else ""))
            door = ({"kind": "record", "target": n["outcome"]}
                    if n.get("outcome") else
                    {"kind": "view", "target": "walk"})
            cost = ({"tokens": n["budget"]} if n.get("budget") else None)
        else:
            label = {"orchestrator": "objective", "review": "review",
                     "human": "you"}.get(role, n["id"])
            door = ({"kind": "record", "target": objective}
                    if role in ("orchestrator", "review") and objective else
                    {"kind": "record", "target": request}
                    if role == "human" and request else
                    {"kind": "view", "target": "objectives"})
            cost = None
        nodes.append({**n, "label": label, "kind": n.get("kind", "seat"),
                      "door": door, **({"cost": cost} if cost else {})})
    edges = [{**e, "kinds": e.get("kinds") or []}
             for e in g.get("edges") or []]
    return {"format": VERSION, "kind": "act-graph",
            "title": g.get("title", ""),
            **({"coordinate": {"objective": objective}} if objective else {}),
            "nodes": nodes, "edges": edges,
            "narrative": list(g.get("narrative") or [])}


def from_manifest_flow(spec: dict, stages: list | None = None,
                       capability: str | None = None) -> dict:
    """The capability-flow dialect → act-v1 (0067 sp2): the manifest's
    declared pipeline joined to the walk's stage records. A stage that has
    RUN opens its own record (the door the family never had); one that has
    not yet run opens the capability's room, honestly. Groups and edge
    labels survive; the serpentine is the drawer's business, not the
    format's. Pipelines carry no narrative — the bijection law applies only
    where a story is told."""
    by_stage = {}
    for st in stages or []:
        sid = st.get("stage") or st
        if isinstance(sid, str):
            by_stage[sid] = st if isinstance(st, dict) else {}
    nodes = []
    for n in spec.get("nodes") or []:
        n = {"id": n} if isinstance(n, str) else dict(n)
        st = by_stage.get(n["id"]) or {}
        ran = bool(st.get("ref"))
        nodes.append({**n, "label": n.get("label") or n["id"].replace("-", " "),
                      "kind": n.get("kind", "stage"),
                      "status": "done" if ran else "pending",
                      **({"digest": st.get("digest")} if st.get("digest")
                         else {}),
                      "door": ({"kind": "record", "target": st["ref"]}
                               if ran else
                               {"kind": "room",
                                "target": capability or "capability"})})
    edges = []
    for e in spec.get("edges") or []:
        e = ({"from": e[0], "to": e[1]} if isinstance(e, (list, tuple))
             else dict(e))
        edges.append({**e, "kinds": e.get("kinds") or []})
    return {"format": VERSION, "kind": "act-graph", "layout": "pipeline",
            "title": spec.get("label", ""),
            **({"groups": spec["groups"]} if spec.get("groups") else {}),
            "nodes": nodes, "edges": edges, "narrative": []}
