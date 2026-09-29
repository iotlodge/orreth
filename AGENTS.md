# AGENTS.md — Orreth repo

MANDATORY for every model working in this repo — Fable, Opus (including after a
safeguard model swap), or anything else:

1. Before your FIRST code edit of a session, read the `orreth-covenant` skill
   (`.agents/skills/orreth-covenant/SKILL.md` — a symlink to the canonical card at
   `.claude/skills/orreth-covenant/SKILL.md`; one truth, never a copy that drifts)
   and hold to its hard rules. They are the enforcement card for the vision in
   `docs/design/0000–0017` and `docs/vision/`.
2. If you are not Fable 5: all work goes to a quarantined `opus/...` (or model-named)
   branch, commits tagged `[<MODEL> · QUARANTINED]`, never pushed to origin, with
   `agents/PROVENANCE.md` updated — it awaits Fable 5 + JB review.
3. Never touch the kernel's crypto surface (`orreth-spine`'s `kernel_self` · `seat` ·
   `desk` · `envelope` · `canonical`) or `contracts/v0` without JB's explicit approval
   for that specific change (covenant rule 9).
4. The dev rig is `scripts/dev.sh` (Docker-first). The kernel `orrethd` is THE door on
   :4600 (`kernel`), the Python reference on :4601 (`reference`), cells on :4602+.

When a rule here conflicts with convenience, the rule wins. When in doubt, ask JB.
