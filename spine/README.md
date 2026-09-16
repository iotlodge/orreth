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
