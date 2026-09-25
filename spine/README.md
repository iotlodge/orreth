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
uv run pytest -q              # envelope laws — no brokers needed (CI runs these)
```

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
`scripts/dev.sh shadow`) spawns one process per seat:

```bash
.venv/bin/python3 -m orreth_spine.body --template templates/echo-resident.v0.json         # one body, standing alone
.venv/bin/python3 -m orreth_spine.body --template templates/workspace-firmware.v0.json --binding bindings/crew.v0.json
.venv/bin/python3 -m orreth_spine.body --seed-shelf                                        # the kernel's boot rite, once
```

A body joins as the same self every life (its seed under `~/.orreth/agents/<name>/`),
keeps its lease while it serves, streams its words to the kernel that spawned it
(`SPINE_KERNEL_DOOR`), serves the kernel's harness command on its bench, and stops
whole on SIGINT. The kernel restarts a body that died (1 s, doubling, capped at 30),
PARKS one that dies three times in five minutes (a fact, `orreth.body.parked.v1`;
"restart the <name> body" is the human's lever), never restarts a refusal, and stops
every body at dark. Dials: `SPINE_BODIES` (crew · none) · `SPINE_CREW` (another
manifest) · `SPINE_PYTHON` (another interpreter) · `SPINE_BODY_EPHEMERAL` (tests).

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
