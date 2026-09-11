# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp1, the byte law and the Basket · 2026-09-10
"""The Basket and the byte law (0069 §3.1) — Wave 2 of the E-RAG program opens.

In plain words: you point at a folder, the Basket lists what's inside, you
tick the files you want, move to another folder and keep ticking — the
Basket keeps your list with each file's origin — and when you're done, one
Import brings them all in. Zips count as folders: the Basket looks inside.

THE BYTE LAW, changed honestly: imported files land as ORIGINS — the mass
rests content-addressed in a class-appropriate object store, and what enters
the signed log is the artifact-POINTER (0039 §6: signed pointer + content
hash + origin metadata + lineage; bulk never enters the mind). The old
256 KB inline path stays for small things, its bar now a dial.

THE QUEUE LAW (the openwiki discipline): interruption is weather. An import
job is a signed record; progress IS the log (an entry is done exactly when
its pointer stands); a crashed import resumes by construction, and the
completion record says "interrupted" rather than pretending completeness.

Safety: every path the Basket touches is resolved against a declared root —
a traversal outside it wears the one face, and dotfiles stay unlisted.
"""
from __future__ import annotations

import hashlib
import json as _json
import zipfile
from pathlib import Path

from . import crypto
from .node import Refusal, make_memory

# the per-file bar on the pointer path — a DIAL governs the live value
# (import-max-mb); this constant is the firmware fallback only
MAX_IMPORT_BYTES = 100 * 1024 * 1024

_TEXTUAL = {"txt", "md", "json", "csv"}


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def _inside(root: Path, p: Path) -> Path:
    """The traversal law: every path resolves and must live under the root —
    outside it, the one face (a prober learns nothing about the host)."""
    rp = p.expanduser().resolve()
    rr = root.expanduser().resolve()
    if rp != rr and rr not in rp.parents:
        raise Refusal("request cannot be served under this capability")
    return rp


