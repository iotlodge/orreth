# 0071 — The Doors That Answer

*Drafted 2026-09-09 from the orreth-EnterpriseRAG proof's charter — the proofs era's seventh
kernel dive, opening Wave 3 (the surfaces): the agents channel, the external API, the
librarian's selector, and the payment of the proof's KCR-0001 (the publishable join door).
Grounded in the join-door/queue/limits survey of 2026-09-09 (Appendix A).*

***Status: 🟡 DRAFTED · LOCKED — all three locks taken by JB's word, 2026-09-09, plainly
stated per the language law: L1 PAY THE QUEUE WOUND NOW (authenticated filing and
resolving, validated statuses, the meter door demanding its token — the forgery hole
closes before any channel opens) · L2 the delegate-credential join door APPROVED (root
signs once at setup and never leaves the operator's safe; KCR-0001's payment design) ·
L3 the traffic law APPROVED (per-identity rate ceilings with dials + deliberate size
limits, at kernel and worker doors alike).***

## 1. The demand, verbatim (the proof's charter)

> Channel 2 (Agents): *"This 'channel' is what all residents and workforce agents leverage
> in fulfillment of Objectives, Intentions, Observations, Thoughts. Request data, get
> data."* Specialized agents may pass the variant; Auto when not passed.
>
> Channel 3 (API): *"works much the same way as 2 with exception of any needed external
> security… Yes this uses our DID architecture as defined by laws/policies. Please ensure
> that human/service/app can detect the variant used in the reply."* Single-shot: *"you
> ask, you get"* — with schema/attributes to alter the how. The test-API button rides the
> canvas (Dive VIII renders it; the contract ships here).
>
> Channel 4 (Librarian): the selector across Auto and the eleven variants in the librarian
> chat windows.
>
> Caching is charter law on the API lane (addendum 3). KCR-0001: a stranger's deployment
> must be able to complete a governed admission.

## 2. The problem — what the survey found

1. **There is no ask door for machines.** `kind:"ask"` does not exist; the SDK offers only
   `join` and a fire-and-forget `gather` (the response is discarded — an agent cannot even
   find its own request afterward). The parlor door *works* and is machine-callable — but
   it is unauthenticated, binds no DID to the asker, and answers in prose with the choice
   ref truncated to eighteen characters inside a sentence.
2. **The queue is a fully open transport.** `POST /requests`, `GET /requests`, and
   `POST /requests/resolve` take no token, no signature, and no status validation —
   anyone who can reach the port can **approve a staged join or forge a lease token into a
   result**. `POST /model/meter` is likewise unauthenticated: anyone can credit or debit
   any subject's fuel. 0047 declared A2A "tokened, budgeted, human-visible" — the survey
   scored it one-for-three.
3. **Rate limiting does not exist, at any layer.** No body limits, no concurrency caps,
   no per-DID or per-endpoint accounting anywhere. The fuel clause meters *cognition
   tokens* only — a joined agent can file ten thousand requests a second and the ledger
   never moves.
4. **The join door is un-publishable, precisely.** The desk logic is pure and extractable;
   the wound is key custody: minting a floor becky **requires the root private key
   in-process** — there is no constructor that adopts a pre-issued delegate credential.
   And the published compose ships no worker at all: a stranger's joins sit pending
   forever. The standing welcome lives in a JSON file no purge can reach; no signed record
   of an admission is ever written by becky's side.
5. **The good news is real:** `craft_serve` is a working, token-verified, DID-bound,
   prod-postured door outside the plane — the exact template a governed answer door should
   copy — and `window-ask` already returns the richest envelope in the kernel (reply, the
   answering DID, typed citations with fidelity, the provenance window, the judgeable
   exchange ref). The seam is extension, not invention.

## 3. The shape

### 3.1 The ask door (plain words first)

