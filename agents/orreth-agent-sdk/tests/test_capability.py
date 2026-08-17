# PROVENANCE: Fable 5 (claude-fable-5) — 0055 · 2026-08-13
from orreth_agent.capability import manifest, PANEL_KINDS
import pytest


def test_manifest_builds_and_guards():
    m = manifest(key="x", name="X", emoji="✦", resident="r", floor="u:demo",
                 port=4520, law="reports only", group="g",
                 view=[{"kind": "markdown", "src": "md"}])
    assert m["door"] == "x" and m["group"] == "g"
    with pytest.raises(ValueError):
        manifest(key="x", name="X", emoji="✦", resident="r", floor="u:demo",
                 port=1, law="l", view=[{"kind": "iframe"}])
    assert "table" in PANEL_KINDS and "flow" in PANEL_KINDS \
        and "reports" in PANEL_KINDS and len(PANEL_KINDS) == 13
