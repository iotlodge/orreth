# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0072 sp1, the grammar grows · 2026-09-11
"""One Place's first laws (0072 §3.1): the capability brings a DECLARATION,
never code; its selector can never drift from the ask door's one menu; and
the declared rooms are exactly the kinds the vocabulary release named."""
import ast
import pathlib

from orreth_sim import variants

GENESIS = (pathlib.Path(__file__).resolve().parents[3]
           / "capabilities" / "e-rag" / "genesis.py")


def _manifest():
    """Pure-data loading: literals, plus names bound to earlier literals —
    a reference to data is still data; a call or import would refuse."""
    tree = ast.parse(GENESIS.read_text())
    out = {}

    def ev(node):
        if isinstance(node, ast.Name):
            return out[node.id]
        if isinstance(node, ast.Dict):
            return {ev(k): ev(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, (ast.List, ast.Tuple)):
            return [ev(x) for x in node.elts]
        return ast.literal_eval(node)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    out[tgt.id] = ev(node.value)
    return out


def test_the_declaration_is_data_never_code():
    """The L1 law, mechanical: the genesis is loadable as PURE LITERALS —
    no call, no import the glass could ever be asked to run."""
    m = _manifest()
    assert m["MANIFEST"]["key"] == "e-rag"
    assert m["CRAFT"] == {}


def test_the_selector_never_drifts_from_the_one_menu():
    m = _manifest()
    chat = next(p for p in m["MANIFEST"]["view"] if p["kind"] == "chat")
    assert chat["selector"] == ["auto"] + list(variants.MENU)


def test_the_rooms_are_the_released_kinds():
    m = _manifest()
    kinds = [p["kind"] for p in m["MANIFEST"]["view"]]
    assert kinds == ["chat", "sources"]
    assert all(p.get("label") for p in m["MANIFEST"]["view"])
