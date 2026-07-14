# 0032 — The Serials Desk (continuous acquisition)

*Design draft — proposed by Fable 5 (design owner), commissioned by JB 2026-07-13
("continuous acquisition is core to the universe's improvement system"). Queued at
0031 §8 and unblocked by its spoonfuls: the freshness triggers (0031 §5) and the
Workshop (0031 §4) both stand. Nothing here builds until JB reads and locks.*

---

## Why this dive

A real library does not only fetch the books a patron asks for. It runs a
**serials desk**: standing subscriptions, issues arriving on schedule, the
difference between issues being the news. Orreth's knowledge loop (0014) has two
of its three modes: **directed** acquisition (a human asks; the librarian
gathers) and **triggered** acquisition (a breaker parks an intent; a freshness
trigger fires). The third mode is missing: **continuous** — the universe watching
the sources it already trusts enough to cite, so that what its residents and
workforce reason from does not silently rot.

JB's framing makes the stakes plain: the improvement engine runs on receipts
(0028); a universe whose knowledge stales is a universe whose improver optimizes
against a world that no longer exists. Continuous acquisition is not a
convenience — it is the improvement system's supply line.

The governing principle, held from the start: **continuous acquisition produces
candidate updates, never production changes.** The desk delivers; it does not
decide. Admission stays quarantined (0014), promotion stays earned, and the
standing spend that a subscription represents is gated by the human — consequence
waits (0012), even when the consequence is a recurring bill.

## 1. The subscription — a governed standing ask

A **subscription** is config-as-memory (R8): a signed, content-addressed record,
human-approved at creation because it commits the universe to standing spend.

```yaml
subscription:                    # kind: semantic, tags: ["subscription", <slug>]
  topic: str                     # the intent it keeps fresh (a domain package's spine)
  sources: [DID] | "any-serving" # named voices, or whatever the Farm serves
  cadence_beats: int             # delivery interval, counted in beats — no wall-clock dial
  budget: {tokens?, calls: int}  # per-delivery ceiling; the meter shows every delivery (0019)
  posture: "deliver" | "paused"  # hibernation is a posture, never a deletion (0009)
  approved: RequestRef           # the human's word — a subscription never self-mints
```

