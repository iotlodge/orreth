# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp1, the registry's suite · 2026-09-09
"""Eleven styles as declarations: the menu is law, built derives, the gate
teaches, and no config record ever has amnesia."""
from orreth_sim import variants
from orreth_sim.tournament import ALL_RETRIEVERS


def test_the_locked_menu_stands_whole():
    assert set(variants.MENU) == {
        "naive", "advanced", "hierarchical", "multimodal", "multi-agent",
        "reasoning-first", "memory-augmented", "graph", "hybrid", "hyde",
        "corrective"}, "the charter's eleven, no more, no less"
    assert set(variants.VARIANTS_V1) == set(variants.MENU)


def test_every_declaration_teaches_completely():
    for s, d in variants.VARIANTS_V1.items():
        for key in ("title", "row", "stages", "requires", "cost_class",
                    "delta", "why", "blast", "genesis"):
            assert key in d, f"{s} lacks {key}"
        assert d["stages"] and all(m in variants.MODULES for m in d["stages"]), \
            f"{s}'s stages must compose over the six module boundaries"
        assert d["genesis"], f"{s} must declare its knobs from birth"


def test_built_derives_from_the_standing_rows():
    b = variants.built(ALL_RETRIEVERS)
    assert set(b) == {"naive", "advanced", "multimodal", "multi-agent",
                      "graph", "hybrid"}, \
        "six styles ride flows that breathe today; five await sp4"
    assert variants.built([]) == [], "no rows, nothing built — never a lie"


def test_legacy_names_resolve_and_router_is_not_a_style():
    assert variants.resolve("rerank") == "advanced"
    assert variants.resolve("swarm") == "multi-agent"
    assert variants.resolve("Advanced") == "advanced"
    assert variants.resolve("router") is None, "Auto is a switch, not a style"
    assert variants.resolve("made-up") is None


def test_gate_refuses_an_undeclared_style_naming_the_menu():
    flaw, _ = variants.gate_check("variant-fancy", {"k": 4})
    assert flaw and "variant-hyde" in flaw and "firmware" in flaw


def test_gate_refuses_an_undeclared_knob_naming_the_declared_ones():
    flaw, _ = variants.gate_check("variant-graph", {"k": 4, "turbo": True})
    assert flaw and "hops" in flaw and "blast" in flaw.lower()


def test_gate_refuses_wrong_types_and_negatives_but_lands_canonical():
    flaw, _ = variants.gate_check("variant-naive", {"k": "many"})
    assert flaw and "int" in flaw
    flaw, _ = variants.gate_check("variant-naive", {"k": -1})
    assert flaw and "negative" in flaw
    flaw, clean = variants.gate_check("variant-naive", {"k": "6"})
    assert flaw is None and clean == {"k": 6}, "a clean turn lands canonical"


def test_config_serves_genesis_under_the_head_and_never_widens():
    assert variants.config("hybrid") == {"k": 4, "w_vector": 0.5,
                                         "w_graph": 0.5}
    c = variants.config("hybrid", {"k": 8, "rogue": 1})
    assert c["k"] == 8 and "rogue" not in c, \
        "a head turns declared knobs only — it never invents new ones"


def test_teachings_ride_without_the_numbers():
    t = variants.teachings("corrective")
    assert t["delta"] and t["blast"] and "genesis" not in t
