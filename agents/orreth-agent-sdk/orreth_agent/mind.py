# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp2, the jacket · 2026-08-07
"""OrrethMind — the governance jacket (0047 §7): identity outside, cognition
inside.

The jacket is OURS and engine-agnostic (0000: lift the contract, port the
engine). Whatever thinks inside it — the built-in governed-predict lane
today, the pinned NOOA engine when the studio's CodeAct lane lands — the
seams never move:

· IDENTITY — a FieldClient: the keypair is the self and survives the
  process (rule 1); the mind joins through becky's gate and holds a lease.
· CRAFT — a generation method names its craft by REFERENCE and the prompt
  is served from the governed shelf (0045 law 8, all four riders): one run,
  one resolution; the run's record names the exact version. This is the
  jacket's deliberate inversion of NOOA — NOOA puts the prompt in the
  docstring; Orreth puts a reference in the decorator and the words in the
  Craft Room, where the humans it serves can read and release them.
· THE GOVERNED SEAM — every thought is `think(klass, prompt) -> str`; the
  plane authorizes, the caller executes on its own keys, the meter
  reconciles (0016/0019). The jacket never touches a model directly.
· TYPED THOUGHT — the 0047 sp1 law, kept at this door: a malformed return
  earns ONE re-ask carrying the named error; a twice-failed thought PARKS
  honestly (0015 — failure is fuel) and raises, never a guessed value.
· THE SCRIBE — one RunRecord per generation-method call, scribe-authored
  (author ≠ agent, 0005), `context_hash` pinning the craft version the
  method thought with.

The CodeAct lane refuses honestly until lock 3 (sandbox posture) lands — a
jacket with an unsandboxed cell would be a hole wearing a nice name.
"""
from __future__ import annotations

import inspect
import json
import re

from .craft import acquire

# Genesis wording (0031 §4: constants are genesis; the shelf may override) —
# the re-ask names the error and the shape, the sp1 law's SDK twin.
_REASK = ("Your previous reply was not valid: {error}. Reply again matching "
          "the contract exactly — {shape} — with no preamble and no code "
          "fences.")


class MindParked(Exception):
    """The thought failed its contract twice and was parked — never guessed.
    Carries the park record id (when the floor accepted it) and the error."""

    def __init__(self, message: str, record: str | None = None):
        super().__init__(message)
        self.record = record


class MindEngineUnavailable(Exception):
    """The requested engine cannot stand yet — the reason names its gate."""


def _shape_of(returns) -> str:
    if isinstance(returns, dict):
        return ("STRICT JSON: {"
                + ", ".join(f'"{k}": {t.__name__}' for k, t in returns.items())
                + "}")
    return "plain text"


def _validate(returns, raw: str):
    """The typed floor (law 4: well-formed is not true). returns may be:
    None/str → raw text passes; a {field: type} dict → strict JSON, fields
    present, types held (int serves float); a callable → returns the value
    or raises ValueError with the error the re-ask will name."""
    if returns is None or returns is str:
        return raw
    if callable(returns) and not isinstance(returns, dict):
        return returns(raw)
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        raise ValueError("no JSON object found in the reply")
    try:
        got = json.loads(m.group(0))
    except Exception as e:
        raise ValueError(f"the JSON did not parse ({e})") from e
    out = {}
    for k, t in returns.items():
        if k not in got:
            raise ValueError(f"the field \"{k}\" is missing")
        v = got[k]
        if t is float and isinstance(v, int):
            v = float(v)
        if not isinstance(v, t):
            raise ValueError(f"the field \"{k}\" is not {t.__name__}")
        out[k] = v
    return out


class Generation:
    """An ellipsis-bodied method worn by the jacket: craft by reference,
    typed return, one named-error re-ask, a scribe line per call."""

    def __init__(self, fn, *, klass: str, craft: str, returns=None,
                 max_asks: int = 2, est_tokens: int = 400):
        self.fn, self.klass, self.craft = fn, klass, craft
        self.returns, self.max_asks = returns, max(1, int(max_asks))
        self.est_tokens = est_tokens
        self.slots = [p for p in inspect.signature(fn).parameters
                      if p != "self"]
        self.__doc__ = fn.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, mind, owner):
        if mind is None:
            return self
        def call(*args, **kwargs):
            return mind._run(self, args, kwargs)
        call.__name__, call.__doc__ = self.name, self.__doc__
        return call


