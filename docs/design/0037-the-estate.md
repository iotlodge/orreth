# 0037 — The Estate (allen, the cloud architect)

*Design draft — proposed by Fable 5 (design owner), from JB's 2026-07-22 session (seed
drafted by JB the night before). The resident that moves Orreth from dev (the laptop
rig) to prod (IAC/CloudFormation/CDK) — and the first resident whose **body is a
tier**. The name carries a biography: in CortexObserver, allen was a workforce agent
("the @allen-likes … doing the actual labor," `../vision/FUTURE-the-conductor-and-the-field.md`);
in Orreth he is promoted to commander. The chain predicted him: 0006 §2's archetype
example has read "Cloud-Architect v3" since July 1st. Companions: `0006` (the chain),
`0010` (the surface), `0012` (the gates), `0018` (the farm that keeps his hands),
`0019` (the stable that saddles his minds), `0021` (the shipyard that grows his
toolroom), `0030` (the ladder he speaks), `0032` (the desk that keeps his knowledge
fresh), `0035` (custody, never identity). Two decisions locked by JB 2026-07-22 in
the seed session (§8). This is the first **create-something-using-Orreth**: the
embedded governance and reflex driving agentic response as we build.*

---

## Why this is a keystone

Every dive so far built the universe a mind, a memory, and a body on one laptop. This
dive builds the resident who can give it a **world**: production infrastructure,
grown and tended under the same governance that grew the universe itself. And it sets
the base deliberately — the next design (seven RAG variants as an ecosystem) will be
allen's first agent customer. Getting allen proven is getting Orreth's *builder*
proven, before anything is built on top.

The design goal in one sentence: *a human says "deploy repo foo to production," and
what follows is an interrogation, a plan with a picture, a human's signature, an
apply with a reverse gear, and an estate the universe can see — with every step
recallable from the spacetime window forever.*

## 1. The embodied field — a resident whose body is a tier

**allen IS a field.** Not an agent living in one — the field's DID (cut by
becky@field's parent in the ordinary chain) is his identity, his signature, his seat
in the parlor. The field's whole apparatus is his cognition:

```
allen  ──  the field DID (the persona; signs as allen; EMBODIED roster member)
│
├─ CONTROL PLANE — the staff born with the layer (0006 §2)
│    planner · critic · librarian seat · steward · governance · becky@field
│    drafts plans, escalates Create, observes and SIGNS the workforce (nothing self-attests)
│
├─ WORKFORCE — archetype → incarnation (0011; did:key, cheap, scope-bound)
│    observers (describe-stacks · drift walks · cost reads)  ← read-only grants
│    actors    (one approved change-set node each)           ← narrow, expiring grants
│
└─ TOOLROOM — his own infrastructure (§5)
```

