# 0041 — The Epoch

*Design draft — proposed by Fable 5 (design owner), seeded by the 2026-07-25 outside
review (`../outside/ORRETH_CHRONICLE_MIND_CANON_MACHINE.md`, loop 1 — "Canon
realization"), triaged and locked for this slot by JB the same day. Companions:
`0037` (allen's plan → deploy → observe → reconcile — the pattern this dive turns on
the universe itself), `0007` (context-hash — the epoch is that instinct grown to the
whole machine), `0028`/`0031` (the lanes every adoption already rides), `0012`
(gates — the revert waits at one), `0039` (the Canon this dive learns to name),
`0013` (the multiverse handshake the schema must not foreclose).*

---

## The question this dive answers

> **"Which machine were you when this happened?"**

Today every Canon asset is versioned, every aperture is pinned, every adoption has a
gate record — and yet no single signed thing names **the complete machine in
force**. Answering "what law governed Tuesday?" means assembling fragments. Worse:
nothing proves an enforcement point actually *loaded* what the Canon *declared* —
configuration drift is an operational fact the Chronicle never hears. The estate
already solved this shape for AWS: plan compiles, the deployed truth is independently
observed, drift is news. This dive points allen's mirror at ourselves.

## 1. The epoch — a signed name for one coherent machine

A **CanonEpoch** is a content-addressed, signed record cut at a scope, naming:

| Field | What it holds |
|---|---|
| `scope` | the floor (or universe) this machine governs |
| `parent` | the prior epoch's id — the chain, walkable forever |
| `assets` | name → head record id, for every ACTIVE Canon asset in scope (routing-standard, distillation-dials, record-class registry, skills, charters, prompts/policies…) |
| `plane` | the binary's version (the rig's `ORRETH_VERSION`) + the tier profile's hash — the structural law's edition |
| `worldlines` | POINTERS to the farm ledger head and stable ledger head — tools and minds keep their own worldlines (0018/0019); the epoch cites where they stood, it does not re-pin them |
| `adoptions` | the gate/request records whose approvals produced this edition (the epoch walks to the humans who signed it) |
| `rollback_parent` | the epoch a revert would restore — present on every epoch, load-bearing on reverts |
| `cut_at` | both clocks (0004) |

