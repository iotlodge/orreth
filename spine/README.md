# The Spine

The new line's transport home (canon `docs/rearch/0002`): the ground
(Postgres), the invocation rail (RabbitMQ), and the events rail (Kafka),
plus the shared envelope every message wears.

## Breathe the rig

```bash
cd spine
docker compose up -d          # the three services (ground on host port 5433)
uv sync                       # install
uv run python -m orreth_spine.heartbeat   # one breath through each rail
```

A healthy rig prints a checkmark per rail with its latency; any failure
names itself and exits non-zero.

## Test the laws

```bash
scripts/dev.sh suite          # the whole suite (885 laws, three to five minutes) — the rig up, no Bridge or kernel lit
uv run pytest -q tests/test_envelope.py   # the envelope laws alone need no rails
```

ONE rig for the whole session (canon 0005, lock 5, 2026-09-27): `tests/conftest.py`
lights it at the first test that asks for `rig` and stops it whole at the end. A test
that serves its own bodies on the session's benches never races that rig's crew,
because THE RIG YIELDS — every test that does not ask for `rig` parks it for its turn
(`BridgeRig.park`: the dispatcher passes every fact by, the crew stand off the
benches, the beats hold) and the next test that asks resumes it. The test-side
dispatcher (`dispatch_once` → `projector.run_once`) ends when the topic is read to its
end, never by waiting out a silence. A Bridge or a Rust kernel lit beside the suite
poisons it (the stale-rig law; `dev.sh suite` refuses to start).

## What lives here (so far)

| Piece | What it is |
|---|---|
| `compose.yaml` | The dev rig: postgres:16 (5433) · rabbitmq:3.13 (5672/15672) · apache/kafka:3.9.1 KRaft (9092) |
| `orreth_spine/envelope.py` | orreth.transport/1 — canonical bytes, content hash, required fields, authority chain |
| `orreth_spine/rails.py` | One breath per rail; the ground writes heartbeat + outbox in ONE transaction from day one |
| `orreth_spine/heartbeat.py` | The runnable proof: `the rig breathes.` |

The RabbitMQ management console is at http://localhost:15672
(orreth / orreth-dev) if you want to watch the queue by eye.

## The bodies as processes (P7 sp6, the bodies' seam)

The kernel spawns and governs every body as its own process. The crew is ONE
manifest, `crew.v0.json`, read by both spines: the Python Bridge (`glass.py`)
seats it in-process as the reference; the Rust kernel (`spine-bridge`,
`scripts/dev.sh shadow`) spawns one process per seat. Beside it, `tools.v0.json`
declares the built-in tools (name · words · schema · class · flags) — data both
kernels read; each kernel seeds the shelf from it and probes a built-in itself,
while a tool's execution stays in the body (`tools.py` binds each name to its
executor and refuses to start when a declaration has none):

```bash
.venv/bin/python3 -m orreth_spine.body --template templates/echo-resident.v0.json         # one body, standing alone
.venv/bin/python3 -m orreth_spine.body --template templates/workspace-firmware.v0.json --binding bindings/crew.v0.json
```

