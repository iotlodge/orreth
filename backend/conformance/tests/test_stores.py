# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp2, the store kind and the first wire · 2026-09-10
"""The store connector's laws (0069 §3.2): the URI reads honestly (growth
named, never faked), the on-premise citizen obeys the traversal law, the
freshness eye sees change, the manifest IS the declared operations — and a
store rides the Farm's one lifecycle unchanged."""
import time

import pytest

from orreth_sim import basket, farm as farm_mod, stores
from orreth_sim.node import Refusal


@pytest.fixture()
def ground(tmp_path):
    root = tmp_path / "shared"
    (root / "reports").mkdir(parents=True)
    (root / "readme.md").write_text("the on-premise citizen")
    (root / "reports" / "q3.csv").write_text("a,b\n1,2")
    (tmp_path / "outside.txt").write_text("never reachable")
    return root


def test_the_uri_reads_honestly():
    s3 = stores.parse_uri("s3://my-bucket/some/prefix")
    assert s3 == {"backend": "s3", "bucket": "my-bucket",
                  "prefix": "some/prefix"}
    ld = stores.parse_uri("file:///data/shared")
    assert ld == {"backend": "localdir", "root": "/data/shared"}


def test_growth_is_recognized_and_refused_with_its_name():
    with pytest.raises(stores.GrowthNotWalked) as e:
        stores.parse_uri("az://container/x")
    assert "Azure" in str(e.value) and "declared growth" in str(e.value)
    with pytest.raises(stores.GrowthNotWalked) as e2:
        stores.parse_uri("gs://bucket/x")
    assert "Google" in str(e2.value)
    # gibberish wears the one face, naming nothing
    with pytest.raises(Refusal) as e3:
        stores.parse_uri("ftp://old-world")
    assert str(e3.value) == "request cannot be served under this capability"


def test_localdir_probe_list_fetch(ground):
    uri = f"file://{ground}"
    assert stores.probe(uri) is True
    assert stores.probe("file:///nowhere/at/all") is False
    rows = stores.list_objects(uri)
    assert [r["key"] for r in rows] == ["readme.md", "reports/q3.csv"]
    assert all(r["size"] > 0 and r["modified"] > 0 for r in rows)
    assert stores.fetch(uri, "readme.md") == b"the on-premise citizen"
    # the prefix narrows
    assert [r["key"] for r in stores.list_objects(uri, prefix="reports/")] \
        == ["reports/q3.csv"]


def test_the_traversal_law_holds_on_the_wire(ground):
    uri = f"file://{ground}"
    for evil in ("../outside.txt", "reports/../../outside.txt", ".hidden"):
        with pytest.raises(Refusal):
            stores.fetch(uri, evil)


def test_the_freshness_eye_sees_change_and_holds_still(ground):
    uri = f"file://{ground}"
    fp1 = stores.fingerprint(uri)
    assert fp1 == stores.fingerprint(uri)          # a still store holds still
    time.sleep(0.02)
    (ground / "new-drop.md").write_text("fresh goods arrived")
    assert stores.fingerprint(uri) != fp1          # a moved store is news


def test_the_manifest_is_the_declared_operations():
    assert [t["name"] for t in stores.manifest()] == ["list", "fetch"]


def test_a_store_rides_the_one_farm_lifecycle():
    """L2 — a distinct kind, ONE lifecycle: plant → attest → beats earn
    serving → the rug-pull door on a changed manifest → only a human
    re-opens. Nothing store-shaped weakens the state machine."""
    f = farm_mod.Farm("u:demo/e:rag/f:swarm")
    f.plant("site-archive", did="did:key:zStoreTest", kind="store",
            endpoint="file:///data/shared", transport="store",
            manifest=stores.manifest())
    svc = f.services["site-archive"]
    assert svc["state"] == "proposed" and svc["kind"] == "store"
    f.attest("site-archive", stores.manifest())
    assert f.services["site-archive"]["state"] == "probation"
    for _ in range(farm_mod.PROBATION_BEATS):
        f.beat("site-archive")
    assert f.services["site-archive"]["state"] == "serving"
    # the rug-pull door: a store whose declared operations change quarantines
    out = f.rejoin("site-archive",
                   stores.manifest() + [{"name": "delete"}])
    assert f.services["site-archive"]["state"] == "quarantined"
    for _ in range(farm_mod.PROBATION_BEATS + 1):  # no silent way back —
        f.beat("site-archive")                     # beats never move quarantine
    assert f.services["site-archive"]["state"] == "quarantined"
    f.reapprove("site-archive")                    # only a human re-opens
    assert f.services["site-archive"]["state"] == "probation"


