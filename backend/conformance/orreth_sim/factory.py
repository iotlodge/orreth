"""The Factory (0011): archetype → incarnation stamping at scale, governed.

CO's farms generalized. Every stamped incarnation walks through the Gateway (0010) —
leased, budgeted, surfaced — and its birth certificate is written as memory (identity
operations are memory too, 0006 §4). Upgrades arrive via the Standards cascade with
memory intact; a re-stamp is a NEW life with the same lineage — a sibling, never a
silent successor (locked 2026-07-02). Rookies play under full observation until their
first bundle earns a track record (locked 2026-07-02).
"""
from __future__ import annotations

from . import crypto
from .agent_surface import AgentSurface
from .identity import NOW
from .schemas import validate


class QuotaExceeded(Exception):
    """0013 §8's hard scale caps, mechanical: the stamp_quota dial refused this order."""


def stamp(node, becky, archetype: dict, count: int, *, generation: str,
          skills: list[dict] | None = None, budget_tokens: int = 5000,
          probation_runs: int = 5) -> list[AgentSurface]:
    """One order, many lives — each doored in through the Gateway, each with a birth certificate."""
    quota = node.profile.get("stamp_quota")
    if quota is not None and node.stamped_live + count > quota:
        raise QuotaExceeded(f"order of {count} exceeds stamp_quota {quota} "
                            f"({node.stamped_live} live)")
    order = {
        "id": crypto.content_hash({"a": archetype["did"], "s": node.scope,
                                   "g": generation, "n": count, "at": NOW()}),
        "archetype": archetype["did"],
        "to_scope": node.scope,
        "count": count,
        "generation": generation,
        **({"skills": skills} if skills else {}),
        "budget_tokens": budget_tokens,
        "probation_runs": probation_runs,
        "ordered_by": becky.did,
    }
    order["sig"] = becky.kp.sign(becky.did, {k: order[k] for k in
                                             ("id", "archetype", "to_scope", "count", "generation")})
    validate(order, "factory.schema.json")

    surfaces: list[AgentSurface] = []
    for _ in range(count):
        ident, kp = becky.issue_identity("instance", node.scope, lineage=archetype["did"])
        lease = becky.issue_token(
            ident["did"], node.scope,
            [{"action": "retrieve", "space": "self"}, {"action": "write", "space": "self"}],
            budget={"tokens": budget_tokens})
        cert = {
            "incarnation": ident["did"],
            "archetype": archetype["did"],
            "generation": generation,
            "order": order["id"],
            "stamped_by": becky.did,
            "born_at": ident["born_at"],
            **({"skills": skills} if skills else {}),
            "probation_until_n": probation_runs,
        }
        cert["sig"] = becky.kp.sign(becky.did, {k: cert[k] for k in
                                                ("incarnation", "archetype", "generation", "order")})
        validate(cert, "factory.schema.json#/$defs/BirthCertificate")
        # identity operations are memory: the certificate lands as a signed record at the scope
        from .node import make_memory
        node.write(make_memory(node.steward, node.steward_kp, node.scope,
                               {"birth_certificate": cert}, kind="semantic",
                               tags=["birth-certificate", generation]))
        node.stamped_live += 1
        surf = AgentSurface(node, ident, kp, lease)
        surf.birth_certificate = cert       # the provenance travels with the handle
        surfaces.append(surf)
    return surfaces


def retire(node, identity: dict) -> None:
    """A governed end-of-life (0002 §1): the memory outlives the incarnation; the quota slot frees."""
    identity["status"] = "retired"
    node.stamped_live -= 1


def judge_rate(node, cert: dict, bundle: dict) -> float:
    """Locked 2026-07-02: full-grade until the first bundle reaches the probation n —
    then the tier's steady-state sampling. Uncertainty pays for observation, nothing else does."""
    if bundle["n"] < cert["probation_until_n"]:
        return 1.0
    return node.profile["model_gateway"]["judge_sample_rate"]
