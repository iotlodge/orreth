# 0040 — The Faculty and the Agent Lab

*Design draft — proposed by Fable 5 (design owner), from JB's 2026-07-23 seed
("Orreth.adaptive.learning.universe.agent") and the round-2 dialog the same day.
**Status: DOCUMENTED IN FULL, BUILD PARKED** — by JB's explicit call, construction
waits until Orreth is "stamped ready to test"; this document is the whole design
so the build starts warm the day the stamp lands. Companions: `0008` (GraphSpec
dual-mode authoring — reserved since 2026-07-02, this dive is why), `0027` (the
fingertip — the ONLY execution engine), `0015` (the parking lot — failure is
fuel), `0001`/`0039` (skills crystallized, graduated, demoted), `0009` (templates
— packages are their descendants), `0029` (upload is an ask), `0038` (the RAG
ecosystem — a REQUIRED COMPONENT of this package), `0039` (the two books this
lives across), `0013` (trust tiers at the package door), `0037` (allen, who will
provision the faculty's ground).*

---

## The north star (JB's sentence, the design's whole point)

> **A flow's nodes carry no prompts and no skills. The Objective describes what
> is needed — and if the universe doesn't have it, the universe has facilities
> to GET the knowledge, CREATE skills from it, and USE them.**

Every workflow tool alive makes the human wire capabilities into boxes. Orreth
inverts it: the human states intent; capability is **summoned, through gates**.
The machinery exists today in pieces and this dive joins them into one walk:

1. A running flow's node meets an objective it lacks the craft for.
2. The lack **parks as a knowledge-acquisition intent** (0015 — failure is fuel).
3. The **librarian gathers** (0014/0032) — sourced, quarantined, promoted on receipts.
4. The knowledge **crystallizes into a skill** with an acceptance rubric (0001),
   entering the Canon through the lanes.
5. The skill **canaries at its serving tier** (0039's graduation — never
   silently dumber), then serves.
6. The flow's next run finds the craft waiting. **The universe grew the hands
   it needed.** Nothing was wired; everything is on the record.

That is what "adaptive learning universe" means here — not a marketing phrase
but a loop with receipts at every joint.

## 1. The Faculty — the package of minds

**The Faculty** is an installable **universe package**: a set of adaptive
ecosystems that give any universe the organs of advanced multi-tier agentic
architecture. The v1 roster, organized as a **worn taxonomy of four faculties**
(legible in the glass without hover — color families, badges, and the names
themselves):

| Faculty | Ecosystems | The mind it adds |
|---|---|---|
| **Deliberation** | `e:planner` · `e:critic` · `e:judge` | the minds that weigh — plans drafted, challenged, decided |
| **Perception** | `e:analyzer` · `e:gap-detector` | the minds that notice — what is, and what's missing |
| **Conduct** | `e:router` · `e:query-optimizer` · `e:grader` | the minds that steer and score |
| **Aegis** | `e:security` | the mind that guards — deliberately its own family, never confusable |

**Why ecosystems, not fields** (JB's instinct, structurally forced): the depth
cap is 3 — a field can never have children. Planner-as-ecosystem can grow
specialist fields (strategic, tactical, domain-specific) and hold eco-level
Canon its fields inherit by the cascade; planner-as-field would be a ceiling.
Room to grow is not a preference here; it is the only shape with a future.

**The package INCLUDES the RAG ecosystem** (0038) as a required component —
the Faculty without the Stacks is a mind without a memory; JB named it
critical. A package declares its components and their versions; installing the
Faculty into a universe that already runs the Stacks reuses the standing eco
(the living-hull guard and the join door already enforce nothing-doubled).

**Packages are product** (a standing Orreth objective): versioned, signed,
marketable artifacts — "add a Faculty to your universe" is a purchase, an
install, and a governed act all at once. The RAG eco was the pattern's proof;
the Faculty is its first product.

## 2. The package law — install is a governed act, never a side-load

- **Resident-mediated, exactly as JB sketched**: *"install package
  the-faculty"* → becky: *"I see no package named 'the-faculty' — hand it to
  me"* → **the drop zone appears, presented by the resident** (0029's
  upload-is-an-ask, reused verbatim). No standing upload chrome; the door
  exists only when a resident opens it.
- **A package is an identity-bearing artifact**: signed by its author,
  manifest-hash-pinned (charlotte's rug-pull law applied at package scale),
  **trust-tier gated** (0013 — a package requiring `verified` refuses an
  anonymous universe).
- **Canon-bearing content never installs silently.** The Faculty ships prompts,
  policies, and skills for its minds — every one enters as a **proposal
  through the lanes** (or, for a fresh universe, as genesis assets explicitly
  listed in the install approval the human signs). A package from a stranger
  installs **quarantined**, the way knowledge does: present, inert, promoted
  on receipts.
- **Spawning rides the existing gates**: the shipyard lays the hulls, the
  field-join door grows standing ecos, allen provisions when the ground is
  cloud. Consequence waits for the human at every hull.
- **The reveal is a show** (design owner's call): the human watches the
  faculty **bloom in the Constellation** — new ecosystems taking their
  inclined planes one by one as they're raised — and the **Agent Lab** tab
  fades into the console only when the last hull beats. Install is a moment,
  not a progress bar.

## 3. The Agent Lab — the human's flow workspace

The Lab (JB's name, kept) is where humans compose **Flows**: directed graphs
of faculty nodes the universe executes.

- **Tiles**: each faculty node is a tile wearing its faculty color and a
  medallion glyph (the residents' faces taught us: people learn icons).
  Drag to the canvas; join with edges; parameter slots show as empty sockets.
- **The bijection — the feature no flow-builder alive has** (0008, finally
  built): as tiles wire, a **living English sentence** composes beneath the
  canvas — *"analyze the corpus; detect gaps; plan against them; the critic
  reviews; the judge decides"* — and it is **bidirectional**: edit the
  sentence and the canvas rewires. Sentence↔node bijection,
  never-guess-silently. Humans who think in pictures and humans who think in
  words share one Lab.
- **The Lab authors GraphSpec v0 and NOTHING ELSE.** No second execution
  engine exists or ever will: a saved Flow compiles (sim-first,
  refused-at-save — 0008's law) onto the AgentSurface verbs, and **execution
  is 0027's fingertip**: objective → orchestration incarnation → slivers to
  the faculty's floors, review riding altitude, HITL parking branches, every
  hop a record.
- **Save** lands the Flow as a **Chronicle artifact** (JB's explicit call:
  Chronicle space, not Canon) — a `flow-config` record class: signed,
  named, recallable forever, 0030's "artifact of artifacts." Runs are
  Objective instances carrying lineage to the human who fired them.

## 4. Running a flow — the librarian completes the ask

*"Run 'market-scan'"* — spoken to the librarian, from the Lab or any seat:

1. She reads the Flow's **declared parameter slots**. Unfilled → she asks, in
   her own voice: *"'market-scan' wants an objective — what shall it pursue?"*
   The human answers without leaving the Lab.
2. The **plan gate applies untouched** (0030): origin plans wait for their
   human; the plan card carries the flow's picture.
3. The fingertip executes; the **walk of the work** shows every seat visited,
   what rode down, what it cost, who graded it — every line ending in a hash.
4. The **standings grade the faculty's nodes** across runs (0005 + 0033), and
   the **improvement engine tunes their Canon** through the lanes — so a
   human's saved flow gets better over time *without the human editing it*.
   Adaptive, earned.

## 5. Flow freshness — the rot solution (designed here, per JB's ask)

A saved Flow **pins the Canon versions of every faculty asset it was authored
against** (the 0007 context-hash pattern, applied to flows). At run time the
librarian diffs pinned-vs-active:

- **Unchanged** → run.
- **Changed** → the Flow drops to **revalidate** (a serials-desk trigger:
  `faculty-shifted`), and the human chooses: **re-bless** against the new
  craft (the pin updates, a sibling version of the flow-config lands), or
  **run against the pinned versions** (reproducibility — yesterday's craft,
  exactly). Never a silent re-run under changed meaning.

## 6. The Aegis — both faces, one blindness (JB's law, verbatim honored)

The security ecosystem is **both**:

- **A callable step** — a flow may route output through `e:security` for
  scanning/policy checks like any faculty node.
- **A standing observer over flows** — vigil's pattern extended: watching flow
  *shape* for abuse (runaway fan-out, exfiltration-shaped step sequences,
  attempts against Orreth itself), staging alarms, never enforcing alone.

And the law that binds both faces: **the security resident cannot see
Chronicle content.** It observes shape, cadence, and structure — content-blind
like vigil, always. The guardrails built through 0000–0039 remain the
*architecture* layer (floors, gates, tokens, the closed loops); the Aegis is
the *workflow* layer. Two layers, named, neither substituting for the other.

## 7. Agents at the Lab's door (flagged for the lock session)

Humans compose flows; agents "just do it naturally" (JB). But a **saved Flow
as a callable skill** — an agent's Intention invoking 'market-scan' with
Objective lineage — would put human-authored flows into the mentor/mentee
economy: composed once by a person, served forever by the workforce.
Recommended **yes, as a later spoonful**, door designed now: an agent invokes
a flow only by name + lineage, through the same gates, never authoring in the
Lab itself in v1.

## 8. The worked example — the Trading Desk (JB, 2026-07-23)

In CortexObserver, JB's team built a Trading Desk: three named agents (equities
· options · crypto) running near-identical, genuinely radical LangGraph flows —
cloned and maintained in triplicate, craft wired into every box, analysis
detailed enough to impress any human who watched. It was three crafted
performances.

In Orreth, the same desk is **one Flow, saved once** in the Lab — *analyze the
market; detect gaps; plan positions; the critic challenges; the judge decides;
the grader scores* — with an Objective slot. Three desks = **three
objectives**. The first options run finds the planner lacking options craft:
the lack parks, the librarian gathers, the skill crystallizes through the
human's gate, canaries, serves — **the options desk teaches itself its own
specialty, on the record** (§ north star, end to end). The detailed analysis is
the walk of the work — every seat, grade, citation, and cost, recallable
forever — and the desks improve without re-wiring because the standings feed
the lanes.

> The difference in one line: **CortexObserver ran impressive flows; Orreth
> grows the institution that makes flows impressive.** One sentence, three
> objectives, and a universe that learns the craft.

## 9. Decisions — flagged, to be locked when the build un-parks

1. The four-faculty taxonomy and v1 roster (§1) — or a leaner six-node start
   with the rest arriving as the first aftermarket packages (proving the
   package door twice).
2. The package law (§2) as written — especially Canon-as-proposals and the
   quarantined-stranger rule.
3. Flow pinning + revalidate (§5) as the freshness law.
4. The Aegis's two faces and content-blindness (§6).
5. Agents invoking flows (§7) — in v1's design, built later.
6. No new resident for the Lab (the librarian runs, grace tends the assets) —
   revisit only if the Lab's walk findings demand a face.
7. Dev packaging: one-hull faculty mode (the RAG precedent) so a laptop
   carries the whole Faculty.

## 10. The spoonfuls (proposed — sized for after the stamp)

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The package door** — the artifact format (manifest, signatures, components, trust tier), becky's install ask + resident-presented drop zone, the quarantined-stranger rule; the Faculty manifest written (including the RAG component reference) | install is a governed act |
| 2 | **The faculty blooms** — hulls raised through the gates, faculties worn in the glass (colors, badges, the Constellation's show), genesis Canon landing as signed install-approval content | the minds arrive |
| 3 | **The Lab authors** — tiles, the canvas, THE BIJECTION (sentence↔node), save-as-Chronicle-artifact with version pins | the pen |
| 4 | **The librarian runs** — parameter slots, her asking voice, the plan gate, fingertip execution, the walk of the work, revalidate-on-shift | the flows live |
| 5 | **The north star walk** — a flow node meets a missing craft: park → gather → crystallize → canary → serve, end to end, proven as a human | the universe grows its hands |

---

*A human states an intent. The universe assembles the minds, summons the
craft it lacks, walks the work with receipts, and gets better every time —
while a security it cannot bribe watches the shape of everything and a human
signs everything that matters. That is Orreth.adaptive.learning.universe.agent —
documented in full, waiting warm for the stamp.* 🥂
