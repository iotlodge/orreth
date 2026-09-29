# Seed — The Identity Layer and the Seat (who you are · what you are called · what you may do)

**Status: SEED (JB, 2026-09-26, after sp8 row 3a) — a row after the join desk (3b); nothing built before the desk.**
JB's direction, captured with Fable's mapping onto the seat as built. The seat
(row 3a) stands; this seed says what changes when a cloud identity layer stands in
front of Orreth, and which of row 3a's choices are dev-ground postures that end then.

## JB's direction, faithfully

- Orreth will have a **cloud identity layer in front of it**: identity PROOFING
  (a real person, at a known assurance), and the security case — "a human that
  should not build something is trying to use an active Operating Instance of
  Orreth to bypass authz or policy."
- The **name of the active DID may live in the DID's profile (humans only)**, so
  the logged-in human sets the name they want to be called across the console
  and the UI — "still allows governance in the metadata due to ontologies
  applied to the Orreth Operating State."
- The pin from the same day, for machines: a **standing key-check** between the
  kernel and its agents on a cadence ("check every so often that agents are WHAT
  they say and WHO they say they are"). This seed treats the human half and the
  machine half as one law.

## Fable's mapping — three things the seat fuses today, pulled apart

Row 3a fused them because the dev ground had nothing else: the name IS the DID
(`did:orreth:person:jb`), the role is a table on the ground (owner · master ·
person), and the proof is Orreth's own authenticator code. With an identity layer:

| Question | Today (row 3a) | With the identity layer |
|---|---|---|
| **Who you are** | the name, as the DID | an OPAQUE DID minted at the first federated proof — `did:orreth:person:` + sha256(issuer · subject)[..32], the same shape as every key-bearing self; never a name |
| **What you are called** | the DID's tail | the PROFILE (row 1): "call me JB" (you told me) beside the issuer's display name (the identity layer told me); every seat word, the YOU tag, the export read the profile's name |
| **What you may do here** | a role row → `grants_for(role)` | the identity layer's ENTITLEMENTS mapped through Orreth's policy and ontology → grants; attenuation-only holds: a seat never widens |
| **The proof** | Orreth's TOTP | the identity layer's token verified at the seat door (issuer pinned, keys fetched, audience = this cell, proofing level and authentication strength read); TOTP stays as the LOCAL mode (air-gapped / self-hosted — 0006's pinned-root posture) |
| **The name never reissued** | baked into the DID | a governed HANDLE claim in the registry with a uniqueness rule (persons.py's law, as metadata) — separate from the display name |

- **The seat becomes the exchange point, not the login.** `POST /seat` takes the
  identity layer's token, verifies it, and mints the Orreth seat exactly as now —
  chained to the kernel's own self as the universe root. One dial chooses the
  mode: `SPINE_IDENTITY=local` (the authenticator) or `oidc:<issuer>`. The pure
  law is the token → grants mapping; it earns a fixture kind (`seat_from_claims`).
- **The seat's life follows the identity session, not a day.** Minutes with a
  silent refresh; back-channel logout arrives as a KERNEL-made leave
  (`orreth.seat.left.v1`, by "the identity layer"). The gate's five-second memory
  already makes a leave land fast on every kernel over the ground.
- **The bypass path closes at the ACTION, not only the door.** The human who
  should not build something will hold a valid seat with the wrong grants; so:
  - every held act carries the seat id and the identity session id in its fact,
    and the export answers "which seat did this, under which proofing level";
  - the consequence class × the seat's entitlement decides the proof level —
    grave acts STEP UP through the identity layer (a fresh, stronger factor with
    a maximum age) instead of Orreth's own code; a master's confirm demands the
    same fresh step-up;
  - passkeys through the identity layer give the first truly HUMAN-SIGNED act
    (0070's missing half): the seat's confirm carries a signature only the
    person's own authenticator could make.
- **One law for people and bodies: consequence re-proves identity.** The human's
  step-up and the machine's standing key-check (JB's pin) are the same act — a
  fresh proof of the key or the factor behind a DID, demanded by the kernel on a
  cadence or at a consequence. The join desk (row 3b) challenges once at the
  door; this repeats it. Both land as facts under the same chain.
- **Harden the seat itself.** Today a stolen wire is a seat until it expires and
  the seat is unbound to a device. Binding the seat to the browser's own
  ephemeral key (the page mints a keypair; its thumbprint rides in the token's
  subject line; governing doors demand a signed nonce) is the seam's signature
  reused at the human door. Cheap to add once the identity layer sets the mode.
- **Federated cells.** A seat rooted in a PINNED peer kernel can be accepted over
  the seam and re-minted locally: the chain already carries the extra hop; the
  seam already pins peer DIDs on first sight (`cells.rs`). "Foreign authority"
  stays the verdict for any root not pinned.
- **Governance in the metadata.** The seat's grants reference the ontology's
  terms (marker kinds, spaces); `orreth.seat.taken.v1` records the issuer, the
  subject hash, the proofing level and the authentication strength as OBSERVED
  claims in the profile ("the identity layer told me"), so the Mirror and the
  ontology govern on them and the human's own words stay theirs.

## What the honest boundary should say meanwhile (row 3a's postures, named)

- The name-as-DID is a dev-ground posture that ends when the identity layer lands.
- Roles on the ground (owner · master · person) stand in for entitlements.
- A stolen wire is a seat until expiry; the seat is unbound to a device.
- Step-up for grave acts is Orreth's own code until the identity layer's stronger factor replaces it.
- The ceremony on a loopback ground admits whoever reaches the box first; the identity layer makes the first prover a proven person.

## Order (Fable's proposal, JB's to lock)

1. **sp8 row 3b — the join desk** (next session): the nonce challenge, the human's
   yes as a kernel-held act, the chained lease with the fuel clause, the body's
   signed knock; the standing key-check designed WITH it (built when a proof asks).
2. **The identity row** (after the release wave, or the first proof that needs a
   second real human): the opaque DID and the profile's name; `SPINE_IDENTITY`;
   the token → grants law and its fixture; the seat's life bound to the session;
   step-up at grave acts; the honest-boundary rows above retired one by one.
3. **Hardening** (with the first stranger's deployment): the device-bound seat;
   the federated seat over the seam; passkeys for the human-signed act.

## JB's word, 2026-09-29 (re-base sp2's spirit read) — identity is a FIRMWARE CHIP

"If Identity is a core element of proof and I as an architect know that the Orreth Firmware will
need an associated Cloud element to effectively action Cloud based Identity Providers, why isn't
it a Firmware chip." Orreth decouples the authority of agents so no one agent can do GRAVE acts
outside its scope — identity as its own firmware resident is that decoupling made flesh.

The mapping onto what stands: today the kernel's self is the root (`kernel_self.rs`, the honest
boundary's crypto row: the kernel IS its own root), the seat is minted by the kernel after the TOTP
proof (row 3a), the join desk admits bodies (row 3b), and the standing key-check is pinned above.
The chip gathers those into one firmware resident, `identity`, of the third kind (0004 block 9):
it holds the ceremony and the seats, re-challenges bodies on the cadence, fronts the cloud identity
layer (OIDC/SAML providers as the proofing step, the assurance level on the seat), and is the one
place a person's name and a DID's profile meet — so authority is decoupled from every other body,
and a cloud element extends the chip rather than the kernel. Fixture `identity-v0`; a template
`firmware-identity.v0.json` on the crew manifest. Not before 0.1.0; it opens with the cloud
identity layer this seed already names.
