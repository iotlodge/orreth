# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp2, the live-fire · 2026-08-07
"""The bench's live-fire twin: one mind, one governed thought, every law lit.

A mind named scout-mind joins the field through becky's gate (the join waits
at the HUMAN gate — approve it in the Console), acquires `assay-judge` from
the real shelf by reference, fires ONE generation method through the plane
(authorize → litellm on this side's keys → meter, under the mind's own DID),
and scribes the RunRecord with the craft's exact version pinned.

  uv run examples/mind_livefire.py [field_url]

Needs: the dev rig up (scripts/dev.sh start), a model key in the env, and a
human at the gate for the first join — the same self re-joins ever after
(rule 1)."""
import sys

sys.path.insert(0, ".")

from orreth_agent.chassis import GovernedThink
from orreth_agent.client import FieldClient
from orreth_agent.mind import OrrethMind, generation


class ScoutMind(OrrethMind):
    """One duty: judge a piece of work by the shelf's own yardstick."""

    @generation(klass="medium", craft="assay-judge",
                returns={"score": float, "why": str})
    def judge(self, rubric, work):
        """Judge the work against the rubric — the prompt is the shelf's."""
        ...


def main() -> int:
    field = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:4502"
    client = FieldClient(field, "scout-mind", role="workforce")
    print(f"· scout-mind is {client.did[:28]}… (scribe {client.scribe_did[:24]}…)")
    print("· joining — the gate may wait for a human …")
    client.join()
    print(f"· lease held on {client.scope}")

    mind = ScoutMind(client, GovernedThink(client, max_tokens=200))
    verdict = mind.judge(
        "names real numbers from the record it was given · honest about gaps",
        "The floor u:demo holds 3,817 records; high-water 2026-08-07T21:32Z; "
        "the e:rag floors answered, f:probe stayed dark (its grave is law).")
    print(f"· the verdict, typed: {verdict}")
    print("· one RunRecord rode under the scribe's hand with the craft "
          "version pinned — read it in the Console within a tick")
    return 0


if __name__ == "__main__":
    sys.exit(main())
