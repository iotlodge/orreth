# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — THE STUDIO sp9c HOW THE KERNEL WORKS (canon 0011 §4c, JB's lock 2026-10-14) · 2026-10-14
"""HOW THE KERNEL WORKS: the kernel's map is a declaration the kernel serves, lit by its own
numbers — never a static picture. This holds `spine/guide/kernel-map.v0.json` to the one graph
model (every node has plain words; a node of kind graph contains a graph whose entry is inside it;
every edge lands on a node that exists — a top-level edge by its path, region:part), holds the
reference door's live numbers to the kernel's own constants, and holds `GET /map` to the door list
(the Rust kernel serves the same file law for law; fixture doors-v0 names the door on both)."""
import json
import urllib.request

import seats
from orreth_spine import doors, glass, ground


def _paths(g, prefix=""):
    out = {}
    for n in g["nodes"]:
        p = (prefix + ":" if prefix else "") + n["id"]
        out[p] = n
        if n.get("graph"):
            out.update(_paths(n["graph"], p))
    return out


def test_the_map_is_one_graph_of_the_model():
    m = glass.map_view()
    assert m["format"] == "orreth-map/1" and m["title"] and m["words"]
    paths = _paths(m)
    assert m["entry"] in paths
    for p, n in paths.items():
        assert n.get("words"), f"{p} has no plain words"
        assert n["kind"] in ("graph", "part"), p
        if n["kind"] == "graph":
            g = n["graph"]
            ids = {x["id"] for x in g["nodes"]}
            assert g["nodes"] and g["entry"] in ids, p
            for e in g.get("edges", []):
                assert e["from"] in ids and e["to"] in ids, f"{p}: {e}"
    for e in m["edges"]:                                     # the story's road, numbered, lands on parts that exist
        assert e["from"] in paths and e["to"] in paths, e
        assert e.get("words"), e
    story = [e["words"] for e in m["edges"] if e["words"][:1].isdigit()]
    assert [w.split(".")[0] for w in story] == [str(i + 1) for i in range(len(story))]


def test_the_live_numbers_are_the_kernels_own():
    live = glass.map_view()["live"]
    assert live["kernel"] == "reference" and live["version"]
    assert live["schema"] == ground.SCHEMA_VERSION
    assert live["doors"] == len(doors.KNOWN) and live["topics"] == len(glass.FEED_TOPICS) and live["tables"] == len(ground.TABLES)
    assert "map" in doors.KNOWN and doors.door_name("GET", "/map?x=1") == "GET /map"


def test_the_map_door_serves_it_seated(rig):
    r = seats.urlopen(f"http://127.0.0.1:{rig.port}/map")
    m = json.loads(r.read())
    assert m["format"] == "orreth-map/1" and m["live"]["kernel"] == "reference" and m["live"]["tables"] == len(ground.TABLES)
    try:                                                     # the unseated wear one face — the map is a seated read (401; 429 when the
        urllib.request.urlopen(f"http://127.0.0.1:{rig.port}/map")   # suite has spent this address's knock ceiling before the stranger knocks)
    except urllib.error.HTTPError as e:
        assert e.code in (401, 429), e.code
    else:
        raise AssertionError("the map opened to a stranger")
