# 0069 — The Estate of Sources

*Drafted 2026-09-08 from the orreth-EnterpriseRAG proof's charter — the proofs era's fifth
kernel dive, opening Wave 2 (the data estate). Grounded in the Farm/upload/embedder survey
of 2026-09-08 and the OpenKB/openwiki research banked in the proof repo (Appendix A).*

***Status: 🟡 DRAFTED · LOCKED — all three locks taken by JB's word, 2026-09-08, plainly
stated per the language law: L1 both keepers (allen charters the resource, charlotte holds
the wire — one onboarding flow walks both, the container-walk pattern made law) · L2 two
connector kinds (`store` and `database`, each with an honest precise fingerprint, one
shared lifecycle) · L3 multilingual default (the standard names a ~100-language model; the
migration machinery lands either way; the three-numbers lie dies).***

## 1. The demand, verbatim (the proof's charter)

> "E-RAG will need to support every mainstream formatted doc types and zip files of those
> [Human upload]… As an architecture E-RAG will need to be able to use Orreth Kernel to
> onboard AWS, AZURE, & GCP Object Stores, and Databases and On Premise [localhost]. Should
> really test out the Farm/Stable with this Proof." — charter, the founding words
>
> "…summarizing it (for example using an OpenWiki architecture for unstructured summaries
> while storing the origins [clouds, localhost] in appropriate object stores)…" — the seam
> (addendum 2), with the two reference repos deep-dived on JB's word (the research report)
>
> The Basket (JB's feature): navigate to a directory, list its files, select one or many,
> keep appending across directories — a list of files and origins — then Import.
>
> "We do need multilingual support and ability to translate." — addendum 5
>
> Streaming sources: **parked to a later wave** (locked 2026-09-06); ingest designed so
> streams join later without surgery.

## 2. The problem — what the survey found

1. **Upload is one file, 256 KB, four formats.** A single drag-drop zone (no file picker
   exists anywhere in the glass), base64-inflated into the record body store; PDF and
   images are admitted *dark* with a parked extraction intent — **there is no PDF text
   extraction anywhere in the repository**. No multi-file, no directory, no zip handling.
2. **The Farm has no kind that means "a store you read from."** Kinds are `mcp | http |
   feed` — and `feed` is declared and dead. The connector machinery an ingest source needs
   is all present and proven (identity, hash-pinned manifest, probation, `env:NAME`
   secrets resolved only at the wire, **meter-as-authorization** so resting/quarantined
   refuse for free, allocations, spend guards, the discredit→recall walk) — it just has
   no store-shaped citizen. No AWS/Azure/GCP SDK exists anywhere in the backend.
3. **allen and charlotte each hold half the answer.** allen's deployment charter already
   speaks store language (residency, retention, data classification; the ask-catalog maps
   "bucket/corpus/store" to S3 shapes) and his brownfield walk proves read-only adoption —
   but he has no read path into contents. charlotte owns the callable wire — but no
   governance of *why a store exists*. The container walk already proved the two-keeper
   split: **allen grows the resource as a deed; charlotte plants the wire.**
4. **The embedder is hardcoded-by-omission and the standard lies three ways.** fastembed's
   default English model (384 dims) vs the plane's `vector(384)` column vs a declared
   `stacks-embedding` standard asset claiming **512** — three numbers, one "standard." No
   model-swap migration path exists (the sweep only finds *absent* rows, not wrong-model
   rows). Multilingual cannot land honestly until the standard tells one truth.
5. **A quiet twin divergence:** `resting` exists in the plane's state machine and not in
   the Python reference — the twinning discipline missed the state machine itself.

## 3. The shape

### 3.1 The Basket, and where bytes actually live (plain words first)

**In plain words: you point at a folder, the Basket lists what's inside, you tick the
files you want, move to another folder and keep ticking — the Basket keeps your list with
each file's origin — and when you're done, one Import button brings them all in. Zips
count as folders: the Basket looks inside them.**

Under it, the byte law changes honestly: the 256 KB inline-body path stays for small
things, but **imported files land as origins in the object store** — the artifact-pointer
law the kernel already owns (a signed pointer record carrying name, place, and content
hash; the mass in a class-appropriate store, never base64 in a record body). The size bar
becomes a dial; the zip unpacks at the door into its file list, each entry remembering the
zip it came from. Ingest jobs ride a **durable, resumable queue** (the openwiki discipline:
interruption is weather — a crashed import resumes, finishing honestly with "interrupted"
metadata rather than pretending completeness).

### 3.2 The connector estate — two keepers, two new kinds

- **Two new Farm kinds**: `store` (things you list and fetch from — S3, Azure Blob, GCS,
  on-premise directories and shares) and `database` (things you query — schema-aware,
  read-only first). Both ride the full existing lifecycle unchanged: planted through the
  human gate wearing their source, manifest pinned (a store's manifest = its declared
  operations and scope), probation earned on heartbeats, secrets by `env:NAME` only,
  metered-as-authorized, restable, allocatable, discreditable.
- **The two-keeper split, made law** (staged as L1): **allen charters the resource** — why
  it exists, what it may hold, where it lives, how long it keeps (his charter's questions,
  verbatim) — and **charlotte holds the wire** — the connector identity that actually
  lists and fetches. A cloud store onboarding is one flow through both: charter answers →
  the resource record → the plant ask → the pinned wire. The cloud SDKs execute
  worker-side in the connector lane, exactly as MCP does; the plane never proxies bytes.
- **Honesty about the clouds**: AWS lands first (the dev rig already rides S3); Azure and
  GCS follow as the register already phrases it — declared growth, proven when walked.
  Streaming stays parked, but a `store` whose contents change gets a freshness beat — the
  seam streams will later enter through, built without the streams.

### 3.3 The extraction matrix — every mainstream format, honestly staged

The parked-intent pattern (formats admitted dark, an intent staged) stops being an apology
and becomes the assembly line: **deterministic extractors** (PDF text, Office documents,
spreadsheets, HTML — worker-side libraries, firmware-versioned) pay the intents for the
formats machines read plainly; **minded extraction** (OCR for scans and images, speech-to-
text for audio, frame description for video) rides the Stable as each eye is saddled —
until then the refusal stays honest, one face. Every extraction lands as a derived record
citing its origin (the lineage chain), and **0068's redaction-at-ingest verbs wire in
here**: a masking rail runs before the extracted text ever becomes a knowledge record.

### 3.4 The wiki — OpenKB's skeleton, openwiki's conscience, Orreth's law

The summarization layer adopts what the research recommended from JB's two repos:

- **From OpenKB** (Apache-2.0, same language and license family): the wiki taxonomy —
  per-origin summary pages, cross-origin concept pages, entity pages with recurrence
  counts, a catalog index, an editable schema-as-craft; the short/long document split
  (long documents get a tree index with page-range retrieval — **this is what 0065's
  Hierarchical variant retrieves over**); the link whitelist that kills hallucinated
  cross-references; the removal cascade.
- **From openwiki** (MIT): **Grounded Claims** — every material statement in a summary
  tied to versioned evidence, staleness detected from evidence versions, and the system
  refusing to call a page current while a stale claim lacks an explicit decision —
  *epistemic standing made mechanical*, landing as signed records in governed memory; the
  durable page-job queue (§3.1); the never-fabricate-trust-metadata discipline.
- **Under Orreth law**: origins in object stores (never filesystem-local state); wiki
  pages as **derived, rebuildable records** of the signed log; the purge cascade running
  through claims (an origin's death retracts every claim its evidence carried, and every
  page wearing a retracted claim is flagged for rewrite — stronger than either project
  has it); the librarian answering *through* the wiki with claim chains as citations.

### 3.5 Multilingual, and the embedding standard that stops lying

The embedding model becomes a **declared standard** (one truth: model name + dimensions,
a versioned asset the plane's table is keyed to), with the migration machinery the survey
found missing (a model swap marks every old-model row for the sweep to re-embed — loud,
resumable, never silent). The multilingual question itself is staged as **L3**. Translation
lands as a governed skill in the flows and the canvas; a person's answer-language
preference lives in their profile (Dive VI's territory, the hook built here).

### 3.6 The found wounds, paid while we are here

The `resting` state twinned into the Python reference (the state machines match again);
the three-dimension disagreement collapsed into the one declared standard (§3.5); and the
single-file upload honestly retired in favor of the Basket + pointer path.

## 4. The razor applied (plain words in parentheses)

| Layer | Class |
|---|---|
| Connector kinds, extractors, the claims machinery, the migration sweep (what cannot be quietly edited) | **Firmware** — release |
| Store charters, connector manifests, the wiki's schema, the embedding standard, pattern lists (what humans write and tune) | **Craft** — gated, versioned |
| Size bars, freshness cadences, extraction concurrency (numbers with pre-set limits) | **Dials** |
| Origins, pointer records, extractions, wiki pages, claims (what actually happened and what was learned) | **Records & projections** — signed, lineage-carrying, purge-reachable |

## 5. The locks (staged for JB, 2026-09-08)

- **L1 — the two keepers**: cloud/on-prem source onboarding = allen charters the resource
  (why/where/how-long) + charlotte holds the wire (the governed connector).
- **L2 — two connector kinds**: `store` (list-and-fetch) and `database` (schema-aware
  query) as distinct kinds on one lifecycle — versus one generic kind.
- **L3 — the default embedding model**: multilingual-capable by default, or English-small
  by default with per-corpus multilingual choice.

## 6. The spoonfuls (proposed order)

1. **sp1 — The byte law and the Basket.** ✅ **LANDED 2026-09-10 — bulk never enters
   the mind, and interruption is weather.** **The byte law** (`orreth_sim/basket.py`):
   imported files land as ORIGINS — the mass rests content-addressed in the object
   store (`~/.orreth/objects/<hh>/<hash>`, torn writes never wear the hash's name)
   and what enters the signed log is the 0039 §6 artifact-POINTER carrying name,
   store URI, content hash, and the ORIGIN (path, and the zip it came from) — never
   base64 in a record body. The free textual floor still extracts (derived from the
   pointer); dark formats park their intent off the pointer exactly as 0029 taught
   (sp3's retry list grows). **The bars became dials**: `upload-inline-kb` (the old
   256 KB drop-zone bar, now the human's) and `import-max-mb` (the pointer path's
   per-file bar) — and the glass's hardcoded client-side 256 KB precheck died (a
   number that would lie the day the dial turns). **The queue is the log**: an
   import job is a SIGNED record before any byte moves; progress derives (an entry
   is done exactly when its pointer stands); the beat carries a few entries a
   breath and a kicked floor beats now (storms are a disease); the completion
   record names interruption instead of pretending completeness. **The Basket
   stands in the glass**: 🧺 beside the librarian's drop zone — the picker walks
   folders under a declared root (traversal one-faced; dotfiles unlisted), zips
   open like folders, the running list keeps every entry's origin, one Import,
   and progress reads from the log while the panel is open. Doors: GET `/basket`
   (+ `?zip=`), GET `/basket/jobs`, POST `/basket/import`. *Proven live on the
   rig: `/etc` REFUSED with the one face; a 4-entry import (two folders + a zip
   member + a PDF) carried whole — 4 content-addressed objects, 4 signed pointers
   with origins, the mass in NO record body, three extractions and one honest
   dark park; then THE CRASH WALK — 8 files imported, the worker KILLED
   mid-carry, replanted with zero memory, and the log alone finished 8/8 with
   ZERO duplicate pointers (12 total across both jobs) and two honest completion
   records.* Suite 519→529 (ten Basket laws). *Honest remainders: the Basket
   root is the operator's home (`ORRETH_BASKET_ROOT` narrows it); the job sweep
   rides the governed retrieve (a projection when volume demands); failed
   entries retry once per worker life by design; the store is local-class — S3
   arrives with sp2's `store` kind.*
2. **sp2 — The store kind and the first wire.** The `store` kind end to end on S3 +
   localhost; the two-keeper flow (charter → resource → plant → pinned wire); freshness
   beats. Suite: lifecycle laws (rest/resume/discredit) on a store.
3. **sp3 — The extraction line.** Deterministic extractors paying the parked intents
   (PDF/Office/HTML/spreadsheets); redaction-at-ingest; lineage on every extraction.
   Minded extraction (OCR/ASR) staged behind the Stable's eyes, refusing honestly.
4. **sp4 — The wiki.** Taxonomy + claims + the queue, on the signed log; the Hierarchical
   variant's tree index fed; the librarian's through-wiki answers; the purge cascade
   proven (kill an origin, watch its claims retract and its pages flag).
5. **sp5 — The database kind + the standard.** The `database` connector (read-only first);
   the embedding standard declared + the migration sweep; L3's model landed; the
   `resting` twin paid.

## 7. The honest boundary rows this dive moves

- The upload row: from one-file-256KB-four-formats to the Basket + pointer path + the
  extraction matrix — each format's row proven or honestly dark.
- New rows: the store/database kinds (AWS + localhost proven; Azure/GCS declared growth);
  the wiki with claims (proven by the purge-cascade walk); the embedding standard (one
  truth, migration proven).
- Parked honestly: streaming (the standing lock); minded extraction per eye until saddled.

## Appendix A — evidence trail (survey 2026-09-08 + the wiki research)

Upload reality (`window.html:4907-4926`, `artifacts.py:20-73` — one file, 256KB, no PDF
extraction anywhere); Farm kinds with `feed` dead (`0018:43`, `console_worker.py:4662-
4670`); the one invoke door + meter-as-authorization (`console_worker.py:4610-4678`,
`farm.rs:159-170`); env:NAME at the wire (`console_worker.py:2732-2738`); the container
walk's two-keeper precedent (`console_worker.py:10280-10429`); allen's charter speaking
store language (`estate.py:31-49, 240-278`) and his read-only hand (`console_worker.py:
6030-6051`); no cloud SDKs anywhere (grep clean); embedder hardcoded-by-omission
(`meaning.py:34-49`), `vector(384)` (`pg.rs:99`), the 512 standard (`stacks.py:33`), no
migration path (`pg.rs:154-168`); the `resting` twin divergence (`farm.rs:20-28` vs
`farm.py:18-28`); the artifact-pointer law (`canon.py:330-360`); the wiki research
(the proof repo's `docs/research/openkb-openwiki-report.md` — adopt/adapt/skip with
licenses).
