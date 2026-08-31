# 0064 — The Open Book

*Reserved 2026-08-31 from JB's seed; drafted the same morning by Fable 5,
grounded in three code-verified survey reports (`tmp/docs-dive/report-kernel.md`,
`report-docs.md`, `report-monolith.md`).*
***Status: 🟢 locked 2026-08-31; sp0 + sp1 LANDED the same day — the book is
LIVE at https://docs.orreth.ai (repo: github.com/iotlodge/orreth-docs, public):
four Learn pages + the quickstart (sp2 v1, clean-machine walk still the named
proof), every page verified 200 over the real domain, pretty-URLs and the 404
face proven, the console's welcome band linking back (cc846e4). En-route
lessons: the deploy needs the jb_support profile with the shell's static keys
unset; the first stack mirror dropped the demo's ARecord block — cert and edge
stood while nothing told DNS where to knock (1819e6f restored it). NAMED
FINDING for JB: the apex orreth.ai itself is DARK (no record at all) — "linked
from orreth.ai" needs a decision about what the apex should BE (redirect to
docs? to demo? a landing?). The demo site inherits the welcome-band link at
its next refresh. Only the dive's name remains JB's to change.
**sp3 LANDED + SEAM S1 CUT the same day**: `ghcr.io/iotlodge/orrethd`
(0.63.465 + latest) publicly pullable — JB granted the token scope and made
the package public with his own click (visibility is UI-only; the API has no
door). The first-world example (docs repo `examples/first-world`: mint script
whose private half never leaves the operator + two tier profiles + compose)
WALKED WHOLE beside the rig on :4600/:4601 — floor joined by one `--parent`
flag, presence up, rules down, console serving — and the tutorial page ships
with the register row moved up per the page's own law. Honest residue: the
full experience (residents, cognition) still runs from the repository until
the agentic layer is packaged — a later, deeper seam.
**sp4 LANDED the same day — SEAMS S2 + S3 CUT**: `pip install orreth-agent`
is real (0.1.0 on PyPI, Apache-2.0 by JB's lock, token via .env never in the
transcript; the `__all__` gap paid — 18 public names; proven by isolated-wheel
import then a fresh install from the live index; 24/24 tests incl. parity).
The first-capability walk ran BEFORE its page: the hello world (one folder,
one file, two names) discovered → tile beside the desks → prompt on the shelf;
folder removed → **the shelf remembers** (state=declared, genesis absent) —
0055's boot-honors-the-shelf law observed live and now taught as the
tutorial's ending. The Reference track opened with the manifest contract page
(genesis rules · every field · thirteen panel kinds · the SDK's mirrored
vocabulary); a formal JSON-Schema file stays named future work. En-route
residue: a `hello` card rests `declared` on the rig's shelf — retire it from
its tile at will.
**sp5 LANDED (docs 52b1a73) — the Reference spine, four pages**: the HTTP API
(35 kernel doors by organ + the three laws every door obeys + the worker's
doors marked as the decoupling layer, dev-only flagged), Configuration
(GENERATED from the dial registry — 36 dials, bounds/home/governs/blast, the
glossary one-source pattern extended so the page cannot drift), the Residents
(guide 03's July debt PAID: nine staff each with the line it will not cross,
four unembodied keepers, the firmware-vs-purpose razor), the Contracts (16
schemas digested + the fixtures asymmetry stated plainly). Book = 13 pages.
SEAM JUDGMENT: S5 (extracting the worker's :4562 door) was NOT needed to
write honestly — the page documents what is and marks it non-contractual;
S4/S6 likewise untouched.
**sp6 LANDED (main 05fe927, docs 58baade) — the language swept back both
ways**: the dictionary grew the five words the book leaned on hardest
(capability · shelf · scope · studio · rollup — 36 → 41 under the suite's
contract; the glass learned their plurals; 371 green), and **quinn took her
first walk over the LIVE book** (web.py grew `--book`: the same stranger
eyes and governed metered vision, seven pages of docs.orreth.ai; report
req-1686). Her 37 findings triaged on the record: the vocabulary strikes
TRUE and paid within the hour (kernel explained before used ·
content-address/DID/token/pinned-root translated into plain consequence ·
the quickstart stops narrating our own seam-cutting at strangers · the API
laws lead plain with the poetic name as the label · mint_root's expected
output shown); her console-lens misfires (docs pages have no buttons)
discarded with the reason named; her glossary-page MUTE stands on the
record — never a clean room. **S7 JUDGMENT: PARKED WITH ITS NAME** — the
sim/wire fork (farm · deed · epoch · stable living twice) was needed by no
page this dive wrote; it waits as the named entry fee of whichever future
page documents those four laws as components. Remaining beyond this dive's
bites: bring-your-own-agent page · the clean-machine walk · formal manifest
JSON-Schema · demo refresh · the dark apex (JB's call) · quinn's book walk
joining a cadence.***

A note on this document's own voice: this dive's product is documentation a
stranger can read, so the charter is written in that voice — plain words first,
the machine's own names in parentheses. If a sentence here needs the glossary,
the sentence loses.

## 1. JB's seed, verbatim (2026-08-31)

> "We need to get started on a long long dive to create comprehensive
> documentation on using and building with Orreth… Unlike frameworks like
> AgentField Orreth is 2 elements the machine/kernel (the binary) and the
> Agentic Capabilities that you or orreth create to run atop the kernel…
> I'm looking for something like [agentfield.ai/docs/learn] to be accessible
> from orreth.ai and linked from the demo site… This documentation will be
> the permanent location for maintaining how to build with and use Orreth.
> If we create packages, we will link them from the documents… Along with the
> documentation we need to actually decouple the monolith that we've created
> and use the documentation to demonstrate how to assemble the elements.
> The trick here friend is understandability and usability… NO cryptic talk…
> Start with a fresh idea and maybe even in a fresh local repo… I as the
> joint architect with you have NO IDEA what the core elements (objects) are
> for Orreth (what ecosystems and fields are inherent in firmware) and I want
> these to make sense vs u:demo, e:prod, e:field."

## 2. The problem — the machine is legible only from inside

Sixty-four design dives, ten articles, four guides — and **no page anywhere
tells a stranger how to install Orreth, what exists when it starts, or how to
build on it.** The survey confirmed the gaps by absence: zero occurrences of
"install" or "quickstart" in any doc; no API reference for the 35 kernel
endpoints; guides 03 (resident reference) and 04 (building agents) listed on
the shelf since July and never written; no published container image; the SDK
packageable but unpublished. The joint architect's own question — *what are
the core objects?* — had no page to point at. That is the wound.

And the second wound, the seed's second half: what the docs would describe is
one 14,502-line worker process (`console_worker.py`) holding every organ in a
single namespace. You cannot hand a stranger a map of a building with no
interior walls. The docs and the decoupling are therefore one dive: **each
page we cannot write honestly names a seam we must cut, and each cut seam
ships with its page as the proof.**

## 3. What the survey established (2026-08-31, code-verified)

The full reports live in `tmp/docs-dive/`; the load-bearing facts:

1. **Orreth is three bodies, not two.** The **kernel** (`orrethd`, one Rust
   binary, ~4,000 lines, 6 crates): a verifying record server — 35 HTTP
   endpoints, append-only signed records, content-addressed bodies, identity
   and permission checks, a model gateway, a tool registry, a human-approval
   queue. It verifies signatures and *cannot create them*: no signing
   function exists in the Rust code; private keys never enter the kernel.
   The **agentic layer** (Python: the worker + 55 `orreth_sim` modules):
   holds every key, does every thought, talks to the kernel over HTTP like
   any outside client. The **console** (`window.html`, 7,327 lines compiled
   into the binary): a two-headed client — half its calls to the kernel,
   half to the worker on :4562.
2. **Nothing is inherent in firmware.** `u:demo / e:prod / e:field` are not
   baked into any binary — they are the dev rig's `compose.yaml`: three
   containers of the *same* binary, each handed a different JSON profile
   (`demo-universe.json` :4500 · `demo-eco.json` :4501 · `demo-field.json`
   :4502), chained parent→child. **The topology is data.** "Build your own
   world" is honestly: write two small JSON files and a compose file.
3. **The terminology bridge already exists and is tested.** 0060's glossary:
   36 terms whose definitions are *contractually* plain English (the suite
   enforces no jargon, no design-doc citations, <240 chars), served live and
   mirrored at `site/fixtures/sentences.json`.
4. **The SDK is the cleanest artifact in the repo.** `agents/orreth-agent-sdk`
   — 832 lines, one dependency (`cryptography`), own pyproject and tests,
   zero imports from the worker. Publishable as-is; never published. (Gap:
   `OrrethMind`, `acquire`, `manifest` missing from `__all__`.)
5. **A capability is a folder with one declaration file.** `genesis.py`
   exporting `CRAFT` (prompt strings) + `MANIFEST` (a declaration the console
   renders blind through typed panels). Install = drop the folder; a flawed
   manifest refuses loudly. 0055 documents the contract in prose; no
   machine-readable schema or panel-kinds reference exists yet.
6. **The worst structural debt is the sim/wire fork:** `farm`, `deed`,
   `epoch`, `stable` each exist twice — a spec-side module the tests hold
   and a divergent re-implementation inside the worker. Documenting either
   alone would mislead.
7. **Ready to lift with light editing:** the honest-boundary register
   (current, = a credible "what works today" page), the objective atlas's
   four architecture diagrams (needs refresh 0055→0063), guides 05 + 06,
   19 vision hero images, the MCP rug-pull security piece, `docs/demos.md`.

## 4. The four locks (JB, 2026-08-31, via the question gate)

1. **Voice: plain-first, canon as labels.** Docs lead with engineer terms;
   the machine's names appear as product labels — *"the tool registry (shown
   in the console as **the Farm**)"* — never the reverse. The glossary
   bridges both directions. The console keeps its voice for now; docs
   vocabulary feeds the later UI language sweep.
2. **Home: a fresh repo + Astro Starlight → docs.orreth.ai**, deployed on
   the same CDK/S3/CloudFront pattern as the demo site, linked from
   orreth.ai and the demo's rail. The fresh repo also hosts the greenfield
   example world — it must consume Orreth from *outside* the monorepo or
   the decoupling is theater.
3. **Docs-driven decoupling.** Write each Build page as if the packages
   existed; every step impossible from outside the monorepo becomes a named
   seam (§7). Each cut seam ships as a docs proof. The main universe
   modularizes second, as a consequence — and is never used as the tutorial.
4. **First bite: anatomy + glossary + site stands** (sp0/sp1 below).

## 5. The product — docs.orreth.ai

Three tracks, the shape proven by the AgentField docs (Learn → Build →
Reference), every page passing one test: *could an engineer who has never
heard of Orreth follow this?*

**LEARN** — What is Orreth (the kernel-and-capabilities story, one diagram) ·
How it works (record flow: sign → verify → file → project) · The anatomy of a
running world (§3.1–3.2 as a page — the page JB asked for) · Orreth vs
frameworks (LangGraph/AgentField are libraries you embed; Orreth is a runtime
your agents *join* — with the two-element distinction from the seed) · What
works today (the honest-boundary register, lifted).

**BUILD** — Quickstart, 10 minutes to a running world (v1: clone +
`scripts/dev.sh start`, works today; v2: `docker pull`, ships when seam S1
is cut) · Build your first world (two profiles + compose — the topology-is-
data tutorial) · Build your first capability (0055 §3 rewritten as a
walkthrough; `trading-desk/genesis.py` the worked example) · Bring your own
agent (join an existing LangGraph agent as workforce — CortexObserver's
bishop is the candidate proof) · Configuration (the 36 dials of 0063, env
vars, profiles — the reference 0063 named and deferred).

**REFERENCE** — HTTP API (the 35 kernel doors + the worker's :4562 routes,
each marked kernel/worker and dev-only where true) · The 16 contract schemas
(`contracts/v0`, field-level) · The resident guide (guide 03, at last: each
built-in staff member, its duty, its floor) · The SDK (`orreth-agent`: every
public symbol) · Panel kinds (generated from `capability.py:PANEL_KINDS`) ·
Glossary (both directions: plain→canon and canon→plain) · The demo reel
(`docs/demos.md` lifted).

Packages, as they publish, are linked from the pages that teach them (the
seed's rule). Articles remain a linked "Writing" section — voice intact,
never mixed into reference.

## 6. The voice law (the enforcement of lock 1)

- A page introduces every canon word at first use with its plain meaning,
  drawn from the glossary; after that the canon word may appear as a label.
- Section names and navigation are plain ("Tool registry", never "the Farm"
  bare).
- The glossary page is generated from `site/fixtures/sentences.json` — one
  source of truth with the console, never a hand-copied fork.
- New vocabulary needed by a docs page but missing from the glossary
  (capability, scope, tier profile, rollup — the known gaps) is added as
  gloss craft through the machine's own door, not as docs-only prose. The
  docs thereby *repair* the console's language debt instead of forking it.

## 7. The seam ledger — what the docs force, in order of leverage

| # | Seam | Forced by which page | Effort (survey) |
|---|---|---|---|
| S1 | **Publish the `orrethd` container image** (nothing in the repo even names an image today) | Quickstart v2 | Low — CI + registry choice (§10) |
| S2 | **Publish the SDK** (`orreth-agent` to PyPI; promote `OrrethMind`/`acquire`/`manifest` to `__all__`; gitignore the committed `.venv`) | Build your first capability · Bring your own agent | Low — it is publishable as-is |
| S3 | **Manifest schema + panel-kinds reference** (today: prose in 0055 + two divergent validators; the worked example bypasses the SDK builder) | Build your first capability | Low-medium |
| S4 | **`window.html` → 3 files** (CSS/HTML/JS are contiguous blocks; `include_str!` concat) | none directly — hygiene that makes the console documentable | Low |
| S5 | **Extract the worker's :4562 door** (`embed_door` + the 21 compose/wire functions ≈ 2,200 lines → their own module) | HTTP API reference (worker half) | Low |
| S6 | **Beat registry + request-kind dispatch table** (30 beats and 41 kinds leave the hardcoded chains; each handler becomes individually documentable) | The resident guide | Medium |
| S7 | **Reconcile the sim/wire fork** (worker imports `orreth_sim.farm/.deed/.epoch/.stable` instead of re-implementing; ~1,850 lines retired; every law gets one home) | any page that documents those four laws honestly | High |

The rule: a seam is cut when its page needs it, not before — and the page
ships in the same motion as its proof. S6–S7 touch worker internals only
(the kernel and `contracts/v0` stay untouched per covenant rule 9; S4 changes
one `include_str!` line in `orrethd`, flagged to JB when it lands).

## 8. The home

- **Repo:** `~/PycharmProjects/orreth-docs` (name at JB's word, §10) — the
  Starlight site, plus `examples/first-world/` (profiles + compose consuming
  the published image) and `examples/first-capability/` once S1/S2 exist.
- **Deploy:** `docs.orreth.ai` — same CDK/S3/CloudFront pattern as
  demo.orreth.ai; diff before deploy; the demo site's rail and orreth.ai
  link to it.
- **Maintenance law (STANDING, proposed):** a dive that changes a public
  surface — a door, a dial, a resident, the SDK, the capability contract —
  updates its docs page in the closing commit, exactly as the atlas and the
  honest boundary already demand. The docs README carries the law.

## 9. The spoonfuls

- **sp0 — the paper foundation.** The anatomy page, the glossary page, the
  what-works-today page (honest boundary, plain-voice pass) — drafted from
  the survey reports. No infrastructure; reviewable as markdown.
- **sp1 — the site stands.** Fresh repo, Starlight skeleton, the three sp0
  pages plus "What is Orreth", deployed to docs.orreth.ai; links from the
  demo rail and orreth.ai. *Proof: a stranger's browser.*
- **sp2 — the quickstart (v1).** Clone + `dev.sh start` + first look through
  the console, written from a clean-machine walk. *Proof: the walk itself.*
- **sp3 — build your first world.** The topology-is-data tutorial; cuts
  **S1** and ships quickstart v2 (`docker pull`). *Proof: the example world
  in the docs repo boots against the published image.*
- **sp4 — build with the SDK.** Cuts **S2 + S3**; the first-capability
  tutorial and bring-your-own-agent page. *Proof: the example capability
  installs into a world by folder-drop, exactly as documented.*
- **sp5 — the reference tracks.** API, contracts, dials, residents, panel
  kinds; cuts **S5** (and **S4/S6** as needed to write honestly).
- **sp6 — the language sweep-back.** Glossary gaps filed as gloss craft;
  docs vocabulary findings fed to the console's language debt; quinn walks
  the docs site as a stranger. **S7** is chartered here if the pages proved
  it necessary, or parked with its name if not.

## 10. The decisions — LOCKED (JB, 2026-08-31, via the question gate)

1. **The dive's name** — "The Open Book" stands as the working name; JB may
   rename on reading (the era it closes to is 0.64 regardless).
2. **Docs repo: `orreth-docs`, docs prose CC BY 4.0, example code MIT** —
   ✅ LOCKED. The main repo's own license remains a separate, later
   decision this dive surfaces but does not own.
3. **Visibility: both site and repo public from day one** — ✅ LOCKED.
   Building in the open, consistent with demo.orreth.ai and the campaign.
4. **Image registry (S1): GHCR** under the repo's GitHub owner — ✅ LOCKED.
5. **SDK name (S2): `orreth-agent`** — keep the existing pyproject name;
   `pip install orreth-agent`, `import orreth_agent` — ✅ LOCKED.

## 11. The honest boundary

Rows this dive will move when it closes: "no install/quickstart exists" →
proven by a stranger's walk; "SDK unpublished" → published with version
named; "capability contract prose-only" → schema + reference page; "no
public API reference" → the door tables. Each row updates in the closing
commit of the spoonful that moves it, per the standing law.
