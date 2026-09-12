# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0072 sp4, the package · 2026-09-12
"""The capability package (0072 §3.3 — KCR-0002's payment): a capability
becomes a sealed, signed box a stranger installs into their own world
through their own human gate — instead of a folder copied into our
repository checkout.

THE FORMAT'S LAWS, all mechanical here:
- **Content-addressed**: the box's identity IS the hash of its declaration
  bytes (canonical, the one byte law — 0000 §3). A changed byte is a
  different box; there is no «edit», only a new box.
- **Publisher-attested**: an Ed25519 signature over the whole box (minus
  itself) by the publisher's did:key — self-certifying, verifiable offline
  by any receiving world (0006 §1).
- **Declarations, never code**: the box carries a manifest (typed panels
  the kernel renders blind — 0055), craft (words for the shelf), and crew
  as CONTAINER IMAGES routed through the deed walk (0062) — the
  repo-relative shell command era's words (`cmd`, `cwd`, `match`) are
  REFUSED at verify: a stranger's box never executes into a checkout.
- **Un-install is a governed retire** — records stay; the world is
  remembered (the capability-verb lane already keeps this law).

This module is pure: pack and verify are functions of bytes and keys.
The install road (the gate card, the shelf planting, the deed walk, the
generalized discoverer) lives in the worker beside its peers.
"""
from __future__ import annotations

from . import crypto

FORMAT = "orreth-package-v1"

# the folder era's crew words — each one a shell into a checkout, none of
# them a stranger's to ask for
_CREW_FORBIDDEN = ("cmd", "cwd", "match", "log")


def crew_flaw(crew) -> str | None:
    """A package's crew is containers by image — never shell commands into
    a checkout. The refusal names the era it retires."""
    if crew is None:
        return None
    if not isinstance(crew, list):
        return "«crew» must be a list of container declarations"
    for c in crew:
        if not isinstance(c, dict) or not c.get("name") or not c.get("image"):
            return ("each crew entry declares {name, image} — a container "
                    "the deed walk can raise, nothing less")
        bad = [k for k in _CREW_FORBIDDEN if k in c]
        if bad:
            return (f"crew entry «{c.get('name')}» carries {'/'.join(bad)} — "
                    "the checkout era's shell words; a package's crew is "
                    "containers by image through the deed walk (0062), "
                    "never commands into a repository")
    return None


def _payload(key: str, declarations: dict) -> dict:
    return {"format": FORMAT, "key": key, "declarations": declarations}


def pack(key: str, manifest: dict, craft: dict | None = None,
         crew: list | None = None, seeds: dict | None = None, *,
         keypair, publisher_did: str) -> dict:
    """Seal the box: declarations → canonical bytes → hash = identity →
    the publisher's signature over everything. The crew law is enforced at
    PACK too — a publisher cannot even build a box that shells out."""
    flaw = crew_flaw(crew if crew is not None else manifest.get("crew"))
    if flaw:
        raise ValueError(flaw)
    declarations = {"manifest": dict(manifest),
                    "craft": dict(craft or {}),
                    "crew": list(crew if crew is not None
                                 else manifest.get("crew") or []),
                    "seeds": dict(seeds or {})}
    payload = _payload(key, declarations)
    box = dict(payload)
    box["id"] = crypto.content_hash(payload)
    box["publisher"] = publisher_did
    box["signature"] = keypair.sign(publisher_did, box)
    return box


def verify(box, panel_kinds=None) -> str | None:
    """The receiving world's whole examination, offline: format · identity
    (the hash re-computed from the bytes) · the publisher's signature
    against their own self-certifying key · the crew law · and, when the
    vocabulary is handed in, every declared panel within the canon. One
    clean None or the FIRST flaw named — a stranger learns exactly what to
    fix, an installer never guesses."""
    if not isinstance(box, dict):
        return "a package is an object — this is not one"
    if box.get("format") != FORMAT:
        return f"unknown package format «{box.get('format')}» — this world speaks {FORMAT}"
    key = str(box.get("key") or "")
    decl = box.get("declarations")
    if not key or not isinstance(decl, dict):
        return "the box declares nothing — «key» and «declarations» are its bones"
    want = crypto.content_hash(_payload(key, decl))
    if box.get("id") != want:
        return ("the bytes do not match the name on the box — its id is "
                "not the hash of its declarations (tampered or corrupt; "
                "a changed byte is a different box)")
    pub = str(box.get("publisher") or "")
    pk = crypto.public_from_did(pub)
    if not pk:
        return "the publisher is not a did:key — provenance must be self-certifying"
    sig = box.get("signature")
    if not isinstance(sig, dict) or not crypto.verify_sig(sig, box, pk):
        return ("the publisher's signature does not verify — the box does "
                "not carry its claimed provenance")
    man = decl.get("manifest")
    if not isinstance(man, dict) or not man.get("key") or not man.get("view"):
        return "the manifest is missing — «key», «view» at least"
    if man.get("key") != key:
        return "the manifest's key differs from the box's — one name, one world"
    flaw = crew_flaw(decl.get("crew"))
    if flaw:
        return flaw
    if panel_kinds is not None:
        for pnl in man.get("view") or []:
            kind = (pnl or {}).get("kind")
            if kind not in panel_kinds:
                return (f"panel kind «{kind}» is beyond this world's canon "
                        "vocabulary — the glass here cannot render it "
                        "(growing the vocabulary is a RELEASE, not an install)")
    return None


def summary(box: dict) -> dict:
    """The gate card's contents — everything the human weighs before the
    word: what it is, what rooms it asks for, what crew it would raise,
    who published it, and the name of its exact bytes."""
    decl = box.get("declarations") or {}
    man = decl.get("manifest") or {}
    return {"key": box.get("key"), "name": man.get("name"),
            "rooms": [p.get("kind") for p in (man.get("view") or [])],
            "floors": [f.get("scope") for f in (man.get("floors") or [])],
            "craft": sorted((decl.get("craft") or {}).keys()),
            "crew_images": [c.get("image") for c in (decl.get("crew") or [])],
            "publisher": box.get("publisher"), "id": box.get("id")}