A body joins as the same self every life (its seed under `~/.orreth/agents/<name>/`),
keeps its lease while it serves, streams its words to the kernel that spawned it
(`SPINE_KERNEL_DOOR`), serves the kernel's harness command on its bench, and stops
whole on SIGINT. The kernel restarts a body that died (1 s, doubling, capped at 30),
PARKS one that dies three times in five minutes (a fact, `orreth.body.parked.v1`;
"restart the <name> body" is the human's lever), never restarts a refusal, and stops
every body at dark. Dials: `SPINE_BODIES` (crew · none) · `SPINE_CREW` (another
manifest) · `SPINE_PYTHON` (another interpreter) · `SPINE_BODY_EPHEMERAL` (tests).

Beside the tools stands `levers.v0.json` — THE LEVER CATALOGUE (P7 sp8 row 3c, the
remediation rail): every governed act the kernel itself can pull, declared as data
(`name · description · needs · consequence · for · doors · settles_s`) and read by both
kernels (`GET /levers`). When a watch goes red the kernel reads the ground first — the
watch, who it names and their state, the last acts on them, the last time it went red —
and hands the planner that dossier with the levers this door serves; the planner answers
IN the catalogue ("LEVER: body.restart name=echo — BECAUSE: …"); the kernel pulls the
lever with its own hands as a recorded hop in the intention's session (a routine lever at
once, a consequential one held for a person's click), then reads the watch again and
says what happened: cured with its cause · self-healed · still red (once more, then the
human with the dossier) · cancelled. The eleventh world check grades it: every red
answered, every green attributed. `SPINE_FAKE_REPLY` scripts the fake mind's one line for
a proof.

## Cells (P7 sp7 — cells · partition · isolation · hardening)

A CELL is one universe's physical home: its own kernel self, its own database
and role (a role that reaches no other database — the tenth health check,
"this cell is sealed", says so), its own benches and topics (`SPINE_QUEUE_NS`
names both), its own bodies with their own seeds, its own policy and meter.
"Cells = worlds." The universe's home stands on the ground (`spine_world`:
cell · epoch · the kernel that keeps it), settled at light and said once as
`orreth.world.homed.v1`; a kernel of another cell may not light over it. Both
doors serve the world card, `/world`.

```bash
scripts/dev.sh cell two                       # u:two on spine_two as cell_two, benches/topics 'two', seeds in ~/.orreth/cells/two, :4602
scripts/dev.sh shadow stop; SPINE_PEERS=two=http://127.0.0.1:4602 scripts/dev.sh shadow   # the first cell names its peer
scripts/dev.sh cell two stop                  # down whole, its bodies with it
```

**The seam** (`seam.rs`, the Rust kernel's): two cells that NAME each other
(`SPINE_PEERS=name=door,…`) speak over one door, `POST /seam`, in messages
signed by their kernels' own selves — the peer's DID pinned on first sight,
every message through every fence (the pin · the signature · the nonce · the
120 s window · the epoch) and a knock ceiling per signer. A hello every 10 s
carries the world card and the roster (the peer's line in the Monitoring:
"cell two · u:two · live" · "3 s behind" · "unreachable since 16:13").
**Commands route home:** "librarian@two, …" is filed here as ROUTED, served in
cell two by its own librarian, and answered on the ask here ("answered in cell
two by librarian"). **Partition:** what cannot go waits in `spine_seam_out`
with a backoff; the ask reads PARKED in plain words; it resumes once when the
peer answers again. **The stop** (rule 11): "stop it" on a routed ask's line
(`POST /asks/stop`) rests it here and at its home within the SLO (2 s).
**Re-homing** ("re-home this universe to cell three") is held at L2; the epoch
advances on the yes, the old home refuses to serve, a stale epoch is fenced.
The proof: `cargo test -p orreth-spine --features bridge --test cells -- --nocapture`.

## The gate (P7 sp8 row 3a — the human seat)

Every door reads the person from a SEAT TOKEN, never from the request body. A
seat is a capability token in the 0006 shape (subject · audience · grants ·
constraints{expiry, direction} · chain · sig; attenuation-only; the contract
`contracts/v0/capability-token.schema.json`), minted by the kernel's own self
as this universe's root after the person's code from their enrolled
authenticator, and carried on every knock as `authorization: Bearer <base64url
of the canonical token>` (the live feed, which a browser cannot send headers
to, takes it as its `seat` query). THE CEREMONY: on a ground no one holds, the
first person to prove an authenticator becomes its OWNER — a master from that
moment — and enrolling anyone else is the owner's (or a master's) word; a
person re-enrolls themselves with their old code. A seat lasts
`SPINE_SEAT_HOURS` (24); "leave my seat" ends it early, recorded. The unseated
wear one face (401 `{"error": "not seated"}`); a seated person lacking a grant
wears the proof's (403). The browser origin is CLOSED (a foreign `Origin` is
refused before the body is read; no open origin on any answer). The knock
ceiling (0071) stands at every door — per person, per address at an open door
— `SPINE_CEILING_RATE` (20 a second) up to `SPINE_CEILING_BURST` (60), then
"the door is busy for you — try again shortly" (429).

