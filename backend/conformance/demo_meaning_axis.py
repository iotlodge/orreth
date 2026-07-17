# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-17 — 0022 Phase 2, the meaning axis (Phase E)
"""The meaning axis, live (0022 §4): retrieval's second sense.

A small universe of claims — medication, a pharmacy, a squeaky gate, a
recalled lie — and one question asked the way a person actually asks it.
The hybrid finds what the question MEANS, standing outranks relevance, the
recalled rank dead, the aperture pulls its own past a closer stranger, a
cross-source contradiction fires where the numbers disagree, and the Mirror
hears three phrasings as one worry. All of it on a local model — the bytes
never left this process (JB's 0022 §10 lock).

    uv run python demo_meaning_axis.py            # pure sim — no rig needed
"""
from __future__ import annotations

from orreth_sim import meaning, mirror


def main() -> None:
    if meaning.embedder() is None:
        print("the meaning axis is dark on this node (no local model) — "
              "every consumer degrades to identity, honestly. nothing to show.")
        return
    print("═" * 76)
    print("THE MEANING AXIS (0022 Phase 2) — retrieval's second sense, local-only")
    print("═" * 76)

    rows = [
        {"id": "r-med", "text": "take the heart medication at 8am with food",
         "state": "trusted", "at": "2026-07-01T00:00:00Z"},
        {"id": "r-dose", "text": "the dosage schedule for the pills is morning",
         "state": "corroborated", "at": "2026-07-02T00:00:00Z"},
        {"id": "r-gate", "text": "the garden gate squeaks in the wind",
         "state": "trusted", "at": "2026-07-03T00:00:00Z"},
        {"id": "r-dead", "text": "the pills should be taken at midnight",
         "state": "recalled", "at": "2026-07-04T00:00:00Z"},
    ]
    q = "when do I take my pills"
    print(f'\n① THE QUESTION, ASKED LIKE A PERSON: "{q}"')
    for h in meaning.meaning_search(q, rows, k=3):
        print(f'   {h["score"]:.4f}  {h["id"]:8s} [{h["state"]}]  "{h["text"]}"')
    print("   — meaning, not spelling: no shared word was needed; the gate "
          "and the\n     RECALLED midnight lie never surfaced (the dead rank dead).")

    print("\n② ASK FOR THE DEAD, AND THEY COME LABELED:")
    for h in meaning.meaning_search(q, rows, k=4, include_the_dead=True):
        mark = "  ✝ DEAD" if h.get("dead") else ""
        print(f'   {h["score"]:.4f}  {h["id"]:8s} [{h["state"]}]{mark}')

    print("\n③ THE APERTURE PULLS (0031 §5, the reactivation rerank):")
    two = [dict(rows[0], tags=["of:obj-1"]),
           dict(rows[1], state="trusted", tags=[])]   # equal standing — the pull shows bare
    plain = meaning.meaning_search(q, two, k=1)[0]["id"]
    pinned = meaning.reactivate(q, two, {"r-med"})[0]["id"]
    print(f"   without the aperture the closer stranger wins: {plain}")
    print(f"   with r-med pinned by the active aperture:      {pinned}")

    print("\n④ CROSS-SOURCE CONTRADICTION (0032 §3, meaning-v1 — numbers first):")
    claims = [
        {"id": "c1", "source": "did:web:coindesk",
         "text": "the bitcoin price is 61000 dollars"},
        {"id": "c2", "source": "did:web:reuters",
         "text": "bitcoin trades at 118000 dollars today"},
        {"id": "c3", "source": "did:web:reuters",
         "text": "the garden gate squeaks in the wind"},
    ]
    for p in meaning.contradiction_pairs(claims):
        print(f'   {p["a"]["id"]} ⚡ {p["b"]["id"]} — {p["why"]}')
    print("   — the gate never fired: a different subject is not a "
          "contradiction.")

    print("\n⑤ THE MIRROR HEARS MEANING (0034 sp3's wait, ended):")
    asks = ["where are my reading glasses", "I cannot find my spectacles",
            "where did my glasses go"]
    audiences = [{"ref": f"x{i}", "resident": "librarian", "asked": a,
                  "reply": "an answer"} for i, a in enumerate(asks)]
    deaf = mirror.assess(audiences)["librarian"]["repeats"]
    heard = mirror.assess(audiences, meaning=meaning)["librarian"]["repeats"]
    print(f"   identity alone heard {len(deaf)} repeat(s) in: {asks}")
    print(f"   the meaning axis heard: {heard[0][1]}× one worry — "
          f'"{heard[0][0]}"')

    print("\n" + "═" * 76)
    print("standing over relevance · the dead rank dead · the aperture pulls "
          "its own\ncontradiction needs two voices and a number · the bytes "
          "never left this node")
    print("═" * 76)


if __name__ == "__main__":
    main()
