# PROVENANCE: Fable 5 (claude-fable-5) — 0050 sp3, the first UAT persona · 2026-08-11
"""Flavor 4 — quinn, the newcomer (0050 sp3 · 0049 §3, JB's charter).

A human-skilled walker: quinn joins through becky's gate as a persistent
citizen (rule 1), acquires her PERSONA from the shelf by reference (the
tester is craft too — tuning her rides the same gates as tuning the
tested), and walks a REAL objective through the same doors the glass uses:
compose → read the approval card as a stranger → approve → read the
close-out as a stranger. Every friction she meets is filed through the
THUMB with her words (0048's loop is her reporting channel); a walk with no
frictions files the quiet 👍. Her judgments are governed thoughts — metered
under her own DID, scribed, typed; a screen she cannot judge is SKIPPED
honestly, never guessed at.

    uv run agents/flavors/04-uat/run.py [--once]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

from orreth_agent.chassis import GovernedThink          # noqa: E402
from orreth_agent.client import FieldClient             # noqa: E402
from orreth_agent.mind import MindParked, OrrethMind, generation  # noqa: E402

UNIVERSE = "http://localhost:4500"     # where the human's doors are
FIELD = "http://localhost:4502"        # the bench: where a medium mind serves
WALK_EVERY = 86400                     # one real walk a day (JB's cadence)

# real-world asks (0049 §1) — rotated; each exercises read → plan → gate →
# fan → assemble, the whole journey a human would take
WALKS = [
    "Report this week's activity across the retail floors: what ran, what "
    "it cost, and anything that needs a decision",
    "Take stock of the knowledge library: what subjects are covered, what "
    "looks stale, and what a new team would want added",
    "Summarize the health of our tools and services: what is serving, what "
    "is quiet, and what spend stands out",
]


def _judge_contract(raw: str) -> dict:
    """quinn's typed word: a judgment or a named error — never a guess."""
    import re as _re
    m = _re.search(r"\{.*\}", raw or "", _re.S)
    if not m:
        raise ValueError("no JSON object found in the reply")
    try:
        got = json.loads(m.group(0))
    except Exception as e:
        raise ValueError(f"the JSON did not parse ({e})") from e
    if not isinstance(got.get("legible"), bool):
        raise ValueError('"legible" must be true or false')
    fr = got.get("frictions")
    if not isinstance(fr, list):
        raise ValueError('"frictions" must be a list')
    return {"legible": got["legible"],
            "frictions": [str(x)[:200] for x in fr][:6],
            "delight": str(got.get("delight") or "")[:160]}


class QuinnMind(OrrethMind):
    """One duty: read a screen as a stranger and say what confused her."""

    @generation(klass="medium", craft="uat-persona-quinn",
                returns=_judge_contract)
    def judge(self, surface, context):
        """The newcomer's read — the persona is the shelf's (law 5)."""
        ...


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=8) as r:
        return json.load(r)


