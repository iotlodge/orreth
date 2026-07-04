"""The Knowledge Loop, live (0014): 'Go gather sourced data on X' — against the real web.

Tavily speaks as an IDENTIFIED source (did:web:tavily.com); everything it says is admitted
QUARANTINED at 0.0000; corroboration promotes with receipts; discrediting recalls the lineage.

    uv run python demo_knowledge_loop.py "your topic"
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from orreth_sim.knowledge import KnowledgeCategory, SourceRegistry
from orreth_sim.world import build

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
TOPIC = sys.argv[1] if len(sys.argv) > 1 else "architecture design strategies for cold climates"


def tavily(query: str, n: int = 3) -> list[dict]:
    req = urllib.request.Request("https://api.tavily.com/search", method="POST",
        data=json.dumps({"api_key": os.environ["TAVILY_API_KEY"],
                         "query": query, "max_results": n}).encode(),
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["results"]


def main() -> None:
    w = build()
    reg = SourceRegistry()
    reg.register("did:web:tavily.com", kind="search-aggregator")
    cat = KnowledgeCategory(w.field_prod, TOPIC, "demo-topic")
    print(f'intent: "Go gather verified and sourced data on {TOPIC}"\n')

    ids = []
    for r in tavily(TOPIC):
        eid = cat.admit(f"{r['title']} — {r['content'][:110]}…",
                        {"did": "did:web:tavily.com", "ref": r["url"]})
        ids.append(eid)
        print(f"  admitted UNTRUSTED (0.0000): {r['title'][:64]}")
        print(f"    source did:web:tavily.com · {r['url'][:70]}")

    v = cat.corroborate(ids[0], receipt_ids=ids[1:2])
    print(f"\ninvestigation: entry 1 corroborated by entry 2 → new version {v[:22]}…")
    states = [(c["state"], c["claim"][:48]) for c in cat.current()]
    for s, c in states:
        print(f"  [{s:>12}] {c}")

    recalled = cat.recall_source("did:web:tavily.com", "demo: source discredited")
    print(f"\nrecall of did:web:tavily.com → {len(recalled)} versions recalled through the lineage")
    print(f"  current view: {sorted({c['state'] for c in cat.current()})}")
    print(f"  history intact: {len(cat.entries())} total versions, nothing rewritten")
    print("\nthe universe saw the web without believing it — and forgot nothing about listening. 🥂")


if __name__ == "__main__":
    main()
