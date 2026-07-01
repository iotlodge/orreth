# 0006 — becky: the identity & capability chain

*Design draft for review. Schemas are language-neutral shapes, not code. **becky is an IAM agent** — resident,
TCB, never a human (locked 2026-07-01). Trust root **locked by JB 2026-07-01**: did:web universe roots +
did:key leaves. **Open decisions** flagged at the end. Pulled forward in the sequence because everything above
already assumes it: `0002`'s CapabilityToken, retrieval authorization, transfers, interviews; `0001`'s
signatures; EH's ingestion gateway.*

---

## Why this is a keystone

Every promise in this architecture reduces to a signature check: Sourced + Verified is a chain of custody,
tenant isolation is a token boundary, the interview sandbox is an attenuated capability, the kill-switch is a
revocation. becky is the resident agent that mints, delegates, revokes, and rotates all of it — the agentic
half of every gate. Until this spec is real, `0002`'s `auth: CapabilityToken` is a stub with excellent manners.

---

## 1. The chain — root → leaf

```
Universe root DID  (did:web:orreth.ai:u:<universe>)     # KMS/HSM-held keys · multi-party rotation ceremony
 └─ becky@universe        (resident TCB agent — THE issuer; its DID chained to the root)
     └─ becky@ecosystem   (delegated sub-issuer — offline-capable delegation certificate)
         └─ becky@field   (delegate)
             ├─ resident roster DIDs        (steward · governance · analysis — born with the layer)
             ├─ archetype DIDs              (templates — carry skills/Standards refs, never memory)
             └─ incarnation DIDs (did:key)  (scope-bound, lineage → archetype; cheap, offline-verifiable)
```

- **did:web at the roots** — publicly resolvable under `orreth.ai`; a customer's auditor can resolve a
  universe root in a browser and verify any agent's chain from it.
- **did:key at the leaves** — issuance is cheap and local (a Field spawning 500 incarnations makes no web
  calls); verification needs only the chain, which travels with the token.
- **Self-hosted / air-gapped universes**: a **pinned root** distributed out-of-band. A policy dial in the
  Tier Profile, not a fork — the chain logic is identical, only root resolution differs.

---

## 2. Issuance flows

