# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0069 sp3, the extraction line · 2026-09-10
"""The extraction line (0069 §3.3) — the parked-intent pattern stops being
an apology and becomes the assembly line.

In plain words: the formats machines read plainly — PDF, Word, Excel,
PowerPoint, HTML — now yield their text DETERMINISTICALLY, worker-side,
firmware-versioned. The formats that need an EYE (scans, images, audio,
video) keep refusing honestly, one face, until the Stable saddles that eye
— the parked list remains the retry list, exactly as 0029 promised.

Every extraction is DERIVED: the knowledge record cites the artifact it was
read from (the lineage chain), wears the extractor's version, and — 0068's
redaction-at-ingest — passes the content rails BEFORE it ever becomes a
knowledge record. The rails' word at the door is final: a refusing rule
means the knowledge is NOT minted (the artifact pointer stands; the refusal
is named), and a masking rule means the mind never holds the raw span.

The Office formats are read with the standard library alone (they are zips
of XML — the text is in the XML); PDF rides pypdf. No format ever
pretends: a parse that fails raises, and the caller keeps the park with
the failure named.
"""
from __future__ import annotations

import io
import re
import zipfile
from html.parser import HTMLParser

VERSION = "extract-v1"

# what this line reads deterministically — the eyes-needed formats are
# everything else the admission bars allow (png/jpg today; audio/video when
# their bars open)
DETERMINISTIC = {"pdf", "docx", "xlsx", "pptx", "html", "htm"}
EYES_NEEDED = {"png": "a vision mind on the Stable (0019)",
               "jpg": "a vision mind on the Stable (0019)",
               "jpeg": "a vision mind on the Stable (0019)",
               "mp3": "a speech-to-text mind on the Stable (0019)",
               "wav": "a speech-to-text mind on the Stable (0019)",
               "mp4": "a frame-description mind on the Stable (0019)"}


class ExtractionFailed(Exception):
    """The format claimed a shape its bytes do not hold — named, never
    silent; the park stays and says why."""


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def can_extract(name: str) -> bool:
    return _ext(name) in DETERMINISTIC


def eye_needed(name: str) -> str | None:
    return EYES_NEEDED.get(_ext(name))


# ---- the readers, one per format ------------------------------------------------------

def _pdf(data: bytes) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader
        r = PdfReader(io.BytesIO(data))
        pages = [(p.extract_text() or "").strip() for p in r.pages]
    except Exception as e:
        raise ExtractionFailed(f"pdf: {str(e)[:80]}")
    text = "\n\n".join(p for p in pages if p)
    if not text.strip():
        raise ExtractionFailed("pdf: no extractable text layer — this may "
                               "be a scan (an eye's work, not this line's)")
    return text, {"pages": len(pages)}


def _xml_texts(xml: bytes, tag: str) -> list[str]:
    """Every <ns:tag>…</ns:tag> text node, namespace-blind — the Office
    formats keep their words in exactly these."""
    return [m.group(1) for m in
            re.finditer(rf"<(?:\w+:)?{tag}(?:\s[^>]*)?>([^<]*)</(?:\w+:)?{tag}>",
                        xml.decode("utf-8", errors="replace"))]


def _zipread(data: bytes, member_pat: str) -> list[tuple[str, bytes]]:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = sorted(n for n in z.namelist() if re.match(member_pat, n))
            return [(n, z.read(n)) for n in names]
    except (zipfile.BadZipFile, KeyError, OSError) as e:
        raise ExtractionFailed(f"office: {str(e)[:80]}")


def _docx(data: bytes) -> tuple[str, dict]:
    parts = _zipread(data, r"word/document\.xml$")
    if not parts:
        raise ExtractionFailed("docx: no document body")
    xml = parts[0][1]
    # paragraphs become lines; text nodes join within them
    paras = re.split(rb"</(?:\w+:)?p>", xml)
    lines = ["".join(_xml_texts(p, "t")) for p in paras]
    text = "\n".join(l for l in lines if l.strip())
    if not text.strip():
        raise ExtractionFailed("docx: an empty document body")
    return text, {"paragraphs": sum(1 for l in lines if l.strip())}


def _xlsx(data: bytes) -> tuple[str, dict]:
    shared = []
    for _, xml in _zipread(data, r"xl/sharedStrings\.xml$"):
        shared = _xml_texts(xml, "t")
    sheets = _zipread(data, r"xl/worksheets/sheet\d+\.xml$")
    if not sheets and not shared:
        raise ExtractionFailed("xlsx: no worksheets")
    rows_out, cells = [], 0
    for name, xml in sheets:
        vals = []
        for m in re.finditer(
                r'<(?:\w+:)?c\b([^>]*)>\s*'
                r'<(?:\w+:)?v>([^<]*)</(?:\w+:)?v>',
                xml.decode("utf-8", errors="replace")):
            attrs, v = m.group(1), m.group(2)
            tm = re.search(r'\bt="(\w+)"', attrs)
            if tm and tm.group(1) == "s":
                try:
                    v = shared[int(v)]
                except (ValueError, IndexError):
                    pass
            vals.append(v)
            cells += 1
        if vals:
            rows_out.append(" · ".join(vals))
    text = "\n".join(rows_out) if rows_out else "\n".join(shared)
    if not text.strip():
        raise ExtractionFailed("xlsx: no cell values")
    return text, {"sheets": len(sheets), "cells": cells}


def _pptx(data: bytes) -> tuple[str, dict]:
    slides = _zipread(data, r"ppt/slides/slide\d+\.xml$")
    if not slides:
        raise ExtractionFailed("pptx: no slides")
    out = []
    for name, xml in slides:
        words = _xml_texts(xml, "t")
        if words:
            out.append(" ".join(w for w in words if w.strip()))
    text = "\n\n".join(out)
    if not text.strip():
        raise ExtractionFailed("pptx: no slide text")
    return text, {"slides": len(slides)}


class _HtmlText(HTMLParser):
    SKIP = {"script", "style"}

    def __init__(self):
        super().__init__()
        self.chunks, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, d):
        if not self._skip and d.strip():
            self.chunks.append(d.strip())


def _html(data: bytes) -> tuple[str, dict]:
    p = _HtmlText()
    try:
        p.feed(data.decode("utf-8", errors="replace"))
    except Exception as e:
        raise ExtractionFailed(f"html: {str(e)[:80]}")
    text = "\n".join(p.chunks)
    if not text.strip():
        raise ExtractionFailed("html: no visible text")
    return text, {"nodes": len(p.chunks)}


_READERS = {"pdf": _pdf, "docx": _docx, "xlsx": _xlsx, "pptx": _pptx,
            "html": _html, "htm": _html}


def extract(name: str, data: bytes) -> dict | None:
    """One artifact's deterministic reading, or None when only an eye could
    read it (the caller parks honestly, naming the missing eye). A failed
    parse raises ExtractionFailed — the park stays and says why."""
    ext = _ext(name)
    reader = _READERS.get(ext)
    if reader is None:
        return None
    text, meta = reader(data)
    return {"text": text, "extractor": f"{ext}-{VERSION}",
            "meta": {**meta, "chars": len(text)}}
