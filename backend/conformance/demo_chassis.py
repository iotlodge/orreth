"""Orreth.agent lives (0015): one chassis, cognition through the governed door, knowledge
from the 0014 loop — deterministic and LLM observations IN PARALLEL, then the verdict.

    uv run python demo_chassis.py
"""
from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv

from orreth_sim.agent_surface import join_workforce
from orreth_sim.chassis import Chassis
from orreth_sim.knowledge import KnowledgeCategory, SourceRegistry
from orreth_sim.model_plane import LiveGateway
from orreth_sim.world import build

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def main() -> None:
    w = build()
    b_prod = w.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(w.field_prod, b_prod, budget_tokens=6000)
    gw = LiveGateway()

    # the 0014 loop seeds what the universe already learned (corroborated knowledge)
    reg = SourceRegistry(); reg.register("did:web:example-standards.org", kind="feed")
    kb = KnowledgeCategory(w.field_prod, "cold-weather building", "cold-kb")
    e1 = kb.admit("heat-pump COP falls below 2.0 under -25C; plan supplemental heat",
                  {"did": "did:web:example-standards.org"})
    e2 = kb.admit("triple-pane low-e glazing cuts envelope loss ~45% vs double",
                  {"did": "did:web:example-standards.org"})
    kb.corroborate(e1, [e2])

    def lookup(question: str) -> str:
        claims = [c["claim"] for c in kb.current() if c["state"] != "recalled"]
        return " | ".join(claims) or "no corroborated knowledge held"

    def think(klass: str, prompt: str) -> str:
        return gw.call(surf, klass, [{"role": "user", "content": prompt}],
                       max_tokens=160)["text"]

    agent = Chassis(surf, think,
                    persona="You are frost, a meticulous cold-climate architect. Be terse.",
                    skills={"lookup": lookup})
    out = agent.run("Give a client the two highest-leverage envelope decisions "
                    "for a home in Leadville, Colorado.")

    print(f"status: {out['status']} in {out['cycles']} cycle(s)")
    print(f"answer: {out['answer']}\n")
    for t in agent.trace:
        print(f"  cycle {t['cycle']}: {t['observations']} parallel observations → {t['verdict']}")
    spent = sum(m.get("tokens", 0) for m in gw.call_log)
    usd = sum(m.get("usd", 0) for m in gw.call_log)
    print(f"  metered: {spent} tokens (${round(usd,5)}) · budget left {surf.budget_left}")
    print(f"  knowledge consulted deterministically: {len(kb.current())} corroborated claims, $0")
    print("\none chassis, one costume, two kinds of thought — every step on the record. 🥂")


if __name__ == "__main__":
    main()
