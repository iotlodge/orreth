# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch canon 0008, the conformance suite's first fixture · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel): watch · stop_demand · absent_words · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp2 (glass): address · offer · citation_name · 2026-09-21
"""The conformance suite (canon 0008): language-neutral fixtures the
Python reference must pass today and `orrethd` must pass in Phase 7 — the
same files, unchanged. A fixture the reference fails is a wound."""
import json
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, export, intent, mitl, monitor, placement, proof

ROOT = Path(__file__).resolve().parents[1] / "conformance"
FIXTURES = sorted(ROOT.glob("*-v*.json"))


def _cases():
    for f in FIXTURES:
        doc = json.loads(f.read_text("ascii"))
        for c in doc["cases"]:
            yield pytest.param(doc["contract"], c, id=f"{f.stem}::{c['name']}")


def test_the_suite_has_fixtures():
    assert FIXTURES, "spine/conformance holds no fixtures — the law says every wire change adds one"


@pytest.mark.parametrize("contract,case", list(_cases()))
def test_fixture(contract, case):
    kind, inp, exp = case["kind"], case["input"], case["expect"]
    if kind == "canonical":
        got = ev.canonical(inp["obj"])
        assert got.decode("ascii") == exp["bytes"]
        assert ev.content_hash(inp["obj"]) == exp["hash"]
    elif kind == "encode":
        assert ev.encode(inp["env"]).decode("ascii") == exp["bytes"]
        assert ev.decode(ev.encode(inp["env"])) == inp["env"]
    elif kind == "encode_refuses":
        with pytest.raises(ValueError) as e:
            ev.encode(inp["env"])
        for name in exp["names"]:
            assert name in str(e.value), f"refusal must name {name!r}: {e.value}"
    elif kind == "decode_preserves":
        assert ev.decode(inp["bytes"].encode("ascii")) == exp["obj"]
    # ---- orreth.proof/1 (P6 sp1): the code, the ladder, the level a class demands ----
    elif kind == "totp":
        assert proof.totp(inp["secret"], inp["time"]) == exp["code"]
    elif kind == "totp_verify":
        assert [proof.verify(inp["secret"], inp["code"], t) for t in inp["at"]] == exp["ok"]
    elif kind == "ladder":
        got = sorted(inp["order"], key=proof.rank)
        assert got == exp["sorted"]
        assert [proof.LEVEL_OF_CLASS[c] for c in got] == exp["levels"]
    elif kind == "class_level":
        assert proof.level_for(inp["class"], master=bool(inp.get("master"))) == exp["level"]
    elif kind == "stop_demand":                  # W5: what the stop of an intention demands
        assert intent.stop_demand(inp["intention_kind"]) == exp
    # ---- orreth.watch/1 (W14): the sense of a watch — red WHEN the condition holds ----
    elif kind == "watch_judge":
        red = monitor.judge_one(inp["op"], inp["value"], inp["threshold"])
        assert (red, "red" if red else "green") == (exp["red"], exp["state"])
    elif kind == "watch_reads":
        assert monitor.reads(inp) == exp["reads"]
    # ---- orreth.ask/1 (W19): the door's refusal for a body that is not here ----
    elif kind == "address":                      # W7: a name at the head selects that body
        assert dispatch.address(inp["text"], inp["names"]) == exp["name"]
    elif kind == "offer":                        # walk #7: the monitor's offer, read from its words
        assert monitor.offer_in(inp["reply"]) == exp["offer"]
    elif kind == "citation_name":                # W15: a citation in a human's name
        assert mitl.citation_name(inp["path"], inp["heading"], inp["rule"]) == exp["name"]
    elif kind == "absent_words":
        assert dispatch.refusal_words(inp["name"], inp["reason"]) == exp["reply"]
    # ---- orreth.compliance/1 (P6 sp2): the hash chain, the chain's status, the verifier ----
    elif kind == "hash_chain":
        got = export.hash_chain(inp["rows"])
        assert got == exp["hashes"]
        assert (got[-1] if got else None) == exp["root_hash"]
    elif kind == "chain_status":
        assert [export.chain_status(r) for r in inp["rows"]] == exp["status"]
    elif kind == "verify":
        assert export.verify(inp["bundle"]) is exp["bundle"]
        assert export.verify(inp["truncated"]) is exp["truncated"]
        assert export.verify(inp["resealed"]) is exp["resealed"]
        assert inp["resealed"]["summary"]["chain_broken"] == exp["resealed_chain_broken"]
    # ---- orreth.impact/1 (P6 sp3): the verdict ladder — rules, never a brain ----
    elif kind == "verdict":
        assert mitl.verdict(inp["touches"]) == exp["verdict"]
    # ---- orreth.placement/1 (P6 sp4): the profile's defaults, the honor rule and its reasons ----
    elif kind == "profile":
        got = placement.profile(inp["template"])
        assert got == exp["profile"]
        assert ev.canonical(got).decode("ascii") == exp["bytes"]
    elif kind == "honor":
        ok, reasons = placement.honor(inp["profile"], inp["ground"])
        assert (ok, reasons) == (exp["honored"], exp["reasons"])
        assert placement.why_here(inp["profile"], inp["ground"]) == exp["why"]
    else:
        pytest.fail(f"unknown case kind {kind!r} in {contract}")
