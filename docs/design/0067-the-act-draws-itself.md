# 0067 — The Act Draws Itself

*Drafted 2026-09-07 from the orreth-EnterpriseRAG proof's charter — the proofs era's third
kernel dive, paying the proof's KCR-0004 (the professional, kernel-reusable act graph).
Grounded in a full survey of the glass's graph machinery the same day (Appendix A).*

***Status: 🟡 DRAFTED · LOCKED — L1 (one view at a time; nothing breaks while anything
moves) taken by JB's word, 2026-09-07, plainly stated per the language law.***

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

1. **sp1 — The format and the pen.** The schema (firmware-versioned, beside contracts,
   v1-earmarked); the unified drawer; the choreography walk migrates first (it is already
   closest); the aperture door opens. Suite: dialect round-trips + the narrative bijection
   + every node a door.
2. **sp2 — The capability flow migrates.** `dkCvNode` defined; the desk's sixteen stages on
   the new drawer, pulse intact; the serpentine survives.
3. **sp3 — The atlas and the estate migrate.** The glow law generalized (`kinds` on the
   shared edge); allen's DAG polish paid; the standalone exporter collapses into the one
   drawer's export.
4. **sp4 — The act accretes.** Live acts (asks, objectives) project their graphs from
   records via `by_coordinate`; 0066's choice nodes and 0065's variant tags appear; the
   E-RAG "answer wears its thinking" contract proven in the glass.

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
