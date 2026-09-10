# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0068 sp1, the grammar's suite · 2026-09-09
"""Every rule says why, the lattice only tightens, absence never removes,
an empty set is legal-but-loud, and the version moves when any rule does."""
from orreth_sim import guardrails as gr


def _rule(cat="pii", direction="leaving", action="mask", reason="why"):
    return {"match": {"category": cat, "direction": direction},
            "action": action, "reason": reason}


def test_the_shape_law_refuses_with_teachings():
    flaw, _ = gr.gate_check("guardrail-universal", {"rules": [
        {"match": {"category": "dreams", "direction": "leaving"},
         "action": "mask", "reason": "x"}]})
    assert flaw and "unknown category" in flaw
    flaw, _ = gr.gate_check("guardrail-universal", {"rules": [
        _rule(action="obliterate")]})
    assert flaw and "ladder" in flaw
    flaw, _ = gr.gate_check("guardrail-universal", {"rules": [
        _rule(reason="  ")]})
    assert flaw and "WHY" in flaw
    flaw, _ = gr.gate_check("guardrail-universal", {"rules": [
        {"match": {"category": "pattern", "direction": "both"},
         "action": "refuse", "reason": "x"}]})
    assert flaw and "pattern_ref" in flaw


def test_an_empty_set_is_legal_explicit_and_scary():
    flaw, clean = gr.gate_check("guardrail-universal", {"rules": []})
    assert flaw is None and clean == {"rules": []}
    assert "scary" in gr.teachings("guardrail-universal")["empty"]


def test_a_clean_set_lands_canonical():
    flaw, clean = gr.gate_check("guardrail-x", {"rules": [
        {"match": {"category": "pci", "direction": "both", "junk": 1},
         "action": "refuse", "reason": "  cards never ride  ", "extra": 2}]})
    assert flaw is None
    assert clean["rules"][0] == {"match": {"category": "pci",
                                           "direction": "both"},
                                 "action": "refuse",
                                 "reason": "cards never ride"}


def test_the_lattice_add_widen_strengthen_are_lawful():
    uni = {"rules": [_rule("pii", "leaving", "mask", "u")]}
    cap = {"rules": [_rule("pii", "both", "refuse", "c"),
                     _rule("pci", "both", "refuse", "new rail")]}
    assert gr.monotone_flaws(uni, cap) == []
    comp = gr.compose(uni, cap)
    pii = next(r for r in comp["rules"] if r["match"]["category"] == "pii")
    assert pii["action"] == "refuse" and pii["match"]["direction"] == "both", \
        "the strengthening and widening took"
    assert len(comp["rules"]) == 2, "the addition joined"


def test_weakening_and_narrowing_refuse_with_the_teaching():
    uni = {"rules": [_rule("pci", "both", "refuse", "u")]}
    weak = {"rules": [_rule("pci", "both", "mask", "c")]}
    flaws = gr.monotone_flaws(uni, weak)
    assert flaws and "never loosens" in flaws[0]
    narrow = {"rules": [_rule("pci", "leaving", "refuse", "c")]}
    flaws = gr.monotone_flaws(uni, narrow)
    assert flaws and "narrow" in flaws[0]


def test_absence_never_removes():
    uni = {"rules": [_rule("pii", "leaving", "mask", "u")]}
    assert gr.monotone_flaws(uni, {"rules": []}) == [], \
        "an empty capability set is lawful — it removes nothing"
    comp = gr.compose(uni, {"rules": []})
    assert len(comp["rules"]) == 1, "the universal rule rides regardless"


def test_the_version_moves_with_any_rule_and_only_then():
    uni = {"rules": [_rule("pii", "leaving", "mask", "u")]}
    a = gr.set_version(gr.compose(uni))
    b = gr.set_version(gr.compose(uni))
    assert a == b and a.startswith("gr-")
    c = gr.set_version(gr.compose(
        {"rules": [_rule("pii", "leaving", "refuse", "u")]}))
    assert c != a, "a changed rule is a changed version — every cached " \
                   "answer revalidates by construction (the 0071 seam)"


def test_the_first_rails_stand_in_genesis():
    flaw, clean = gr.gate_check("guardrail-universal", gr.GENESIS_UNIVERSAL)
    assert flaw is None and len(clean["rules"]) == 2
    cats = {r["match"]["category"]: r["action"] for r in clean["rules"]}
    assert cats == {"pii": "mask", "pci": "refuse"}, \
        "PII masked, PCI refused — the charter's own first rails"
