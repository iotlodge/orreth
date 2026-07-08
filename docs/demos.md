# The demo reel — true stories against the live rig

Every demo in the reel runs the real thing: identities minted from real keys, gates
that actually hold, memories signed onto the actual record. Nothing is mocked. When
marketing time comes, this is the script — and until then it's the fastest way to
*feel* what a dive shipped.

## Running the reel

```bash
scripts/dev.sh start        # the rig first: universe :4500 · eco :4501 · field :4502
scripts/demo.sh             # list the reel
scripts/demo.sh farm        # roll one story
```

Or from the Console: **Ask tab → 🎬 the reel** — click a story and the transcript
plays in the glass. The click rides the request queue (`kind: demo`), the worker
rolls the story in a side thread (the round keeps turning — the story's own requests
need tending), and the transcript lands as the request's result. One story at a time.

## The stories

| name | dive | the story it tells |
|---|---|---|
| `farm` | 0018 | A service's whole life: a REAL remote MCP planted, probed, hash-pinned, attested, earning `serving` beat by beat — then a rug pull caught at the gate and read back off its worldline. |
| `life` | 0002 | Two acts, two processes. Process one is born, remembers, and dies. Process two — sharing nothing but the key — attaches and remembers everything. Reboot ≠ death. |
| `spacetime` | 0002/0004 | One query at the field scrubs 500 days and crosses **three tiers** — recent memory stays local, deep time answers from the apex, one merged Sourced+Verified answer. On a lived-in rig the apex first *refuses a backdate* out loud: lived time is monotone. |
| `knowledge` | 0014 | Knowledge admitted quarantined at 0.0000, promoted on receipts, recalled by lineage. |
| `chassis` | 0015 | One governed thought through the fixed loop — authorize, think, meter, record. |
| `model` | 0016 | The model plane end to end: the plane authorizes and meters; it never sees the prompt. |
| `stable` | 0019 | A mind's whole life: saddled off the real OpenRouter market, deal pinned, earned by canary, deprecated by the calendar — and swapped by appointment, never outage. |
| `parlor` | 0020 | Humans ask; residents fetch. An audience with charlotte, ada, and vigil — every exchange signed onto the window. |
| `recall` | 0014 §4 | Discredit a source and the librarian walks its lineage — every tainted entry re-versioned, the poison visibly dead. |
| `gate` | 0006/0012 | The hardened join door: a genuine agent proves its key and waits for the human; an imposter is found out. |
| `window` | 0008 | Seed a biography and open the Console itself. |

## The reel replays

The demos run against a **long-lived** rig, and the rig's own laws refuse naive
replays — the stable turns away a saddle over an occupied stall, the farm turns away
a plant over a living plot, the apex turns away backdated memory. So every story
clears its own stage the governed way (retire → sunset, decom → decommissioned, both
legal to rise from) or meets the refusal head-on and narrates it. Run the reel twice;
the second telling is the proof.

## Where this goes

These stories are the seeds of **agent templates**: Universe / ecosystem / field
blueprints mapped to Docker (dev) and cloud (prod), grown the Shipyard way — by
conversation. That's further down the build pipeline; the reel grows first, one true
story per dive.
