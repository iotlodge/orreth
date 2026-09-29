# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: THE MIGRATOR (lock 2) · 2026-09-28
"""THE MIGRATOR's laws on the reference (canon 0005 row 4, lock 2 — "the single-writer
schema migrator"): the first birth on a ground migrates it and records the version; the
next birth runs no DDL and verifies; the tables the ground holds are exactly the ones
the contract names (fixture `schema-v0.json`); a ground whose version lies (a declared
table dropped) is refused in plain words; a kernel lighting beside a migrating one
waits at the lock and then verifies — one writer, ever."""
import threading

import psycopg
import pytest

from orreth_spine import ground

from conftest import DSN


def _fresh(conn, name: str) -> None:
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(f"DROP SCHEMA IF EXISTS {name} CASCADE")
        cur.execute(f"CREATE SCHEMA {name}")
    conn.execute(f"SET search_path TO {name}")


def _tables(conn, schema: str) -> list[str]:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
                " AND table_name LIKE 'spine\\_%%' ORDER BY 1", (schema,))
    return [r[0] for r in cur.fetchall()]


def test_the_first_birth_migrates_and_the_next_verifies():
    with psycopg.connect(DSN, autocommit=True) as a:
        _fresh(a, "spine_mig_a")
        first = ground.ensure_all(a)
        assert first == {"found": 0, "ground": ground.SCHEMA_VERSION, "kernel": ground.SCHEMA_VERSION,
                         "migrated": True}
        assert ground.SCHEMA["migrated"] is True                   # the health door's word
        assert _tables(a, "spine_mig_a") == sorted(ground.TABLES)  # the contract, exactly
        cur = a.cursor()
        cur.execute("SELECT version, kernel FROM spine_schema")
        assert cur.fetchall() == [(ground.SCHEMA_VERSION, "reference")]
        with psycopg.connect(DSN, autocommit=True) as b:           # a second connection, born later
            b.execute("SET search_path TO spine_mig_a")
            second = ground.ensure_all(b)                           # this process's memo: trusted, nothing asked
            assert second["migrated"] is False and second.get("memo") is True
            assert ground.ensured(b) >= set(ground.TAGS)            # flagged, no DDL run
            ground.forget(b)                                        # another process's birth: verified on the ground
            second = ground.ensure_all(b)
            assert second["migrated"] is False and second["found"] == ground.SCHEMA_VERSION and "memo" not in second
        cur.execute("SELECT count(*) FROM spine_schema")
        assert cur.fetchone()[0] == 1                               # one version row, one writer
        assert "verified" in ground.words(second) and f"migrated 0 → {ground.SCHEMA_VERSION}" in ground.words(first)


def test_a_ground_whose_version_lies_is_refused():
    with psycopg.connect(DSN, autocommit=True) as a:
        _fresh(a, "spine_mig_b")
        ground.ensure_all(a)
        a.execute("DROP TABLE spine_mitl")
        with psycopg.connect(DSN, autocommit=True) as b:
            b.execute("SET search_path TO spine_mig_b")
            ground.forget(b)                                        # a fresh process would not carry the memo
            with pytest.raises(ground.GroundRefused) as e:
                ground.ensure_all(b)
            assert "spine_mitl is missing" in str(e.value) and "not stood on" in str(e.value)


def test_two_kernels_birthing_together_have_one_writer():
    with psycopg.connect(DSN, autocommit=True) as a:
        _fresh(a, "spine_mig_c")
    outs, errs = [], []

    def birth():
        try:
            with psycopg.connect(DSN, autocommit=True) as c:
                c.execute("SET search_path TO spine_mig_c")
                outs.append(ground.ensure_all(c))
        except Exception as e:                                      # noqa: BLE001 — the proof reads it
            errs.append(e)

    ts = [threading.Thread(target=birth) for _ in range(3)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(60)
    assert not errs, errs
    assert sum(1 for o in outs if o["migrated"]) == 1               # exactly one writer (the others: the memo, or verified)
    assert all(o["ground"] == ground.SCHEMA_VERSION for o in outs)  # the rest waited, then verified