| Flow | Trigger | What becky does |
|---|---|---|
| **Resident issuance** | layer provisioning (a template's TCB manifest, `0009`) | issues the resident roster's DIDs *first* — **a layer is born with its staff**, before any workforce exists |
| **Archetype registration** | a template identity is created ("Cloud-Architect v3", "you, the player") | issues an archetype DID carrying skill/Standard refs — capabilities, never memory |
| **Incarnation spawn** | archetype + target scope | issues a did:key with `lineage → archetype` (`0002` §1): inherits skills, opens a fresh, isolated memory branch |
| **Workforce join** | any-SDK agent presents at the Gateway | verifies sponsor + lease terms → issues a scoped DID + an AgentFacts VC shell; the **join-spectrum floor is a term of the lease credential** |
| **Human enrollment** | a human principal is entitled | same machinery — a DID + a directional, separated entitlement (`governed-human-oversight.md`); **apex entitlements require multi-party co-sign** |
| **Transfer** | `0002` Transfer | re-issues scope binding; portable memory follows, branch-bound stays; the old scope's tokens are revoked atomically with the re-bind |

---

## 3. The CapabilityToken — attenuation-only, all the way down

```
CapabilityToken {
  subject     : DID
  audience    : ScopePath                       # where it may be presented
  grants      : [ {
      action     : "retrieve" | "write" | "distill" | "interview" | "govern" | "transfer" | "issue"
      space      : "self" | { ancestors: N } | "apex" | { scope: ScopePath }    # 0000 §1 — never tier-named
      time       : TimeWindow?                  # how deep in time this grant reaches
      visibility : TenancyScope[]?              # e.g. portfolio-only (the interview)
  } ]
  constraints : { expiry, direction: "down" | "within" | "up" | "across", budget?: Budget }
  chain       : DelegationProof[]               # every hop from the universe root — verifiable offline
  sig         : Sig
}
```

- **Attenuation-only.** Every delegation hop may *narrow* a token — never widen it. becky itself cannot grant
  what its own delegation lacks. There is no key in the system that can amplify authority; there is only the
  root, and the root is a ceremony, not a login.
- **The interview is just a token**: `action: interview, visibility: [portfolio], direction: within,
  time: bounded, budget: query-budget` — the `0002` §5 sandbox falls out of the shape, including the
  adaptive-query budget from the review findings.
- **Budget-miss ≡ authz-miss to the caller** (`0002` §4 amendment) — the token's budget exhausting is
  indistinguishable from not being authorized; only the privileged access log knows which.
- **Humans hold the same shape.** A regulator's token: `retrieve, scope: their-jurisdiction, direction: down,
  no govern grants`. Total transparency, zero levers — the read/control separation is two grant lists, not
  two systems.

---

## 4. Revocation & rotation

- **The NANDA index** resolves DID → key + status. Revoking an **ancestor revokes the subtree** — that is the
  incident kill-switch: one revocation at the ecosystem delegate ends every credential beneath it.
- **Workforce tokens are short-TTL + refresh** — revocation latency is bounded by TTL even if an index check
  is missed. Residents run longer TTLs with scheduled rotation.
- **Root rotation is a ceremony**: KMS/HSM-held, **multi-party** (humans co-sign; becky executes), and the
  outgoing root signs its successor — chain continuity, no flag-day.
- Every issuance, delegation, revocation, and rotation is itself a **signed MemoryRecord** — identity
  operations are memory too, Sourced + Verified, forever. The audit trail of *who could do what, when* is a
  first-class citizen of the substrate it protects.

---

## 5. AgentFacts — runtime-earned trust

AgentFacts are W3C Verifiable Credentials on an identity: declared **capabilities** at issuance, plus
**evaluations earned at runtime** — rolled scores written by the EH governance loop (never self-asserted;
resident-authored only, the `0001` rubric rule). They are the substance behind the `0002` portfolio: when a
candidate agent claims "0.94 mean score across 3 engagements" in an interview, that claim resolves to a
becky-chained VC, not to marketing.

---

## 6. Security properties (consolidated)

- No identity without a chain to a universe root; no authority without an attenuation proof to match.
- Tenant isolation is enforced **in the token**: audience + direction; `across` exists only as an explicit,
  human-gated grant.
- The kill-switch is structural (ancestor revocation), not procedural.
- becky is TCB but bounded — it executes issuance under policy; it cannot exceed its own delegation, and apex
  grants require human co-signs. **The IAM agent is governed by the same physics it administers.**
- Ed25519 signatures + content-addressing from day one (`0000` §3 — the HMAC stand-in is never rebuilt).

---

## 7. Decisions — **all locked by JB, 2026-07-01** (recorded in `../decisions/`)

1. **Token format: biscuit-style.** Tokens carry their delegation chain; attenuation and verification are
   fully offline (Rust: `biscuit-auth`). A Field can grant and every layer can verify with no callback —
   the authority model and the token model are the same shape.
2. **Co-signs: 2 for apex actions, 3 for root rotation.** Universe-wide raw reads, cross-tenant grants, and
   erasure take two entitled humans (workable at 3 a.m.); rotating the trust root itself — scheduled, never
   urgent — takes three.
3. **TTLs: Tier Profile dials** (`0004`), starting values workforce 24h · resident 30d · session Attachment
   keys per-session. The spec locks the shape; the universe's policy sets the number.

---

*Unblocks: `0002`'s authorization becomes real (capability tokens exist) · the interview sandbox is buildable ·
`0010` (AgentField & Gateways — the doors these tokens are presented at) · and the interop/UX dive that
follows, where NLP-driven engineering of agent graphs gets its governed surface.* 🥃
