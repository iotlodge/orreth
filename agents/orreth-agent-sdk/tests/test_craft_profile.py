# PROVENANCE: Fable 5 (claude-fable-5) — 0050 sp3 · 2026-08-11
"""The supply line learns the persona shelf: a chronicle asset whose profile
IS a template renders exactly like firmware — the tester is craft too."""
from orreth_agent.craft import ResolvedCraft


def test_a_chronicle_template_renders_like_firmware():
    rc = ResolvedCraft({"name": "uat-persona-quinn", "ref": "sha256:x",
                        "version": 3, "lifecycle": "chronicle",
                        "profile": {"template": "hello ⟦who⟧"}})
    assert rc.render(who="quinn") == "hello quinn"


def test_a_dict_profile_without_template_stays_unrenderable():
    rc = ResolvedCraft({"name": "fingertip-default", "ref": "sha256:y",
                        "version": 1, "lifecycle": "chronicle",
                        "profile": {"max_cycles": 3}})
    assert rc.text is None and rc.render() == ""