- **Subscribing is an ask.** `subscribe to <topic>` at the librarian's card →
  the request STAGES (0012's lane — a standing spend is a consequence). The
  human approves in the decision inbox; the subscription record derives from the
  approved ask. `unsubscribe from <topic>` retires it with a record — cancelled
  is a state on the worldline, never an absence.
- **Cadence rides the beat, not the clock.** `cadence_beats` counts delivery
  sweeps in beats (0004's universe-time posture) — no tier-profile clock dial is
  needed, so rule 9 stays untouched. A wall-clock `review_interval` dial remains
  0031's OPEN item, unchanged by this dive.
- **Out of fuel → paused, never dropped** (0009's law): a floor that cannot pay
  for its subscriptions hibernates them loudly; the desk keeps the ledger.

## 2. The delivery beat — the desk's standing duty

The librarian's desk sweeps on the beat (a standing duty like the improver's —
R8; **zero new residents**, 0031 §3's law holds):

```text
for each subscription due (cadence elapsed, posture = deliver):
  1. re-gather the topic from its sources — charlotte's serving roster only;
     a recalled source is refused at the door as ever (0026 §5 immunity)
  2. DEDUP against the domain's existing claims (content match):
       new claim        → admitted QUARANTINED at 0.0000 (0014 §3 — always)
       repeat claim     → a refresh note on the delivery — NEVER a promotion
       changed claim    → admitted quarantined + a CONTRADICTION CANDIDATE (§3)
       vanished claim   → noted on the delivery — absence is a finding
  3. write the DELIVERY NOTE: one signed record per sweep — what arrived, what
     repeated, what changed, what vanished, what it cost — deriving from the
     subscription; the desk's worldline is auditable sweep by sweep
  4. the lane: a quiet delivery is LOG (low); news — anything in the changed or
     vanished columns — wears a medium marker (0024): visible, never blocking
```

**Same voice twice is still one voice.** A repeat from the subscribed source
refreshes nothing but the delivery note — corroboration requires an independent
source (0014's law, kept absolute). The desk can never promote its own
deliveries; it can only stock the shelf for the investigation skill and the
human to act on.

## 3. The difference is the news — contradiction gets its mechanism

0031 §5 named contradiction as a freshness trigger and honestly deferred it (no
meaning axis to detect it). The desk supplies the v0 mechanism *without*
semantics: a subscribed source re-speaking on the same topic with **changed
content on the same ref** (the same URL/document saying something new) is a
contradiction candidate the desk can detect by identity, not meaning:

```text
changed claim (same source, same ref, different content)
  → the new claim admits quarantined (its own record, its own state)
  → the OLD head drops to 'investigating' via the revalidation walk
    (0031 §5 — trigger: "superseded-at-source", the pair named in the marker)
  → the medium lane notifies; the librarian's investigation skill — or the
    human — resolves which version earns corroboration
```

Nothing auto-supersedes. The desk marks; residents and humans decide. The
meaning-axis contradiction detector (claims that disagree across *different*
sources) still waits for 0022 Phase 2, stated plainly.

## 4. The charter coupling — "and keep it fresh"

An acquisition objective (0030's ladder: *"acquire knowledge of Y"*) completes
into a domain package (0031 §5). The plan gate gains one readable line: when the
orchestration seat curates such an objective, the staged plan may offer **"…and
keep it fresh"** — approving the plan with that line stages the subscription ask
at the same gate. One approval moment, both consequences legible; the
subscription still mints as its own record deriving from the human's word. The
report's domain package then names its subscription — the package and its supply
line, one picture.

## 5. Who owns what — the existing seats, unchanged

| Duty | Seat |
|---|---|
| The desk, the sweeps, the delivery notes, admission | the librarian (0023 — all knowledge, zero levers) |
| The sources' identities, manifests, the rug-pull door | charlotte (0018) |
| The standing-spend gate, subscription approval | the human, via 0012's queue |
| Consuming the receipts (fresh evidence for proposals) | grace (0028/0031) — deliveries feed `evidence()` like every record |
| Watching the shape of it all | vigil (0013) — content-blind, as ever |

## 6. Rules this dive writes

1. **The desk delivers; it never decides** — continuous acquisition produces
   quarantined admissions and candidates, never production changes.
2. **A subscription is the human's standing word** — it stages, it is approved,
   it retires on the record; out of fuel it pauses, never vanishes.
3. **Same voice twice is still one voice** — a subscribed source can never
   corroborate itself; promotion is earned by independence (0014, kept).
4. **The difference is the news** — deliveries report arrivals, repeats,
   changes, and absences; only news wears a marker.
5. **Change at the source is doubt at the shelf** — a changed claim drops its
   old head to `investigating` (0031 §5's walk), and the pair is named.

## 7. The spoonfuls

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The subscription** — the record shape; `subscribe to <topic>` / `unsubscribe` at the librarian's card (staged → the human's gate); the desk listed in her room | ✅ landed 2026-07-14 — `orreth_sim/serials.py` (make_subscription minted only from an approved ask · subscriptions() heads · set_posture as sibling versions — cancelled is a state, never an absence) · the librarian's card gains subscribe…/the serials desk chips; subscribing STAGES verbatim ("a standing spend is a consequence — consequence waits for you at the gate"), unsubscribing acts without a gate (stopping a spend is safe; the record keeps it honest) · the wire: kind `subscription` stages with terms readable (every 100 beats · 4 calls/delivery), the human's word mints the record librarian-seat-signed, deny leaves the choice on the record · her room gains the desk panel · **proven as a human in the glass**: subscribed at her card → "open the subscription" at the gate → the desk answered in her governed voice, honest that the delivery beat arrives with sp2. 3 tests, 149/149 |
| 2 | **The delivery beat** — the standing sweep; dedup; quarantined admissions; the delivery note; quiet=log, news=medium | ✅ landed 2026-07-14 — `serials.py` grows the beat's pure organs (is_due: the first issue arrives with the subscription, then cadence · dedup by content match, all four columns on the note from day one · make_delivery_note derives from the subscription · news() grades the lane · content-addressed re-arrivals count as repeats, never colliding re-writes) · the worker's `serials_beat` rides `beat_due` on every floor: serving roster only, 0026 §5 immunity at the door, the call metered, admissions quarantined with the subscription in their lineage, one signed note per sweep; a restarted worker re-seeds from the wire and waits a fresh cadence · her card and room speak the issues ("issue 1 landed: 3 new · 0 repeated") · **proven as a human in the glass**: gathered a topic → subscribed → opened at the gate → issue 1 landed within a beat at 0 new · 3 repeated (dedup live — same voice twice stayed one voice) · **a live catch**: the governed voice rewrote the quiet lane into "medium-priority issues" — the desk ledger now travels VERBATIM (the 0020 voiced-reply lesson, applied). 5 tests, 153/153 |
| 3 | **The difference is the news** — changed-at-source detection; the revalidation walk fired with `superseded-at-source`; vanished-claim notes | ✅ landed 2026-07-14 — `dedup` grows the §3 columns, by identity never meaning (content match = repeat · same-ref-different-content = CHANGED, its old heads named in `supersedes` · a subscribed-voice ref the sweep no longer carries = VANISHED, and only the subscribed voice can go quiet) · a changed claim admits quarantined as its own record while `supersede()` drops the old head to `investigating` in the revalidation walk's exact shape — trigger `superseded-at-source`, the pair named in the body and on the note; doubt never stacks (an investigating head is not re-dropped), nothing auto-supersedes · vanished is noted, never acted on — absence is a finding · the news marker names its columns ("N changed at source · M vanished") · **the cadence dial** (per §8's proposal — the dial lives on the subscription record; the default remains JB's lock): "subscribe to X **every N beats**" rides the ask → the gate shows it → the record mints with it · proven live: a 10-beat subscription on a price topic delivered issues on its own dial, honest quiet issues while the source's snippets held still (the difference signal fires only when the world moves — that is the point); changed/vanished semantics proven by test. 3 tests + the dial, 156/156 |
| 4 | **The charter coupling** — "…and keep it fresh" on acquisition plans; the domain package names its subscription | ✅ landed 2026-07-14 — `keep_fresh_offer` shapes the offer from the objective's own words ("acquire knowledge of/on/about Y" — never pressed on a plan it doesn't fit); the staged plan carries it, and the glass renders the line with a checkbox, plainly worded, **unchecked by default** (§8's proposal; the check survives the console's 4s breath via the WALKOPEN pattern) · approving with the line checked rides `keep_fresh` inside the SAME resolve — one approval moment, both consequences legible; the worker fans the plan AND mints the subscription (librarian-seat-signed, `approved` naming that very request; idempotent — one subscription, never two) · `named_supply` puts the supply line on the domain package ("kept fresh — every N beats"; a paused desk is not a supply line) — the package and its supply line, one picture · zero plane-code changes (resolve already persists `result`; the glass is the only orrethd touch) · **proven as a human in the glass**: stated "acquire knowledge of hempcrete wall insulation" → the plan staged with the offer unchecked → checked the line, fanned the plan → the worker's own words: "the plan fans AND the desk opens — kept fresh on the same word" → issue 1 delivered within a beat (3 new) → the domain package view names its supply lines live. 1 test, 157/157 — **0032 whole; §8 stays JB's** |

## 8. Decisions

**Canon per JB (2026-07-13):** continuous acquisition is core to the universe's
improvement system · it follows the design owner's lead · it lands after the
freshness triggers and the Workshop (both stand as of f513d58).

**Closed by the design owner (JB may veto):** the name — the Serials Desk, the
librarian's duty, zero new residents · subscriptions are human-gated standing
asks · cadence in beats, not wall-clock (rule 9 untouched) · same-source
repetition never promotes (0014 applied) · contradiction v0 is same-ref-changed
detection, by identity not meaning · nothing auto-supersedes.

**OPEN (JB's locks after reading):**
- **The default cadence and per-delivery budget** — proposed: 100 beats ·
  4 calls; dials on the subscription record, not the tier profile.
- **The delivery-note lane** — proposed: quiet deliveries low (log), news
  medium; may a *persistently* changing source escalate to high on its own?
- **Auto-offer "keep it fresh"** — on every acquisition plan, or only when the
  human asks? (Proposed: offered on every acquisition-shaped objective, plainly
  worded, unchecked by default.)
- **The subscription quota** — how many standing subscriptions may a floor
  carry before the ask escalates? (Proposed: a Tier Profile concern for the day
  it matters; v0 relies on the human gate.)

---

*A library that only answers questions is an archive. The desk that keeps the
subscriptions is what makes it a living one — and a universe that improves
itself had better be reading the news.* 🥂
