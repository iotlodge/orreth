# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""Flavor 2 — the same lifeforce, as an explicit LangGraph StateGraph.

Where Flavor 1 hides the loop inside the Chassis, this draws it as a graph you can
read edge-by-edge: prepare → plan → execute → review, with review routing to replan
(cycles remain), persist (objective met), or park (breaker). Deterministic by default —
the nodes reason with rules, not a model — because JB asked this flavor to be
"quite deterministic": the same inputs trace the same path through the graph every time.

Every node still speaks to the universe through the SDK's FieldClient, so this agent
joins, remembers, and appears in the Console exactly like any other — it just thinks in
a shape you can audit.
"""
from __future__ import annotations

from typing import Callable, TypedDict

from langgraph.graph import END, StateGraph

from orreth_agent import FieldClient


class AgentState(TypedDict, total=False):
    intent: str
    memory: str
    cycle: int
    max_cycles: int
    results: list          # [(skill, question, answer)]
    verdict: str
    done: bool
    answer: str
    missing: str


def build_graph(client: FieldClient, skills: dict, *, persona: str = "",
                max_cycles: int = 3, max_obs: int = 3):
    """Compile a deterministic governed-loop graph bound to one agent on one floor."""

    def prepare(state: AgentState) -> AgentState:
        hits = client.recall(days=365).get("hits", [])[:5]
        mem = "; ".join(f"{h['occurred_at'][:10]} {h.get('fidelity','?')}" for h in hits)
        return {"memory": mem or "(no prior memory)", "cycle": 1, "max_cycles": max_cycles}

    def plan(state: AgentState) -> AgentState:
        # deterministic planner: one observation per available skill (bounded), then reason
        chosen = list(skills)[:max_obs - 1] + ["reason"]
        return {"_plan": chosen} if False else {"results": [("_plan", "", ",".join(chosen))]}

    def execute(state: AgentState) -> AgentState:
        chosen = state["results"][0][2].split(",") if state.get("results") else ["reason"]
        results = []
        for name in chosen:
            if name in skills:
                try:
                    results.append((name, state["intent"], str(skills[name](state["intent"]))))
                except Exception as e:
                    results.append((name, state["intent"], f"(skill error: {e})"))
            else:
                results.append(("reason", state["intent"],
                                f"reasoned over {len(results)} observation(s) toward the objective"))
        return {"results": results}

    def review(state: AgentState) -> AgentState:
        useful = [r for r in state["results"] if "(skill error" not in r[2]]
        done = len(useful) >= 1
        client.diary(state["intent"], cycle=state["cycle"], done=done)
        if done:
            answer = "; ".join(f"{k}: {v}" for k, v, r in
                               [(r[0], r[2], r) for r in useful])[:400]
            return {"done": True, "verdict": "DONE", "answer": answer}
        return {"done": False, "verdict": "RETRY", "missing": "every observation errored"}

    def persist(state: AgentState) -> AgentState:
        client.remember({"objective": state["intent"], "answer": state["answer"]},
                        kind="episodic", tags=["objective", "answered", "langgraph"])
        return {}

    def park(state: AgentState) -> AgentState:
        client.park(state["intent"], state.get("missing", "unresolved"))
        return {}

    def route(state: AgentState) -> str:
        if state.get("done"):
            return "persist"
        if state["cycle"] < state["max_cycles"]:
            return "replan"
        return "park"

    def replan(state: AgentState) -> AgentState:
        return {"cycle": state["cycle"] + 1}

    g = StateGraph(AgentState)
    g.add_node("prepare", prepare)
    g.add_node("plan", plan)
    g.add_node("execute", execute)
    g.add_node("review", review)
    g.add_node("replan", replan)
    g.add_node("persist", persist)
    g.add_node("park", park)

    g.set_entry_point("prepare")
    g.add_edge("prepare", "plan")
    g.add_edge("plan", "execute")
    g.add_edge("execute", "review")
    g.add_conditional_edges("review", route,
                            {"persist": "persist", "replan": "replan", "park": "park"})
    g.add_edge("replan", "plan")
    g.add_edge("persist", END)
    g.add_edge("park", END)
    return g.compile()
