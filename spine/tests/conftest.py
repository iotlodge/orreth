# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp1, the durability boundary (M1) · 2026-09-16
"""The ground fixture: a throwaway schema per test session so every run
starts clean. Skips politely when the rig is down — unless
SPINE_REQUIRE_PG is set (CI sets it: there, no ground means FAIL, never
a silent skip)."""
import os

import pytest

DSN = os.environ.get(
    "SPINE_PG", "postgresql://orreth:orreth-dev@localhost:5433/spine")


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
