# Decisions

Locked architectural decisions. Lightweight ADRs — one short file per decision once it's *settled*
(not while it's still being argued in a `design/` draft).

## Already locked (this is the canonical list; the full rationale lives in `../vision/FUTURE-the-orreth.md`)

- **Name:** Orreth. Repo `orreth`. "Harness" stays the architectural primitive. Tiers = Universe / Ecosystem / Field / Agents.
- **One recursive primitive**, `tier` = a Tier Profile (config, not code) — not three codebases.
- **Depth capped at 3** for now; expandable by SDK/CDK.
- **Roll-up:** monoidal sufficient statistics + signed content-addressed pointers; count-weighted confidence.
- **Cascade:** inherited Standards; floors non-overridable (lexicographic); soft = most-specific-wins; skills additive.
- **Consent = the join spectrum:** fully-joined / floors-only / observe-only / decoupled. **Floors compelled for the joined, everything else offered**; leased-agent floor enforced by lease/capability credential.
- **Targeting:** one selector primitive — `all` / `role` / `ecosystem` / `field` / `selection`; target at-or-below only.
- **Security:** recursive DID chain; **resident (TCB) vs registered (workforce)** agents; tenant isolation recurses.
- **Rust** for the plane (ingestion, identity-verify, cascade resolver, drift gating, brainstem); **Python/LangGraph** for cognition.
- **Headroom** adopted as the byte substrate (compression · CacheAligner · CCR reversible store · cross-agent memory); governance stays ours; vendor/pin/review.
- **Memory fabric:** per-node API; append-only + content-addressed + signed; promoted-up-as-pointers; **governed-tombstone erasure** (GDPR-compatible); built on CortexObserver L1–L4 + headroom CCR.
- **Skills are promoted memories** — one substrate.

## ADR convention (when we start logging individual ones)

`NNNN-short-title.md` with: **Context · Decision · Consequences · Status (proposed/accepted/superseded)**.
