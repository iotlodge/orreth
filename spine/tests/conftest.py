# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp1, the durability boundary (M1) · 2026-09-16
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
    os.environ.pop("SPINE_QUEUE_NS", None)
    os.environ.pop("SPINE_SCOPE", None)


@pytest.fixture(scope="session")
def pg():
    psycopg = pytest.importorskip("psycopg")
    try:
        conn = psycopg.connect(DSN)
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


@pytest.fixture(scope="module")
def rig(pg, _queue_ns):
    """One standing world PER MODULE — the production shape (one
    dispatcher membership, one feed membership, living residents), but
    never outliving the file that walks it. A rig's residents poll the
    session's benches every 50ms; a rig left standing across files
    steals the commands of any test serving its OWN resident, refuses
    them as strangers to its ground, and starves that test (found live:
    every resident-serving test after the first rig's birth timed out).
    Tests AIM it by setting rig.resident.gateway and targeting by name."""
    from orreth_spine import glass
    r = glass.BridgeRig(gateway=None, port=0).start()
    assert r.wait_ready(30), "the standing rig never became ready"
    yield r
    r.stop()