def test_store_bytes_ride_the_pointer_tail_with_store_origin(ground, tmp_path):
    """The sp2 join: a store object's bytes enter through import_bytes with
    the STORE as origin — the same signed pointer law as a local file."""
    from orreth_sim.world import build
    w = build()
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    uri = f"file://{ground}"
    data = stores.fetch(uri, "readme.md")
    r = basket.import_bytes(w.universe, ident, kp, data=data,
                            name="readme.md",
                            origin={"store": "site-archive",
                                    "key": "readme.md"},
                            store_root=tmp_path / "objects")
    assert r["status"] == "extracted"
    import json as _json
    from orreth_sim import crypto
    b = _json.loads(crypto._b64d(
        w.universe.records[r["pointer"]]["body"]).decode())["artifact_pointer"]
    assert b["meta"]["origin"] == {"store": "site-archive",
                                   "key": "readme.md"}


def test_the_resting_twin_is_paid():
    """0069 §2.5's found divergence: `resting` lived in the plane's state
    machine and not the Python reference — twinned now, same moves."""
    f = farm_mod.Farm("u:demo")
    f.plant("night-archive", did="did:key:zRest", kind="store",
            endpoint="file:///data", transport="store",
            manifest=stores.manifest())
    f.attest("night-archive", stores.manifest())
    for _ in range(farm_mod.PROBATION_BEATS):
        f.beat("night-archive")
    f.rest("night-archive")
    assert f.services["night-archive"]["state"] == "resting"
    for _ in range(farm_mod.PROBATION_BEATS + 1):
        f.beat("night-archive")                # beats never wake the resting
    assert f.services["night-archive"]["state"] == "resting"
    f.resume("night-archive")
    assert f.services["night-archive"]["state"] == "probation"


# ---- 0069 sp5: the database kind ---------------------------------------------------
@pytest.fixture()
def dbfile(tmp_path):
    import sqlite3
    p = tmp_path / "site.db"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE materials (name TEXT, r_value REAL)")
    c.executemany("INSERT INTO materials VALUES (?,?)",
                  [("rammed earth", 0.4), ("hempcrete", 2.1),
                   ("straw bale", 1.45)])
    c.commit(); c.close()
    return p


def test_db_uri_reads_honestly_and_growth_is_named():
    assert stores.parse_db_uri("sqlite:///data/site.db") == \
        {"backend": "sqlite", "path": "/data/site.db"}
    with pytest.raises(stores.GrowthNotWalked) as e:
        stores.parse_db_uri("postgres://host/db")
    assert "PostgreSQL" in str(e.value)


def test_db_schema_and_query_through_the_read_law(dbfile):
    uri = f"sqlite://{dbfile}"
    assert stores.db_probe(uri) is True
    sch = stores.db_schema(uri)
    assert [c["name"] for c in sch["tables"]["materials"]] == \
        ["name", "r_value"]
    out = stores.db_query(uri, "SELECT name FROM materials "
                               "WHERE r_value > 1 ORDER BY name")
    assert out["rows"] == [["hempcrete"], ["straw bale"]]
    assert out["capped"] is False


def test_the_read_only_law_wears_one_face(dbfile):
    uri = f"sqlite://{dbfile}"
    for evil in ("INSERT INTO materials VALUES ('x', 1)",
                 "DELETE FROM materials",
                 "SELECT 1; DROP TABLE materials",
                 "UPDATE materials SET r_value = 0",
                 "PRAGMA writable_schema=1"):
        with pytest.raises(Refusal) as e:
            stores.db_query(uri, evil)
        assert str(e.value) == Refusal.PUBLIC
    # ...and the rows are untouched (the second lock held too)
    out = stores.db_query(uri, "SELECT count(*) FROM materials")
    assert out["rows"] == [[3]]


def test_db_rows_cap_honestly(dbfile):
    uri = f"sqlite://{dbfile}"
    out = stores.db_query(uri, "SELECT name FROM materials", limit=2)
    assert len(out["rows"]) == 2 and out["capped"] is True
