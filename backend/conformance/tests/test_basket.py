# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp1, the byte law and the Basket · 2026-09-10
"""The Basket's laws (0069 §3.1): bulk never enters the mind, every entry
cites its origin, zips count as folders, the root's law refuses traversal
with one face, and interruption is weather — a crashed import resumes."""
import json
import zipfile

import pytest

from orreth_sim import basket, crypto
from orreth_sim.node import Refusal
from orreth_sim.world import build


@pytest.fixture()
def ground(tmp_path):
    """A little estate: a root with files, a subfolder, a zip, and a secret
    OUTSIDE the root that must stay unreachable."""
    root = tmp_path / "home"
    (root / "docs").mkdir(parents=True)
    (root / "notes.md").write_text("rammed earth walls breathe")
    (root / "docs" / "spec.txt").write_text("the basket keeps origins")
    (root / "docs" / "scan.pdf").write_bytes(b"%PDF-1.4 fake scan bytes")
    with zipfile.ZipFile(root / "bundle.zip", "w") as z:
        z.writestr("inner/readme.md", "carried inside the zip")
        z.writestr("inner/data.bin", b"\x00\x01\x02")
    (tmp_path / "secret.txt").write_text("outside the root")
    w = build()
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    store = tmp_path / "objects"
    return {"root": root, "node": w.universe, "store": store,
            "author": ident, "kp": kp}


def _body(node, ref):
    return json.loads(crypto._b64d(node.records[ref]["body"]).decode())


def test_ls_lists_and_marks_zips(ground):
    out = basket.ls(ground["root"])
    names = {e["name"]: e["kind"] for e in out["entries"]}
    assert names["docs"] == "dir"
    assert names["bundle.zip"] == "zip"
    assert names["notes.md"] == "file"


def test_the_root_law_refuses_traversal_with_one_face(ground):
    for evil in ("../secret.txt", str(ground["root"].parent / "secret.txt")):
        with pytest.raises(Refusal):
            basket.ls(ground["root"], ground["root"] / evil)
        with pytest.raises(Refusal):
            basket.read_entry(ground["root"], {"path": str(ground["root"] / evil)})


def test_zip_counts_as_a_folder(ground):
    out = basket.ls_zip(ground["root"], ground["root"] / "bundle.zip")
    assert {e["name"] for e in out["entries"]} == {"inner/readme.md",
                                                  "inner/data.bin"}


def test_import_lands_pointer_with_origin_and_extracts_free_text(ground):
    g = ground
    r = basket.import_entry(g["node"], g["author"], g["kp"], root=g["root"],
                            store_root=g["store"],
                            entry={"path": str(g["root"] / "notes.md")})
    assert r["status"] == "extracted"
    b = _body(g["node"], r["pointer"])["artifact_pointer"]
    assert b["content_hash"].startswith("sha256:")
    assert b["meta"]["origin"]["path"].endswith("notes.md")   # the origin cited
    # the mass rests in the store, NOT in the record body
    assert "bytes_b64" not in json.dumps(_body(g["node"], r["pointer"]))
    obj = g["store"] / b["content_hash"][7:9] / b["content_hash"][7:]
    assert obj.read_text() == "rammed earth walls breathe"
    # the free textual floor extracted, derived from the pointer
    assert g["node"].records[r["extraction"]]["derived_from"] == [r["pointer"]]


def test_a_zip_member_remembers_its_zip(ground):
    g = ground
    r = basket.import_entry(g["node"], g["author"], g["kp"], root=g["root"],
                            store_root=g["store"],
                            entry={"path": str(g["root"] / "bundle.zip"),
                                   "zip_member": "inner/readme.md"})
    o = _body(g["node"], r["pointer"])["artifact_pointer"]["meta"]["origin"]
    assert o["path"].endswith("bundle.zip")
    assert o["zip_member"] == "inner/readme.md"


def test_a_dark_format_parks_its_intent_off_the_pointer(ground):
    g = ground
    r = basket.import_entry(g["node"], g["author"], g["kp"], root=g["root"],
                            store_root=g["store"],
                            entry={"path": str(g["root"] / "docs" / "scan.pdf")})
    assert r["status"] == "dark"
    assert g["node"].records[r["parked"]]["derived_from"] == [r["pointer"]]


def test_the_bar_is_a_dial_and_wears_one_face(ground):
    g = ground
    with pytest.raises(Refusal):
        basket.import_entry(g["node"], g["author"], g["kp"], root=g["root"],
                            store_root=g["store"],
                            entry={"path": str(g["root"] / "notes.md")},
                            max_bytes=4)


def test_store_is_idempotent_and_reimport_skips_honestly(ground):
    g = ground
    e = {"path": str(g["root"] / "notes.md")}
    r1 = basket.import_entry(g["node"], g["author"], g["kp"], root=g["root"],
                             store_root=g["store"], entry=e)
    already = basket.held_hashes(g["node"])
    r2 = basket.import_entry(g["node"], g["author"], g["kp"], root=g["root"],
                             store_root=g["store"], entry=e, already=already)
    assert r2["status"] == "already-held"
    assert r2["content_hash"] == r1["content_hash"] == \
        _body(g["node"], r1["pointer"])["artifact_pointer"]["content_hash"]


def test_a_crashed_import_resumes_without_duplicates(ground):
    """Interruption is weather: pass one imports a slice; the 'crash' loses
    nothing because progress IS the log; pass two finishes the rest and the
    goods are never doubled."""
    g = ground
    entries = [{"path": str(g["root"] / "notes.md")},
               {"path": str(g["root"] / "docs" / "spec.txt")},
               {"path": str(g["root"] / "bundle.zip"),
                "zip_member": "inner/readme.md"}]
    job = basket.make_job(g["author"], g["kp"], "u:demo", entries)
    g["node"].write(job)
    first = basket.run_job(g["node"], g["author"], g["kp"], root=g["root"],
                           store_root=g["store"], entries=entries,
                           job_ref=job["id"], limit=1)
    assert first["attempted"] == 1 and first["of"] == 3
    # ---- the crash: a fresh pass reads only the log ----
    second = basket.run_job(g["node"], g["author"], g["kp"], root=g["root"],
                            store_root=g["store"], entries=entries[1:],
                            job_ref=job["id"])
    assert second["failed"] == []
    pointers = [r for r in g["node"].records.values()
                if "artifact-pointer" in (r.get("tags") or [])]
    assert len(pointers) == 3                      # one per entry, no doubles
    done = basket.finish_job(g["node"], g["author"], g["kp"], "u:demo",
                             job_ref=job["id"], imported=3, skipped=0,
                             failed=[])
    assert _body(g["node"], done)["import_done"]["interrupted"] is False


def test_a_vanished_file_finishes_interrupted_never_pretending(ground):
    g = ground
    gone = g["root"] / "gone.txt"
    gone.write_text("here for a moment")
    entries = [{"path": str(gone)}, {"path": str(g["root"] / "notes.md")}]
    job = basket.make_job(g["author"], g["kp"], "u:demo", entries)
    g["node"].write(job)
    gone.unlink()                                  # the weather
    out = basket.run_job(g["node"], g["author"], g["kp"], root=g["root"],
                         store_root=g["store"], entries=entries,
                         job_ref=job["id"])
    assert len(out["failed"]) == 1
    done = basket.finish_job(g["node"], g["author"], g["kp"], "u:demo",
                             job_ref=job["id"], imported=1, skipped=0,
                             failed=out["failed"])
    d = _body(g["node"], done)["import_done"]
    assert d["interrupted"] is True and d["failed"] == 1
