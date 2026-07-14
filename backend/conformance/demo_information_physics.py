# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0033, the Physics of Memory
"""The physics of memory, live (0033): entropy is a dial, not a decay.

Two worlds watch the same 400 days of observations age. The mortal world — logs
without provenance — loses a link forever every time a horizon passes: its
reconstruction entropy is a staircase that only climbs. The Orreth world distills
under contract and tombstones on schedule: bytes leave, stubs remain, and the
uncertainty of reconstructing any moment stays BOUNDED — set by governance,
proven by the walk. Then the rest of the harness reads the same log: the
pyramid's compression ratio, provenance completeness, voices vs echoes, and
restraint as a number.

    uv run python demo_information_physics.py          # pure sim — no rig needed
"""
from __future__ import annotations

from orreth_sim import crypto, infotheory as it
from orreth_sim.knowledge import KnowledgeCategory
from orreth_sim.node import make_memory
from orreth_sim.world import build

AGES = [7.0, 30.0, 90.0, 180.0, 400.0]        # how old each observation is "today"
FIELD_HORIZON = 90.0                          # the mortal world's log retention


def main() -> None:
    world = build()
    f = world.field_prod

    print("═" * 76)
    print("  THE PHYSICS OF MEMORY — reconstruction entropy, two worlds, one history")
    print("═" * 76)

    # one history: five observations, distilled at the field (0003's metabolism)
    ids = []
    for i, age in enumerate(AGES):
        rid = f.write(make_memory(f.steward, f.steward_kp, f.scope,
                                  {"observation": f"reading {i} — verbose detail " * 6,
                                   "age_days": age},
                                  kind="episodic", tags=["physics-demo"]))
        ids.append(rid)
    dist = f._distill(ids, push=False)
    print(f"\n  five observations distilled under contract → {dist['id'][:22]}…")

    # time passes: every raw older than the horizon leaves — but leaves a STUB
    print(f"\n  the schedule fires at {FIELD_HORIZON:.0f} days: bytes leave, stubs stay\n")
    print(f"  {'age of oldest link':>20} │ {'mortal world (bits)':>20} │ {'orreth (bits)':>14}")
    print(f"  {'─' * 20}─┼─{'─' * 20}─┼─{'─' * 14}")
    dropped = set()
    for horizon_now in AGES:
        for rid, age in zip(ids, AGES):
            if age <= horizon_now and age > FIELD_HORIZON and rid not in dropped:
                f.tombstone(rid, by=f.steward["did"], reason="retention schedule")
                dropped.add(rid)
        aged = [a for a in AGES if a <= horizon_now]
        mortal = it.mortal_reconstruction_entropy(aged, retention_days=FIELD_HORIZON)
        orreth = it.reconstruction_entropy(f, dist["id"])["bits"]
        # the mortal staircase climbs without bound; orreth holds at the contract
        print(f"  {horizon_now:>17.0f} d │ {mortal:>20.1f} │ {orreth:>14.1f}")

    r = it.reconstruction_entropy(f, dist["id"])
    print(f"\n  the walk, itemized: {r['live']} live · {r['stubs']} stubs "
          f"(≤ {it.STUB_BITS:.0f} bits each, by contract) · {r['missing']} missing")
    print("  ↳ in the mortal world, gone is gone — every expired link costs "
          f"{it.MISSING_BITS:.0f} bits, forever")
    print("  ↳ in orreth, loss is a GOVERNED quantity: the stub proves what existed,"
          "\n    and the distillation still answers for the whole window")

    # ---- the rest of the harness reads the same log --------------------------------
    print("\n" + "─" * 76)
    dr = it.distillation_ratio(f)
    print(f"  the pyramid  · {dr['raw_bytes']} raw bytes → {dr['distilled_bytes']} "
          f"distilled — ratio {dr['ratio']}× (0003, measured)")

    pc = it.provenance_completeness(f)
    print(f"  provenance   · {pc['resolved']}/{pc['refs']} references resolve "
          f"(completeness {pc['completeness']:.2f}) — a stub is an honest answer")

    cat = KnowledgeCategory(f, "physics demo", "physics-demo-kb")
    e1 = cat.admit("larch outlasts pine in standing water",
                   {"did": "did:web:forestry.example"})
    echo = cat.admit("larch outlasts pine (syndicated copy)",
                     {"did": "did:web:forestry.example"})
    other = cat.admit("larch holds in wet ground", {"did": "did:web:timber.example"})
    cat.corroborate(e1, receipt_ids=[echo, other])
    ci = it.corroboration_independence(f, "physics-demo-kb")
    c = ci["claims"][0]
    print(f"  voices       · {c['receipts']} receipts, {c['independent_voices']} "
          f"independent voice(s) — the echo is detected (0014: same voice twice "
          "is one voice)")

    dist_id = {"a": 0.52, "b": 0.31, "c": 0.17}
    sharpened = {"a": 0.95, "b": 0.04, "c": 0.01}
    print(f"  another look · H {it.entropy(dist_id):.2f} bits → "
          f"{it.entropy(sharpened):.2f} bits — the second modality was worth "
          f"{it.information_gain(dist_id, sharpened):.2f} bits (0029's gate, as math)")

    # ---- the contract act: the intolerables survive the climb (0033 sp2) -----------
    print("\n" + "─" * 76)
    f.set_distortion_contract("medication", {
        "must_preserve": ["dosage", "timing"], "prohibited_loss": ["prescriber"],
        "may_compress": ["narrative"], "distortion_bound": 0.0})
    meds = [f.write(make_memory(f.steward, f.steward_kp, f.scope,
                                {"dosage": f"{d}mg", "timing": "morning",
                                 "prescriber": "dr. hale",
                                 "narrative": "a long bedside conversation " * 10},
                                kind="episodic", tags=["medication"]))
            for d in (10, 20)]
    d1 = f._distill(meds, push=False)
    d2 = f._distill([d1["id"]], push=False)       # the next tier up
    for rid in meds:                               # every raw byte leaves on schedule
        f.tombstone(rid, by=f.steward["did"], reason="retention schedule")
    cf = it.contract_fidelity(f, d2["id"])
    carried = {e["value"] for e in it._body(d2)["preserved"]["dosage"]}
    print("  the contract · two medication records distilled TWICE, then every raw")
    print(f"                 byte purged — and the top still reads dosage {sorted(carried)},")
    print(f"                 contract fidelity {cf['fidelity']:.1f}: the intolerables survive")
    print("                 the climb, each value citing its honest stub (0033 §5)")
    print("  the refusal  · a distillation that DROPS a contract-named key is refused")
    print("                 at save — never discovered at incident review")

    print("\n" + "═" * 76)
    print("  entropy is a dial, not a decay — the governance sets it; the log proves it")
    print("═" * 76)


if __name__ == "__main__":
    main()