**In plain words: one new kind of request — "here is my question, answer it with your
governed retrieval" — that any agent, the librarian's window, and the external API all use.
The asker is a known identity; the answer comes back as structured data: the reply, the
citations, which of the eleven architectures served it, the decision record behind that
choice, and which guardrail set governed it.**

- `kind:"ask"`: DID-bound and token-authenticated (the `craft_serve` template: verify the
  becky-chained lease, subject must equal the asker, prod refuses tokenless, one-face
  refusal). Body: `{text, variant?, attributes?}` — variant absent means Auto;
  `attributes` is the charter's "schema/attributes alter the how" (top-k, effort class,
  output-shape hints), validated against the registry.
- **The envelope extends `window-ask`'s proven shape**: `{reply, by, citations[],
  variant, choice_ref (a whole ref — the kernel's own no-truncation law finally honored),
  guardrail_set_version, exchange, cost}`. The record is the source of truth; the
  envelope is its projection (0065 §3.5's law) — so the canvas, the API, and the
  librarian's voice all read the same facts.
- **The SDK grows `ask()`** — file, poll, return the envelope. The librarian's chat
  windows surface the selector (Auto + the eleven) and ride the same door. The parlor
  remains the human's *audience* door (personality, conversation — Dive VI's thread);
  the ask door is the machine's *data* door. Single-shot both lanes: you ask, you get.
- **Caching lands here** per the charter law: the semantic ask-cache keyed on the ask +
  variant + guardrail-set version — a hit under a changed guardrail version revalidates;
  purge and recall reach the cache because it is a projection of records.

### 3.2 The queue learns who is speaking (staged as L1)

0047's unpaid promise, paid: **filing** an ask binds the asker (DID-signed intent for
agents/API; the glass's walk-up files through the worker wearing the floor or person seat
— 0070's registry); **resolving** becomes an authorized act — approvals, denials, and any
resolution carrying a token or consequence verify a seat entitled to speak them; the
plane validates status transitions instead of accepting any string; and **`/model/meter`
demands the same token `authorize` already checks.** The one-face law holds at every new
refusal. The queue stays human-visible — what changes is that *writing* to it stops being
anonymous.

### 3.3 The traffic law (staged as L3)

Per-DID request-rate limits at the doors — a new, deliberate law distinct from the fuel
clause (fuel meters *thinking*; this meters *knocking*): windows and ceilings as dials,
enforced at the plane and the worker doors alike, with deliberate body-size limits
replacing the accidental defaults. The external API cannot stand without it; the internal
doors deserve it too.

### 3.4 The publishable join door — KCR-0001 paid (staged as L2)

**In plain words: a small program an operator runs beside their own kernel, holding only
its OWN key — never the root's. At setup, the operator's root signs that key's credential
once; from then on the door can challenge joiners, verify their proofs, wait for the
human's click, and mint properly chained leases — while the root key stays in the
operator's safe.**

- becky grows the missing constructor: **adopt a persisted keypair + a pre-signed
  delegation credential** instead of requiring the parent key in-process. The root signs
  once, offline; the door holds a delegate.
- The door ships with the SDK (`python -m orreth_agent.joindoor`): the pure desk state
  machine (already extractable), the poll/resolve loop, lease dials, the capacity
  confession — and it rides §3.2's authenticated resolve like everyone else.
- Two honesty upgrades ride along: **the standing welcome becomes signed records** on the
  floor (rebuildable, purge-reachable — the JSON file retires), and **becky's side finally
  writes the admission record** (the joiner's birth memory stops being the only witness).
- The compose example grows the door as a service — a stranger's world completes a
  governed join with published artifacts only. The wound KCR-0001 named, closed.

### 3.5 The variant seam, finished end to end

0065 promised it, 0066 designed the choice record, this dive serves it: the answer record
wears the variant (the arm-tag pattern), the envelope carries it typed, and every channel
— canvas, API reply, librarian voice — reads the same selection off the same record.
"Detect the variant used in the reply" becomes a field, not an archaeology.

## 4. The razor applied (plain words in parentheses)

| Layer | Class |
|---|---|
| The ask kind + envelope, queue authentication, the rate limiter, the join-door constructor (the doors themselves) | **Firmware** — release |
| Lease terms, ask attributes' bounds, welcome policies (what operators tune) | **Craft & dials** — gated, versioned |
| Rate windows, cache TTLs, body limits (numbers with limits) | **Dials** |
| Asks, answers, admissions, welcomes, cache entries (what happened) | **Records & projections** — signed, purge-reachable |

## 5. The locks (staged for JB, 2026-09-09)

- **L1 — pay the open-queue wound now**: authenticated filing and resolving (the forgery
  hole closed) versus staged or parked.
- **L2 — the join door's key custody**: the operator-run door holding only a delegate
  credential the root signed once — root never leaves the operator's safe.
- **L3 — the traffic law**: per-DID request-rate limits as a new door law with dials.

## 6. The spoonfuls (proposed order)

1. **sp1 — The resolve door locks.** Authenticated resolution + validated statuses +
   `/model/meter` authenticated; the glass rides the worker's seat. Suite: a forged
   approval refused with one face; a forged lease result impossible.
2. **sp2 — The ask door.** `kind:"ask"` + the envelope + SDK `ask()`; the librarian
   selector rides it; the variant/choice/guardrail fields served whole. Suite: an agent
   asks and reads the envelope; the choice ref opens.
3. **sp3 — The join door ships.** The adopt-a-credential constructor; the standalone
   door; welcomes as records; becky's admission record; the compose example grown.
   Proven by a stranger-shaped walk: published artifacts only, one governed join, twice
   (the second on the standing welcome).
4. **sp4 — The traffic law.** Per-DID limits + deliberate body limits at plane and worker
   doors; dials; the API posture (prod refuses tokenless everywhere the craft door
   already does).
5. **sp5 — The cache.** The semantic ask-cache as a projection: hit/revalidate/purge
   proven, guardrail-version revalidation live.

## 7. The honest boundary rows this dive moves

- The becky-lite wound (on file since the proofs era opened): **paid** — a stranger's
  governed join with published artifacts, walked.
- The open-queue rows: from unwritten danger to named-and-paid (filing, resolving, and
  the meter door authenticated).
- New rows: the ask door + envelope (proven by an agent's walk); the traffic law; the
  cache's honesty (revalidation on guardrail change, purge reach).
- Parked honestly: push/streaming delivery of answers (polling stands; the park rides the
  standing streaming lock); cross-ecosystem entitlement asks (0027 §7's horizon).

## Appendix A — evidence trail (survey 2026-09-09)

The desk pure + keys worker-side (`joindoor.py:30-85`, `console_worker.py:190-253`); root
key required in-process, no adopt-constructor (`identity.py:74-79`); compose ships no
worker (`infrastructure/compose.yaml`); the welcome file (`console_worker.py:1407-1433`,
`14148-14191`); the open queue (`main.rs:1525-1595` — unauthenticated file/read/resolve,
no status validation) and the unauthenticated meter (`main.rs:857-863`); zero rate
limiting (no tower limits; axum defaults; worker `ThreadingHTTPServer` uncapped); the
fuel clause's true scope (`model.rs:268-295`); 43 request kinds inventoried (the worker's
dispatch chain `console_worker.py:14087-14417`); no `kind:"ask"`; `gather` fire-and-forget
(`client.py:210-212`); the parlor as the nearest door (`console_worker.py:8787-9228`,
envelope `:9177-9180`); `craft_serve` the authenticated template
(`console_worker.py:11773-11807`); `window-ask` the richest envelope
(`console_worker.py:13574-13580`); the truncated choice ref (`:6653-6654`) vs the kernel's
own no-truncation law (`:13598-13603`); 0047's A2A prescription (`0047:165-174`).
