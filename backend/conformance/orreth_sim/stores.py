# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp2, the store kind and the first wire · 2026-09-10
"""The store connector (0069 §3.2) — the Farm's first store-shaped citizen.

In plain words: a `store` is a thing you LIST and FETCH from — an S3 bucket,
an on-premise directory — planted on the Farm like any service: through the
human gate, manifest pinned, probation earned on heartbeats, restable,
discreditable, metered-as-authorized. This module is the WIRE charlotte
holds; WHY the store exists is allen's charter (the two-keeper law, L1).

The manifest of a store is its DECLARED OPERATIONS — list · fetch — so the
one invoke door's off-the-manifest refusal holds for stores exactly as it
does for tools. Its "endpoint" is a URI naming the backend and scope:

    s3://bucket/prefix        the first cloud (AWS lands first — the rig
                              already rides S3; credentials are AMBIENT,
                              boto3's default chain — a key in ZERO records)
    file:///absolute/path     the on-premise citizen (a rooted directory;
                              the Basket's traversal law holds here too)
    az:// · gs://             declared growth — recognized, refused honestly
                              until walked (the register's own phrasing)

FRESHNESS: a store whose contents change gets noticed — fingerprint() is a
cheap eye over the newest listing (keys · sizes · stamps), so the beat can
say "this store moved" without reading a single object. The seam streams
will later enter through, built without the streams (the standing lock).
"""
from __future__ import annotations

import re
from pathlib import Path

from . import crypto
from .node import Refusal

BACKENDS = ("s3", "localdir")
GROWTH = {"az": "Azure Blob", "gs": "Google Cloud Storage"}

LIST_CAP = 500                     # one listing's ceiling — paging is honest


class GrowthNotWalked(Exception):
    """A recognized backend not yet proven — named to the OPERATOR at the
    onboarding gate (this is a human-facing honesty, never a probe surface;
    the wire's own doors still wear the one face)."""


def manifest() -> list[dict]:
    """A store's pinned manifest IS its declared operations — nothing more
    may be invoked, exactly the tool law."""
    return [{"name": "list"}, {"name": "fetch"}]


def parse_uri(uri: str) -> dict:
    """The endpoint's honest reading. Growth backends are RECOGNIZED and
    refused with their name — declared growth, proven when walked."""
    u = str(uri or "")
    if u.startswith("s3://"):
        rest = u[5:]
        bucket, _, prefix = rest.partition("/")
        if not bucket:
            raise Refusal("request cannot be served under this capability")
        return {"backend": "s3", "bucket": bucket, "prefix": prefix}
    if u.startswith("file://"):
        p = u[7:]
        if not p.startswith("/"):
            raise Refusal("request cannot be served under this capability")
        return {"backend": "localdir", "root": p}
    for scheme, name in GROWTH.items():
        if u.startswith(scheme + "://"):
            raise GrowthNotWalked(
                f"{name} is declared growth — recognized, not yet walked "
                "(0069 §3.2); AWS and on-premise serve today")
    raise Refusal("request cannot be served under this capability")


def _s3():
    """boto3, ambient credentials only (the default chain — env/profile/
    role); the URI carries scope, never a secret."""
    import boto3
    return boto3.client("s3")


def probe(uri: str) -> bool:
    """The heartbeat's touch: can this store answer a one-key listing?
    False is silence, never an exception — the keeper counts misses."""
    try:
        cfg = parse_uri(uri)
        if cfg["backend"] == "localdir":
            return Path(cfg["root"]).is_dir()
        _s3().list_objects_v2(Bucket=cfg["bucket"],
                              Prefix=cfg.get("prefix") or "", MaxKeys=1)
        return True
    except Exception:
        return False


def list_objects(uri: str, *, prefix: str = "", limit: int = 200) -> list[dict]:
    """The listing: [{key, size, modified}], keys relative to the store's
    own scope, capped honestly (LIST_CAP), dotfiles unlisted on disk."""
    cfg = parse_uri(uri)
    limit = max(1, min(int(limit or 200), LIST_CAP))
    if cfg["backend"] == "localdir":
        root = Path(cfg["root"]).resolve()
        if not root.is_dir():
            raise Refusal("request cannot be served under this capability")
        rows = []
        for p in sorted(root.rglob("*")):
            if not p.is_file() or any(part.startswith(".")
                                      for part in p.relative_to(root).parts):
                continue
            key = str(p.relative_to(root))
            if prefix and not key.startswith(prefix):
                continue
            st = p.stat()
            rows.append({"key": key, "size": st.st_size,
                         "modified": int(st.st_mtime)})
            if len(rows) >= limit:
                break
        return rows
    full = (cfg.get("prefix") or "")
    if prefix:
        full = full.rstrip("/") + "/" + prefix if full else prefix
    out = _s3().list_objects_v2(Bucket=cfg["bucket"], Prefix=full,
                                MaxKeys=limit)
    rows = []
    strip = (cfg.get("prefix") or "")
    for o in out.get("Contents") or []:
        key = o["Key"]
        if strip and key.startswith(strip):
            key = key[len(strip):].lstrip("/")
        if not key:
            continue                          # the prefix's own marker object
        rows.append({"key": key, "size": int(o.get("Size") or 0),
                     "modified": int(o["LastModified"].timestamp())
                     if o.get("LastModified") else 0})
    return rows


