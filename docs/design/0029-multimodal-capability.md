# 0029 — Multimodal Capability (documents & images)

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §12 — JB's addition, placement
confirmed in the same pass). The dive's last spoonful: the universe learns to
receive, understand, and eventually create documents and images — through the
organs it already has, never around them.*

---

## Why this is a keystone

A universe that can only eat text is half-blind. §12's requirement: upload documents
and images in many formats, create them, and give agents recognition/OCR
capabilities. The placement insight (JB's Stable instinct, confirmed): **a vision
model is not a tool; it is a mind with a lifecycle** — and a format converter is not
a mind; it is a service with a manifest. The universe already has a home for each.

## 1. Placement — split by nature (§12, confirmed)

- **Models are minds → the Stable (0019).** OCR, vision, embedding, and generation
  models saddle like any mind: DEAL pinned, metered per agent, price-drift watched,
  EOL on the pasture calendar.
- **Converters are services → the Farm (0018).** Deterministic format pipelines
  join as manifest-pinned, keeper-tended tools.
- **Agents reach both through skills** (`read-document` · `describe-image` ·
  `generate-figure`) — the chassis never knows the difference.

## 2. Upload is an ask — no side door for files

The human hands a file to the **Librarian**: her workspace (0028) grows a drop
zone, declared on her calling card (`accepts: ["upload"]`) so the glass stays
generic. The drop becomes a `kind:"upload"` request on the queue — human-visible,
vigil-seen, like every ask. The Librarian admits it with her own authority:

- **The artifact record**: the bytes land content-addressed (`ingested-archive`
  provenance, the store is modality-blind — 0022), tagged `artifact`.
- **The extraction record**: what the modality yields as TEXT, written as
  knowledge **derived from the artifact**, `untrusted`, **quarantined at 0.0000**
  like all outside knowledge (0014). The scanned page becomes retrievable
  knowledge, not a dark blob.

## 3. The keyless floor, and the parked eye

Extraction runs at the best rung available (degrade-where-pins-allow, 0010):

- **Text-bearing formats** (txt · md · json · csv) extract deterministically —
  instant, free, the keyless floor.
- **Formats needing an eye** (images, scanned PDFs): when no vision mind is
  saddled, the artifact is admitted honestly DARK and the Librarian **parks an
  extraction intent** (0014/0015 — failure is fuel): the moment a vision mind
  saddles on the Stable, the parked assignment is the retry list. The universe
  never pretends to have read what it cannot read.

## 4. Creation — deferred, doored

Document/image *generation* minds saddle on the Stable when fueled; the workspace
doc panel (0028) is already the rich-output surface. Nothing lands this spoonful
beyond the door being named. (Ledger.)

## 5. What lands this spoonful

| Piece | Where | Status |
|---|---|---|
| Upload-is-an-ask: drop zone (card-declared) → `kind:"upload"` | glass + worker | this dive |
| Artifact + extraction records, quarantined; parked eye for dark formats | sim `artifacts.py` + worker | this dive |
| `read-document` skill (chassis binds extracted knowledge) | sim | this dive |
| Pinned-organ roster fix (rule-7 drift, JB 2026-07-11) | plane `residents()` | this dive |
| Vision/OCR mind saddled on the Stable | ada's gate — when JB stages one | deferred |
| Converters planted on the Farm | 0018 machinery — as needed | deferred |
| Generation minds + multimodal RAG (meaning axis per modality) | 0022 P2 / model plane | deferred |

## 6. Decisions

**Pre-confirmed (§12 pass):** minds→Stable, converters→Farm, skills as the reach ·
upload-is-an-ask, quarantined 0.0000 · store stays modality-blind.

**Closed by the design owner (JB may veto):** two records per upload (artifact +
extraction, lineage between) · extraction at the keyless floor first, minds when
saddled · the drop zone is card-declared (0020's decoupling kept).

**Locked by JB (2026-07-11, AskUserQuestion):** the v0 bars are **256KB · txt /
md / json / csv / pdf / png / jpg** — beyond them, the uniform refusal · dark
formats are **admitted dark + the extraction intent parks** (0014: failure is
fuel; the parked list IS the retry list when an eye saddles) · this spoonful ships
the **keyless floor**; a real vision mind saddles at JB's gate (0019 staging, his
spend, his moment) — the parked assignments will be waiting.

---

*The universe opens its hands: what you give it, it signs, quarantines, and learns
to read — and what it cannot read yet, it honestly parks until it grows the eye.* 🥂