Control orchestration happens **above** the workforce: allen plans; incarnations
execute prescribed observations and actions on their AgentSurfaces; the staff
attests. This is the CortexObserver Field shape ("a commander, an agent roster, its
own farms + local governance") made Orreth-native — and the pattern generalizes: any
field may one day be promoted to a persona. allen is the first **embodied tier**.

**Placement**: allen hangs directly off the universe — he works *for* it, as becky
and vigil do. The provisioner today parents fields only under ecos; universe-parented
fields are a small structural allowance (§8, open). He is a specialist, not a
conductor: **master of cloud, nothing else.** Objective breakout happens above him;
what reaches him is typed speech.

## 2. The typed speech — how humans and agents talk to allen

The 0030 ladder is the interaction contract, enforced at his door:

- **Human → allen: an Objective.** "Create me an S3 bucket." "Deploy repo foo to
  production." Plain speech, insufficient by design — and *every* Objective enters
  planning/gap-analysis before anything else happens (§3).
- **Agent → allen: an Intention or an Observation. Nothing else.** Humans alone
  originate Objectives (0030, canon) — so every agent Intention must carry **lineage
  to a human Objective, verified at the gateway**. An ask with no ancestry is refused,
  uniformly (0002 §4). Nobody builds infrastructure because a machine wanted it.
- **allen → other residents: Intentions.** Work outside his scope escalates
  *laterally*, as humans borrow expertise: knowledge from the librarian, a tool from
  charlotte, classification from a future compliance resident. Their answers return
  as Observations with provenance.

Every rung lands as memory — which is why the ladder is stored at all: the spacetime
window queries it. *"Why does this bucket exist?"* becomes a walk: the Objective (who
asked, in their words) → the Intentions (what allen decided, whom he asked) → the
Observations (what the cloud and the residents said) → the actions applied, signed.
Unanswerable in every real cloud shop; a query here.

## 3. The deployment charter — gap analysis made mechanical

A bare ask deployed literally is deployed **incorrectly**. So the plan compiles
against a **charter** — RTO · RPO · data classification · interoperability patterns ·
caching · residency · retention — and every unanswered question is a **gap**:

> **A plan with gaps cannot compile for production.** Refused-at-save — the same
> shape GraphSpec has enforced since 0008. Charter depth rides the environment
> ladder: a sandbox bucket needs almost nothing; prod demands the full charter.

Gaps **route**, they never merely block: each is a question aimed at whoever can
answer — a specialist resident where one exists, **the human seat where one doesn't
(locked by JB 2026-07-22)**, carried as questions on the HITL card. Answers are
memory, so the charter *compounds*: "your last three buckets under this product were
`classification: internal` — reuse?" The charter gets shorter as the estate matures.

And its second life: **the charter is the birth-certificate backlog for future
residents.** Every gap the human keeps answering by hand — classification again, RTO
again — is a resident waiting to be designed. The org chart grows exactly where the
questions pile up, from evidence instead of guesswork.

> **The subject anchor (JB's walk finding, 2026-07-22 — reworked the same day).**
> An answer is a property of a **workload** — the bucket, the repo — never of the
> universe: sp2's first cut stored answers floor-globally, and the glass exposed the
> flattening (seven subject-less questions reading as homework in docker land). The
> corrected model, now structural: every answer binds to a **subject**; *"answer
> \<question\> for the estate: …"* is a deliberate speech act that sets policy for
> everything, auto-applying beneath any workload's own word; another workload's
> history is **offered in the question** ("last time: `internal` for «rag-corpus» —
> reuse?"), never silently inherited. And a human never meets a question except
> **inside a deployment ask**, anchored to its subject, at its rung — the room shows
> what is answered (policy · per-workload), the inbox reserves itself for
> consequence, and dev owes nothing, ever.

## 4. The two DAGs and the Estate — the blueprint and the building

allen must at any time produce a **live, beautiful DAG** — and there are always two:

1. **The planned DAG** rides the HITL approval card: the human approves the *picture
   and the change-set as one artifact*. Stacks, nested stacks, cross-stack
   exports/imports, stack-set propagation across accounts — rendered live, Brain
   Glass aesthetic. You approve what you can see.
2. **The deployed DAG** is the as-built, reconciled on completion from
   CloudFormation's **own resource graph** — derived from truth, never drawn by hand
   (rule 7). The planned-vs-deployed diff is itself **news**: a resource that
   materialized differently than approved is a loud-lane event, never a footnote.

His AWS grammar is native: **stacks** are the unit of change, **nested stacks** are
composition, **stack sets** are propagation — and a stack-set target maps cleanly
onto a rung of the environment ladder. The full dependency picture is the resource
graph *plus the Objective lineage above it* — one unbroken chain from a person's
sentence to a security group's rule.

**The Estate view**: allen's floor in the Console, where a human browses the
deployed world and pulls any artifact. The yaml templates are workshop-shaped assets
(0031) — content-addressed, versioned, provenance-carrying, walk-of-the-work doors —
kept fresh by the serials coupling. Parlor grammar, same as every resident: *"show
the estate" · "show the plan for the retail bucket" · "walk stack foo."*

## 5. The hands — toolroom, custody, and the apply gate

- **The toolroom.** A CLI needs a real machine: allen's field carries an execution
  substrate — in dev, a Shipyard-grown container (0021) with the SDK/CDK/`aws` CLI
  installed. Each tool is a **farm service with a worldline** (0018): an upgraded CDK
  is a keeper-attested lifecycle event, HITL'd, never a silent mutation of his hands.
  Executions happen only inside the sandbox; stdout, change-sets, and errors land as
  signed memory. Endgame: once prod exists, **the toolroom itself becomes IAC** —
  allen maintains his own body through the same plan/apply gate. Self-maintaining,
  never self-approving.
- **Custody, never identity** (0035, third application). Cloud credentials live
  under becky; allen holds attenuated CapabilityTokens whose `budget` is **dollars**
  — cloud spend is lifeforce (0017), metered on the beat, with a forecast on every
  HITL card ("this change is ~$X/mo") in the deal-fit shape ada already speaks.
- **Plan is free; Apply is a gate.** `cdk synth`/`diff` is the sim — unlimited,
  read-only, reversible. Apply always escalates (0012). Blast radius grades the lane
  (0024): IAM, network, and data-store changes ride high/critical (co-sign); tags
  and scaling ride as nudges. **Every apply carries its reverse** — a plan without
  its undo is not approvable. Failed applies park and retry (0014); they never
  silently re-run.
- **Drift is the serials desk pointed at the actual cloud** (0032, verbatim): the
  deployed estate is a subscription; cadence walks compare stack reality to template
  truth; drift lands as *news* — a rug-pulled security group is the same event as a
  rug-pulled model price.
- **Prod heartbeats back.** Deployed stacks report into `/topology` so the orrery
  and the Brain Glass show the body the universe wears (rule 7: one world, one
  picture). Today OrrethDemoStack and jsbarth-pipeline are invisible to the universe
  — which hands us the first walk (§7).

## 6. Knowledge and minds

- **Cloud facts are retrieval-only.** A mind's training data on AWS is always months
  stale, so allen **never answers a cloud question from a model's memory**: AWS
  documentation is living, resident-maintained knowledge — the librarian gathers it
  (an official AWS documentation MCP server can serve at charlotte's farm as the
  supply), the serials desk keeps it fresh (difference-is-news on the docs;
  superseded-at-source kills a stale idiom the moment the new one lands), and every
  answer cites. Self-maintaining by design, aimed at AWS.
- **Minds are saddled as needed** (0019). The planner and critic seats pin strong
  tiers — and a pin is a floor: unaffordable fails honestly, never silently dumber
  (0010). Observer incarnations ride cheap tiers. Whether allen's cognition is one
  mind or five is a stable decision, not an architecture change; the meter tells the
  truth either way.

## 7. The first walk — adopt, then build

allen's first act is **brownfield adoption, not greenfield creation**: import the
existing OrrethDemoStack and jsbarth-pipeline under governance — read-only.
Observe, attest, render the deployed DAG, register the templates as assets, open the
Estate view. The whole loop proves out with zero blast radius before allen is ever
allowed to Create. Then the first greenfield walk: a human says *"create me an S3
bucket"* in the glass, the charter interrogates, the human answers the gaps, the
planned DAG rides the card, apply runs in a sandbox account, the deployed DAG
reconciles — proven as a human, per the standing rule.

## 8. Decisions — **all seven locked by JB 2026-07-22** (via AskUserQuestion; recorded in `../decisions/`)

*The seed session:*

1. **Charter gaps route to the human seat** while specialist residents don't yet
   exist — prod never blocks; answers land as memory and are reused; every
   hand-answered gap is evidence for which resident to design next.
2. **This dive proceeds** — drafted ahead of design 2 (the seven RAG variants),
   which becomes allen's first agent customer.

*The lock session — every one on the recommended path:*

3. **Placement: universe-parented field.** The provisioner gains the allowance;
   "staff of the universe" is a real category (becky and vigil already live there);
   no decorative eco.
4. **Authority ceiling: plan-and-propose first.** Every Apply is human-fired.
   Graduating low classes to auto-apply is a LATER, revisable lock — earned by
   record, never by declaration.
5. **Co-sign classes: all four.** IAM changes · network topology · data-store
   delete/replace · cross-account stack sets — distinct-signer quorum (0012) on
   Apply.
6. **Spend rides the lease token** (`constraints.budget`, in dollars) — authority
   and allowance one artifact, attenuation-only, budget-miss ≡ authz-miss uniform.
7. **Brownfield adoption is the acceptance gate** — §7's read-only walk must
   complete before greenfield Create unlocks.

## 9. The spoonfuls (proposed — JB may re-cut)

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The embodied field & the typed door** — the universe-parent allowance in the provisioner; allen joins the roster (EMBODIED; the field DID signs as him); his parlor card; typed speech enforced at the door: humans speak Objectives, agent asks carry walkable Objective lineage or meet a TEACHING refusal (deliberately not the uniform authz shape — the door teaches the ladder; 0002 §4 keeps protecting retrieval) | ✅ landed 2026-07-22, same day as the locks — `estate.py` (the door: agent objectives refused with the law in the message · lineage must be walkable · the acceptance gate refuses Create with its own words) + `provisioner.staff_field` (one-hop chain, root-verified; the template schema's hard landing staged for a later rule-9 gate, the 0033 soft-first pattern) + the parlor seat (card/replies verbatim — the door and gate are law, and a governed voice never rewrites law) + the wire (pin-only residency like the smith, `surveying`, sky-blue in the glass, parietal on the brain) — **198/198** (was 193) · **proven on the wire**: the card landed signed under his own DID with honest zeros; a human asked *"create me an S3 bucket"* and the gate answered *"I adopt before I create (0037 §8.7)"* verbatim; dollars ride the Budget shape's `cost` axis (contracts/v0 untouched) |
| 2 | **The deployment charter** — the charter as a versioned asset; gap analysis at compile (prod refuses with gaps); gaps ride the HITL card as questions to the human seat; answers land as memory and are recalled on the next ask | ✅ landed 2026-07-22, same day — the charter is a **versioned asset planted under allen's own signature** (0031's shape: grace may propose revisions through the lanes; the questions are DATA) · seven genesis questions (classification · rto · rpo · interoperability · caching · residency · retention) with the **environment ladder** (sandbox owes nothing, staging two, prod all) · `CharterGaps` = refused-at-compile carrying the open questions — they ARE the HITL card's text · answers land signed with the question they answer and who spoke, and **compound**: the second ask re-asks nothing · conversational doors: *"show the charter"* · *"answer &lt;key&gt;: &lt;words&gt;"* · a satisfied create stages `estate-plan` toward 0012 with answers pinned — **202/202** · **proven on the wire**: the charter planted at first look (`sha256:1287423…`), *"show the charter"* spoke 7 open; *"answer data_classification: internal — universe records only"* landed signed (`sha256:4b11863…`); the read-back said **1 answered · 6 open** with provenance — the charter visibly shortened · **HONEST WART, caught by JB in the glass and reworked the same day**: the first cut stored answers floor-globally and the room showed subject-less prod questions as ambient homework — the SUBJECT ANCHOR (§3 amendment) landed in its place: answers bind to workloads, *"for the estate"* is deliberate policy, history is offered ("reuse?") never inherited, legacy subject-less records skipped rather than reinterpreted; re-proven live — estate policy `residency: us-west-2` landed and the charter read back as policy + workloads, no to-do list |
| 3 | **The two DAGs & the Estate** — the planned DAG on the approval card (approve the picture and the change-set as one artifact); the deployed DAG reconciled from the resource graph; planned-vs-deployed diff lands as news; the Estate view with recallable yaml assets | the blueprint and the building |
| 4 | **The hands & the first walk** — the toolroom (CLI as a farm service with a worldline); custody tokens with dollar budgets; **brownfield adoption**: OrrethDemoStack + jsbarth-pipeline observed read-only, attested, rendered, registered — the acceptance gate passes and the demo stack becomes visible to the universe | the proof |

---

*The universe has had a mind, a memory, and a body. allen is the first resident who
can build it a home — asking first, showing his drawings, keeping the receipts, and
never once holding the keys himself.* 🥂
