# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp1, the durability boundary (M1) · 2026-09-16
"""M1's fault schedule (canon 0002 · 0005 P1 sp1): state and publish-
intent are inseparable, duplicates cause one effect, gaps refuse to
guess, the backlog refuses by name, and success never depends on the
sink. Every 'crash' is injected deterministically — same deaths, no
processes killed."""
import secrets

import pytest

from orreth_spine import envelope as ev
from orreth_spine import inbox, outbox


@pytest.fixture(scope="session", autouse=True)
def _schema(pg):
    outbox.ensure_schema(pg)
    inbox.ensure_schema(pg)
    with pg.transaction():
        pg.cursor().execute(
            "CREATE TABLE IF NOT EXISTS spine_counter ("
            " aggregate_id text PRIMARY KEY, value int NOT NULL DEFAULT 0)")


def _env(seq=None, aid="c1"):
    return ev.make_envelope(
        kind="event", type="orreth.counter.incremented.v1",
        universe_id="u:dev", scope_path="u:dev",
        payload={"ref": "r", "hash": "sha256:x"},
        aggregate={"type": "counter", "id": aid, "sequence": seq}
        if seq is not None else None)


def _fresh(pg, aid):
    with pg.transaction():
        pg.cursor().execute(
            "INSERT INTO spine_counter (aggregate_id) VALUES (%s)"
            " ON CONFLICT DO NOTHING", (aid,))


def _value(pg, aid):
    cur = pg.cursor()
    cur.execute("SELECT value FROM spine_counter WHERE aggregate_id=%s", (aid,))
    return cur.fetchone()[0]


def _bump(aid):
    def effect(cur):
        cur.execute("UPDATE spine_counter SET value = value + 1"
                    " WHERE aggregate_id = %s", (aid,))
    return effect


# ---- the write side: state and event are one fate --------------------------------

def test_committed_state_always_carries_its_event(pg):
    """Fault 2: a crash after commit loses nothing — both rows are already
    down, atomically."""
    env = _env()
    raw = ev.encode(env)
    aid = "atomic-" + secrets.token_hex(4)
    _fresh(pg, aid)
    outbox.commit_with_outbox(pg, raw, env["message_id"], _bump(aid))
    assert _value(pg, aid) == 1
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE message_id=%s",
                (env["message_id"],))
    assert bytes(cur.fetchone()[0]) == raw


def test_rolled_back_state_never_emits(pg):
    """Fault 1: the writer dies mid-transaction — no state, no event,
    no phantom."""
    env = _env()
    aid = "rollback-" + secrets.token_hex(4)
    _fresh(pg, aid)

    def dying(cur):
        _bump(aid)(cur)
        raise RuntimeError("writer killed before commit (injected)")

    with pytest.raises(RuntimeError):
        outbox.commit_with_outbox(pg, ev.encode(env), env["message_id"], dying)
    assert _value(pg, aid) == 0
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_outbox WHERE message_id=%s",
                (env["message_id"],))
    assert cur.fetchone()[0] == 0


def test_success_never_depends_on_the_sink(pg):
    """The broker being down cannot fail a write: the commit succeeds and
    the lag meter reports the pending truth."""
    env = _env()
    outbox.commit_with_outbox(pg, ev.encode(env), env["message_id"])
    lag = outbox.outbox_lag(pg)
    assert lag["pending"] >= 1 and lag["oldest_age_s"] is not None


# ---- the relay: at-least-once, honestly ------------------------------------------

def test_relay_death_before_publish_retries(pg):
    """Fault 3: the sink refuses — the row stays unpublished with its
    attempt counted, and a later relay delivers it exactly as written."""
    outbox.drain(pg, outbox.MemorySink())          # clean slate
    env = _env()
    outbox.commit_with_outbox(pg, ev.encode(env), env["message_id"])
    sink = outbox.MemorySink(fail_before=1)
    out = outbox.relay_once(pg, sink)
    assert out["published"] == 0 and outbox.outbox_lag(pg)["pending"] == 1
    out = outbox.relay_once(pg, sink)              # sink healed
    assert out["published"] == 1
    assert sink.published[0] == (env["message_id"], ev.encode(env))


