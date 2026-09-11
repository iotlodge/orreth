# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp3, the extraction line · 2026-09-10
"""The extraction line's laws (0069 §3.3): the deterministic formats yield,
the eyes-needed refuse honestly by name, a failed parse is named never
silent, every extraction is derived, the ingest rails run BEFORE knowledge
is minted — and the parked list is finally the retry list."""
import io
import json
import zipfile

import pytest

from orreth_sim import basket, crypto, extract, guardrails
from orreth_sim.librarian import parked_intents
from orreth_sim.world import build

GENESIS = guardrails.compose(guardrails.GENESIS_UNIVERSAL)


def _docx(text_lines):
    buf = io.BytesIO()
    body = "".join(f"<w:p><w:r><w:t>{l}</w:t></w:r></w:p>" for l in text_lines)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml",
                   f'<w:document xmlns:w="x"><w:body>{body}</w:body></w:document>')
    return buf.getvalue()


def _xlsx(shared, cells):
    buf = io.BytesIO()
    ss = "".join(f"<si><t>{s}</t></si>" for s in shared)
    cs = "".join(f'<c r="A{i}" t="{t}"><v>{v}</v></c>'
                 for i, (t, v) in enumerate(cells, 1))
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/sharedStrings.xml", f"<sst>{ss}</sst>")
        z.writestr("xl/worksheets/sheet1.xml",
                   f"<worksheet><sheetData><row>{cs}</row></sheetData></worksheet>")
    return buf.getvalue()


def _pptx(slides):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for i, words in enumerate(slides, 1):
            body = "".join(f"<a:t>{w}</a:t>" for w in words)
            z.writestr(f"ppt/slides/slide{i}.xml", f"<p:sld>{body}</p:sld>")
    return buf.getvalue()


