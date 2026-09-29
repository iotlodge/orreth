# Orreth

**A kernel for fleets of agents.** Identity, memory, rails, meter, gate, watches and levers are held
by the kernel; policy is held by humans; an intention is the unit of control. Everything a body does
lands on one signed record, and a person can always stop what the machine manages.

<!-- PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp2: the README rewritten for the new world · 2026-09-29.
     The 0.72 README (seventy-three dives, the Living Brain, the demo reel) rests at the tag main-v0.72-old-world. -->

---

## Why a kernel

The systemic problem in agent fleets today is **entropy**. Every agent brings its own identity story,
its own memory, its own way of calling a tool, its own idea of what it may do and what it costs; put
twenty of them on one problem and nobody can say who did what, under which law, for how much, or
how to stop it. Frameworks add loops; they do not remove the entropy.

An operating system removed that entropy for programs by taking the rigid parts away from them —
processes, files, permissions, the clock — and holding them in one place under one law. Orreth does
that for agents. The kernel holds the **rigid control**:

- **Identity** — a keypair is a self, and a self survives the process. A body re-joins as the same
  self, every life; a person sits with a seat the kernel minted after a proof.
- **Memory** — one signed, append-only record on the ground; corrections are siblings, never
  overwrites; a purge is a governed act that leaves a hash, never words.
- **Rails** — every ask, reply, fact and tool call rides the same envelope over the same rails
  (Postgres · RabbitMQ · Kafka), poison parked with its evidence, nothing lost.
- **Meter** — every thought a body has goes through one gateway under the body's own key, and
  lands in dollars. Nothing thinks off-meter.
- **Gate** — a body joins through a five-status desk; a person's word is the only thing that admits
  it; scopes only narrow; refusal wears one face.
- **Watches and levers** — the kernel watches its own doors, benches, leases and outbox; every
  remedy is a lever a person can see, and a consequence holds until a person says yes.

Because the control is rigid, the experience can be fluid: **one chat** to every body, and **THE
PANEL** — one live drawing of the world where geometry is what is declared, light is what is
happening, colour is who did it. Humans sit outside and apply control (policy · security · a hand
on the interlock · the forensic turn); Orreth applies ontology to the running state so the world
stays **reproducible, trusted, understood, and evolving**. Intentions such as cost, recovery time
and return are how humans control scale.

---

## What is running today, on one laptop

- **Two kernels, one law.** `orrethd` — the Rust kernel (`backend/plane/crates/orreth-spine`) —
  is THE door on `:4600`. The Python reference (`spine/orreth_spine`) is the same kernel written
  first, on `:4601`, and stays the reference: every law is pinned by a conformance fixture both
  kernels must pass unchanged (`spine/conformance/*.json`, thirty fixtures; 730 cases on the Rust
  side, the Python suite in the nine hundreds).
- **The crew.** The kernel seats every body as a process it governs: the librarian and echo
  (residents), the planner, critic, grader, MITL, toolkeeper and stablekeeper (firmware — bodies
  with a function and no persona). A body that dies comes back as the same self; one that dies
  three times in five minutes is parked and said.
- **The ground and the rails.** A versioned schema the first kernel migrates and the next verifies
  (forty tables, one writer ever); the outbox as a queue with retention; the feed on thirty-three
  topics; every door clocked (p50/p95) and every knock pooled.
- **The gateway.** LiteLLM, run and managed by Orreth: every mind is a stall with a pinned deal,
  every body its own key with a fuel clause in dollars, drift and end-of-life watched by a keeper
  that proposes and never acts alone.
- **Cells.** A second universe is one command away (`scripts/dev.sh cell two`): its own database and
  role, benches, topics, kernel self and seeds, sealed from every other; two cells speak only over a
  signed seam.
- **The seat.** A person proves a TOTP code and receives a capability token the kernel signed;
  every door reads the person from the seat; the first prover on an empty ground is its owner.
- **The remediation rail.** A red watch opens a forensic dossier, the kernel pulls the lever itself
  when the lever is routine, and holds for a person when it is consequential; the outcome is
  attributed on the record.

The full register of what is proven, partial or parked — with the evidence named — is
[`docs/design/the-honest-boundary.md`](docs/design/the-honest-boundary.md). A claim not on that
page is a claim we do not make.

---

## Run it

```bash
scripts/dev.sh up          # the rig rises: ground · invoke · events · gateway (Docker)
scripts/dev.sh kernel      # orrethd on :4600, a release build, the crew as its processes
open http://127.0.0.1:4600 # the glass: the one chat and THE PANEL
scripts/dev.sh status      # what is lit
scripts/dev.sh kernel stop # everything down whole, nothing left running
```

