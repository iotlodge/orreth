"""LiteLLM through the floors, live (0016): the first REAL model call governed end to end.

An agent joins through the gateway (leased budget), the ladder resolves its class to a real
model, LiteLLM routes it, the meter charges actual tokens — and the lifecycle proves that a
sunset model can never be reached. Requires ANTHROPIC_API_KEY in ../../.env (never committed).

    uv run python demo_model_plane.py
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from orreth_sim import rollup
from orreth_sim.agent_surface import BudgetExceeded, join_workforce
from orreth_sim.model_plane import LiveGateway, ModelSunset
from orreth_sim.world import build

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def main() -> None:
    w = build()
    b_prod = w.beckys["u:demo/e:cloud/f:prod"]
    agent = join_workforce(w.field_prod, b_prod, budget_tokens=5000)
    gw = LiveGateway()
    print(f"agent {agent.identity['did'][:34]}… · lease budget {agent.budget_left} tokens")

    # ---- the first governed live call: class-resolved, budget-gated, metered ------------
    r = gw.call(agent, "low", [{"role": "user",
        "content": "In one sentence: what does it mean for memory to outlive its process?"}])
    print(f"\n[{r['class']} → {r['model']}]")
    print(f"  {r['text'].strip()}")
    print(f"  metered: {r['tokens']} tokens (${r['usd']}) · budget left {agent.budget_left}")

    # ---- usage rolls up like everything else (0005) --------------------------------------
    run = {"outcome": "success", "cost": {"tokens": r["tokens"], "model_calls": 1,
                                          "usd": r["usd"]},
           "scores": [{"objective": "reliability", "score": 1.0}]}
    bundle = rollup.merge(rollup.empty_bundle(), rollup.bundle_of(run))
    print(f"  rolled up: cost={bundle['cost']} — the universe's usage view is a standings query")

    # ---- the lifecycle: a sunset model is unreachable, the class re-routes ---------------
    gw.set_state("anthropic/claude-haiku-4-5-20251001", "sunset")
    fallback = gw.resolve("low")
    print(f"\nsunset the primary → class 'low' now resolves to: {fallback}")
    gw.set_state("openai/gpt-4o-mini", "sunset")
    try:
        gw.resolve("low")
    except ModelSunset as e:
        print(f"whole class dead → refused loudly: {e}")

    # ---- pins still hold: an unaffordable pinned class fails, never silently dumber ------
    agent.budget_left = 10
    try:
        gw.call(agent, "xhigh", [{"role": "user", "content": "hi"}], pinned=True)
    except BudgetExceeded as e:
        print(f"pinned xhigh on 10 tokens → {e}")

    print("\nthe door to real minds is governed: config falls, misses climb, usage rises. 🥂")


if __name__ == "__main__":
    main()
