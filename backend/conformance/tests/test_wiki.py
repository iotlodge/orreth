# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp4, the wiki · 2026-09-10
"""The wiki's laws (0069 §3.4): every statement grounded to signed
evidence, links whitelisted against the real, pages rebuildable never
edited, the purge cascade running THROUGH claims — and a flagged page
refusing to call itself current until an explicit, recorded rebuild."""
import json

import pytest

from orreth_sim import basket, crypto, stacks, wiki
from orreth_sim.world import build


@pytest.fixture()
def ground(tmp_path):
    w = build()
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    n = w.universe
    store = tmp_path / "objects"
    # two origins, overlapping vocabulary — the concept page's food
    r1 = basket.import_bytes(n, ident, kp,
        data=b"Rammed earth walls hold thermal mass beautifully. "
             b"The thermal mass smooths every winter swing.",
        name="earth.md", origin={"path": "/x/earth.md"}, store_root=store)
    r2 = basket.import_bytes(n, ident, kp,
        data=b"Hempcrete also carries thermal mass, with insulation besides. "
             b"Lime skins protect the hempcrete from rain.",
        name="hemp.md", origin={"path": "/x/hemp.md"}, store_root=store)
    return {"node": n, "author": ident, "kp": kp,
            "p1": r1["pointer"], "k1": r1["extraction"],
            "p2": r2["pointer"], "k2": r2["extraction"]}


def _body(node, ref):
    return json.loads(crypto._b64d(node.records[ref]["body"]).decode())


def test_claims_are_grounded_to_evidence_and_origin(ground):
    g = ground
    claims = wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    assert len(claims) == 2
    c = _body(g["node"], claims[0])["claim"]
    assert c["evidence"] == g["k1"]               # the id IS the version
    assert c["origin"] == g["p1"]
    assert g["node"].records[claims[0]]["derived_from"] == [g["k1"]]
    assert wiki.claimed_evidence(g["node"]) == {g["k1"]}


def test_the_link_whitelist_kills_hallucinated_references(ground):
    g = ground
    claims = wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    pid = wiki.build_origin_page(
        g["node"], g["author"], g["kp"], g["p1"], claims, title="earth.md",
        links=[g["p2"], "sha256:made-up-page-that-never-existed"],
        subjects={g["p1"], g["p2"]})
    p = _body(g["node"], pid)["wiki_page"]
    assert p["links"] == [g["p2"]]                 # the invention did not survive


def test_concepts_recur_across_distinct_origins(ground):
    g = ground
    wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    wiki.mint_claims(g["node"], g["author"], g["kp"], g["k2"])
    cm = wiki.concept_map(g["node"])
    assert "thermal" in cm and cm["thermal"]["recurrence"] == 2
    assert "hempcrete" not in cm                   # one origin is not a concept
    cid = wiki.build_concept_page(g["node"], g["author"], g["kp"],
                                  "thermal", cm["thermal"])
    assert _body(g["node"], cid)["wiki_page"]["recurrence"] == 2


def test_the_cascade_runs_through_claims_and_flags_pages(ground):
    """Kill an origin: its claims retract on their own worldlines, the page
    wearing them flags, and the page may NOT call itself current until an
    explicit rebuild — which names the retraction and derives from the
    flag. Nothing deleted anywhere."""
    g = ground
    c1 = wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    pid = wiki.build_origin_page(g["node"], g["author"], g["kp"],
                                 g["p1"], c1, title="earth.md")
    assert wiki.page_status(g["node"], pid) == "current"
    out = wiki.cascade(g["node"], g["author"], g["kp"], g["k1"])
    assert set(out["retracted"]) == set(c1)
    assert out["flagged"] == [pid]
    assert wiki.page_status(g["node"], pid) == "flagged"   # refuses current
    assert set(wiki.live_claims(g["node"])) == set()        # all retracted
    flag = wiki.flagged_pages(g["node"])[pid]
    new = wiki.rebuild_after_flag(g["node"], g["author"], g["kp"], pid, flag)
    np = _body(g["node"], new)["wiki_page"]
    assert np["claims"] == [] and "retraction of 2" in np["note"]
    assert pid in g["node"].records[new]["derived_from"]
    assert flag in g["node"].records[new]["derived_from"]
    assert wiki.page_status(g["node"], pid) == "current"    # answered
    assert wiki.flagged_pages(g["node"]) == {}


def test_a_second_cascade_never_doubles_retractions(ground):
    g = ground
    c1 = wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    wiki.cascade(g["node"], g["author"], g["kp"], g["k1"])
    again = wiki.cascade(g["node"], g["author"], g["kp"], g["k1"])
    assert again == {"retracted": [], "flagged": []}


def test_the_catalog_lists_the_heads(ground):
    g = ground
    c1 = wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    wiki.build_origin_page(g["node"], g["author"], g["kp"], g["p1"], c1,
                           title="earth.md")
    cat = wiki.build_catalog(g["node"], g["author"], g["kp"])
    entries = _body(g["node"], cat)["wiki_page"]["entries"]
    assert any(e["kind"] == "origin" and e["title"] == "earth.md"
               for e in entries)


def test_the_pointer_text_hook_feeds_whole_documents(ground):
    """0065's Hierarchical tree finally retrieves over WHOLE documents: with
    the hook aimed, a pointer record's derived text is the full extraction
    — without it, pointers stay non-material exactly as before."""
    g = ground
    rec = g["node"].records[g["p1"]]
    assert stacks.derived_text(g["node"], g["p1"], rec, set()) is None
    stacks.pointer_text_reader = lambda ap: ("the whole document, every page"
                                             if ap.get("name") == "earth.md"
                                             else None)
    try:
        lane, text, doc, trust, state, when = stacks.derived_text(
            g["node"], g["p1"], rec, set())
        assert lane == "document" and doc == "earth.md"
        assert text == "the whole document, every page"
    finally:
        stacks.pointer_text_reader = None


def test_the_cascade_reads_the_seal_never_probes_a_door(ground):
    """0026's seal is the signed death notice — sealed_refs reads the LAW,
    so a dark wire can never be mistaken for a death."""
    from orreth_sim import purge
    g = ground
    wiki.mint_claims(g["node"], g["author"], g["kp"], g["k1"])
    seal = purge.make_seal(g["author"], g["kp"], "u:demo", [g["k1"]],
                           reason="the cascade walk")
    g["node"].write(seal)
    assert g["k1"] in wiki.sealed_refs(g["node"])
    out = wiki.cascade(g["node"], g["author"], g["kp"], g["k1"])
    assert len(out["retracted"]) == 2
