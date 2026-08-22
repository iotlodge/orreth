# PROVENANCE: Fable 5 (claude-fable-5) — the lease learns to renew · 2026-08-22
"""The fuel judgment, suite-held: which lease is drained, what the card says,
and the one-card-per-window key. The plane's refill law lives in orrethd's own
tests (model.rs); this suite holds the watch that makes the silence loud."""
from orreth_sim import fuel


def _row(remaining, renew_days=1.0, window="2026-08-22T00:00:00Z",
         subject="did:key:zvera", tokens=49581):
    return {"subject": subject, "tokens": tokens, "usd": 0.1, "calls": 12,
            "remaining": remaining,
            "fuel": {"allowance": 50000, "renew_days": renew_days,
                     "window_started": window,
                     "renews_at": "2026-08-23T00:00:00Z" if renew_days else None}}


def test_a_fueled_lease_is_quiet():
    assert fuel.posture(_row(50000)) == "fueled"
    assert fuel.drain_cards([_row(50000)]) == []


def test_the_est_floor_is_the_drain_line():
    # 419 of 50k was the wound: positive dust that cannot clear one thought
    assert fuel.posture(_row(fuel.EST_FLOOR)) == "fueled"
    assert fuel.posture(_row(fuel.EST_FLOOR - 1)) == "drained"
    assert fuel.posture(_row(419)) == "drained"


def test_a_drained_window_names_its_turn():
    cards = fuel.drain_cards([_row(0)], names={"did:key:zvera": "vera"})
    assert len(cards) == 1
    c = cards[0]
    assert c["posture"] == "drained"
    assert "vera" in c["text"]
    assert "2026-08-23T00:00:00Z" in c["text"]   # the human sees WHEN it self-heals
    assert c["action"] == "replenish"


def test_the_lump_confesses_forever():
    c = fuel.drain_cards([_row(0, renew_days=0)])[0]
    assert c["posture"] == "lump-dry"
    assert "until a human word" in c["text"]


def test_unknown_fuel_never_cards():
    # a subject the ledger has never seen has nothing to confess
    assert fuel.posture({"subject": "did:key:znew", "remaining": None}) == "unknown"
    assert fuel.drain_cards([{"subject": "did:key:znew", "remaining": None}]) == []


def test_a_turned_window_is_already_healed():
    # the plane renews lazily at the next debit — a past renews_at means the
    # next ask refills, so there is NOTHING to card (found live 2026-08-22:
    # a 30s proof window drew fresh cards for a subject one ask from whole)
    row = _row(100)
    assert fuel.posture(row, now="2026-08-24T00:00:00Z") == "fueled"
    assert fuel.drain_cards([row], now="2026-08-24T00:00:00Z") == []
    # mid-window the drain still cards
    assert fuel.posture(row, now="2026-08-22T12:00:00Z") == "drained"


def test_the_window_is_the_dedup_key():
    # a new window's early drain is NEW news — the card key must move with it
    a = fuel.drain_cards([_row(0, window="2026-08-22T00:00:00Z")])[0]
    b = fuel.drain_cards([_row(0, window="2026-08-23T00:00:00Z")])[0]
    assert a["window"] != b["window"]
    assert (a["kind"], a["did"]) == (b["kind"], b["did"])
