# /// script
# requires-python = ">=3.11"
# dependencies = ["langgraph", "cryptography"]
# ///
# PROVENANCE: Fable 5 (claude-fable-5) — 0045 sp5, the supply line · 2026-08-03
"""A REAL LangGraph flow on Orreth's supply line (0045 law 8).

The flow keeps its own deterministic shape — a plain StateGraph — but where
it would have embedded a prompt string, it ACQUIRES the prompt from the
universe's registry by reference. What it inherits for free: version
control, the one law of change, arm visibility if an argument is running,
and a run record that names the exact word that drove it.

The citizen rider: the DID persists across runs (a self, not a mayfly)."""
import json
import os
import sys
import uuid
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orreth_agent.craft import acquire  # noqa: E402

from langgraph.graph import END, START, StateGraph  # noqa: E402

# a consumer is a citizen: the DID survives the process (the F1 lesson)
_seed = Path(os.path.expanduser("~/.orreth/craft-cache/citizen.did"))
_seed.parent.mkdir(parents=True, exist_ok=True)
if not _seed.exists():
    _seed.write_text("did:demo:langgraph-" + uuid.uuid4().hex[:12])
CITIZEN = _seed.read_text().strip()


class RunState(TypedDict, total=False):
    craft: object
    verdict_prompt: str
    report: str


def resolve_craft(state: RunState) -> RunState:
    # ONE resolution, carried through the run — the version cannot move
    # under the later nodes' feet (law 8's run-coherence rider)
    c = acquire("assay-judge", did=CITIZEN, on_dark="stale")
    return {"craft": c}


def compose_verdict_request(state: RunState) -> RunState:
    c = state["craft"]
    prompt = c.render(rubric="cite at least three sources",
                      work='{"answer": "the demo work under judgment"}')
    return {"verdict_prompt": prompt}


def report(state: RunState) -> RunState:
    c = state["craft"]
    rec = {"flow": "langgraph-supply-line-demo", "citizen": CITIZEN,
           "craft": c.name, "version": c.version, "ref": c.ref,
           "arm": c.arm, "stale": c.stale,
           "prompt_chars": len(state["verdict_prompt"])}
    return {"report": json.dumps(rec, indent=1)}


g = StateGraph(RunState)
g.add_node("resolve", resolve_craft)
g.add_node("compose", compose_verdict_request)
g.add_node("report", report)
g.add_edge(START, "resolve")
g.add_edge("resolve", "compose")
g.add_edge("compose", "report")
g.add_edge("report", END)

if __name__ == "__main__":
    out = g.compile().invoke({})
    print("THE RUN'S RECORD NAMES ITS WORD:")
    print(out["report"])
