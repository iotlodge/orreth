# 0021 — The Shipyard: a universe that grows by conversation

*Drafted and landed 2026-07-07 by Fable 5 (claude-fable-5), from JB's vision drop the same
evening: "can you add it so it builds a true docker container of an ecosystem? … please
include something like 'would you like one or more fields for ecosystem.foo'… please please
ensure Human has smooth transitions between the Planes of view as their Universe expands."*

---

## §0 What it is

**0009's provisioner, first wire landing — dev-rig grade.** A human asks becky, in the
parlor, for a new ecosystem. The shipyard drafts a launch plan; the plan waits at the
human gate (0012 — growing the universe is consequential); on LAUNCH, real containers
come up on the rig's own network. Each new floor is the same one binary under a
generated TierProfile (0000: tier = a profile), pulls its parent's floors at boot, and
beats into the orrery by itself — **the topology was always assembled from heartbeats,
so a new world is just a new heartbeat.**

## §1 The conversation is the interface

```
you    · create ecosystem retail
becky  · laying a hull for e:retail — would you like one or more fields for it?
you    · create ecosystem retail with fields web, pos
becky  · staging e:retail with field(s) web, pos. consequence waits for you at the gate.
         [Requests tab: "the shipyard drafted: e:retail on :4503 with web:4504, pos:4505"]
you    · [LAUNCH]
         → u:demo/e:retail :4503 · …/f:web :4504 · …/f:pos :4505 — live, beating, visible
```

Flow-control words travel **verbatim** — a governed voice may phrase facts, never
rewrite a question or a staging confirmation (learned live: the voiced pass once
paraphrased the fields *question* into an "as is" *statement*; `verbatim: true` now
pins protocol language).

## §2 The pieces

- **Brain** (`orreth_sim/shipyard.py`, pure): name validation (lowercase-kebab — slugs
  travel in DIDs, DNS, paths), port allocation around whatever is taken, TierProfiles
  generated with the same dials the composed rig boots with (eco P395D, field P90D,
  same trust root).
- **Grammar** (`orreth_sim/parlor.py::parse_grow`): create/add/grow/new/build ecosystem
  X [with fields a, b | as is]; missing fields → becky ASKS before anything stages.
- **Dock crew** (`console_worker.py::Shipyard`): stages on pending, launches on
  approved (`docker run` on the rig network: same image, mounted profiles, per-hull
  bodies volume, `--parent` by container DNS, shared Postgres), ledgers every hull in
  `~/.orreth/shipyard/floors.json`, **replants** hulls the rig lost at worker boot, and
  the worker tends every dynamic floor's queue — charlotte, ada, the parlor, organ
  pins, all of it, automatically.
- **Lifecycle**: `dev.sh stop` removes dynamic hulls with the rig (they ride its
  network); the ledger + replant bring them back on start. `dev.sh status` lists them.
  Since 2026-08-28 `stop` also writes a rig-level down word
  (`~/.orreth/shipyard/rig-down`) that the launchd keeper's `replant` honors — a
  whole-rig stop is the human's word, never a wound to heal — and rests (never
  removes) the `orreth-body-*` tool containers; `start` lifts the word, re-ties each
  body to the fresh rig network, and wakes it. `dev.sh status` shows all three
  container families beside the ledgers that govern them.

## §3 One glass, every floor

JB: "I have to go to 3 separate URLs to see just my 1 ecosystem and 1 field." No more:

- Every floor's beat now carries its **port**; orrethd opens **CORS** (dev rig —
  capability, not origin, remains the boundary: every cross-floor call still meets the
  token checks and the uniform refusal).
- The Console aims every call through a switchable base: **click any world** — rail row
  or orrery body — and the same glass becomes *that floor's* view. Descents push
  **breadcrumbs**; the trail climbs back. The spectator shim matches on pathname, so
  the demo snapshot behaves identically.
- And the orrery **holds its breath while you look**: orbits pause under the cursor,
  so a hover card can finally be caught.

## §4 Honest limits (the dev-rig grade, named)

- The gate's approve click is still unsigned queue plumbing (0012 signer registry —
  the same residual as farm/stable/join gates).
- Scale-out is one hull per `docker run` on one machine — 0009's real provisioner
  (templates, fuel, hibernation, BYO-key) remains the product path; this is its
  proving ground.
- Dynamic floors default to the demo trust root and the rig's shared Postgres;
  per-universe DIDs and isolation arrive with the multiverse dive (vision discussion
  open with JB — Orreth.ai portal, opt-in visibility, flight-deck landing).

## §5 Decisions taken (design-owner calls)

1. Name: **the Shipyard**; hulls and moons; "sailing alone" for a fieldless eco.
2. Growing rides the parlor + request queue — no new plane routes beyond CORS/port.
3. Fields-question-first when unspecified (JB's ask, made protocol).
4. Verbatim flag for flow-control parlor replies.