`scripts/dev.sh walk` is `up` + `kernel` in one word. `scripts/dev.sh reference` lights the Python
reference on `:4601` beside or instead of the kernel. Provider keys ride in from your shell or a
`.env` at the root — a key value lives in no record and no file of Orreth's.

As a box: `docker build -t ghcr.io/iotlodge/orrethd .` then
`docker compose -f spine/compose.yaml --profile kernel up -d` — the kernel and its crew in one image
beside the rig's four boxes, its selves kept on a named volume.

## Test it

```bash
scripts/dev.sh rust        # the Rust workspace, hermetic — no rig needed
scripts/dev.sh suite       # the Python reference's laws on the rig (kernel and reference dark first)
scripts/dev.sh rust rails  # the Rust rail proofs on the rig
```

Every proof refuses to run beside a lit kernel: a rig older than the code on disk poisons every
test dispatcher (the stale-rig law).

---

## How to read this repo

| Path | What it is |
|---|---|
| `backend/plane/crates/orreth-spine` | **The kernel.** The pure laws (hermetic, fixture-held) and, behind the `bridge` feature, the ground, the rails, the doors, the feed, the bodies' seam, the cells, the desk, the seat — the `orrethd` binary. |
| `spine/orreth_spine` | **The reference.** The same kernel in Python, written first; the Bridge on `:4601`; the bodies every kernel spawns (`orreth_spine.body`). |
| `spine/conformance` | The fixtures both kernels pass unchanged — the contract between them (canon `0008`). |
| `spine/glass/index.html` | The one page: the chat and THE PANEL, served by either kernel. |
| `spine/crew.v0.json` · `spine/templates` · `spine/tools.v0.json` · `spine/levers.v0.json` | The crew, the templates, the tools' declarations and the lever catalogue — data both kernels read. |
| `docs/rearch/0001`–`0009` | **The canon of the new world**: the experience charter, transport, memory, agent, the build plan, markers, intent, the port, the old world carried. |
| `docs/design/0000`–`0017` | **The constitution** the covenant enforces; `the-honest-boundary.md` is the standing register. |
| `docs/vision` | The vision the constitution serves. |
| `contracts/v0` | The wire schemas (sacred: they change only on JB's word). |
| `agents/orreth-agent-sdk` | The SDK (`orreth-agent`, Apache-2.0): a stranger's body with a permanent identity; its parity test holds the SDK to the reference's bytes. |
| `agents/PROVENANCE.md` | The ledger: every file names the model that wrote it. |
| `scripts/dev.sh` | The rig. |
| `.claude/skills/orreth-covenant` | The covenant — the hard rules every model coding here holds to. |

**Where the old world went.** Orreth's first architecture — seventy-three design dives, the Living
Brain, the Console, the demo reel, the old `orrethd` plane and its Python sim — was halted on
2026-09-14 for the foundation this world stands on (performance for hundreds of bodies, one signed
log, one law at every layer). It is kept whole, never deleted, at the tag `main-v0.72-old-world`
and the branch `old-world/main-v0.72`; `docs/rearch/0009` is the ledger of what each old organ
became here. The book at [docs.orreth.ai](https://docs.orreth.ai) still teaches that world; it is
rewritten for this one at the release wave.

---

## The rules this world is built under

Twelve of them are in the covenant; the ones a newcomer feels first:

1. **A keypair is a self, and a self survives the process.** A new DID per run is a defect.
2. **Nothing grades its own yardstick.** A verdict is signed by someone other than the actor.
3. **Joining is a governed request.** A person's word admits a body; a lease chains to the root.
4. **Refusal wears one face.** A prober learns nothing from how it was refused.
5. **The kernel authorizes and meters; it never sees the prompt.**
6. **The human can always stop what the machine manages** — a lever the human lacks is a defect.
7. **Every word aimed at a human is plain.**
8. **A performance or experience wound stops the line.**

---

## License & provenance

The source is public for review and evaluation; a license is deliberately not yet chosen — all
rights reserved meanwhile. The SDK is the exception: `agents/orreth-agent-sdk` is **Apache-2.0**
and published as [`orreth-agent`](https://pypi.org/project/orreth-agent/); the documentation
([orreth-docs](https://github.com/iotlodge/orreth-docs)) is CC BY 4.0 with MIT examples. Every
source file names its authoring model; `agents/PROVENANCE.md` is the ledger.

*This build is my résumé — I'm exploring senior agentic-infrastructure / architecture roles:
[jsbarth.com](https://jsbarth.com).*

*JB owns the vision. Claude owns the code and usability. We move at the speed of the ideas.* 🥂
