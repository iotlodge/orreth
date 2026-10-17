# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — W153: the working memory's tables at a fresh world's first light · 2026-10-16
"""W153 (found 2026-10-16 on the 0.2.0 walk, reproduced on a fresh first world: 22 deadlocks at one
light, every body's first serve). The saver's migrations end in three `CREATE INDEX CONCURRENTLY`,
which wait for every open transaction's snapshot. Held under the DDL guard's key (742199) while the
bodies birthing beside it waited for that same key INSIDE a transaction, the holder waited for them
and they for it; a body blocked on a plain `pg_advisory_lock` was a transaction with a snapshot too.

The proof stages that shape on a schema of its own, with no checkpoint table yet (so the indexes
are really built): one life lays the memory tables while a second transaction holds a snapshot and
then asks for the DDL guard, and a third life lays the same tables at the same moment. Before the
cure this deadlocked; now every party finishes, nobody is killed, and the tables stand once.
"""
from __future__ import annotations

import threading
import time

import psycopg
import pytest

from orreth_spine import ground, resident

SCHEMA = "spine_w153"


def _conn(dsn: str, password: str | None):
    return psycopg.connect(dsn, password=password, autocommit=True, options=f"-c search_path={SCHEMA}")


@pytest.fixture
def scratch(pg):
    """A schema of its own on the rig's ground — no checkpoint table stands in it yet."""
    dsn, pw = pg.info.dsn, pg.info.password
    with psycopg.connect(dsn, password=pw, autocommit=True) as c:
        c.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
        c.execute(f"CREATE SCHEMA {SCHEMA}")
    yield dsn, pw
    with psycopg.connect(dsn, password=pw, autocommit=True) as c:
        c.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")


def test_the_memory_lock_is_its_own_key():
    """The saver's key is never the DDL guard's and never a beat's."""
    assert resident.MEMORY_LOCK != 742199
    assert resident.MEMORY_LOCK < ground.BEAT_LOCK


def test_two_lives_lay_the_memory_tables_beside_a_birth_without_a_deadlock(scratch):
    dsn, pw = scratch
    errors: list[BaseException] = []
    done: dict[str, float] = {}
    t0 = time.monotonic()

    def life(name: str, delay: float, hold: float = 0.0):
        time.sleep(delay)
        try:
            r = resident.Resident.__new__(resident.Resident)      # a life's shell: the name and the flag are all the tables need
            r.name, r._ckpt_setup = name, False
            with _conn(dsn, pw) as conn:
                r.memory_tables(conn, patience_s=30, _hold_s=hold)
            done[name] = time.monotonic() - t0
        except BaseException as e:                                # noqa: BLE001 — the verdict is the list
            errors.append(e)

    def birth(delay: float):
        """A body birthing beside them: a snapshot taken, then the DDL guard asked for inside the
        same transaction — the very shape that cycled with the saver before the cure."""
        time.sleep(delay)
        try:
            with psycopg.connect(dsn, password=pw, autocommit=False, options=f"-c search_path={SCHEMA}") as conn:
                cur = conn.cursor()
                cur.execute("SELECT count(*) FROM pg_class")       # the snapshot
                cur.execute("SELECT pg_advisory_xact_lock(742199)")
                time.sleep(1.0)                                     # held a while, as a verify is
                conn.commit()
            done["birth"] = time.monotonic() - t0
        except BaseException as e:                                # noqa: BLE001
            errors.append(e)

    # alpha holds the memory lock and pauses 0.6 s before its migrations — the window: the birth
    # (a snapshot, then the DDL guard) and beta (the same tables) both arrive while it is held
    threads = [threading.Thread(target=life, args=("alpha", 0.0, 0.6)),
               threading.Thread(target=birth, args=(0.15,)),
               threading.Thread(target=life, args=("beta", 0.3))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert not [t for t in threads if t.is_alive()], "a party never finished — the cycle is back"
    assert not errors, [f"{type(e).__name__}: {e}" for e in errors]
    assert set(done) == {"alpha", "beta", "birth"}
    with _conn(dsn, pw) as c:
        rows = c.execute("SELECT count(*) FROM pg_indexes WHERE schemaname = %s AND indexname = 'checkpoints_thread_id_idx'",
                         (SCHEMA,)).fetchone()[0]
        assert rows == 1, "the saver's index stands once"
        held = c.execute("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' AND objid = %s", (resident.MEMORY_LOCK,)).fetchone()[0]
        assert held == 0, "the memory lock is let go"