Open doors (no seat): the page, `/health`, `/guide`, `/harness`, `GET /seat`;
`POST /seat` and `POST /enroll/confirm` (the code IS the proof); `/seam` (its
own signature); the join desk's `/join` · `/join/prove` · `/join/lease` and a
join's status (their proof is a signature); `POST /enroll` while no one holds
the ground. `POST /delta` (a body's own words) needs the body's LEASE — a seat
with the role `body` (row 3b). Governing doors (the owner's or a master's seat):
`/world/rehome`, `/bodies/restart`, the shelf's and the Stable's changes.
Doors: `GET /seat` → `{ceremony, hours}` · `POST /seat {person, code}` → the
token, its wire, the role, the words · `POST /seat/leave`. The reference is
`orreth_spine/seat.py` (the gate is `glass.py`'s `_admit`); the Rust kernel's
twin is `seat.rs` · `seat_live.rs` with a tower layer in `bridge.rs`; the
fixture is `conformance/seat-v0.json`; the proof `tests/gate.rs`. In the
tests, `tests/seats.py` runs the ceremony through the doors so every door test
sits before it knocks.

## The join desk (P7 sp8 row 3b — the machine's gate)

A BODY joins through a five-status desk the kernel keeps (`orreth_sim/joindoor.py`
carried law for law): `pending → challenged → proved → staged → done | denied`.
`POST /join {did, name, role, public_key, template_hash, policy_hash, ticket?}`
asks and is CHALLENGED in the same breath — the desk's own nonce; a DID here is
a hash of the key, so the key rides beside it and must derive it. `POST
/join/prove {id, did, sig}` is the body's signature over `{did, join_nonce}`
(the old SDK's exact bytes): a forged proof is DENIED with the one face ("join
refused"); a stale nonce (120 s) is re-challenged; a proven key is admitted at
once on a standing word — the CREW MANIFEST (a one-time `SPINE_SPAWN_TICKET`
the kernel handed the process, and the template it spawned) or the STANDING
WELCOME (the same self admitted here before) — else STAGED: the kernel holds
`join.admit` in the chat like a keeper's proposal, cancel the default, and only
a GOVERNING seat's click admits it (a person's seat wears the one face; a hold
nobody answers in fifteen minutes is denied, recorded). The body then COLLECTS
its lease at `POST /join/lease {id, did, sig}` with the same key (a signature
over `{did, join, join_nonce}`; an id alone collects nothing): the 0006 token
to its DID, this world the audience, grants `retrieve self · write self`, the
FUEL CLAUSE in its budget (`{cost, renew_days}` — `SPINE_LEASE_USD` ·
`SPINE_LEASE_RENEW_DAYS`) for `SPINE_JOIN_LEASE_DAYS` (30). The lease is a SEAT
with the role `body`: it opens the body's own words at `/delta` and nothing
more. `GET /join/<id>` is a join's status (open; the lease never rides it);
`GET /join` is the desk — "who is at the door?" in the glass. Facts
`orreth.join.asked.v1 · .proved.v1 · .admitted.v1 · .denied.v1` and the
lease's `orreth.seat.taken.v1`; table `spine_desk`.

Built once on the Rust kernel (`desk.rs` · `desk_live.rs` · the doors in
`bridge.rs` · the `join.admit` arm of the settle · the ticket in `bodies.rs`)
and once in the fixture `conformance/desk-v0.json` (JB's lock: the Python
reference grows no new doors). `orreth_spine/desk.py` is the reference's pure
law AND the body's side of the knock: `desk.knock` — `body.py` joins through
the kernel's door when a kernel spawned it, wears its lease on every `/delta`
knock, and exits refused when turned away. Proofs: `tests/desk.rs` (one Rust
kernel; a stranger's whole road) · `tests/bodies.rs` (the crew admitted on the
manifest) · `tests/test_desk.py` (the body's knock against a played desk). The
standing key-check (JB's pin) is this desk's own act — a re-join proves the key
again and is admitted on the welcome in silence; its cadence waits for a proof.