The epoch's id commits to all of it. Two universes — or one universe and its
skeptical human — can compare machines by comparing one hash. **The multiverse
room**: every field above is already content-addressed or a pointer, so a future
handshake (0013's descendants) can verify a peer's claimed machine without reading
its content. Nothing in this schema assumes a single trust domain. (No `contracts/v0`
cut in this dive — epoch and attestation ride as tagged MemoryRecords; the hard
schema awaits its own rule-9 gate, the 0033 Phase D pattern.)

## 2. The cut — diff-is-news, on the beat

Epochs are not ceremonies; they are noticings. An **epoch beat** (the worker's beat
idiom, cadence a dial) recomputes the scope's machine fingerprint; when it differs
from the last epoch record, a new epoch is cut citing exactly **what changed and by
whose adoption**. An adoption walked through a gate produces an expected cut; a
change with *no* adoption record behind it is itself the first drift signal. One
organ, both jobs.

## 3. The attestation — what the enforcement point actually loaded

The Canon declaring v2 does not make v2 the law anywhere; loading it does. Each
enforcement point reports, on the record, what it is actually running:

- **the worker** (cognition-law: routing standards, dials, skills, charters) attests
  the asset heads it resolved and acted under, plus its own code identity;
- **the plane** (structural law: tokens, floors, budgets, refusal) already speaks
  its version and profile on `/health` — the attestation cites it.

An attestation is a small signed record: `epoch` claimed · `loaded` (name → id
actually resolved) · the point's identity · both clocks. Cadence: **on change,
plus a slow standing re-attestation** — so a silent enforcement point becomes
*visible as silent* (absence is detectable, never assumed fine). Attestations are
diff-quiet: unchanged re-attestations may collapse into the heartbeat's rollup.

## 4. Drift is news — detection stages, never enforces

The reconcile (same beat) compares the declared epoch against arriving attestations:

- **match** → silence, on the record (the rollup notes coverage);
- **lag** → an adoption landed and a point still attests the old head: a marker,
  amber, expected to converge within a declared window — loud only when it doesn't;
- **drift** → a point attests something the epoch never declared, or a machine
  change appears with no adoption behind it: a **staged finding** (vigil's law —
  detection wears no levers) and a request card at the human's gate, carrying the
  diff and the offered responses.

The glass wears it: rooms and the floor rail carry the epoch's short hash and an
age; drift turns the badge amber. "What law governs this floor right now, and can
it prove it?" becomes a glance.

## 5. Revert-to-sibling — the first pre-authorized containment posture

The drift card (and a standing door: *"revert to the prior epoch"*) offers ONE
pre-authorized, reversible response: **re-adopt the `rollback_parent`'s asset heads
as new siblings**. Nothing is deleted, nothing rewritten — the old heads become the
new heads through the same versioned shelf, the revert epoch cites both parents,
and the gate record carries the human's word. Auto-revert on drift is deliberately
REFUSED in v1: detection stages, a human signs, and the revert is merely the
easiest yes on the card. (This is the seed of the containment-posture vocabulary
the triage parked — throttle, seal, fail-closed arrive with the Custodian.)

## 6. The constitution of the constitution

The epoch machinery is itself Canon: the cut cadence, the attestation windows, the
drift thresholds, and the revert door are **assets with versions**, changed only
through the same lanes — sibling proposals, independent grading, human gates. The
deepest recursion closes in one sentence: **the law that governs change governs
changes to itself, and the epoch names both.** No adaptation can route around its
own governor, because routing around it would change a machine some epoch must
name, some attestation must load, and some human must have signed.

## 7. Honest boundaries

- In dev, the attesting points share one host and one worker process — attestation
  here proves *separated bookkeeping*, not adversarial independence (the same
  boundary named in 0042's observer).
- The worker attests what it RESOLVED, not what every code path used — v1's
  attestation covers the assets the organs read through their standard doors
  (dispatcher, dials, skills); a rogue code path is a code-review problem, not an
  attestation problem, and we say so.
- The plane's Canon-blindness stands: orrethd never reads cognition assets; its
  attestation is version + profile, nothing more.

## 8. Decisions — LOCKED 2026-07-25 (JB, via AskUserQuestion; all recommended paths)

1. **Granularity — LOCKED**: per-floor epochs + a universe roll-up epoch citing the
   floors' heads. Raw near life, rolled at the apex; "which floor drifted" stays a
   glance.
2. **Cut trigger — LOCKED**: beat-detected diff. One organ notices both gated
   adoptions and undeclared change.
3. **Attestation cadence — LOCKED**: on change + a slow standing re-attestation
   (~6h dev dial, itself a Canon asset). A silent point becomes visibly silent.
4. **Drift law — LOCKED**: stage + human gate, revert-to-sibling offered as the
   pre-authorized easy yes on the card. **Auto-revert REFUSED** — detection never
   enforces.
5. **The signing seat** *(mechanism, design owner's call)*: dev cuts and attests
   through the existing floor seat idiom with the organ named in the body; a
   dedicated governance DID per floor is the prod path, noted not built.
6. **v1 machine scope** *(mechanism, design owner's call)*: Canon asset heads +
   plane version/profile + farm/stable ledger POINTERS — worldlines stay where
   they live.

## 9. The spoonfuls

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The cut** — fingerprint, epoch record, the epoch beat, the chain; the glass wears the short hash and age | the machine gets a name |
| 2 | **The attestation** — worker + plane report what they loaded; coverage in the rollup | loading becomes provable |
| 3 | **Drift is news** — reconcile, lag vs drift, the staged finding and the card; proven live by adopting a tournament promotion and catching the attestation lag converge | the mirror turns on ourselves |
| 4 | **The revert** — rollback_parent walked at a human's gate, siblings never deletions, the revert epoch citing both parents; proven live by reverting the routing standard and watching the dispatcher obey | the first pre-authorized posture |

---

*Forty dives taught the universe to remember, to argue, to forget with a meter, and
to teach its own minds. This one teaches it to answer the auditor's first question
— which machine were you? — with a hash, a chain of signatures, and the proof that
the machine on paper was the machine in force.* 🥂