def ls(root: str | Path, path: str | Path | None = None) -> dict:
    """One directory's honest listing: folders first, then files with sizes,
    zips marked as openable. Dotfiles stay private to the host."""
    root = Path(root)
    p = _inside(root, Path(path) if path else root)
    if not p.is_dir():
        raise Refusal("request cannot be served under this capability")
    dirs, files = [], []
    for child in sorted(p.iterdir(), key=lambda c: c.name.lower()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            dirs.append({"name": child.name, "kind": "dir"})
        elif child.is_file():
            files.append({"name": child.name,
                          "kind": "zip" if _ext(child.name) == "zip" else "file",
                          "size": child.stat().st_size})
    parent = str(p.parent) if p != root.expanduser().resolve() else None
    return {"path": str(p), "parent": parent, "entries": dirs + files}


def ls_zip(root: str | Path, zip_path: str | Path) -> dict:
    """A zip counts as a folder: its file list, each entry remembering the
    zip it came from (directories inside are implicit; dot-entries skipped)."""
    p = _inside(Path(root), Path(zip_path))
    try:
        with zipfile.ZipFile(p) as z:
            rows = [{"name": i.filename, "kind": "file", "size": i.file_size}
                    for i in z.infolist()
                    if not i.is_dir()
                    and not Path(i.filename).name.startswith(".")]
    except (zipfile.BadZipFile, OSError):
        raise Refusal("request cannot be served under this capability")
    return {"path": str(p), "zip": True, "entries": rows}


def read_entry(root: str | Path, entry: dict) -> bytes:
    """One basket entry's bytes: a file on disk, or a member inside a zip —
    both under the root's law."""
    p = _inside(Path(root), Path(str(entry.get("path") or "")))
    member = entry.get("zip_member")
    if member:
        with zipfile.ZipFile(p) as z:
            info = z.getinfo(str(member))
            if info.is_dir():
                raise Refusal("request cannot be served under this capability")
            return z.read(info)
    if not p.is_file():
        raise Refusal("request cannot be served under this capability")
    return p.read_bytes()


def store_object(store_root: str | Path, data: bytes) -> tuple[str, str]:
    """The mass rests content-addressed in the object store — idempotent by
    construction (same bytes, same address; a re-import writes nothing).
    Returns (content_hash, uri)."""
    h = "sha256:" + hashlib.sha256(data).hexdigest()
    d = Path(store_root) / h[7:9]
    d.mkdir(parents=True, exist_ok=True)
    f = d / h[7:]
    if not f.exists():
        tmp = f.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.rename(f)                     # a torn write never wears the hash's name
    return h, f"store://local/{h[7:]}"


def held_hashes(node) -> set[str]:
    """Which goods the log already points at — the resume law's memory."""
    out = set()
    for rec in node.records.values():
        if "artifact-pointer" not in (rec.get("tags") or []):
            continue
        try:
            b = _json.loads(crypto._b64d(rec["body"]).decode())
            h = ((b.get("artifact_pointer") or {}).get("content_hash"))
            if h:
                out.add(h)
        except Exception:
            continue
    return out


def import_entry(node, author: dict, kp, *, root: str | Path,
                 store_root: str | Path, entry: dict,
                 max_bytes: int | None = None,
                 already: set[str] | None = None,
                 rails: dict | None = None) -> dict:
    """One LOCAL entry's whole admission on the pointer path: bytes read
    under the root's law, then the shared tail (import_bytes). A store
    entry's bytes arrive through the governed connector instead — same
    tail, different origin (0069 sp2)."""
    data = read_entry(root, entry)
    name = Path(str(entry.get("zip_member") or entry.get("path"))).name
    origin = {"path": str(entry.get("path") or ""),
              **({"zip_member": str(entry["zip_member"])}
                 if entry.get("zip_member") else {})}
    return import_bytes(node, author, kp, data=data, name=name,
                        origin=origin, store_root=store_root,
                        max_bytes=max_bytes, already=already, rails=rails)


def import_bytes(node, author: dict, kp, *, data: bytes, name: str,
                 origin: dict, store_root: str | Path,
                 max_bytes: int | None = None,
                 already: set[str] | None = None,
                 rails: dict | None = None) -> dict:
    """The pointer path's shared tail: the bar (a dial) → the object store →
    the SIGNED pointer carrying its origin — then THE EXTRACTION LINE
    (0069 sp3): plain text free as always, PDF/Office/HTML deterministically,
    an eye-needing format parked honestly naming its eye, a failed parse
    parked naming its flaw. `rails` is 0068's redaction-at-ingest: the
    composed content rules run on the extracted text BEFORE it becomes a
    knowledge record — a refusing rule means no knowledge is minted (the
    refusal named on the record), a masking rule means the mind never holds
    the raw span. Every receipt cites its origin and carries the rails'
    events for the caller's audit."""
    from . import canon, extract
    bar = max_bytes if max_bytes is not None else MAX_IMPORT_BYTES
    if not data or len(data) > bar:
        raise Refusal("request cannot be served under this capability")
    h, uri = store_object(store_root, data)
    if already is not None and h in already:
        return {"status": "already-held", "content_hash": h, "origin": origin}
    pid = canon.make_pointer(
        node, author, kp, name=name, uri=uri, content_hash=h,
        meta={"origin": origin, "size": len(data), "ext": _ext(name),
              "via": "the-basket"})
    if already is not None:
        already.add(h)
    receipt = {"status": "held", "pointer": pid, "content_hash": h,
               "origin": origin}
    text, ex_meta = None, {}
    if _ext(name) in _TEXTUAL:
        text = data.decode("utf-8", errors="replace")
    else:
        try:
            got = extract.extract(name, data)
            if got is not None:
                text = got["text"]
                ex_meta = {"extractor": got["extractor"], **got["meta"]}
        except extract.ExtractionFailed as e:
            return _park(node, author, kp, pid, name, receipt,
                         missing=f"a readable shape — {e}")
    if text is None:
        return _park(node, author, kp, pid, name, receipt,
                     missing=extract.eye_needed(name)
                     or "a saddled eye on the Stable (0019)")
    events = []
    if rails is not None:
        from . import rails as _rails
        rr = _rails.enforce(rails, "entering", text)
        events = rr["events"]
        receipt["redaction"] = events
        if rr["refused"]:
            ref = make_memory(author, kp, node.scope,
                              {"redaction_refusal": {
                                  "artifact": pid, "name": name,
                                  "why": rr["refusal"],
                                  "events": events}},
                              kind="episodic",
                              tags=["redaction-refused", name])
            ref["derived_from"] = [pid]
            receipt.update(status="refused-at-ingest",
                           refusal=node.write(ref))
            return receipt
        text = rr["text"]
    ext = make_memory(author, kp, node.scope,
                      {"knowledge": text[:2000],
                       "source": {"did": author["did"], "ref": name},
                       "state": "untrusted",
                       "intent": f"basket import: {name}",
                       **({"extraction": ex_meta} if ex_meta else {})},
                      kind="semantic", tags=["knowledge", "document"],
                      provenance_class="ingested-archive")
    ext["derived_from"] = [pid]
    receipt.update(status="extracted", extraction=node.write(ext))
    return receipt


def _park(node, author, kp, pid: str, name: str, receipt: dict, *,
          missing: str) -> dict:
    """The honest park, its missing thing NAMED — the retry list the day
    the eye saddles or the shape heals."""
    parked = make_memory(author, kp, node.scope,
                         {"parked_intent": f"extract the artifact {name}",
                          "missing": missing,
                          "handoff": "knowledge-acquisition",
                          "artifact": pid},
                         kind="semantic", tags=["parked", "knowledge-intent"])
    parked["derived_from"] = [pid]
    receipt.update(status="dark", parked=node.write(parked))
    return receipt


def pay_parked(node, author: dict, kp, *, read_bytes, rails: dict | None = None,
               limit: int = 2) -> list[dict]:
    """0069 sp3 — THE PARKED LIST IS THE RETRY LIST, finally paid: sweep the
    lot for parks whose artifact the line can now read; extract, run the
    ingest rails, and land the knowledge tagged `librarian-handled` and
    derived from BOTH the artifact and the park — the lot forgets a paid
    park by the librarian's own law. `read_bytes(artifact_ref) -> bytes|None`
    is the caller's hand into its store. A failed parse or a dark eye leaves
    the park standing, honestly."""
    from . import extract
    from .librarian import parked_intents
    paid = []
    for park_id, body in parked_intents(node)[:max(1, limit) * 4]:
        aid = str((body.get("parked_intent") and body.get("artifact")) or "")
        if not aid:
            continue
        art = node.records.get(aid)
        if art is None:
            continue
        name = ""
        try:
            ab = _json.loads(crypto._b64d(art["body"]).decode())
            name = str((ab.get("artifact_pointer") or {}).get("name")
                       or (ab.get("artifact") or {}).get("filename") or "")
        except Exception:
            continue
        if not extract.can_extract(name):
            continue
        data = read_bytes(aid)
        if not data:
            continue
        try:
            got = extract.extract(name, data)
        except extract.ExtractionFailed:
            continue                          # the park stands, its why known
        if got is None:
            continue
        text, events = got["text"], []
        if rails is not None:
            from . import rails as _rails
            rr = _rails.enforce(rails, "entering", text)
            events = rr["events"]
            if rr["refused"]:
                continue                      # refused at ingest — the park
                                              # stands under the rails' word
            text = rr["text"]
        rec = make_memory(author, kp, node.scope,
                          {"knowledge": text[:2000],
                           "source": {"did": author["did"], "ref": name},
                           "state": "untrusted",
                           "intent": f"the parked intent paid: {name}",
                           "extraction": {"extractor": got["extractor"],
                                          **got["meta"]}},
                          kind="semantic",
                          tags=["knowledge", "document", "librarian-handled"],
                          provenance_class="ingested-archive")
        rec["derived_from"] = [aid, park_id]
        paid.append({"park": park_id, "artifact": aid, "name": name,
                     "knowledge": node.write(rec), "redaction": events})
        if len(paid) >= limit:
            break
    return paid


def make_job(author: dict, kp, scope: str, entries: list[dict]) -> dict:
    """The import job, signed onto the log BEFORE any byte moves — the queue
    the openwiki discipline demands. Progress is derived, never stored."""
    clean = []
    for e in entries:
        if e.get("store") and e.get("key"):    # a governed store's object (sp2)
            clean.append({"store": str(e["store"]), "key": str(e["key"])})
        elif e.get("path"):
            clean.append({"path": str(e["path"]),
                          **({"zip_member": str(e["zip_member"])}
                             if e.get("zip_member") else {})})
    if not clean:
        raise Refusal("request cannot be served under this capability")
    return make_memory(author, kp, scope,
                       {"import_job": {"entries": clean, "count": len(clean)}},
                       kind="episodic", tags=["import-job"])


def run_job(node, author: dict, kp, *, root, store_root, entries: list[dict],
            job_ref: str, max_bytes: int | None = None,
            limit: int | None = None, already: set[str] | None = None) -> dict:
    """The resumable run: each entry attempted once per pass, `limit` at a
    time (storms are a disease — a beat imports a few and yields). `already`
    is the resume law's memory — the hashes the log already points at; the
    sim derives it from the node, the wire lane injects its own (the worker's
    node shim is write-only by design). A failure is an ANSWER (recorded,
    never retried forever)."""
    if already is None:
        already = held_hashes(node)
    receipts, failed = [], []
    todo = list(entries)[: (limit if limit else len(entries))]
    for e in todo:
        try:
            r = import_entry(node, author, kp, root=root,
                             store_root=store_root, entry=e,
                             max_bytes=max_bytes, already=already)
        except Refusal:
            r = {"status": "refused", "origin": {"path": str(e.get("path"))}}
            failed.append(r)
        except Exception as ex:
            r = {"status": "failed", "origin": {"path": str(e.get("path"))},
                 "why": str(ex)[:120]}
            failed.append(r)
        receipts.append({**r, "entry": e})
    return {"receipts": receipts, "failed": failed,
            "attempted": len(todo), "of": len(entries)}


def finish_job(node, author: dict, kp, scope: str, *, job_ref: str,
               imported: int, skipped: int, failed: list) -> str:
    """The completion record — honest about interruption: a job whose
    entries could not all land says so, never pretends completeness."""
    rec = make_memory(author, kp, scope,
                      {"import_done": {"job": job_ref, "imported": imported,
                                       "skipped": skipped,
                                       "failed": len(failed),
                                       "interrupted": bool(failed),
                                       "flaws": [f.get("origin", {}).get("path", "?")
                                                 for f in failed][:20]}},
                      kind="episodic", tags=["import-done"])
    rec["derived_from"] = [job_ref]
    return node.write(rec)
