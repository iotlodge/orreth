# PROVENANCE: Fable 5 (claude-fable-5) — 0019, the Stable · 2026-07-06
"""The Stable (0019): lifecycle legality, price drift as a rug-pull, EOL as an appointment.

Minds are identities with worldlines: every transition an event, nothing self-attested,
a changed DEAL (pricing/context bytes) deprecated until a human re-approves the new pin,
an announced expiry flipped loud inside the horizon, sunset never served.
"""
import pytest

from orreth_sim.stable import CANARY_BEATS, IllegalTransition, Stable, manifest_hash

SCOPE = "u:demo/e:cloud/f:prod"
SONNET = "anthropic/claude-sonnet-4-6"
DEAL = {"pricing": {"prompt": "0.000003", "completion": "0.000015"},
        "context_length": 200000, "modalities": ["text"]}


def saddle(st: Stable, mid: str = SONNET, klass: str = "medium") -> dict:
    return st.saddle(mid, provider="anthropic", route="litellm-direct",
                     did="did:web:anthropic.com", klass=klass, manifest=DEAL)


def serve(st: Stable, mid: str = SONNET) -> None:
    st.attest(mid, DEAL)
    for _ in range(CANARY_BEATS):
        st.canary_beat(mid)


# ---------------------------------------------------------------- lifecycle & worldline
def test_full_lifecycle_writes_the_worldline():
    st = Stable(SCOPE)
    saddle(st)
    st.attest(SONNET, DEAL)                             # human opened the gate
    assert st.stalls[SONNET]["state"] == "canaried"
    for _ in range(CANARY_BEATS):
        st.canary_beat(SONNET)                          # service is earned, not granted
    assert st.stalls[SONNET]["state"] == "available"
    st.retire(SONNET)
    assert st.stalls[SONNET]["state"] == "sunset"
    assert [e["event"] for e in st.events] == \
        ["saddled", "attested", "available", "retired"]


def test_illegal_moves_are_refused():
    st = Stable(SCOPE)
    saddle(st)
    with pytest.raises(IllegalTransition):
        st._move(SONNET, "available", "cheat")          # candidate cannot skip the gate
    st.retire(SONNET)
    with pytest.raises(IllegalTransition):
        st._move(SONNET, "available", "resurrect")      # sunset is terminal
    with pytest.raises(IllegalTransition):
        saddle(st, "nobody/asked").update() or st._move("ghost", "sunset", "x")


def test_canary_only_counts_on_canary():
    st = Stable(SCOPE)
    saddle(st)
    with pytest.raises(IllegalTransition):
        st.canary_beat(SONNET)                          # not attested yet


# ---------------------------------------------------------------- the rug-pull door
def test_price_drift_walks_the_rug_pull_door():
    st = Stable(SCOPE)
    saddle(st)
    serve(st)
    hiked = dict(DEAL, pricing={"prompt": "0.000004", "completion": "0.000015"})
    out = st.sync(SONNET, hiked)
    assert out["drift"] is True
    assert st.stalls[SONNET]["state"] == "deprecated"   # loud, still resolvable, not silent
    assert st.stalls[SONNET]["manifest_hash"] == manifest_hash(DEAL)   # old pin holds
    assert st.stalls[SONNET]["proposed_hash"] == manifest_hash(hiked)
    st.reapprove(SONNET)                                # human accepts the new deal
    assert st.stalls[SONNET]["state"] == "available"
    assert st.stalls[SONNET]["manifest_hash"] == manifest_hash(hiked)  # re-pinned


def test_clean_sync_is_just_freshness():
    st = Stable(SCOPE)
    saddle(st)
    serve(st)
    out = st.sync(SONNET, dict(DEAL))
    assert out["drift"] is False and st.stalls[SONNET]["state"] == "available"


# ---------------------------------------------------------------- the pasture calendar
def test_eol_inside_horizon_flips_loud_and_outside_does_not():
    st = Stable(SCOPE)
    saddle(st)
    serve(st)
    st.sync(SONNET, dict(DEAL), expires_at="2026-07-21")
    assert st.eol_scan("2026-07-06") and st.stalls[SONNET]["state"] == "deprecated"
    st2 = Stable(SCOPE)
    saddle(st2)
    serve(st2)
    st2.sync(SONNET, dict(DEAL), expires_at="2026-12-01")
    assert st2.eol_scan("2026-07-06") == [] and st2.stalls[SONNET]["state"] == "available"


def test_deprecated_serves_loudly_and_sunset_never():
    st = Stable(SCOPE)
    saddle(st)
    serve(st)
    st.sync(SONNET, dict(DEAL), expires_at="2026-07-21")
    st.eol_scan("2026-07-06")
    assert st.resolve("medium") == {"id": SONNET, "deprecated": True}
    st.retire(SONNET, reason="expired")
    assert st.resolve("medium") is None                 # the retired-model outage, impossible


# ---------------------------------------------------------------- the recommendation
def test_recommendation_prefers_the_stable_then_the_catalog():
    st = Stable(SCOPE)
    saddle(st)
    serve(st)
    saddle(st, "openai/gpt-5", klass="medium")
    st.attest("openai/gpt-5", DEAL)
    for _ in range(CANARY_BEATS):
        st.canary_beat("openai/gpt-5")
    pick = st.recommend(SONNET, catalog=[])
    assert pick == {"id": "openai/gpt-5", "why": "already serving this class",
                    "in_stable": True}


def test_recommendation_ranks_catalog_by_price_then_recency():
    st = Stable(SCOPE)
    saddle(st)
    serve(st)
    catalog = [
        {"id": "cheap/older", "pricing": {"prompt": "0.000003"}, "created": 100},
        {"id": "cheap/newer", "pricing": {"prompt": "0.000003"}, "created": 200},
        {"id": "pricy/new", "pricing": {"prompt": "0.00003"}, "created": 300},
        {"id": "dying/soon", "pricing": {"prompt": "0.000003"}, "created": 400,
         "expires_at": "2026-07-21"},                   # never recommend the next casualty
    ]
    pick = st.recommend(SONNET, catalog)
    assert pick["id"] == "cheap/newer" and pick["in_stable"] is False