def _post(base: str, path: str, payload: dict) -> dict:
    req = urllib.request.Request(base + path, method="POST",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.load(r)


_SENT: dict = {}


def _sent(name: str, fallback: str, **slots) -> str:
    """quinn's eye reads from the SAME shelf the glass renders from
    (0051 sp4 — the first re-walk graded a synthetic OLD card because her
    surface builders were stale mirrors; the instrument must see what the
    human sees, so the words come from the /sentences door, live)."""
    global _SENT
    if not _SENT:
        try:
            _SENT = _get("http://localhost:4562/sentences").get("sentences", {})
        except Exception:
            _SENT = {}
    t = _SENT.get(name) or fallback
    for k, v in slots.items():
        t = t.replace("⟦" + k + "⟧", str(v))
    return t


def _leaf(s: str) -> str:
    """Floors as the glass names them: leaf · parent, never the raw path."""
    p = str(s or "").split("/")
    leaf = (p[-1] if p else str(s)).split(":")[-1]
    up = p[-2].split(":")[-1] if len(p) > 2 else ""
    return f"{leaf} · {up}" if up else leaf


def _card_surface(r: dict) -> str:
    """The approval card as the GLASS shows it — quinn sees what a human
    sees, nothing more (the naive eye reads renderings, not records)."""
    res = r.get("result") or {}
    plan, u = res.get("plan") or {}, res.get("understanding") or {}
    pb = res.get("planned_by") or {}
    lines = [f"objective · {r.get('text', '')}", f"{r.get('id')} · staged",
             "journey: asked → "
             + ("read and understood" if u.get("state") == "read"
                else "being read") + " → planned → ["
             + _sent("journey-word", "waiting on you — approve sends the "
                     "work to the floors; decline stops it here and keeps "
                     "the record") + "]"]
    if u.get("reading"):
        lines.append(f"🧠 the universe understood: {u['reading']}"
                     + (f" · gaps: {'; '.join(u.get('gaps') or [])}"
                        if u.get("gaps") else "")
                     + (f" · confidence {u.get('confidence')}"
                        if "confidence" in u else ""))
    if pb.get("label"):
        lines.append(f"🗺 {pb['label']}")
    for i in (plan.get("intentions") or [])[:6]:
        lines.append(f"→ {_leaf(i.get('seat'))} — {i.get('intent', '')[:90]}")
    if plan.get("question"):
        lines.append(f"…and it will ask you: {plan['question'][:110]}")
    off = res.get("keep_fresh_offer")
    if off:
        lines.append(f"…and keep “{off.get('topic')}” fresh — "
                     f"{off.get('terms')} · a standing spend (0032)")
    lines.append("[input: " + _sent("gate-word-placeholder",
                                    "add words to your decision (optional)")
                 + "]")
    lines.append("[buttons: fan the plan · decline]")
    return "\n".join(lines)


def _closeout_surface(r: dict) -> str:
    """The close-out card as the glass shows it."""
    res = r.get("result") or {}
    a = res.get("assembly") or {}
    lines = [f"objective · {r.get('text', '')}", f"{r.get('id')} · done",
             "journey: asked → read → planned → ["
             + _sent("journey-resolved", "done — the report below is yours")
             + "] → " + _sent("journey-assayed-later",
                              "the observatory will grade this work in time"),
             f"verification · {a.get('verification', '?')}"]
    for b in (a.get("branches") or [])[:6]:
        lines.append(f"→ {_leaf(b.get('seat'))} {b.get('status')} — "
                     f"{str(b.get('answer', ''))[:80]}")
    if a.get("waiting"):
        lines.append("waiting: " + "; ".join(a["waiting"]))
    lines.append(_sent("journey-report-line",
                       "the full report is saved on the record (⟦short⟧…)",
                       short=str(res.get("record", ""))[:18]))
    if a.get("coordinate_citations"):
        lines.append(f"the coordinate · {a['coordinate_citations']} "
                     "record(s) across the floors cite this objective (0033)")
    lines.append("[chips: 👍 👎 · ⤳ walk the work — how each seat thought]")
    return "\n".join(lines)


def _find(reqs: list, rid: str) -> dict | None:
    return next((x for x in reqs if x.get("id") == rid), None)


def walk_once(mind: QuinnMind, client: FieldClient, ask: str) -> None:
    print(f"· quinn asks: “{ask[:70]}”")
    rid = _post(UNIVERSE, "/requests", {"kind": "objective", "text": ask})["id"]
    frictions: list[str] = []

    def look(surface: str, context: str) -> None:
        try:
            j = mind.judge(surface, context)
        except MindParked as e:
            print(f"· quinn could not judge ({context}): {e} — skipped honestly")
            return
        for f in j["frictions"]:
            frictions.append(f"[{context}] {f}")
        print(f"· quinn read {context}: "
              + ("clear" if j["legible"] else "CONFUSING")
              + f" · {len(j['frictions'])} friction(s)"
              + (f" · liked: {j['delight'][:48]}" if j["delight"] else ""))

    # 1 — the approval card (wait for the plan, read it, then approve)
    for _ in range(60):
        time.sleep(4)
        r = _find(_get(UNIVERSE + "/requests").get("requests", []), rid)
        if r and r.get("status") == "staged" and (r.get("result") or {}).get("plan"):
            look(_card_surface(r), "the approval card for your own request")
            _post(UNIVERSE, "/requests/resolve",
                  {"id": rid, "status": "approved",
                   "result": r.get("result") or {}})
            print("· quinn approves — her own gate, her own word")
            break
    else:
        print("· the plan never staged — quinn walks away (a finding in itself)")
        return
    # 2 — the close-out (wait for the assembly, read it, then thumb)
    for _ in range(90):
        time.sleep(4)
        r = _find(_get(UNIVERSE + "/requests").get("requests", []), rid)
        if r and r.get("status") == "done" and (r.get("result") or {}).get("assembly"):
            look(_closeout_surface(r), "the finished report of your request")
            record = (r.get("result") or {}).get("record") or ""
            if not record:
                print("· no report record to thumb — a finding in itself")
                return
            if frictions:
                # J3's first triage found the first defect HERE: a 480-char
                # cap swallowed nine of quinn's twelve frictions — the
                # reporter must never truncate the report (2026-08-11)
                words = " · ".join(frictions)[:2000]
                out = _post(UNIVERSE, "/requests",
                            {"kind": "thumb", "of": record, "up": False,
                             "text": words,
                             "text_summary": "👎 quinn, the newcomer"})
                print(f"· quinn files 👎 ({len(frictions)} frictions) — {out['id']}")
            else:
                out = _post(UNIVERSE, "/requests",
                            {"kind": "thumb", "of": record, "up": True,
                             "text": "", "text_summary": "👍 quinn, the newcomer"})
                print(f"· quinn files the quiet 👍 — {out['id']}")
            return
    print("· the work never came home — quinn walks away (a finding in itself)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="one walk, then rest")
    a = ap.parse_args()
    client = FieldClient(FIELD, "quinn", role="workforce")
    print(f"· quinn is {client.did[:28]}… (scribe {client.scribe_did[:24]}…)")
    print("· joining — the gate may wait for a human …")
    client.join()
    print(f"· lease held on {client.scope} — walking as the newcomer")
    mind = QuinnMind(client, GovernedThink(client, max_tokens=700))
    n = 0
    while True:
        walk_once(mind, client, WALKS[n % len(WALKS)])
        n += 1
        if a.once:
            return 0
        time.sleep(WALK_EVERY)


if __name__ == "__main__":
    sys.exit(main())
