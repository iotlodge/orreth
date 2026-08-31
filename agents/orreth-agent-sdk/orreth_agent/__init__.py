"""orreth-agent — the lifeforce kit.

    from orreth_agent import FieldClient, Chassis, RuleThink, GovernedThink

    client = FieldClient("http://127.0.0.1:4502", name="scout")
    client.join()                       # a governed request; becky answers with a lease
    Chassis(client, RuleThink()).run("say hello to the universe")
    # …and the agent is now visible in the Console: roster, orrery, diary, spend.
"""
from .capability import PANEL_KINDS, manifest
from .chassis import Chassis, GovernedThink, RuleThink
from .client import FieldClient, JoinRefused
from .craft import ResolvedCraft, acquire
from .crypto import KeyPair, canonical, content_hash, did_key_for
from .mind import Generation, MindEngineUnavailable, MindParked, OrrethMind, generation

__all__ = ["FieldClient", "JoinRefused", "Chassis", "RuleThink", "GovernedThink",
           "KeyPair", "canonical", "content_hash", "did_key_for",
           "OrrethMind", "Generation", "generation", "MindParked", "MindEngineUnavailable",
           "acquire", "ResolvedCraft", "manifest", "PANEL_KINDS"]
