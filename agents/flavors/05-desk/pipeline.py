# PROVENANCE: Fable 5 (claude-fable-5) — 0054 sp3, the desk's walk · 2026-08-12
"""The Trading desk's sixteen stages as a governed walk (0054 sp3).

The reference ran this as a LangGraph; here it is charles's OWN morning
walk: every prompt acquired from the shelf by ref (never a local copy),
every thought authorized and metered under his lease (medium = sonnet,
high = opus — JB's L-D), every tool call through the Farm's invoke door,
every search through the librarian's gather (quarantined at admission,
under the daily ceiling), every stage a signed record on f:charles as it
lands (rule 7 — the glass reads records, there is no partial-persist
blob), and the bundle written in the sample's exact shape. The delta
reads his own prior report from his own recall — run one says so
honestly: the baseline establishes itself.

The desk observes and reports. It never executes a trade.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.request
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOL_DOOR = "http://localhost:4562/tool"
SERVICE = "local.desk/tradingdata"
CRAFT = [  # every word the walk speaks, by shelf name
    "market-analyst", "social-analyst", "news-analyst", "fundamentals-analyst",
    "bull-researcher", "bear-researcher", "research-manager", "trader",
    "aggressive-risk", "conservative-risk", "neutral-risk", "portfolio-manager",
    "compare-to-prior", "format-report", "compliance-disclaimer",
    "hint-research-plan", "hint-trader-proposal", "hint-pm-decision"]


def _tool(name: str, ticker: str, did: str, port: int) -> dict:
    req = urllib.request.Request(TOOL_DOOR, method="POST",
        data=json.dumps({"service": SERVICE, "tool": name, "did": did,
                         "port": port, "args": {"ticker": ticker}}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def _ask(client, text: str, timeout: float = 90.0) -> dict:
    """A gather through the librarian's queue door — findings come back
    typed; the records stay quarantined on the floor either way."""
    _, made = client._call("POST", "/requests", {"kind": "gather", "text": text})
    rid = made.get("id")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for r in client._call("GET", "/requests")[1].get("requests", []):
            if r.get("id") == rid and r.get("status") == "done":
                out = r.get("result")
                return out if isinstance(out, dict) else {"note": str(out), "findings": []}
        time.sleep(2)
    return {"note": "the librarian did not answer in time", "findings": []}


def _findings_text(res: dict) -> str:
    return "\n".join(f"- {f['title']}: {f['content']}" for f in res.get("findings", [])) \
        or "(no findings — the analyst must say the ground is thin, never invent)"


def _parse_json(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw or "", re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {"_raw": (raw or "")[:800]}


def _md(title: str, ticker: str, date: str, body: str) -> str:
    return (f"# {title}\n\n_Ticker: `{ticker}` · Date: {date}_\n\n"
            + (body.strip() if body and body.strip() else "_(not produced)_") + "\n")


def _clip(s: str, n: int) -> str:
    return (s or "")[:n]


def _think(fn, klass: str, prompt: str) -> str:
    """One retry on an empty reply, then an honest placeholder — a silent
    None must never ride into a debate as an empty section."""
    for _ in (1, 2):
        out = fn(klass, prompt)
        if isinstance(out, str) and out.strip():
            return out
    return "(the mind returned nothing for this stage — the ground is thin, said honestly)"


def run(client, think_med, think_high, think_fmt, ticker: str, date: str,
        say=print, refresh: bool = False) -> dict:
    """The whole walk. Returns {bundle, decision, rating, report_ref}."""
    from orreth_agent.craft import acquire

    did, port = client.did, int(client.base.rsplit(":", 1)[1])
    craft = {n: acquire(f"charles-trading-{n}", did=did) for n in CRAFT}
    say(f"· {len(craft)} craft acquired from the shelf, every one by ref")

    def record(stage: str, digest: str, **extra):
        client.remember({"stage": stage, "ticker": ticker, "date": date,
                         "digest": _clip(digest, 400), **extra},
                        kind="episodic", tags=["desk", "stage", stage, ticker])
        say(f"  ✦ {stage} — on the record")

    # ── 1 · retrieve context: his own lived past ──────────────────────
    hits = client.recall(days=365).get("hits", [])
    prior_report, lessons = None, []
    for h in hits:
        body = client.body_of(h["ref"]) or {}
        if body.get("report") and body.get("ticker") == ticker and not prior_report:
            prior_report = body
        if body.get("reflection"):
            lessons.append(str(body["reflection"])[:300])
    past = ("Lessons from prior decisions:\n" + "\n".join(f"- {x}" for x in lessons[:5])
            ) if lessons else "No prior lessons on record yet."
    record("retrieve-context", f"prior report: {'yes' if prior_report else 'none'} · "
                               f"{len(lessons)} lesson(s)")

    # ── 2 · fetch data: the Farm's stall + the librarian's searches ───
    # after a rig restart the stall re-earns serving through probation
    # (~3 beats); a walk that starts inside that window would run dark for
    # nothing — wait for the stall, say so, give up honestly at 75s
    deadline = time.monotonic() + 75
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/farm", timeout=5) as fr:
                states = {x.get("name"): x.get("state")
                          for x in json.load(fr).get("services", [])}
            if states.get(SERVICE) == "serving":
                break
            say(f"  · the stall is {states.get(SERVICE, 'absent')} — waiting for serving")
        except Exception:
            pass
        time.sleep(8)
    data, dark = {}, []
    for t in ["get_stock_data", "get_indicators", "get_fundamentals",
              "get_balance_sheet", "get_cashflow", "get_income_statement",
              "get_insider_transactions", "get_chart_series"]:
        out = _tool(t, ticker, did, port)
        if "error" in out:
            dark.append(f"{t}: {out['error']}")
        data[t] = out
    news = _ask(client, f"{ticker} stock news earnings")
    macro = _ask(client, "macroeconomic indicators federal reserve interest rates inflation")
    social = _ask(client, f"{ticker} reddit twitter stocktwits sentiment investor opinions")
    record("fetch-data", f"{8 - len(dark)}/8 tools · "
           f"{sum(len(x.get('findings', [])) for x in (news, macro, social))} findings",
           data_quality_errors=dark[:9])

    rows = data["get_stock_data"].get("rows", [])
    tape = "\n".join(f"{r['date']} o{r['open']} h{r['high']} l{r['low']} "
                     f"c{r['close']} v{int(r['volume'])}" for r in rows)
    inds = data["get_indicators"].get("indicators", {})
    ind_txt = "\n".join(f"{k}: latest {v.get('latest')} · " +
                        " ".join(f"{p['date'][5:]}={p['value']}" for p in v.get("series", [])[-10:])
                        for k, v in inds.items())
    fund_txt = json.dumps(data["get_fundamentals"].get("fundamentals", {}), indent=0)
    stmts = "\n".join(f"[{w}] " + json.dumps(data[f"get_{w}"].get("rows", {}))[:900]
                      for w in ["balance_sheet", "cashflow", "income_statement"])
    insider = json.dumps(data["get_insider_transactions"].get("insider", []))[:800]

    # ── 3-6 · the four analysts (medium) ──────────────────────────────
    def analyst(name: str, payload: str) -> str:
        out = _think(think_med, "medium", craft[name].text + "\n\n" + payload)
        record(name, out)
        return out

    prior_sections = (prior_report or {}).get("sections") or {}
    if refresh and prior_sections:
        # the cheap path (L-B): market/sentiment/fundamentals REUSE the prior
        # walk's work under an honest banner; news ALWAYS re-runs — staleness
        # in news is a wrong answer, staleness in a balance sheet is a banner
        banner = (f"_(reused from the {prior_report.get('date', '?')} walk — "
                  f"refresh mode; news re-ran fresh)_\n\n")
        reports = {k: banner + str(prior_sections.get(k, ""))
                   for k in ("market", "sentiment", "fundamentals")}
        for k in ("market", "sentiment", "fundamentals"):
            record(f"{k}-analyst" if k != "sentiment" else "social-analyst",
                   f"reused from {prior_report.get('date', '?')} (refresh)")
        reports["news"] = analyst("news-analyst",
                                  f"Ticker: {ticker} · Date: {date}\n\nCOMPANY NEWS:\n"
                                  + _findings_text(news) + "\n\nMACRO NEWS:\n"
                                  + _findings_text(macro))
    else:
        reports = {
            "market": analyst("market-analyst",
                          f"Ticker: {ticker} · Date: {date}\n\nINDICATORS:\n{ind_txt}\n\n"
                          f"LAST {len(rows)} SESSIONS (OHLCV):\n{tape}"),
            "sentiment": analyst("social-analyst",
                                 f"Ticker: {ticker} · Date: {date}\n\nSOCIAL FINDINGS:\n"
                                 + _findings_text(social)),
            "news": analyst("news-analyst",
                            f"Ticker: {ticker} · Date: {date}\n\nCOMPANY NEWS:\n"
                            + _findings_text(news) + "\n\nMACRO NEWS:\n" + _findings_text(macro)),
            "fundamentals": analyst("fundamentals-analyst",
                                    f"Ticker: {ticker} · Date: {date}\n\nFUNDAMENTALS:\n{fund_txt}\n\n"
                                    f"STATEMENTS:\n{stmts}\n\nINSIDER:\n{insider}"),
        }
    block = (f"MARKET:\n{_clip(reports['market'], 2500)}\n\n"
             f"SENTIMENT:\n{_clip(reports['sentiment'], 2000)}\n\n"
             f"NEWS:\n{_clip(reports['news'], 2500)}\n\n"
             f"FUNDAMENTALS:\n{_clip(reports['fundamentals'], 2500)}")

    # ── 7-8 · the research debate (one round, two voices) ─────────────
    bull = "Bull Analyst: " + _think(think_med, "medium", craft["bull-researcher"].text
                                        + f"\n\n{block}\n\nDebate so far: (opening)")
    record("bull-researcher", bull)
    bear = "Bear Analyst: " + _think(think_med, "medium", craft["bear-researcher"].text
                                        + f"\n\n{block}\n\nDebate so far:\n{_clip(bull, 2500)}")
    record("bear-researcher", bear)
    research_debate = bull + "\n\n" + bear

    # ── 9 · the research manager (HIGH — opus) ────────────────────────
    plan = _parse_json(_think(think_high, "high", craft["research-manager"].text
                                  + f"\n\n{block}\n\nDEBATE:\n{_clip(research_debate, 4000)}"
                                  + f"\n\n{past}\n\nReply ONLY with JSON:\n"
                                  + craft["hint-research-plan"].text))
    record("research-manager", json.dumps(plan)[:400])

    # ── 10 · the trader (medium, structured) ──────────────────────────
    proposal = _parse_json(_think(think_med, "medium", craft["trader"].text
                                     + f"\n\nRESEARCH PLAN:\n{json.dumps(plan)}\n\n"
                                     f"MARKET:\n{_clip(reports['market'], 2000)}\n\n"
                                     "Reply ONLY with JSON:\n" + craft["hint-trader-proposal"].text))
    record("trader", json.dumps(proposal)[:400])

    # ── 11-13 · the risk debate (three voices) ────────────────────────
    risk_hist = ""
    for voice in ["aggressive-risk", "conservative-risk", "neutral-risk"]:
        turn = _think(think_med, "medium", craft[voice].text
                         + f"\n\nTRADER PROPOSAL:\n{json.dumps(proposal)}\n\n"
                         f"{_clip(block, 3000)}\n\nDebate so far:\n{_clip(risk_hist, 2500)}")
        label = voice.split("-")[0].capitalize()
        risk_hist += f"{label} Risk Analyst: {turn}\n\n"
        record(voice, turn)

    # ── 14 · the delta vs prior — his own recall is the retrieval ─────
    if prior_report:
        delta = _think(think_med, "medium", craft["compare-to-prior"].text
                          + f"\n\nPRIOR REPORT ({prior_report.get('date', '?')}):\n"
                          + _clip(str(prior_report.get("report", "")), 4000)
                          + f"\n\nTODAY ({date}) — PLAN: {json.dumps(plan)} · "
                          f"PROPOSAL: {json.dumps(proposal)}\n\nINDICATORS:\n{ind_txt}")
    else:
        delta = "This run establishes the baseline."
    record("compare-to-prior", delta)

    # ── 15 · the portfolio manager (HIGH — opus) ──────────────────────
    decision = _parse_json(think_high("high", craft["portfolio-manager"].text
                                      + f"\n\nRESEARCH PLAN:\n{json.dumps(plan)}\n\n"
                                      f"TRADER PROPOSAL:\n{json.dumps(proposal)}\n\n"
                                      f"RISK DEBATE:\n{_clip(risk_hist, 3500)}\n\n"
                                      f"DELTA VS PRIOR:\n{_clip(delta, 1500)}\n\n{past}\n\n"
                                      "Reply ONLY with JSON:\n" + craft["hint-pm-decision"].text))
    record("portfolio-manager", json.dumps(decision)[:400])

    # ── 16 · assemble, polish, bundle, persist ────────────────────────
    disclaimer = craft["compliance-disclaimer"].text
    plan_md = (f"**Recommendation**: {plan.get('rating', '?')}\n\n"
               f"**Rationale**: {plan.get('rationale', plan.get('_raw', ''))}\n\n"
               f"**Strategic Actions**: {plan.get('strategic_actions', '')}")
    prop_md = (f"**Action**: {proposal.get('action', '?')}\n\n"
               f"**Reasoning**: {proposal.get('reasoning', proposal.get('_raw', ''))}\n\n"
               f"**Entry Price**: {proposal.get('entry_price', '?')}\n\n"
               f"**Stop Loss**: {proposal.get('stop_loss', '?')}")
    dec_md = (f"**Rating**: {decision.get('rating', '?')}\n\n"
              f"**Executive Summary**: {decision.get('executive_summary', '')}\n\n"
              f"**Investment Thesis**: {decision.get('investment_thesis', decision.get('_raw', ''))}\n\n"
              f"**Price Target**: {decision.get('price_target', '?')}")
    raw = "\n\n".join([
        f"# Trading Research Report — {ticker} ({date})",
        "## Final Decision\n\n" + dec_md,
        "## Delta vs Prior Report\n\n" + delta,
        "## Trader Proposal\n\n" + prop_md,
        "## Research Manager Plan\n\n" + plan_md,
        "## Bull / Bear Researcher Debate\n\n" + research_debate,
        "## Risk Debate\n\n" + risk_hist.strip(),
        "## Market Analyst\n\n" + reports["market"],
        "## Sentiment Analyst\n\n" + reports["sentiment"],
        "## News Analyst\n\n" + reports["news"],
        "## Fundamentals Analyst\n\n" + reports["fundamentals"],
        "---\n\n" + disclaimer])
    polished = _think(think_fmt, "medium", craft["format-report"].text + "\n\n" + raw)
    if not polished or len(polished) < 400:
        polished = raw                       # honest fallback, never a blank page
    if "Disclaimer" not in polished and "disclaimer" not in polished:
        polished += "\n\n---\n\n" + disclaimer
    record("format-report", polished)

    charts = {"price_series": data["get_chart_series"].get("price_series", []),
              "indicator_series": data["get_chart_series"].get("indicator_series", {})}
    bundle = REPO / "tmp" / f"charles-{ticker}-{date}"
    (bundle / "charts").mkdir(parents=True, exist_ok=True)
    files = {
        "00_full_report.md": polished,
        "00_full_report_raw.md": raw,
        "01_market.md": _md("Market Analyst", ticker, date, reports["market"]),
        "02_sentiment.md": _md("Sentiment Analyst", ticker, date, reports["sentiment"]),
        "03_news.md": _md("News Analyst", ticker, date, reports["news"]),
        "04_fundamentals.md": _md("Fundamentals Analyst", ticker, date, reports["fundamentals"]),
        "10_research_debate.md": _md("Bull / Bear Researcher Debate", ticker, date, research_debate),
        "11_risk_debate.md": _md("Risk Debate", ticker, date, risk_hist),
        "20_investment_plan.md": _md("Investment Plan", ticker, date, plan_md),
        "21_trader_proposal.md": _md("Trader Proposal", ticker, date, prop_md),
        "22_final_decision.md": _md("Final Decision", ticker, date, dec_md),
        "23_delta_vs_prior.md": _md("Delta vs Prior Report", ticker, date, delta),
        "decision.json": json.dumps(
            {"rating": decision.get("rating"), "executive_summary": decision.get("executive_summary"),
             "investment_thesis": decision.get("investment_thesis"),
             "price_target": decision.get("price_target"),
             "time_horizon": decision.get("time_horizon")}, indent=2),
        "charts/price_series.json": json.dumps(charts["price_series"], indent=1),
        "charts/indicator_series.json": json.dumps(charts["indicator_series"], indent=1),
    }
    for name, body in files.items():
        (bundle / name).write_text(body)
    zpath = bundle.with_suffix(".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in files:
            z.write(bundle / name, name)

    charts_bytes = json.dumps(charts, sort_keys=True).encode()
    client.remember({"artifact_pointer": {"kind": "desk-charts",
                                          "sha256": hashlib.sha256(charts_bytes).hexdigest(),
                                          "path": str(bundle / "charts")},
                     "ticker": ticker, "date": date},
                    kind="episodic", tags=["desk", "charts", ticker])
    client.remember({"report": polished, "decision": decision, "ticker": ticker,
                     "date": date, "rating": decision.get("rating"),
                     "outcome_pending": True, "refresh": refresh,
                     "sections": {k: _clip(v, 8000) for k, v in reports.items()},
                     "debates": {"research": _clip(research_debate, 12000),
                                 "risk": _clip(risk_hist, 12000)},
                     "delta": _clip(delta, 8000),
                     "data_quality_errors": dark[:9]},
                    kind="episodic", tags=["desk", "report", ticker, date])
    say(f"· the report is on the record; the bundle stands at {bundle}")
    return {"bundle": str(bundle), "zip": str(zpath),
            "rating": decision.get("rating"), "decision": decision}


def grade_pending(client, think_med, say=print) -> int:
    """The reflection beat (0054 sp5): every report still wearing
    outcome_pending past the holding window gets graded against what the
    market ACTUALLY did — realized return vs SPY over the same window, one
    governed thought, one lesson on the record. The next walk's
    retrieve-context recalls it. A grade before the full window says so
    (graded_early) and keeps its lesson provisional. Returns lessons written."""
    import os
    from datetime import date as _date
    from orreth_agent.craft import acquire

    holding = int(os.environ.get("ORRETH_DESK_HOLDING_DAYS", "7"))
    did, port = client.did, int(client.base.rsplit(":", 1)[1])
    hits = client.recall(days=365).get("hits", [])
    reports, reflected = [], set()
    for h in hits:
        body = client.body_of(h["ref"]) or {}
        if body.get("report") and body.get("outcome_pending"):
            reports.append((h["ref"], body))
        if body.get("reflection") and body.get("report_ref"):
            reflected.add(body["report_ref"])
    wrote = 0
    for ref, rep in reports:
        if ref in reflected:
            continue
        ticker, rdate = rep.get("ticker"), rep.get("date")
        try:
            elapsed = (_date.today() - _date.fromisoformat(rdate)).days
        except Exception:
            continue
        if elapsed < holding and not os.environ.get("ORRETH_DESK_GRADE_NOW"):
            continue
        rows = _tool("get_stock_data", ticker, did, port).get("rows", [])
        spy = _tool("get_stock_data", "SPY", did, port).get("rows", [])
        def _entry_latest(rr):
            ent = next((x["close"] for x in rr if x["date"] >= rdate), None)
            return ent, (rr[-1]["close"] if rr else None)
        e1, l1 = _entry_latest(rows)
        e2, l2 = _entry_latest(spy)
        if not all((e1, l1, e2, l2)):
            say(f"  · {ticker} {rdate}: the tape would not answer — grading waits")
            continue
        ret = 100 * (l1 - e1) / e1
        spy_ret = 100 * (l2 - e2) / e2
        alpha = ret - spy_ret
        early = elapsed < holding
        craft = acquire("charles-trading-reflection", did=did)
        thesis = str((rep.get("decision") or {}).get("investment_thesis", ""))[:500]
        word = _think(think_med, "medium",
                      craft.text + f"\n\nDECISION ({rdate}): {rep.get('rating')} on "
                      f"{ticker} · entry close {e1}\nTHESIS DIGEST: {thesis}\n\n"
                      f"WHAT HAPPENED ({elapsed} day(s) elapsed"
                      f"{' — GRADED EARLY, before the full window' if early else ''}):\n"
                      f"{ticker} return {ret:+.2f}% · SPY {spy_ret:+.2f}% · "
                      f"alpha {alpha:+.2f}%")
        client.remember({"reflection": word, "ticker": ticker, "date": rdate,
                         "report_ref": ref, "return_pct": round(ret, 2),
                         "spy_return_pct": round(spy_ret, 2),
                         "alpha_pct": round(alpha, 2), "graded_early": early,
                         "elapsed_days": elapsed},
                        kind="episodic", tags=["desk", "reflection", ticker])
        say(f"  ✦ reflection on {ticker} {rdate}: {ret:+.2f}% vs SPY "
            f"{spy_ret:+.2f}% (α {alpha:+.2f}%){' · graded early' if early else ''} "
            "— the lesson is on the record")
        wrote += 1
    return wrote