def test_relay_death_after_publish_duplicates_harmlessly(pg):
    """Fault 4 + 5: crash between publish and mark ⇒ the same message is
    published again — and the inbox absorbs the duplicate into ONE
    effect."""
    outbox.drain(pg, outbox.MemorySink())
    env = _env()
    outbox.commit_with_outbox(pg, ev.encode(env), env["message_id"])
    sink = outbox.MemorySink(fail_after=1)
    outbox.relay_once(pg, sink)                    # published, mark lost
    assert outbox.outbox_lag(pg)["pending"] == 1
    outbox.relay_once(pg, sink)                    # published AGAIN
    dup_ids = [m for m, _ in sink.published]
    assert dup_ids.count(env["message_id"]) == 2   # the wire truly duplicated
    aid = "relaydup-" + secrets.token_hex(4)
    _fresh(pg, aid)
    consumer = "c-" + secrets.token_hex(4)
    for m, _body in sink.published:
        inbox.apply_once(pg, consumer, m, _bump(aid))
    assert _value(pg, aid) == 1                    # one effect, ever


# ---- the inbox: effects are once, order is law -----------------------------------

def test_five_deliveries_one_effect(pg):
    """Fault 5: deliver 5 times — the counter moves once, the duplicate
    meter confesses 4."""
    env = _env()
    aid = "dup-" + secrets.token_hex(4)
    _fresh(pg, aid)
    consumer = "c-" + secrets.token_hex(4)
    results = [inbox.apply_once(pg, consumer, env["message_id"], _bump(aid))
               for _ in range(5)]
    assert results == ["applied"] + ["duplicate"] * 4
    assert _value(pg, aid) == 1
    assert inbox.duplicates_seen(pg, consumer) == 4


def test_failed_effect_rolls_back_its_footprint(pg):
    """A dying effect leaves no inbox footprint — the redelivery retries
    clean and succeeds."""
    env = _env()
    aid = "retry-" + secrets.token_hex(4)
    _fresh(pg, aid)
    consumer = "c-" + secrets.token_hex(4)

    def dying(cur):
        raise RuntimeError("consumer killed mid-effect (injected)")

    with pytest.raises(RuntimeError):
        inbox.apply_once(pg, consumer, env["message_id"], dying)
    assert inbox.apply_once(
        pg, consumer, env["message_id"], _bump(aid)) == "applied"
    assert _value(pg, aid) == 1


def test_reorder_gap_refuses_then_recovers(pg):
    """Fault 6: sequence 3 arrives before 2 — the gap refuses to guess;
    once 2 lands, 3 applies, and the aggregate ends exactly right."""
    aid = "order-" + secrets.token_hex(4)
    _fresh(pg, aid)
    consumer = "c-" + secrets.token_hex(4)
    e1, e2, e3 = _env(1, aid), _env(2, aid), _env(3, aid)
    assert inbox.apply_event(pg, consumer, e1, _bump(aid)) == "applied"
    with pytest.raises(inbox.GapDetected) as gap:
        inbox.apply_event(pg, consumer, e3, _bump(aid))
    assert gap.value.expected == 2 and gap.value.got == 3
    assert _value(pg, aid) == 1                    # nothing guessed
    assert inbox.apply_event(pg, consumer, e2, _bump(aid)) == "applied"
    assert inbox.apply_event(pg, consumer, e3, _bump(aid)) == "applied"
    assert _value(pg, aid) == 3


def test_stale_sequence_is_recorded_and_skipped(pg):
    """An older truth can never overwrite a newer one: a replayed earlier
    sequence reports stale and moves nothing."""
    aid = "stale-" + secrets.token_hex(4)
    _fresh(pg, aid)
    consumer = "c-" + secrets.token_hex(4)
    e1, e2 = _env(1, aid), _env(2, aid)
    inbox.apply_event(pg, consumer, e1, _bump(aid))
    inbox.apply_event(pg, consumer, e2, _bump(aid))
    assert inbox.apply_event(pg, consumer, _env(1, aid), _bump(aid)) == "stale"
    assert _value(pg, aid) == 2


# ---- the budget: backpressure by name --------------------------------------------

def test_outbox_budget_refuses_by_name_then_relents(pg):
    """Fault 7: the backlog at budget refuses new writes with the numbers
    in the refusal; publishing drains the backlog and the write lands."""
    outbox.drain(pg, outbox.MemorySink())
    for _ in range(3):
        e = _env()
        outbox.commit_with_outbox(pg, ev.encode(e), e["message_id"])
    blocked = _env()
    with pytest.raises(outbox.OutboxBudgetExceeded, match="3 unpublished"):
        outbox.commit_with_outbox(pg, ev.encode(blocked),
                                  blocked["message_id"], budget=3)
    assert outbox.drain(pg, outbox.MemorySink()) == 3
    outbox.commit_with_outbox(pg, ev.encode(blocked),
                              blocked["message_id"], budget=3)
    assert outbox.outbox_lag(pg)["pending"] == 1
