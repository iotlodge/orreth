# 0067 — The Act Draws Itself

*Drafted 2026-09-07 from the orreth-EnterpriseRAG proof's charter — the proofs era's third
kernel dive, paying the proof's KCR-0004 (the professional, kernel-reusable act graph).
Grounded in a full survey of the glass's graph machinery the same day (Appendix A).*

***Status: ✅ CLOSED WHOLE 2026-09-09 — four spoonfuls in ONE DAY; KCR-0004 PAID. One
graph language (act-v1, v1-earmarked, the sacred v0 untouched) with the four laws in
validate(); four dialects converted (the walk · the capability flow · the atlas · the
estate) onto one drawer with lanes (compact walk · serpentine pipeline · the
schematic sheet · the dag) and ONE export idiom; the three unpaid doors all paid
(dkCvNode defined at last · the aperture opened after two months unread · allen's DAG
polish); and the accretion law live — an answer wears its thinking, projected from
signed records alone, growing as judgments land, degrading honestly when records
leave. Fourth out-of-order close: VERSION holds 0.71 (the monotone era law). L1 held
throughout: no view broke while any moved. Lock as taken 2026-09-07: L1 progressive
unification.***

## 1. The demand, verbatim (the proof's charter)

> "A graph format sounds like a great thing to output/append as an act progresses and should
> be kernel reusable and professional. Given importance let's mature as needed." — JB, the
> atlas read (KCR-0004)
>
> "Please keep that LangGraph mentality to graph and visualize the flows used in requests."
> — addendum 1
>
> The Workshop requirement rides on this format (addendum 4): spectacular per-variant
> graphs, any node opened to its inputs/outputs and the prompts/skills/policies driving it,
> the live flow lighting as a test request runs.

## 2. The problem — what the survey found

The kernel draws living graphs in five places — and speaks four different graph languages
to do it:

| Dialect | Where it lives | Drawer |
|---|---|---|
| Manifest **flow** (0055) | capability declarations | `dkCanvas` + the older `dkFlow` |
| **Choreography** (0031/0008) | the objective walk | `renderGraph` |
| Estate **DAG** (0037) | allen's deployments | `renderGraph` + a separate SVG exporter |
| **Atlas** flow (0061) | the live schematic | `atlRender` |

Four dialects, five hand-rolled drawers, no shared helper. And three precise wounds beside
the babel:

1. **Manifest-flow boxes are the one node family that is not a door** — `dkCvNode` is
   referenced but never defined (`window.html:5626`); the 0056v2 inspector ("sp-B") never
   landed. Every other law says every box is a door (0052).
