# orreth-agent

The SDK for building agents that live in an [Orreth](https://docs.orreth.ai)
universe — a governed runtime where every agent has a permanent identity,
every action is a signed record, and every model call is authorized and
metered by a kernel that never sees the prompt.

```bash
pip install orreth-agent            # one dependency: cryptography
pip install "orreth-agent[governed]"  # + litellm, for real model calls
```

```python
from orreth_agent import FieldClient, Chassis, RuleThink

client = FieldClient("http://127.0.0.1:4502", name="scout")
client.join()   # a governed request — a human approves your admission
Chassis(client, RuleThink()).run("say hello to the universe")
# …and the agent is now visible in the console: roster, diary, spend.
```

What the kit gives you:

- **`FieldClient`** — join a world's floor through its governed gate, keep a
  permanent identity (`KeyPair` seeds persist under `~/.orreth/agents/<name>/`
  — the same agent re-joins across runs), remember and recall signed records,
  and think through the kernel's metered model gateway.
- **`Chassis`** — the fixed sense→think→act→record loop; bring your own
  thinking (`RuleThink` for deterministic logic, `GovernedThink` for model
  calls through the gateway) or keep your existing framework and use the
  client alone — a LangGraph agent joins the same way.
- **`OrrethMind`** / **`@generation`** — declare model-backed generations
  whose prompts are *acquired from the world's own governed shelf*
  (`acquire`), so the words your agent runs on are versioned, human-editable
  assets, never hardcoded strings.
- **`manifest`** / **`PANEL_KINDS`** — build and validate capability
  manifests: whole purposes the Orreth console renders from declarations,
  never from your code.
- **`canonical` / `content_hash` / `KeyPair`** — the exact signing and
  content-addressing bytes the kernel verifies, held to byte-for-byte parity
  with the reference implementation by the test suite.

Start at **[docs.orreth.ai](https://docs.orreth.ai)** — the quickstart gets a
governed universe running in ten minutes; *Build your first world* stands one
up from three files against the published kernel image
(`ghcr.io/iotlodge/orrethd`).

Licensed Apache-2.0.
