"""Schema registry: every wire object in the simulator validates against contracts/v0.

The contracts are the product (0000 §4); the simulator exists to prove them.
"""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

_CONTRACTS = Path(__file__).resolve().parents[3] / "contracts" / "v0"
_NS = "https://orreth.ai/contracts/v0/"


class SchemaError(Exception):
    pass


def _load() -> dict[str, dict]:
    out = {}
    for f in sorted(_CONTRACTS.glob("*.schema.json")):
        s = json.loads(f.read_text())
        out[s["$id"]] = s
    if not out:
        raise SchemaError(f"no contracts found at {_CONTRACTS}")
    return out


_SCHEMAS = _load()
_REGISTRY = Registry().with_resources(
    [(sid, Resource.from_contents(s)) for sid, s in _SCHEMAS.items()]
)
_VALIDATORS: dict[str, Draft202012Validator] = {}


def _validator(ref: str) -> Draft202012Validator:
    if ref not in _VALIDATORS:
        if "#" in ref:
            base, frag = ref.split("#", 1)
            schema = {"$ref": f"{_NS}{base}#{frag}"}
        else:
            schema = {"$ref": f"{_NS}{ref}"}
        _VALIDATORS[ref] = Draft202012Validator(schema, registry=_REGISTRY)
    return _VALIDATORS[ref]


def validate(instance: dict, ref: str) -> dict:
    """Validate an instance against a contract ref like 'memory-record.schema.json'
    or 'retrieval.schema.json#/$defs/Query'. Returns the instance for chaining."""
    errors = sorted(_validator(ref).iter_errors(instance), key=lambda e: str(e.path))
    if errors:
        msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:3])
        raise SchemaError(f"{ref}: {msgs}")
    return instance