2. **The aperture record — the true "what could this seat see" envelope — is built,
   coordinate-stamped, and never once opened by the glass** (`fingertip.py:323-341` vs
   `walkDetail`, which prints the graph node's summary fields instead). The deepest answer
   the walk could give sits unread on the shelf.
3. **allen's DAG polish is a standing TODO** (`docs/design/README.md:65`) — a third view
   waiting on exactly this consolidation.

And one rule-9 fact that shapes everything: **`coordinate` already lives in contracts/v0**
(`memory-record.schema.json:178-201` — objective · intention · observation · thought, riding
unsigned beside `derived_from`), and `contracts/README.md:35-38` already reserves a
**GraphSpec** slot pointed at contracts/**v1** (0008's own plan). **This dive needs no
change to the sacred v0 contracts** — every record an act graph would draw already has a
coordinate address.

## 3. The shape

### 3.1 One graph language (plain words first)

**In plain words: one way to describe any picture of work — who did what, in what order,
what each step saw and cost — that every view in the system can draw, and where clicking
any box opens the real record behind it.**

The dialect (canon: the act-graph format, GraphSpec's successor, firmware-versioned beside
the contracts and earmarked for contracts/v1 exactly as 0008 planned):

- **Node**: `id · label · kind · status · door · coordinate · cost · span` — the union the
  four dialects already almost agree on. `door` follows the atlas grammar (a room, a floor,
  a record, a view); `coordinate` is the v0 field verbatim; `cost` carries tokens/usd where
  metered.
- **Edge**: `from · to · label · kind · kinds` — `kinds` keeps the atlas's proven glow law
  (an edge lights only from real activity; empty means structural).
- **Narrative**: the choreography's sentences-to-nodes bijection survives — a graph a human
  can *read aloud*, each sentence highlighting its nodes (the 0008 §3 discipline,
  test-checked today).
- **Accretion**: the graph of a live act is **a projection of its signed records** — it
  grows because records land, never because anyone edits a picture. `by_coordinate` is the
  join; the signed log stays the only truth; a graph can always be rebuilt from nothing.

### 3.2 One drawer, five views (progressive, never big-bang)

One rendering function in the glass — grown from `renderGraph` (already shared by two
dialects) with `dkCanvas`'s earned goods (serpentine bands for long pipelines, pan/zoom
that survives re-render, the minimap, the live-pulse halo) — behind the five refresh rules
the survey codified (self-gated timers · a typing hand outranks the refresh · composed
doors rendered blind · a dark door says so · re-render idempotent over UI state), plus the
headless-eye law (the picture must be whole without waiting on animation). Views migrate
**one per spoonful**; no view breaks while another moves.

### 3.3 The doors the survey found unpaid

- `dkCvNode` gets defined: a manifest-flow node opens its inspector — the stage's latest
  record, its digest, its craft. The one node family without a door joins the law.
- **The walk opens the aperture**: a seat's drill-down fetches the real signed aperture
  record — WHAT RODE DOWN stops being a summary and becomes the envelope itself.
- The E-RAG demands land structurally: the router's choice (0066), the variant worn by the
  answer (0065), and each module boundary emit act-graph nodes — so "the answer wears its
  thinking" is this format rendered beside a reply, and the Workshop's node-inspection is
  this format's doors opened over craft. The canvas renderer itself rides Dive VIII; the
  format and the glass renderer are this dive's.

### 3.4 What the Workshop needs, delivered here

Selecting a node shows inputs/outputs (the records on its coordinate) and the applied
prompts/skills/policies (the craft refs its aperture pins — `context_hash` already names
them). Versioning/diff/rollback ride the existing shelf machinery; the graph only ever
*points*. The test-dialog's "light the live flow" is the choreography status join the desk
flow already proves at 10-second cadence.

## 4. The razor applied (plain words in parentheses)

| Layer | Class |
|---|---|
| The act-graph schema + the one drawer (the format and the pen) | **Firmware** — release |
| Declared shapes: atlas flows, capability flows, variant pipelines (the pictures whose shape is chosen) | **Craft** — gated, versioned |
| Live acts' graphs (the pictures that grow as work happens) | **Projections of records** — rebuildable, purge-reachable, never edited |

## 5. The lock (staged for JB, 2026-09-07)

- **L1 — progressive unification.** New format + one drawer land first; the five existing
  views migrate one per spoonful (walk → capability flow → atlas → estate DAG → exporter);
  nothing breaks while anything moves.

## 6. The spoonfuls (proposed order)

1. **sp1 — The format and the pen.** ✅ **LANDED 2026-09-09 — one language, the first
   dialect converted, and the deepest answer finally read.** `orreth_sim/actgraph.py`
   is the format (firmware `act-v1`, v1-earmarked in its own words — the sacred v0
   untouched, exactly as §2 promised): nodes with `label · kind · status · door ·
   coordinate · cost · span`, edges keeping the atlas's glow list, and `validate()`
   holding the four laws — **every node a door or the picture is refused** (0052 made
   structural), the narrative a bijection (every sentence's nodes exist, every node
   covered — silent boxes named), edges bind existing nodes. **The choreography
   converted first**: `from_choreography` maps the walk with NOTHING lost (the
   narrative verbatim, every detail field surviving), a finished seat's door opening
   its own outcome record, the human's opening the request, and the objective
   coordinate riding the graph root. All three worker walk sites emit act-v1. **The
   pen**: the glass's drawer learned the format — `label` served when present, any
   doored node opening the REAL record behind it via the standing reader (old payloads
   untouched, L1 held). **The aperture door opened**: a new `/aperture` worker door
   fetches the signed envelope BY COORDINATE (objective + seat) across every floor,
   and the walk's detail grew THE ENVELOPE — what this seat could see, whole: law ·
   task · behavior · knowledge refs, with the record itself one click deeper. *Proven
   live on the rig: a filed objective's staged plan came back `format: act-v1`, every
   node a door, `validate()` flawless ON THE WIRE (then cancelled politely with its
   why); the aperture door served a REAL July envelope by coordinate — law hash, task
   with intent and budget, behavior profile, seat; the glass serves the new pen. One
   walk-find: the :4562 doors ride an allow-list — a new door must join it or 404s
   (now it has). Suite 484→489 (five format laws). Rust green (the glass rides the
   plane).* *Honest remainders: the aperture hunt walks floors serially on a click —
   fine for a human's hand, a cache when it itches; pre-0033 apertures wear no
   coordinate and the miss says so honestly; the remaining dialects migrate sp2–sp3
   per L1.*
2. **sp2 — The capability flow migrates.** ✅ **LANDED 2026-09-09 — the last door-less
   family joins the law.** **`dkCvNode` is finally defined** (referenced since 0055,
   never written — the 0056v2 inspector's unpaid seam): a stage that has RUN opens its
   own record in the standing reader; one that has not yet run says so in plain words
   on a small honest card (its label, kind, latest digest, and the promise: "its box
   opens a record the moment one stands") — never a fake ref, never a dead click. The
   plank underneath: **stage rows now carry their record ref** at the desk compose
   (the ref was always at hand and never threaded). **The second dialect converted**:
   `actgraph.from_manifest_flow` — the manifest's declared pipeline joined to the
   walk's stage records, run stages dooring their records, unrun ones dooring the
   capability's room honestly, groups and edge labels surviving; pipelines carry no
   narrative and `validate()` says that's lawful. **The one drawer grew its
   dispatcher**: `renderAct` routes act-v1 pipelines to the SERPENTINE lane (dkCanvas
   with all its earned goods — bands, pan/zoom, minimap, the live-pulse halo — intact)
   and everything else to `renderGraph`; the flow panel builds act-v1 through
   `actFromFlow` (the glass twin of the sim converter, same laws) and rides the
   dispatcher. *Proven live on the rig: the glass serves all four new functions;
   **48 of 48 stage rows on the desk carry their record refs**; a stage box's door
   walked end to end — `retrieve-context` → the cross-floor door → the real record on
   f:charles, body whole, digest «prior report: yes · 9 lesson(s)». Suite 489→490
   (the second dialect's law). Rust green (the glass rides the plane).* *Honest
   remainders: the room-door's jump (an unrun stage navigating to its capability's
   tab) is a card today, a navigation when the tab router earns a door grammar; the
   glass twin `actFromFlow` mirrors the sim converter by discipline, not by import —
   a divergence would surface at the suite's converter law first.*
3. **sp3 — The atlas and the estate migrate.** ✅ **LANDED 2026-09-09 — four dialects,
   one language; allen's standing TODO paid.** **The door grammar became the atlas's**,
   absorbed whole (§3.1's own words): `DOOR_KINDS` grew to record · room · floor ·
   view · resident · parlor · world · brain. **The atlas converts**
   (`from_atlas`) — a renaming, which is the point: the schematic taught the format
   its doors and its glow law and now speaks it back, legacy keys riding inside the
   act door so the standing sheet renderer loses nothing (L1 both directions);
   `atlDoor` opens either shape. **The estate converts** (`from_estate_dag`) and
   **allen's DAG polish is paid**: every card opens the TEMPLATE ASSET RECORD that
   declared it — what you can click is what you signed — with the template ref
   threaded through the compose (it was always at hand and always dropped), an
   unknown ref dooring the view honestly, and the category colors/types surviving for
   the drawer. **The standalone exporter collapsed**: one export idiom — the dag's
   `svgOfDag` reads the act payload unchanged, and the serpentine lane gained the
   same ⇩ svg door (the drawn SVG itself is the document). *Proven live on the rig:
   the /atlas door serves `format: act-v1 · layout: schematic` with becky's door
   `{kind: resident, target: becky}` and the first edge's glow list `[join,
   field-join]` — the sheet rendering unchanged. The estate side is suite-proven
   (deed doors · honest view-door fallback · categories survive); no estate stands
   deployed on this rig today, so its live receipt lands with allen's next
   deployment — named, never faked. Suite 490→492 (the two dialects' laws). Rust
   green.* *Honest remainders: the atlas sheet renderer remains its own lane (the
   whole atlas is four lanes + worlds + bodies — one graph is not the sheet); sp4
   accretes live acts and closes the dive.*
4. **sp4 — The act accretes.** ✅ **LANDED 2026-09-09 — the answer wears its thinking,
   live.** `actgraph.accrete_ask`: a live ask's whole picture PROJECTED from its signed
   records and nothing else — the asker, **0066's choice node** (dooring its record,
   wearing its features, its why read aloud in the story), **0065's style** (the
   variant worn, dooring the rulebook version), the answer with its signals, and
   **every judgment that has landed since**: run it again after a verdict lands and
   the picture has GROWN — because a record landed, never because anyone edited a
   picture. A missing record's node is simply absent and the story says so — the
   projection rebuilds from nothing and degrades honestly (suite-held: the purged
   choice case). **The `/act` door** serves it on a human's click (riding the
   standings pull — asks, choices, verdicts with their lineage already in hand), and
   **the glass reader wears it**: opening an ask's exchange record draws "the answer
   wears its thinking — who chose, why, and what judged it" beneath the body, on the
   one drawer. *Proven live on the rig: an SDK ask, then the /act door — `format:
   act-v1`, the chain you → choice → style → answer whole, validate() flawless, the
   choice dooring its real record, the story reading the router's why aloud; the
   glass serves the hook. Suite 492→495 (three accretion laws: rebuild-from-nothing ·
   a landed verdict grows the picture · a purged choice degrades honestly). Rust
   green.* *Honest remainders: objectives' accretion rides the standing choreography
   emission (their lit walks are already act-v1 projections of branches) — a
   `by_coordinate` objective accretor generalizes when the Workshop (0072) wants the
   deeper join; the reader's ask-detection is a text heuristic until record kinds
   ride the pane's metadata.*

## 7. The honest boundary rows this dive moves

- New proven row at close: one graph language, five views, every node a door — with the
  migration commits as evidence.
- The aperture-never-opened gap: closed, named.
- Parked honestly: the canvas renderer (Dive VIII's), contracts/v1 extraction (waits for
  v1's own season, per 0008).

## Appendix A — evidence trail (survey 2026-09-07)

Four dialects/five drawers (`window.html:5556-5648, 5655-5686, 6851-6880, 7029-7120,
4612-4638`); `dkCvNode` undefined (`window.html:5626`); choreography shape
(`fingertip.py:214-288`); aperture built-never-read (`fingertip.py:323-341`);
`coordinate` in v0 (`memory-record.schema.json:178-201`); GraphSpec reserved for v1
(`contracts/README.md:35-38`, `0008:40-66,157`); atlas glow law (`atlas.py:17-21`,
`window.html:7081-7089`); refresh discipline (`window.html:7310-7329` + the five rules);
the headless-eye law (`agents/flavors/04-uat/web.py:88-105`); allen's DAG TODO
(`docs/design/README.md:65`).
