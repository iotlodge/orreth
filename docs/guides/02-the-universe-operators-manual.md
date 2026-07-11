# Guide 02 — The Universe Operator's Manual

*First edition 2026-07-11 (Fable 5). The SOP: how to raise a universe, keep it
healthy, and be the human its gates wait for. Guide 01 taught you to talk to the
residents; this one teaches you to run their world.*

---

## 0. What you are operating

One binary (`orrethd`), many floors. The dev rig composes three — **universe
:4500 → ecosystem :4501 → field :4502** — plus any floors the Shipyard grows
(:4503+). Beside the plane runs one process of cognition, the **console worker**:
every resident's duties, keys held worker-side (the plane verifies, never signs,
and never sees a prompt). Postgres is the memory that outlives everything.

Three truths to operate by:
1. **The plane authorizes and meters; cognition lives in the worker.** A dead
   worker means silent residents, not a broken universe.
2. **Everything that matters is a signed record or a queued request.** If you
   can't find it in the Window or the queue, it didn't happen.
3. **You are a gate, not a driver.** The universe stages; you decide. Silence is
   denial — an unattended queue expires closed, never open.

## 1. First light

```bash
scripts/dev.sh start      # root key synced → compose up --build → worker launched
scripts/dev.sh status     # floors, health, join door
scripts/dev.sh logs       # the daemons (follow)
tail -f ~/.orreth/tmp/worker.log   # the residents' side of every story
```

Open the Console: **`http://localhost:4500/window`** (every floor serves its own
at `:PORT/window`). The left rail is the world: floors, residents (pinned organs
show even on quiet floors — honest zeros), workforce. The orrery is live; the
spacetime window pulls up from the bottom; the parlor opens on any resident.

`stop` downs everything (dynamic hulls included); `restart` = stop + rebuild +
up. The worker's **replant** relaunches Shipyard floors from `~/.orreth/shipyard`
on start — floors you grew come back by themselves.

## 2. What survives what

| You lose… | What happens |
|---|---|
| a daemon (restart) | Nothing. Records, runs, requests, meter, **purge stubs** boot-restore from postgres; presence re-pins within seconds. |
| the worker | The world keeps turning, beats keep landing; asks queue up unanswered until it returns. Restart-safe: residents reload their seeds. |
| `~/.orreth` seeds | **Identity death.** Residents would be reborn as strangers (new DIDs). Back this directory up; a keypair is a self. |
| postgres volume | The universe's memory. Don't. |

`~/.orreth/` map: `residents/` (every resident/seat/scribe seed) · `agents/`
(SDK lifeforce seeds) · `farm/`, `stable/`, `shipyard/` (charlotte's, ada's, and
the dock's ledgers — replant/re-saddle sources) · `tmp/` (worker log).

## 3. The gates that wait for you

Watch the **Requests** tab (amber ring on the orrery = something pending). Your
verbs are approve/deny — by resolving the request. What arrives:

| Kind | What it is | Your move |
|---|---|---|
| `join` (staged) | An agent proved its key at becky's door | Approve → becky mints the lease. Deny → turned away. |
| `service` (staged) | charlotte probed a planting; manifest pinned | Approve → it serves. A **quarantined** service moved under its pin — re-open only if you trust the change. |
| `mind` (staged) | ada pinned a deal on a staged saddle | Approve → it thinks. Price drift comes back here as a decision, never an outage. |
| `question` | A flow asks you something mid-objective (0027) | Resolve with your answer. **Expiry is denial.** |
| `entitlement` | An orchestration wants to dispatch beyond its token | Grant deliberately or let it die dark. |
| `improvement` (staged) | The improver proposed a **rewrite** — the high lane | Resolve `approved` to adopt; nudges already adopted loudly on medium. |
| `purge` (staged) | Operational erasure staged; the seal already holds | It stays held: *destruction waits for humans, plural* — quorum machinery arrives with the signer registry. |

## 4. Growing the universe

In becky's parlor: `create ecosystem retail with fields web, pos` → the Shipyard
drafts, **you approve**, real containers rise on the rig network, pull their
parent's floors at boot, and beat into the orrery. They're floors like any other:
tended queues, pinned organs, their own `/window`.

Joining workforce: `scripts/dev.sh agent 01-prototype --once` (or `02-langgraph`,
`03-agentfield-sentinel`) — the agent presents its DID, answers the nonce
challenge, and waits at your gate. Same agent, same seed, same self every run.

## 5. Money and meters

Every thought is metered under the DID that thought it — residents included; the
honest zero shows. ada's room (⛶ in her parlor) is the running bill: stalls,
spend, the pasture calendar. Budgets ride lease tokens; a floor out of fuel
degrades to deterministic floors and flags — nothing dies, it hibernates.
Keys live in the repo-root `.env` (`TAVILY_API_KEY` for the librarian's gather;
model keys for the stable's minds).

## 6. The knobs

| Knob | Default | Meaning |
|---|---|---|
| `ORRETH_IMPROVER_EVERY` | 600s | How often the improver reads the receipts |
| Upload bars | 256KB · txt/md/json/csv/pdf/png/jpg | 0029 locks — beyond them, the uniform refusal |
| `BEAT_EVERY` (worker) | 6s | Heartbeat cadence |
| Floor profiles | `backend/plane/profiles/*.json` | Retention, horizons, budgets, gates per tier |

## 7. When something looks wrong

- **A floor shows dark** in `status` → `docker ps` + `dev.sh logs`. Dynamic floors
  seconds after start are usually just replanting.
- **Residents not answering** → is the worker alive? (`pgrep -f console_worker`,
  read `~/.orreth/tmp/worker.log`). One poison request never silences a floor —
  refusals are relayed onto the record and the round goes on.
- **A service in quarantine** → that's the rug-pull door doing its job. Nothing
  serves un-attested; re-open at the gate or let it rot.
- **Librarian missing from a rail** → she shouldn't be (pinned organs always
  show, 0029). If a floor mines instead of pins, the worker isn't tending it.
- **"restored N purge stub(s)"** at boot → correct and expected: readability
  never resurrects.
- **demo.orreth.ai looks stale** → it's a snapshot, not a feed; refresh it
  deliberately (snapshot + cdk deploy).

## 8. The operator's creed

You own the gates, the keys under `~/.orreth`, the `.env`, and the spend.
The universe owns everything else — and writes it down, signed, so you can
always ask it what happened. When in doubt: ask a resident before you touch a
container. Humans never read the world; they ask it — **operators included.**

🥂