def fetch(uri: str, key: str) -> bytes:
    """One object's bytes — under the store's own scope, traversal refused
    with the one face on disk exactly as the Basket refuses it."""
    cfg = parse_uri(uri)
    k = str(key or "").lstrip("/")
    if not k or k.startswith(".") or ".." in k.split("/"):
        raise Refusal("request cannot be served under this capability")
    if cfg["backend"] == "localdir":
        root = Path(cfg["root"]).resolve()
        p = (root / k).resolve()
        if root not in p.parents or not p.is_file():
            raise Refusal("request cannot be served under this capability")
        return p.read_bytes()
    full = ((cfg.get("prefix") or "").rstrip("/") + "/" + k).lstrip("/") \
        if cfg.get("prefix") else k
    try:
        return _s3().get_object(Bucket=cfg["bucket"], Key=full)["Body"].read()
    except Exception:
        raise Refusal("request cannot be served under this capability")


# ---- the database kind (0069 sp5): things you QUERY — schema-aware, ----------
# ---- READ-ONLY FIRST; sqlite is the on-premise citizen (stdlib, no deps) -----

DB_ROW_CAP = 200


def db_manifest() -> list[dict]:
    """A database's pinned manifest IS its declared operations — schema ·
    query, read-only; nothing else invokable."""
    return [{"name": "schema"}, {"name": "query"}]


def parse_db_uri(uri: str) -> dict:
    u = str(uri or "")
    if u.startswith("sqlite:///"):
        return {"backend": "sqlite", "path": "/" + u[len("sqlite:///"):]}
    for scheme, name in (("postgres", "PostgreSQL"), ("postgresql", "PostgreSQL"),
                         ("mysql", "MySQL")):
        if u.startswith(scheme + "://"):
            raise GrowthNotWalked(
                f"{name} is declared growth — recognized, not yet walked "
                "(0069 §3.2); sqlite serves on-premise today")
    raise Refusal("request cannot be served under this capability")


def _sqlite_ro(path: str):
    import sqlite3
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=4)


def db_probe(uri: str) -> bool:
    try:
        cfg = parse_db_uri(uri)
        with _sqlite_ro(cfg["path"]) as c:
            c.execute("SELECT 1").fetchone()
        return True
    except Exception:
        return False


def db_schema(uri: str) -> dict:
    """The schema-aware read: tables and their columns — what a caller may
    honestly plan a query against, never a byte of row data."""
    cfg = parse_db_uri(uri)
    try:
        with _sqlite_ro(cfg["path"]) as c:
            tables = [r[0] for r in c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            out = {}
            for t in tables:
                out[t] = [{"name": r[1], "type": r[2]}
                          for r in c.execute(f'PRAGMA table_info("{t}")')]
    except Exception:
        raise Refusal("request cannot be served under this capability")
    return {"tables": out}


_DB_READ_RX = None


def _read_only_sql(sql: str) -> str:
    """THE READ-ONLY LAW: one statement, SELECT (or WITH…SELECT) alone —
    anything else wears the one face. The connection is already mode=ro
    (the second lock); this gate refuses before a byte moves."""
    s = re.sub(r"/\*.*?\*/", " ", str(sql or ""), flags=re.DOTALL)
    s = re.sub(r"--[^\n]*", " ", s).strip().rstrip(";").strip()
    if not s or ";" in s:
        raise Refusal("request cannot be served under this capability")
    if not re.match(r"(?is)^(select|with)\b", s):
        raise Refusal("request cannot be served under this capability")
    return s


def db_query(uri: str, sql: str, *, limit: int = 100) -> dict:
    """One read-only query, rows capped honestly — {columns, rows, capped}."""
    cfg = parse_db_uri(uri)
    clean = _read_only_sql(sql)
    limit = max(1, min(int(limit or 100), DB_ROW_CAP))
    try:
        with _sqlite_ro(cfg["path"]) as c:
            cur = c.execute(clean)
            cols = [d[0] for d in cur.description or []]
            rows = cur.fetchmany(limit + 1)
    except Refusal:
        raise
    except Exception:
        raise Refusal("request cannot be served under this capability")
    capped = len(rows) > limit
    return {"columns": cols,
            "rows": [list(r) for r in rows[:limit]],
            "capped": capped}


def fingerprint(uri: str, *, limit: int = 50) -> str:
    """The freshness eye: a content hash over the newest listing's keys,
    sizes, and stamps — cheap enough for a beat, honest enough to say
    «this store moved» without reading one object."""
    rows = sorted(list_objects(uri, limit=limit),
                  key=lambda r: (-(r.get("modified") or 0), r["key"]))[:limit]
    return crypto.content_hash({"listing": rows})
