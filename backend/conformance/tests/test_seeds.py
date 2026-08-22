# PROVENANCE: Fable 5 (claude-fable-5) — 0059 sp1, the seed catalog · 2026-08-21
"""The Seed Catalog (0059 sp1) — under conformance.

Under test: the registry's version rows fold to one seed per server name
preferring the row marked latest; provenance rides every seed; what already
stands on the rig OUTRANKS what could be planted (local first in the merge);
the per-query cache answers inside its TTL without touching the wire; and a
downed wire serves the last good answer, labeled stale — a note, never an
outage."""
import json

from orreth_sim import seeds


def _reg(rows):
    return {"servers": [
        {"server": {"name": n, "description": d, "version": v,
                    "remotes": [{"type": "streamable-http", "url": u}]},
         "_meta": {"io.modelcontextprotocol.registry/official":
                   {"status": "active", "isLatest": latest}}}
        for n, d, v, u, latest in rows]}


def test_versions_fold_to_latest():
    fetch = lambda url: _reg([
        ("acme/search", "old", "1.0.0", "https://a/mcp", False),
        ("acme/search", "new", "1.2.0", "https://a/mcp", True),
        ("beta/tools", "only", "0.1.0", "https://b/mcp", False)])
    out, note = seeds.registry_search("search", fetch=fetch)
    assert len(out) == 2
    acme = next(e for e in out if e["id"] == "acme/search")
    assert acme["version"] == "1.2.0" and acme["latest"] is True
    assert acme["source"] == "mcp-registry"
    assert acme["remotes"][0]["url"] == "https://a/mcp"
    assert out[0]["latest"] is True          # the latest stand first


def test_local_outranks_the_market(tmp_path):
    fetch = lambda url: _reg([("acme/search", "x", "1.0", "https://a", True)])
    local = [{"id": "tavily-mcp", "description": "the rig's own search",
              "source": "toolshed", "state": "serving"}]
    out = seeds.search(tmp_path, "search", local=local, fetch=fetch)
    assert out["entries"][0]["id"] == "tavily-mcp"    # what stands, first
    assert out["local"] == 1 and out["registry"] == 1
    assert out["stale"] is False


def test_cache_answers_inside_ttl(tmp_path):
    calls = {"n": 0}

    def fetch(url):
        calls["n"] += 1
        return _reg([("acme/search", "x", "1.0", "https://a", True)])
    seeds.search(tmp_path, "search", fetch=fetch)
    seeds.search(tmp_path, "search", fetch=fetch)
    assert calls["n"] == 1                    # the second answer was the cache's


def test_downed_wire_serves_the_last_good_answer(tmp_path):
    fetch = lambda url: _reg([("acme/search", "x", "1.0", "https://a", True)])
    seeds.search(tmp_path, "search", fetch=fetch)

    def boom(url):
        raise RuntimeError("the wire is down")
    out = seeds.search(tmp_path, "search", fetch=boom, force=True)
    assert out["stale"] is True
    assert any(e["id"] == "acme/search" for e in out["entries"])
    assert "wire is down" in out["note"]


def test_cache_is_json_on_disk(tmp_path):
    fetch = lambda url: _reg([("acme/search", "x", "1.0", "https://a", True)])
    seeds.search(tmp_path, "search", fetch=fetch)
    raw = json.loads((tmp_path / "seeds-cache.json").read_text())
    assert any(v.get("q") == "search" for v in raw.values())
