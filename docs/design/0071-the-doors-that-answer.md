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

1. **sp1 — The resolve door locks.** ✅ **LANDED 2026-09-08, the build season's first
   brick.** The two-lane law in the plane (tokenless = the joiner's nonce answer alone,
   result keys held to {nonce, proof}; everything else demands the root-chained pen);
   transitions became law (terminal statuses immutable — "a settled word is never
   rewritten"); `/model/meter` demands the authorize door's own token with subject match,
   and the credential is stripped before the ledger keeps the entry. **The pen is a NEW
   narrow action — `resolve` on the `queue` space — added to the sacred token grammar by
   JB's explicit rule-9 word (2026-09-08)**, so the queue's pen never requires `govern`
   (the shred-lever class). The worker mints its pen once at the one call() choke point
   (100+ resolve sites untouched); the glass rides the worker's new `/resolve` door;
   capability specialists and trusted crew (the studio) re-mint with the pen at becky's
   welcome while strangers stay retrieve-only; the four demo reels carry the pen; the SDK
   meters with its own lease. *Proven live on a fresh plane: five forgeries refused with
   the one face and the card unmoved · the pen resolves · the proved lane serves ·
   denied→approved refused with its teaching · the meter's three cases. 371 Python + all
   Rust green; the register row landed in this commit.* *Honest remainders → later
   spoonfuls: filing still unauthenticated (sp2's ask door + sp4 bind the asker);
   done→done idempotent races now surface as 409s (rare, loud, acceptable); the bare-
   kernel Inbox's approve buttons now honestly require the worker's road — the book's
   first-world page mentions Approve and gets its note at the dive's close per the
   release-alignment law.*
2. **sp2 — The ask door.** ✅ **LANDED 2026-09-08.** One design amendment made at the
   drafting table: the ask files on the PUBLIC queue, so it authenticates by
   **signature, never bearer** — a lease token in a queue row would be a stealable
   credential; the asker signs {did, text, at} with its own key instead (sp4's
   filing-authentication, begun early for this kind). The pieces: `orreth_sim/askdoor.py`
   (the law: verify-by-DID, the envelope with refs held WHOLE — a builder that *refuses*
   a shortened id); the dispatcher's `force` (the asker's chosen row, Auto standing
   aside, the choice still a signed record saying who chose — and an unbuilt choice
   still falls loudly); `wire_stacks_answer` (the ask path made structured; the old
   prose face kept byte-shaped for the parlor and yardstick); `on_ask` in the worker
   (signature → standing-welcome check → answer → a signed exchange record → the
   envelope: reply · by · citations · variant · whole choice_ref · exchange · cost ·
   guardrails-confessing-honestly-until-0068); SDK `FieldClient.ask()`. Dev grace
   mirrors the craft door for UNSIGNED asks only — **and the live walk earned its keep:
   a present-but-invalid signature rode the grace lane on the first run (an imposter
   signing the victim's DID was served with a confession); the hole was closed the same
   hour — a failed signature is a forgery attempt and refuses in every mode, one face.**
   *Proven live on the rig: scout-from-outside rejoined on its standing welcome and read
   a whole envelope (Auto chose «rerank», the choice ref opened); «graph» chosen by the
   asker and confessed in the reply; the forged ask denied with the one face; an unknown
   variant refused with a teaching naming the standing rows. Suite 371→379 (eight
   askdoor laws).* *Honest remainders: answers ride the public queue result exactly as
   parlor replies always have — authority-scoped answers arrive with 0072's build + the
   person registry; attributes are received and confessed unhonored until the registry
   dive (0065) gives them meaning; the librarian window's visual selector is Dive
   VIII glass — the door it will ride is this one.*
3. **sp3 — The join door ships.** ✅ **LANDED 2026-09-08 — KCR-0001's machinery, built
   and walked.** The pieces: `Becky.adopt` + `mint_delegation` in the reference (the
   root signs a delegate's credential ONCE, offline; the returned bundle carries the
   delegate's seed and cert — never the root's key; an adopted becky issues, the plane
   verifies against the pinned root as always); the SDK's `orreth_agent/joindoor.py` —
   `mint` (run where the root lives) · `serve` (the desk twin: challenge, verify,
   stage, mint; a restart re-challenges; an approval without a proven key mints
   nothing) · `pending`/`approve` (the operator's word from their own terminal); the
   SDK's crypto grew its verify half (vendored). Two honesty upgrades from birth: **the
   STANDING WELCOME is a signed record on the floor** (the standalone door has no
   private file at all; the rig worker now writes the record beside its cache) and
   **becky's side writes the ADMISSION record** — the joiner's birth memory stops being
   the only witness. *Proven by the stranger walk: a fresh world from the door + the
   SDK alone (no worker, no repo imports beyond the package) — credential minted with
   the root key never leaving its file; one governed join end to end (challenged →
   proved → staged → the operator's CLI word → a lease that WORKS: remember + recall);
   a second join honored by the welcome RECORD with no click owed — and the walk's own
   find fixed in the hour: the final resolution had been clobbering the "approved by
   your standing welcome" line, so the WHY now survives the minting, door and rig
   both. Suite 379→384 (five delegation laws: the bundle carries no root key; the
   adopted door's issues verify at the root; a foreign root's credential refuses; a
   cert for someone else's key refuses; only the root mints a door).* *Honest
   remainders → the dive's close, per the release-alignment law: the SDK republishes to
   PyPI carrying the door; the compose example and the book's first-world page grow the
   door service; the GHCR image republishes with sp1's locked plane. A session note for
   the record: the safeguard classifier flagged one in-flight chat message during this
   spoonful's build (`[cyber]` — the hardening vocabulary reading as offense); no work
   was lost, no other model ran, and the prose stays matter-of-fact hereafter.*
4. **sp4 — The traffic law.** ✅ **LANDED 2026-09-08 — knocking is metered, per identity,
   inside the operator's ceilings.** The law itself is one page of counting
   (`orreth_sim/traffic.py`): a fixed window per caller — under the ceiling every knock
   serves; at the ceiling the answer is «the door is busy for you — try again shortly»
   with an honest `retry_after_s`; identities never share a ledger line (one caller's
   flood never slows another); limit 0 is the operator's open door; a sweep forgets dead
   callers only. Both halves of the boundary enforce it: **the plane** (`knock()` +
   `too_many()` in `main.rs`, wired into egress, model authorize, model meter, resolve,
   and submit — keyed by the token's subject or the filer's DID) and **the worker**
   (`do_POST` gates every request BEFORE reading the body: a 413 body ceiling, then the
   per-DID 429). Body limits stopped being axum accidents: the plane wears
   `DefaultBodyLimit` from `ORRETH_BODY_LIMIT_BYTES` (default 2 MB), the worker reads
   its ceiling from the shelf. **Two new dials** by the 0063 pattern — `rate-per-min`
   (genesis 240) and `body-limit-kb` (genesis 2048), declaration firmware, value craft,
   bounds and blast on their faces. And the craft door's prod posture reached
   `tool_invoke`: prod demands a token whose subject is the caller; dev grace confesses
   aloud. *Proven live against a strict plane (ceiling 5, body 2000): eight knocks →
   exactly [200×5, 429×3]; a second identity served 200 through the first one's flood;
   the busy face named its wait; a 4 KB body refused 413. The default-ceiling smoke
   re-ran whole — 240/min never bites an honest walk. Suite 384→390 (six traffic laws);
   Rust green.* *Honest remainders: the window is fixed, not sliding — burst-at-the-seam
   is accepted and named; the worker's book is per-process (a multi-worker floor would
   need a shared book — no such floor exists); per-scope or per-door ceilings wait for
   demand.*
5. **sp5 — The cache.** ✅ **LANDED 2026-09-08 — an answer serves again only inside the
   human's word, always confessed, never a second truth.** The law
   (`orreth_sim/askcache.py`): an answer already given may serve again ONLY for the same
   words (canonicalized — case folded, whitespace collapsed), the same variant, the same
   floor, and the same guardrail-set version — all four live inside the cache key, so a
   changed guardrail set revalidates BY CONSTRUCTION, no invalidation hooks. The cache
   is a projection, never a second truth (0065 §3.5): every entry leans on its signed
   exchange record by whole ref, and the worker checks the record ALIVE read-side before
   serving any hit — purge and recall reach the cache the way dial bounds are enforced,
   at the moment of the read. Every hit is confessed in the envelope (`cached: {age_s,
   hits, note}`); the original exchange stands as the judgeable ref. The TTL is the
   human's dial (`ask-cache-ttl-s`, genesis 300, ladder-homed — freshness is a floor's
   own word; 0 is the operator's closed cache), and grace-served answers never cache.
   `askdoor.guardrails_version()` is the one seam 0068's build replaces. *Proven live on
   the rig: scout-from-outside's cold ask answered fresh; the SAME words in different
   clothes (case, whitespace) served from the cache with the confession and the original
   exchange ref; the dial turned to 0 through the one-motion door and the same words
   answered FRESH with a new exchange; canon restored (300). Suite 390→398 (eight cache
   laws, purge-reach among them).* *Honest remainders: matching is same-words today —
   meaning-similar serving (one question's answer for a merely similar question) is a
   named horizon awaiting its own lock, a correctness risk a human weighs; the live
   guardrail turn arrives with 0068 (the law is suite-proven: the version lives in the
   key); a live purge is a human's gated click, so purge reach is proven by the
   read-side law in the suite; the book is per-process like the traffic book's;
   per-asker exchange records on cross-asker hits wait for demand.*

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
