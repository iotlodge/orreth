# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0068 sp4, the rails and the audit · 2026-09-10
"""The rails' laws (0068 §3.3): detectors are firmware, actions ride the
ladder exactly, and NOTHING the rails saw ever leaves as content."""
import json
import sys
import types

from orreth_sim import guardrails, rails
from orreth_sim.model_plane import LiveGateway

CARD = "4111 1111 1111 1111"          # Luhn-valid test number
SSN = "078-05-1120"                   # the famous specimen SSN
GENESIS = guardrails.compose(guardrails.GENESIS_UNIVERSAL)


def test_pci_detector_luhn_checked():
    hits = rails.detect(f"pay with {CARD} today")
    assert len(hits["pci"]) == 1
    # a random long number that fails Luhn is NOT an incident
    assert rails.detect("order 4111 1111 1111 1112 shipped")["pci"] == []
    # dashed form detected too
    assert len(rails.detect("4111-1111-1111-1111")["pci"]) == 1


def test_pii_detector_roster():
    t = f"call 555-867-5309 or mail jo@example.com re {SSN}"
    hits = rails.detect(t)
    assert len(hits["pii"]) == 3


def test_mask_leaving_hides_the_content():
    r = rails.enforce(GENESIS, "leaving", f"the SSN on file is {SSN}.")
    assert SSN not in r["text"] and "[masked: pii]" in r["text"]
    assert not r["refused"] and not r["review"]
    assert r["events"][0]["category"] == "pii"
    assert r["events"][0]["count"] == 1


def test_refuse_both_ways_with_the_reason():
    for direction in ("entering", "leaving"):
        r = rails.enforce(GENESIS, direction, f"charge {CARD} please")
        assert r["refused"] and r["text"] is None
        assert "pci" in r["refusal"]
        assert "payment-card" in r["refusal"]     # the rule's own reason


def test_direction_law_pii_entering_passes_under_genesis():
    # genesis masks PII LEAVING only — the same SSN entering is untouched
    r = rails.enforce(GENESIS, "entering", f"my SSN is {SSN}")
    assert r["text"] == f"my SSN is {SSN}" and r["events"] == []


def test_quarantine_masks_and_stages_review():
    tightened = guardrails.compose({"rules": [
        {"match": {"category": "pii", "direction": "leaving"},
         "action": "quarantine", "reason": "hold PII answers for a human"}]})
    r = rails.enforce(tightened, "leaving", f"record shows {SSN}")
    assert r["review"] and SSN not in r["text"]
    assert "[masked: pii]" in r["text"] and not r["refused"]


def test_annotate_records_without_touching():
    soft = {"rules": [{"match": {"category": "pii", "direction": "leaving"},
                       "action": "annotate", "reason": "count PII sightings"}]}
    r = rails.enforce(soft, "leaving", f"reach me at a@b.co")
    assert r["text"] == "reach me at a@b.co"
    assert r["events"][0]["action"] == "annotate"


def test_refuse_outranks_mask_when_both_hit():
    r = rails.enforce(GENESIS, "leaving", f"{SSN} paid with {CARD}")
    assert r["refused"]                            # pci refuse wins the exchange
    # ...and the audit still shows everything that saw content
    assert {e["category"] for e in r["events"]} == {"pii", "pci"}


def test_events_never_carry_the_matched_content():
    r = rails.enforce(GENESIS, "leaving", f"{SSN} and {CARD} and jo@x.io")
    flat = json.dumps(r["events"])
    for secret in (SSN, "4111", "jo@x.io"):
        assert secret not in flat


def test_pattern_rules_ride_their_craft_list():
    rule = {"rules": [{"match": {"category": "pattern",
                                 "pattern_ref": "codewords",
                                 "direction": "both"},
                       "action": "mask", "reason": "project codewords stay in"}]}
    r = rails.enforce(rule, "entering", "operation NIGHTJAR is live",
                      patterns=lambda ref: [r"NIGHTJAR"] if ref == "codewords" else None)
    assert "NIGHTJAR" not in r["text"] and "[masked: pattern]" in r["text"]
    # an unresolvable list never silently passes — it confesses in the events
    r2 = rails.enforce(rule, "entering", "operation NIGHTJAR is live")
    assert r2["text"] == "operation NIGHTJAR is live"
    assert "unresolved" in r2["events"][0]["reason"]


def _echo_litellm(monkeypatch):
    """A stub model that parrots the last user message — so the leaving
    check has real content to judge, with no wire and no keys."""
    m = types.ModuleType("litellm")

    def completion(model, messages, max_tokens):
        usage = types.SimpleNamespace(total_tokens=12, prompt_tokens=7,
                                      completion_tokens=5)
        msg = types.SimpleNamespace(content=messages[-1]["content"])
        return types.SimpleNamespace(usage=usage,
                                     choices=[types.SimpleNamespace(message=msg)])
    m.completion = completion
    m.completion_cost = lambda completion_response: 0.0
    monkeypatch.setitem(sys.modules, "litellm", m)


def _surface(budget=5000):
    return types.SimpleNamespace(identity={"did": "did:key:zRailTest"},
                                 budget_left=budget)


def test_the_lane_refuses_entering_before_any_budget_burns(monkeypatch):
    """0068 §3.3 — inputs checked BEFORE the call: a PCI hit entering
    refuses the whole exchange, no model is reached, no budget spent."""
    _echo_litellm(monkeypatch)
    gw = LiveGateway(rails=GENESIS)
    s = _surface()
    r = gw.call(s, "low", [{"role": "user", "content": f"charge {CARD}"}])
    assert r["refused"] == "guardrail" and r["tokens"] == 0
    assert s.budget_left == 5000
    assert CARD not in json.dumps(gw.call_log)     # the log carries counts, never content


def test_the_lane_masks_leaving_and_meters_truthfully(monkeypatch):
    """0068 §3.3 — outputs checked before they return: the echo model
    repeats an SSN; the reader sees the mask, the meter sees the real
    spend (the tokens WERE burned — the meter never lies for the rail)."""
    _echo_litellm(monkeypatch)
    gw = LiveGateway(rails=GENESIS)
    s = _surface()
    r = gw.call(s, "low", [{"role": "user", "content": f"repeat: {SSN}"}])
    assert SSN not in r["text"] and "[masked: pii]" in r["text"]
    assert r["tokens"] == 12 and s.budget_left == 5000 - 12
    events = [e for row in gw.call_log for e in row.get("guardrail", [])]
    assert any(e["category"] == "pii" and e["direction"] == "leaving"
               for e in events)


def test_a_railless_gateway_is_unchanged(monkeypatch):
    _echo_litellm(monkeypatch)
    gw = LiveGateway()                             # rails=None — pre-0068 behavior whole
    r = gw.call(_surface(), "low", [{"role": "user", "content": f"repeat: {SSN}"}])
    assert SSN in r["text"]


def test_outcome_is_the_strongest_thing_that_happened():
    assert rails.outcome_of([], []) == "clean"
    m = [{"category": "pii", "action": "mask", "direction": "leaving",
          "count": 1, "reason": "x"}]
    q = [{"category": "pii", "action": "quarantine", "direction": "leaving",
          "count": 2, "reason": "x"}]
    assert rails.outcome_of(m, []) == "masked"
    assert rails.outcome_of(m, q) == "quarantined"
    # a rule that saw nothing (count 0) never colors the outcome
    z = [{"category": "pattern", "action": "annotate", "direction": "entering",
          "count": 0, "reason": "unresolved"}]
    assert rails.outcome_of(z) == "clean"
