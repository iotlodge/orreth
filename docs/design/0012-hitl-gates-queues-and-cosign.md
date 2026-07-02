# 0012 — HITL: Gates, Queues & the Co-sign (consequence waits for humans)

*Design draft for review — proposed by Fable 5 (design owner). The last reserved dive (0000 §2/§8) — the
mechanics that `0006`'s co-sign counts, `0013 §7`'s placement map, and `0008`'s governed lane have been leaning
on by reference. **All decisions locked by JB 2026-07-02** (via AskUserQuestion, §6). Contract + simulator
landed with the dive.*

---

## Why this is a keystone

The placement rule is already law: *if an action can affect a party who did not initiate it, it escalates to a
human — machine speed for detection, human judgment for consequence* (0013 §7). This dive builds the machine
that rule runs on: what an escalation **is**, how a gate **decides what it costs**, how signatures **collect
and complete**, and what happens when nobody answers. Everything here runs on **wall-clock** (0004): the
universe may dream at any speed; consequence happens at ours.

---

## 1. The Escalation — staged by machine, decided by humans

`contracts/v0/escalation.schema.json`: **action_class · the staged act (opaque to the queue) · scope ·
staged_by · signed evidence refs · the GateRule it must satisfy · staged_at / expires_at · state ·
approvals[]**. Staging is free — vigil stages what it detects (0013 §3: detect and *stage*, never enforce),
stewards stage promotions, gateways stage quota breaches, humans stage anything. Deciding is gated. Every
transition validates against the contract and lands on the record: **the watchers are watched, including here.**

## 2. The Gate — co-sign bars are floors

A GatePolicy maps action classes → `{co_signs, legal_signoff?, cooling_off?, ttl}` — the `0013 §7` map and
`0006`'s locks, expressed as policy instead of prose. Gate policies **cascade tighten-only, exactly like
floors**: a child tier may *raise* co_signs, *lengthen* cooling-off, or *shorten* ttl — never the reverse.
(One resolver philosophy, third application: retention had two monotone directions, gates have three.)

## 3. The Co-sign — distinct, entitled, offline-verifiable

An approval is a signed act by a **control-entitled human principal** (a DID via becky, entitlement checked
against `governed-human-oversight.md`'s separation — read-entitlement never suffices): **distinct principals
only, no DID signs twice**, every signature carried on the escalation. Quorum completion stamps `approved_at` —
and approval is *still* not execution:

> **Cooling-off is approved-but-held.** For the gravest classes (destroy, floor-loosen), quorum starts a clock
> instead of an action — and during that window **any single entitled voice can abort.** It takes three to
> destroy a universe and one to save it. That asymmetry is the entire point of the window.

**No break-glass exists, deliberately.** The 2-co-sign apex bar was *sized* for 3 a.m. (0006's rationale);
an emergency path that bypasses quorum would be the backdoor 0013 §6 promises doesn't exist.

## 4. Expiry — silence never approves

> **Locked 2026-07-02: expire = deny + signal.** A pending escalation past its wall-clock TTL is **denied by
> default** — re-staging requires fresh evidence — and the expiry itself is a **vigil signal**: an ignored
> freeze request means something is unattended, and that is a finding about the org, not just the item.
> Queues cannot rot into ambient authority; the failure mode of an understaffed org is *inaction, never
> unreviewed action.*

## 5. Bars are absolute — the honest bootstrap

> **Locked 2026-07-02: co-sign bars never clamp to headcount.** Until the Custodian org has ≥2 (or ≥3)
> control-entitled humans, those actions are **structurally unavailable** — staging itself refuses, loudly.
> The trust-tier gate (0013 §8) must not admit tenants whose obligations require unavailable quorums: **no
> regulated tier before a legal-process quorum exists.** This is the solo-founder question answered with
> spine: "no single employee is a god" is true from day one, not aspirational — "what if the founder goes
> rogue" has a structural answer, and the capability gap becomes a published, honest launch gate instead of
> a quiet exception.

## 6. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **Expiry = deny + signal.** Default-deny on TTL; the silence is itself a vigil finding.
2. **Bars absolute; actions unavailable below quorum.** No bootstrap clamping, no quorum debt — staffing is a
   launch gate, published.

## 7. Contract & simulator (landed with the dive)

`escalation.schema.json` (Escalation + GateRule) · simulator `hitl.py` (`EscalationQueue` —
stage/approve/execute/reject/expire, `cascade_gate` tighten-only). **Four new tests, 27/27 passing:**
quorum-lifecycle-and-distinct-signers · bars-absolute-for-a-solo-org · silence-never-approves ·
cooling-off-holds-and-gates-tighten-only (including the one-voice abort).

---

*This dive also retires a ghost: the commit that once cited "0012's co-sign machinery" before 0012 existed
(see 0013's provenance note) now has a real referent. Unblocks: the Custodian's quarantine ladder (0013 §5)
has its queue; `0008`'s governed lane is a gate with `co_signs: 1`; `0007` (resolver) and `0009` (Build My
First Universe) are all that remain of the dive sequence. It takes three to destroy a universe and one to
save it.* 🥃