def generation(*, klass: str = "medium", craft: str, returns=None,
               max_asks: int = 2, est_tokens: int = 400):
    """Declare a generation method. `craft` names the shelf record whose
    ⟦slots⟧ are this method's parameters; `returns` is the typed contract."""
    def wrap(fn):
        return Generation(fn, klass=klass, craft=craft, returns=returns,
                          max_asks=max_asks, est_tokens=est_tokens)
    return wrap


class OrrethMind:
    """The jacket. Subclass it, declare @generation methods, hand it a
    joined FieldClient and a governed think — then call the methods like
    ordinary Python. Engines: "governed-predict" (built-in, the default);
    "nooa" declares the pinned engine seat (lock 1) and refuses honestly
    until its CodeAct sandbox posture (lock 3) lands."""

    def __init__(self, client, think, *, engine: str = "governed-predict",
                 craft_base: str = "http://localhost:4562",
                 on_dark: str = "refuse", pins: dict | None = None,
                 craft_fetch=None):
        if engine == "nooa":
            try:
                import nooa  # noqa: F401
            except Exception as e:
                raise MindEngineUnavailable(
                    "the pinned nooa engine is not installed (lock 1: "
                    f"uv add nooa) — {e}") from e
            raise MindEngineUnavailable(
                "the nooa adapter lands with the studio seat — its CodeAct "
                "cell waits on lock 3 (sandbox posture); the jacket's seams "
                "are ready for it")
        if engine != "governed-predict":
            raise MindEngineUnavailable(f"no engine named \"{engine}\"")
        self.client, self.think = client, think
        self.on_dark, self.pins = on_dark, dict(pins or {})
        self._craft_base = craft_base
        self._fetch = craft_fetch or (lambda name: acquire(
            name, did=client.did, base=craft_base,
            pin=self.pins.get(name), on_dark=on_dark))
        self._crafts: dict = {}       # one run, one resolution (law 8)

    def _craft(self, name: str):
        if name not in self._crafts:
            self._crafts[name] = self._fetch(name)
        return self._crafts[name]

    def _run(self, g: Generation, args, kwargs):
        resolved = self._craft(g.craft)
        slots = dict(zip(g.slots, args))
        slots.update(kwargs)
        prompt = resolved.render(**{k: slots.get(k, "") for k in g.slots})
        unfilled = sorted(set(re.findall(r"⟦(\w+)⟧", prompt)))
        if unfilled:
            raise ValueError(
                f"the craft \"{g.craft}\" wants slots this method does not "
                f"fill: {', '.join(unfilled)} — declare them as parameters")
        intent = f"mind.{g.name}"
        t0 = getattr(self.think, "last_tokens", 0)
        error = None
        for ask in range(1, g.max_asks + 1):
            ask_prompt = prompt if error is None else (
                prompt + "\n\n" + _REASK.format(
                    error=error, shape=_shape_of(g.returns)))
            raw = self.think(g.klass, ask_prompt)
            try:
                value = _validate(g.returns, raw)
            except ValueError as e:
                error = str(e)
                continue
            self.client.diary(intent, cycle=ask, done=True,
                              tokens=getattr(self.think, "last_tokens", 0) - t0,
                              model_calls=ask, context_hash=resolved.ref)
            return value
        # the breaker (0015): parked with the error named, never a guess
        rec = self.client.park(intent, f"the reply failed its contract "
                                       f"{g.max_asks}x: {error}")
        self.client.diary(intent, cycle=g.max_asks, done=False,
                          tokens=getattr(self.think, "last_tokens", 0) - t0,
                          model_calls=g.max_asks, context_hash=resolved.ref)
        raise MindParked(
            f"{intent} failed its contract {g.max_asks}x ({error}) — parked",
            record=rec)
