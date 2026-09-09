# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp2, the chunk law · 2026-09-09
"""The chunk/tree law (0065 §3.4) — the ONE deterministic cutter behind the
standing projection.

The standing projection holds POINTERS, never blobs (the pg.rs law): a chunk
row is (seq · span into the derived text · the piece's hash · its lane), and
a reader re-derives the text from the record's body with this same law. That
is what makes the projection rebuildable-therefore-disposable: cutting the
same text under the same policy yields byte-identical rows, forever — the
suite holds this as the rebuild-identical law.

The policy (chunk size, overlap) is CRAFT — the standing `stacks-chunking`
asset — and every row wears the policy's hash: a turned policy makes old
rows visibly stale, and the sweep re-cuts them; nothing ever serves under a
policy it was not cut by.

The tree (Hierarchical's substrate): leaf spans group into parent nodes,
level by level, each parent's span covering exactly its children — a long
document's own structure as rows, walked by the Hierarchical style when sp4
builds it. Fanout is firmware: the tree's SHAPE is law, its depth a variant
knob.
"""
from __future__ import annotations

import hashlib
import json

TREE_FANOUT = 8          # leaves per parent, parents per grandparent — firmware
LANES = ("document", "chronicle", "knowledge")


def policy_hash(policy: dict) -> str:
    """The policy's name on every row it cut."""
    raw = json.dumps({"chunk_chars": int(policy["chunk_chars"]),
                      "overlap_chars": int(policy["overlap_chars"])},
                     sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cut(text: str, size: int, overlap: int) -> list[tuple[int, int]]:
    """Spans over the text — the same walk project() has always taken,
    written once: start at 0, step size-minus-overlap, never an empty piece."""
    spans = []
    n = len(text or "")
    step = max(1, int(size) - int(overlap))
    i = 0
    while i < n:
        spans.append((i, min(i + int(size), n)))
        i += step
    return spans


def rows_for(text: str, lane: str, policy: dict) -> list[dict]:
    """A record's chunk rows under the policy: seq · span · the piece's hash.
    The text is the DERIVED text of the lane (a document's own bytes, a
    chronicle's flattened words, a knowledge claim) — the reader re-derives
    with the same lane law and slices by span; the hash catches any drift
    between cutter and reader before it can serve."""
    if lane not in LANES:
        raise ValueError(f"unknown lane «{lane}» — the law cuts only: "
                         + ", ".join(LANES))
    size, ov = int(policy["chunk_chars"]), int(policy["overlap_chars"])
    return [{"seq": i, "span": [s, e], "lane": lane,
             "hash": hashlib.sha256(text[s:e].encode()).hexdigest()[:16]}
            for i, (s, e) in enumerate(cut(text, size, ov))]


def tree_for(rows: list[dict], levels: int = 2) -> list[dict]:
    """Parent nodes over leaf rows: level 1 groups TREE_FANOUT leaves, level 2
    groups level-1 parents, and so on — each parent's span covering exactly
    its children. Rows for a SHORT text (one group or fewer) earn no tree:
    structure that does not exist is never invented."""
    out: list[dict] = []
    children = rows
    for level in range(1, max(1, int(levels)) + 1):
        if len(children) <= 1:
            break
        parents = []
        for i in range(0, len(children), TREE_FANOUT):
            group = children[i:i + TREE_FANOUT]
            parents.append({"seq": len(parents), "level": level,
                            "span": [group[0]["span"][0],
                                     group[-1]["span"][1]],
                            "lane": group[0]["lane"],
                            "covers": [c["seq"] for c in group]})
        if len(parents) == len(children):
            break
        out.extend(parents)
        children = parents
    return out


# ---- the standing book, as pure law (the plane's Postgres twin: the suite
# ---- proves the lifecycle here; the wire proves it on the rig) -------------

def put(book: dict, record_id: str, phash: str, rows: list[dict],
        tree: list[dict] | None = None) -> None:
    """One record, one policy, one truth: landing rows replaces every row
    the record had, whatever policy the old ones wore."""
    book[record_id] = {"policy": phash, "rows": list(rows),
                       "tree": list(tree or [])}


def evict(book: dict, record_id: str) -> int:
    """Purge reach: a shredded record's chunks and tree die in the same
    breath — deleted, not marked; the worklist may re-list only what still
    lives in the log."""
    e = book.pop(record_id, None)
    return (len(e["rows"]) + len(e["tree"])) if e else 0


def missing(book: dict, live_ids, phash: str) -> list[str]:
    """The sweep's worklist: living records with no rows under the CURRENT
    policy — the uncut and the stale alike; the purged never appear because
    they are not in live_ids."""
    return [rid for rid in live_ids
            if book.get(rid, {}).get("policy") != phash]