def _pdf(text):
    """A minimal one-page PDF with a real text object — pypdf reads it."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objs = [
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n",
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n",
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
        b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n",
        b"4 0 obj<</Length " + str(len(stream)).encode() + b">>stream\n"
        + stream + b"\nendstream endobj\n",
        b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for o in objs:
        offsets.append(len(out))
        out += o
    xref_at = len(out)
    out += b"xref\n0 6\n0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (b"trailer<</Size 6/Root 1 0 R>>\nstartxref\n"
            + str(xref_at).encode() + b"\n%%EOF")
    return out


def test_every_deterministic_format_yields():
    assert "walls breathe" in extract.extract(
        "a.docx", _docx(["rammed earth", "walls breathe"]))["text"]
    x = extract.extract("b.xlsx", _xlsx(["hempcrete"], [("s", "0"), ("n", "42")]))
    assert "hempcrete" in x["text"] and "42" in x["text"]
    assert "straw bale" in extract.extract(
        "c.pptx", _pptx([["straw bale", "R-30"]]))["text"]
    h = extract.extract("d.html",
                        b"<html><style>x{}</style><body><h1>Site plan</h1>"
                        b"<script>evil()</script><p>south glazing</p></body>")
    assert "Site plan" in h["text"] and "south glazing" in h["text"]
    assert "evil" not in h["text"]
    p = extract.extract("e.pdf", _pdf("thermal mass wins winters"))
    assert "thermal mass wins winters" in p["text"]
    assert p["extractor"] == "pdf-" + extract.VERSION
    assert p["meta"]["pages"] == 1


def test_eyes_needed_refuse_honestly_by_name():
    assert extract.extract("scan.png", b"\x89PNG") is None
    assert "vision mind" in extract.eye_needed("scan.png")
    assert "speech-to-text" in extract.eye_needed("call.mp3")


def test_a_failed_parse_is_named_never_silent():
    with pytest.raises(extract.ExtractionFailed) as e:
        extract.extract("broken.docx", b"not a zip at all")
    assert "office" in str(e.value)
    with pytest.raises(extract.ExtractionFailed):
        extract.extract("fake.pdf", b"%PDF-1.4 no real objects here")


@pytest.fixture()
def ground(tmp_path):
    w = build()
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    return {"node": w.universe, "author": ident, "kp": kp,
            "store": tmp_path / "objects"}


def _body(node, ref):
    return json.loads(crypto._b64d(node.records[ref]["body"]).decode())


def test_an_import_now_extracts_office_with_lineage_and_version(ground):
    g = ground
    r = basket.import_bytes(g["node"], g["author"], g["kp"],
                            data=_docx(["the site faces south"]),
                            name="site.docx", origin={"path": "/x/site.docx"},
                            store_root=g["store"], rails=GENESIS)
    assert r["status"] == "extracted"
    b = _body(g["node"], r["extraction"])
    assert "faces south" in b["knowledge"]
    assert b["extraction"]["extractor"] == "docx-" + extract.VERSION
    assert g["node"].records[r["extraction"]]["derived_from"] == [r["pointer"]]


def test_the_ingest_rail_refuses_and_no_knowledge_is_minted(ground):
    g = ground
    card = _docx(["charge the client card 4111 1111 1111 1111 monthly"])
    r = basket.import_bytes(g["node"], g["author"], g["kp"], data=card,
                            name="billing.docx", origin={"path": "/x/b.docx"},
                            store_root=g["store"], rails=GENESIS)
    assert r["status"] == "refused-at-ingest"
    assert "extraction" not in r                   # no knowledge minted
    assert any(e["category"] == "pci" for e in r["redaction"])
    flaw = _body(g["node"], r["refusal"])["redaction_refusal"]
    assert "4111" not in json.dumps(flaw["events"])  # the record never leaks
    assert g["node"].records[r["refusal"]]["derived_from"] == [r["pointer"]]


def test_the_ingest_rail_masks_when_the_human_widened_the_rule(ground):
    g = ground
    both = guardrails.compose({"rules": [
        {"match": {"category": "pii", "direction": "both"}, "action": "mask",
         "reason": "identifiers masked at the door too"}]})
    r = basket.import_bytes(g["node"], g["author"], g["kp"],
                            data=_docx(["contact 078-05-1120 for access"]),
                            name="contacts.docx", origin={"path": "/x/c.docx"},
                            store_root=g["store"], rails=both)
    assert r["status"] == "extracted"
    k = _body(g["node"], r["extraction"])["knowledge"]
    assert "078-05-1120" not in k and "[masked: pii]" in k


def test_a_failed_parse_parks_with_its_flaw_named(ground):
    g = ground
    r = basket.import_bytes(g["node"], g["author"], g["kp"],
                            data=b"not a zip", name="broken.docx",
                            origin={"path": "/x/broken.docx"},
                            store_root=g["store"], rails=GENESIS)
    assert r["status"] == "dark"
    park = _body(g["node"], r["parked"])
    assert "office" in park["missing"]


def test_the_parked_list_is_finally_the_retry_list(ground):
    """A PDF parked DARK before the line existed gets PAID: the sweep
    extracts it, the knowledge cites artifact AND park, and the librarian's
    own lot forgets it."""
    from orreth_sim import artifacts
    g = ground
    pdf = _pdf("the parked page finally read")
    rec = artifacts.admit_upload(g["node"], g["author"], g["kp"],
                                 "old-plan.pdf", "application/pdf", pdf)
    # simulate the pre-sp3 world: the park exists (admit now extracts pdf,
    # so build the park by hand exactly as 0029 used to)
    if rec["status"] == "extracted":
        from orreth_sim.node import make_memory
        parked = make_memory(g["author"], g["kp"], "u:demo",
                             {"parked_intent": "extract the artifact old-plan.pdf",
                              "missing": "a vision mind on the Stable (0019)",
                              "handoff": "knowledge-acquisition",
                              "artifact": rec["artifact"]},
                             kind="semantic", tags=["parked", "knowledge-intent"])
        parked["derived_from"] = [rec["artifact"]]
        g["node"].write(parked)
    lot_before = len(parked_intents(g["node"]))
    assert lot_before >= 1
    import base64
    paid = basket.pay_parked(
        g["node"], g["author"], g["kp"],
        read_bytes=lambda aid: base64.b64decode(
            _body(g["node"], aid)["artifact"]["bytes_b64"]),
        rails=GENESIS)
    assert len(paid) == 1
    assert "finally read" in _body(g["node"], paid[0]["knowledge"])["knowledge"]
    df = g["node"].records[paid[0]["knowledge"]]["derived_from"]
    assert paid[0]["artifact"] in df and paid[0]["park"] in df
    assert len(parked_intents(g["node"])) == lot_before - 1   # the lot forgets
