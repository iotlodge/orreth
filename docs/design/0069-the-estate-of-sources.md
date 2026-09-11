# 0069 — The Estate of Sources

*Drafted 2026-09-08 from the orreth-EnterpriseRAG proof's charter — the proofs era's fifth
kernel dive, opening Wave 2 (the data estate). Grounded in the Farm/upload/embedder survey
of 2026-09-08 and the OpenKB/openwiki research banked in the proof repo (Appendix A).*

***Status: ✅ CLOSED WHOLE 2026-09-10 — five spoonfuls in ONE DAY (Wave 2's first dive):
the Basket and the byte law · the store kind and the first cloud wire · the extraction
line · the wiki with the seal-read cascade · the database kind and the standard that
stopped lying. Sixth out-of-order close: VERSION holds 0.71 (the monotone high-water
law). All three locks were taken by JB's word, 2026-09-08, plainly stated per the
language law: L1 both keepers (allen charters the resource, charlotte holds
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
2. **sp2 — The store kind and the first wire.** ✅ **LANDED 2026-09-10 — the Farm has
   its first store-shaped citizen, and the first cloud wire is AWS.** **The connector**
   (`orreth_sim/stores.py`): a `store` is a thing you LIST and FETCH from; its endpoint
   is a URI (`s3://bucket/prefix` · `file:///path`); its pinned manifest IS its declared
   operations (list · fetch — nothing else invokable, exactly the tool law); credentials
   are AMBIENT (boto3's default chain — a key in ZERO records); the on-premise citizen
   obeys the Basket's own traversal law; Azure/GCS are RECOGNIZED and refused with
   their names (GrowthNotWalked — an operator honesty, never a probe surface; the wire's
   doors keep the one face). **One lifecycle, unchanged**: planted through the human
   gate, probation earned on heartbeats (svc_probe answers a one-key listing), the
   rug-pull door quarantines a changed operation set, resting refuses at the meter for
   free, resumption re-earns serving. **The two-keeper law (L1), one flow**: a
   `store-onboard` card stages wearing allen's charter questions verbatim (why · what
   it may hold · where · how long) + the wire's scope read aloud; ONE approval mints
   allen's signed resource record AND plants charlotte's wire riding the same word
   (the carried idiom). **The freshness eye**: a cheap listing fingerprint per serving
   store at the store-freshness-min dial's cadence — a moved store lands a
   charlotte-signed observation (the seam streams later enter through). **The Basket
   rides the wire**: 🛰 serving stores appear as sources beside 💽 local disk; a store's
   listing and every fetched byte travel through the ONE metered invoke door (bulk
   never rides a response — fetch lands content-addressed and answers with the hash);
   an imported object's pointer cites {store, key} as its origin. *Proven live on the
   rig: BOTH stores onboarded through the gate on one word each (site-share on-premise
   · jb-documents = s3://jbiotlodgebucket/documents) — allen's resource records +
   charlotte's wires → probation → SERVING on earned beats; both listed through the
   door; THE FIRST CLOUD IMPORT — a 1.1 MB PDF from S3 (4× the old inline bar) landed
   content-addressed with its pointer citing the store origin, byte-size matching on
   disk; the freshness dial turned 10→1 through the craft door, a dropped file landed
   «site-share MOVED» signed on the log, the dial turned home; and the lifecycle walk —
   rest staged with its blast radius, approved, the Basket's listing REFUSED one-faced
   for free, resumed, probation re-earning serving.* Suite 529→537 (eight store laws)
   + boto3 arrives as a declared dependency (the charter's word: AWS lands first).
   *Honest remainders: Azure/GCS declared growth; the `database` kind is sp5's; S3
   listing pages at 500 (paging honest, deep paging when demanded); the S3 walk rode
   the rig's ambient env keys — a per-store credential name (env:NAME) joins when two
   stores need two identities.*
3. **sp3 — The extraction line.** ✅ **LANDED 2026-09-10 — the parked-intent pattern
   stopped being an apology and became the assembly line.** **The readers**
   (`orreth_sim/extract.py`, firmware-versioned `extract-v1`): PDF (pypdf, declared),
   Word/Excel/PowerPoint read with the standard library alone (they are zips of XML —
   the text is in the XML), HTML stripped clean (script/style dropped). A failed parse
   raises with its flaw NAMED — the park stays and says why; an eyes-needing format
   (images, audio, video) refuses honestly naming its missing eye (vision ·
   speech-to-text · frame description — the Stable's future saddles). **0068's
   redaction-at-ingest, wired**: the composed content rails run on the extracted text
   BEFORE it ever becomes a knowledge record — a refusing rule means NO knowledge is
   minted (a redaction-refusal record lands, carrying events never content; the
   artifact itself stands), a masking rule means the mind never holds the raw span;
   the sp4 audit lands either way in the «extraction» lane. **Lineage on everything**:
   the knowledge cites its pointer; a paid park's knowledge cites artifact AND park.
   **The retry list, retried at last**: a beat sweeps each floor's lot for parks the
   line can now read and PAYS them — tagged librarian-handled so the librarian's own
   lot forgets a paid park by her standing law; two a beat, storms refused. The drop
   zone joined the line too (admit_upload extracts PDF and kin, rails at the door).
   *Proven live on the rig: a real Word file imported and EXTRACTED
   (docx-extract-v1, paragraphs counted); a billing doc with a card number REFUSED
   AT THE INGEST RAIL in the same job — no knowledge minted, the refusal record
   holding zero card digits, the audit on the log; and THE MORNING'S DARK PARKS
   swept — the fake site-plan.pdf honestly unpayable («Stream has ended
   unexpectedly», the park stands), and the 1.1 MB AWS PDF imported from S3 this
   morning PAID WHOLE: 100,391 characters extracted, the knowledge deriving from
   artifact AND park, the chain reading knowledge → pointer → origin
   {store: jb-documents, key: choosing-the-right-aws-service…pdf} on the signed
   log.* Suite 537→545 (eight extraction laws); pypdf declared. *Honest
   remainders: OCR/ASR/frame eyes await their Stable saddles (the parks name
   them); knowledge bodies cap at 2000 chars by the standing claims law — the
   full text serves retrieval through the chunk law's projections (0065), whose
   ingest-side join is sp4-of-this-dive's wiki territory; scanned PDFs without a
   text layer refuse toward the eye, honestly.*
4. **sp4 — The wiki.** ✅ **LANDED 2026-09-10 — OpenKB's skeleton, openwiki's
   conscience, Orreth's law.** **Grounded claims** (`orreth_sim/wiki.py`): every
   material statement a signed record citing its EVIDENCE (a content-addressed id —
   the id IS the version) and its ORIGIN; deterministic sentence-claims as the honest
   v1 (a voiced summary is a later garnish, never a replacement for the chain).
   **The taxonomy**: origin pages (one per artifact, rebuilt as SIBLINGS when the
   claim set moves — never edited), concept pages (terms recurring across ≥2 distinct
   origins, the one-term law's own tokenizer), the catalog; **the link whitelist**
   kills hallucinated cross-references at validation. **THE PURGE CASCADE RUNS
   THROUGH CLAIMS**: the cascade READS THE LAW — 0026's seal records are the signed
   death notices (never a door-probe, so a dark wire can never be mistaken for a
   death — the 0042 blindness law made structural); a sealed origin's claims retract
   on their own worldlines, every current page wearing one FLAGS (page_status refuses
   «current» until an explicit recorded rebuild — openwiki's refusal, mechanical),
   and the rebuild NAMES the retraction, deriving from page AND flag. **The
   Hierarchical tree fed at last**: `stacks.pointer_text_reader` — a settable hook
   the worker aims at the object store + the extraction line — makes a pointer
   record's derived text the WHOLE document, so 0065's chunk/tree projections cut
   full documents, not 2000-char claims; and the walk found ITS OWN WOUND — the raw
   full text was entering the projection AROUND the ingest rail that had protected
   the knowledge record (the card number reachable through re-derivation) — the
   rails now ride the hook itself (refused text never becomes rows; masked spans
   never serve), the tainted rows truncated, the 0065 hash-drift law refusing any
   stale survivor. **The librarian answers through the wiki**: her grounding facts
   carry the catalog's heads and live claims each wearing its evidence ref — claim
   chains as citations, never bare prose. *Proven live on the rig: claims minted
   with evidence+origin cited; origin pages + concept pages + the catalog built and
   REINDEXED by the beat; a real purge card sealed one origin's knowledge
   (containment active, quorum honestly held at 1-of-2 for destruction) and THE
   CASCADE FIRED — 1 claim retracted, 4 pages flagged, the flags answered by
   rebuilds naming the retraction; 14 whole documents cut into the standing
   projection under the rail.* Suite 545→553 (eight wiki laws + the seal-read law).
   *Honest remainders: the pull-filter wound's THIRD strike paid (artifact-pointer
   joins the keep list) but the capped pull's recency window still gates WHICH
   pointers chunk — an import-time cut is the seed; page prose is deterministic
   claims (a governed voiced summary awaits demand); the wiki view's sweeps ride
   the governed retrieve (a projection when volume demands).*
5. **sp5 — The database kind + the standard.** ✅ **LANDED 2026-09-10 — the query
   citizens arrive, and the three-numbers lie dies measurably.** **The `database`
   kind**: schema-aware, READ-ONLY FIRST — sqlite as the on-premise citizen (stdlib,
   zero deps; PostgreSQL/MySQL recognized growth, refused by name); the read law
   DOUBLE-LOCKED (mode=ro connections AND a one-statement SELECT/WITH gate that
   refuses before a byte moves, one face); rows capped honestly; the same two-keeper
   onboarding card routes by URI (a sqlite wire charters and plants as `database`
   with schema·query as its pinned manifest). **The embedding standard tells ONE
   truth (L3)**: the stacks-embedding asset declares model + dims — genesis
   MULTILINGUAL by the lock (`paraphrase-multilingual-MiniLM-L12-v2`, ~50 languages
   at the plane's own 384 dims; the ~100-language models are 1024-dim and wait on a
   column migration, named); `meaning` reads the DECLARED model (the shelf's head
   aims the live axis within the minute); **the migration machinery the survey found
   missing**: every vector row now WEARS its model (the plane's embeddings table
   grew the column; both doors carry it), the missing-door lists absent AND
   wrong-model rows, and the chunk policy wears the model too — a turn re-cuts and
   re-embeds the world at the sweeps' own pace, loud, resumable, never a spike.
   **The `resting` twin PAID**: the Python reference's state machine matches the
   plane's at last (probation/serving→resting, resting→probation·decommissioned;
   beats never wake the resting). *Proven live on the rig: site-materials.db
   onboarded through the SAME card (allen's charter + charlotte's `database` wire →
   serving on earned beats); the schema read and a real SELECT served through the
   one metered door; INSERT/DELETE/PRAGMA and off-manifest ops REFUSED one-faced
   (the Refusal un-wrapped from the dead-stall dressing in the same hour); and THE
   GREAT RE-EMBEDDING BEGAN — 31,525 rows visibly «(pre-standard)» by name, 291
   re-embedded under the declared multilingual model within minutes, 64 a beat.*
   Suite 553→558 (five database laws + the resting twin) + Rust 24 (the model-aware
   doors). *Honest remainders: PostgreSQL/MySQL wires await their walk; the Mirror's
   similarity threshold retuned to the new model's cosine range (thresholds are
   model-relative — named); fastembed's POOLING for this model changed across
   library versions (JB's log find) — a future library flip would shift vectors
   without a name change; pin deliberately when it matters (noted in the standard
   itself); the full migration runs for hours at beat pace by design.*

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
