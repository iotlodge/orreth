# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp4, MEM-2 resume · 2026-09-19
"""MEM-2 (canon 0003): working memory on the ground — a life that dies
mid-graph resumes at its hop, never re-hearing, never re-recalling,
owing what it owed; the journey says so."""
import secrets
from pathlib import Path

from orreth_spine import dispatch, gateway, glass, resident

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"


class CutOnce(gateway.FakeGateway):
    """A power cut in the middle of the first think."""
    def __init__(self, reply):
        super().__init__(reply=reply); self.attempts = 0

    def think(self, conn, **kw):
        self.attempts += 1
        if self.attempts == 1:
            raise RuntimeError("power cut mid-think")
        return super().think(conn, **kw)


def test_a_body_that_dies_mid_think_resumes_at_think(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    gw = CutOnce("the answer, after the cut")
    lib = resident.Resident(SPINE / "templates" / "librarian-resident.v0.json", gateway=gw)
    lib.load_policy(POLICY); lib.join(pg); lib._serve_conn = pg
    lib.prepare(pg)                                    # working memory on the ground
    assert lib._ckpt_graph is not None
    ask = dispatch.submit_ask(pg, "what survives a cut?", person="did:orreth:person:test")
    try:
        with pg.transaction():
            lib._serve_ask(pg.cursor(), ask, ["did:orreth:person:test"])
        raise AssertionError("the cut should have raised")
    except RuntimeError as e:
        assert "power cut" in str(e)
    assert glass.ask_view(pg, ask)["status"] == "received"          # the serve rolled back
    snap = lib._ckpt_graph.get_state({"configurable": {"thread_id": ask}})
    assert snap.next == ("think",)                                   # but the hops before it stayed
    with pg.transaction():                                           # the next life serves again
        lib._serve_ask(pg.cursor(), ask, ["did:orreth:person:test"])
    view = glass.ask_view(pg, ask)
    assert view["status"] == "replied" and view["reply"] == "the answer, after the cut"
    assert gw.attempts == 2 and len(gw.calls) == 1                  # one cut, one thought
    notes = view["journey"]
    assert sum("heard the ask" in n for n in notes) == 1              # never re-heard
    assert sum("recalled" in n for n in notes) == 1                   # never re-recalled
    assert any("resumed at think" in n for n in notes)                # and it says so
