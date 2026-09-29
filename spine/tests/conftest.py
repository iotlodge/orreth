# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp1, the durability boundary (M1) · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 lock 5, one rig per test session; the rig yields to a test that serves its own bodies · 2026-09-27
"""The ground fixture: a throwaway schema per test session so every run
starts clean. Skips politely when the rig is down — unless
SPINE_REQUIRE_PG is set (CI sets it: there, no ground means FAIL, never
a silent skip)."""
import os
import secrets

import pytest

DSN = os.environ.get(
    "SPINE_PG", "postgresql://orreth:orreth-dev@localhost:5433/spine")


@pytest.fixture(scope="session", autouse=True)
def _queue_ns():
    """The session's own benches: a unique queue namespace so tests can
    never race a live rig (or a past session) on the shared broker."""
    tok = "t" + secrets.token_hex(3)
    os.environ["SPINE_QUEUE_NS"] = tok
    os.environ["SPINE_SCOPE"] = "u:test-" + tok
    yield
    try:                                            # the perf cure (2026-09-29): the session's residue on the
        from orreth_spine import prune              # brokers — its topics, its queues, the empty test groups —
        prune.namespace(tok)                        # leaves with it (found live: 5,288 topics after six days)
    except Exception:                               # noqa: BLE001 — a dark broker prunes nothing
        pass
    os.environ.pop("SPINE_QUEUE_NS", None)
    os.environ.pop("SPINE_SCOPE", None)


@pytest.fixture(scope="session")
def pg():
    psycopg = pytest.importorskip("psycopg")
    try:
        # autocommit: a session-long connection handed to library code must
        # never sit inside an implicit transaction — a bare execute here
        # once pinned ensure_schema's xact-scoped advisory lock for the rest
        # of the session, and every later rig's dispatcher queued behind it
        conn = psycopg.connect(DSN, autocommit=True)
    except Exception as e:
        if os.environ.get("SPINE_REQUIRE_PG"):
            raise
        pytest.skip(f"the ground is not up ({type(e).__name__}) — "
                    "start spine/compose.yaml or set SPINE_PG")
    try:
        with conn.transaction():
            cur = conn.cursor()
            cur.execute("DROP SCHEMA IF EXISTS spine_test CASCADE")
            cur.execute("CREATE SCHEMA spine_test")
        conn.execute("SET search_path TO spine_test")
        yield conn
    finally:
        conn.close()


_LIT: dict = {"rig": None}      # the session's one rig, once a test has asked for it


@pytest.fixture(scope="session")
def rig(pg, _queue_ns):
    """ONE standing world PER SESSION (canon 0005, JB's lock 5, 2026-09-27) —
    the production shape (one dispatcher membership, one feed membership,
    the crew living), lit at the first test that asks for it and stopped
    whole when the session ends. It used to be one per MODULE: eighteen
    boots a run (ten bodies joined, the shelf seeded and probed, MITL
    acquiring the canon, each time) — most of the suite's six minutes.
    A session rig was tried once before and stole every self-serving
    test's commands (its crew poll the session's benches by name), so
    now THE RIG YIELDS: `_benches` parks it for every test that does not
    ask for it, and resumes it for every test that does.

    Tests AIM it by setting rig.resident.gateway and targeting by name;
    the aim is undone after each test (every seat back to the rig's own
    mind), so no test inherits another's."""
    from orreth_spine import glass
    r = glass.BridgeRig(gateway=None, port=0, home=None).start()  # ephemeral
    assert r.wait_ready(30), (
        "the standing rig never became ready — feed_ready="
        f"{r.feed_ready.is_set()} dispatcher_ready={r.dispatcher_ready.is_set()} "
        f"threads alive={sum(t.is_alive() for t in r._threads)}/{len(r._threads)}")
    _LIT["rig"] = r
    yield r
    _LIT["rig"] = None
    r.stop()


@pytest.fixture(autouse=True)
def _benches(request):
    """THE RIG YIELDS (lock 5). A test that asks for `rig` gets it awake;
    any other test runs with the session's rig parked — its dispatcher
    passing every fact by, its crew off the benches, its beats held — so
    a test that lights its own bodies (or a whole rig of its own) walks
    the session's benches alone, exactly as it did when no rig outlived
    a file. Parking waits for every loop's word (≤ a second, once per
    switch); a rig that never parks fails the test by name rather than
    letting it be raced by a ghost."""
    r = _LIT["rig"]
    if r is None:                    # no rig lit yet: nothing to yield
        yield
        return
    if "rig" in request.fixturenames:
        r.resume()
        try:
            yield
        finally:
            for body in r.residents:     # the aim undone: every seat wears the rig's own mind
                body.gateway = r.gateway
    else:
        assert r.park(), "the session's rig never yielded the benches — a loop of it is wedged"
        yield
