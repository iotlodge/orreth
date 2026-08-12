# PROVENANCE: Fable 5 (claude-fable-5) — 0054 sp2, the desk's data hands · 2026-08-12
"""tradingdata — market data for the desk, the reference's INTENT ported.

The reference (CortexObserver tradingdata.py) taught five hard-won laws,
kept here without its code: (1) ONE SNAPSHOT — OHLCV is fetched once per
ticker per half-hour and everything slices from it, because parallel
yfinance history() calls silently return empty frames; (2) a retry ladder
with backoff and a Ticker.history fallback; (3) honest data quality —
a failed fetch is a named error the caller carries, never an exception
that kills the run and never an empty frame reasoned over; (4) indicators
computed from the one snapshot (pandas only — SMA, Wilder RSI, MACD,
Bollinger middle, Wilder ATR); (5) chart series capped at the last 35
sessions, the shape the report bundle carries.

Pure machinery: no wire, no signing — the worker's farm stall wraps it.
Requires yfinance + pandas at the call site (the worker runs under uv).
"""
from __future__ import annotations

import time

_CACHE: dict[str, tuple[float, object]] = {}     # ticker -> (fetched_at, DataFrame)
_TTL = 1800.0
_LOOKBACK_DAYS = 460                              # room for the 200-SMA plus a year
_BACKOFF = (0.0, 0.8, 2.0, 4.0)
INDICATORS = ["close_50_sma", "close_200_sma", "rsi", "macd", "boll", "atr"]


def _fetch_ohlcv(ticker: str):
    """The one snapshot. Serial, retried, cached; None means honestly dark."""
    hit = _CACHE.get(ticker)
    if hit and time.time() - hit[0] < _TTL:
        return hit[1]
    import yfinance as yf
    df = None
    for pause in _BACKOFF:
        if pause:
            time.sleep(pause)
        try:
            df = yf.download(ticker, period=f"{_LOOKBACK_DAYS}d", interval="1d",
                             progress=False, auto_adjust=True)
            if df is None or df.empty:
                df = yf.Ticker(ticker).history(period=f"{_LOOKBACK_DAYS}d",
                                               auto_adjust=True)
            if df is not None and not df.empty:
                break
        except Exception:
            df = None
    if df is None or df.empty:
        return None
    if hasattr(df.columns, "get_level_values") and df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
    _CACHE[ticker] = (time.time(), df)
    return df


def _indicator_frame(df):
    import pandas as pd  # noqa: F401 — the frame math below rides pandas
    out = {}
    close, high, low = df["close"], df["high"], df["low"]
    out["close_50_sma"] = close.rolling(50).mean()
    out["close_200_sma"] = close.rolling(200).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    out["rsi"] = 100 - 100 / (1 + rs)
    out["macd"] = (close.ewm(span=12, adjust=False).mean()
                   - close.ewm(span=26, adjust=False).mean())
    out["boll"] = close.rolling(20).mean()
    prev_close = close.shift(1)
    tr = (high - low).combine((high - prev_close).abs(), max).combine(
        (low - prev_close).abs(), max)
    out["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    return out


def get_stock_data(ticker: str, days: int = 30) -> dict:
    """Last `days` sessions as rows — the market analyst's tape."""
    df = _fetch_ohlcv(ticker)
    if df is None:
        return {"error": f"no OHLCV for {ticker} — the tape is dark"}
    tail = df.tail(days)
    rows = [{"date": str(ix)[:10], "open": round(float(r["open"]), 2),
             "high": round(float(r["high"]), 2), "low": round(float(r["low"]), 2),
             "close": round(float(r["close"]), 2), "volume": float(r["volume"])}
            for ix, r in tail.iterrows()]
    return {"ticker": ticker, "days": len(rows), "rows": rows}


def get_indicators(ticker: str, look_back: int = 30) -> dict:
    """All six indicators over the window, latest value first — one call,
    one snapshot (the reference made six; the intent said one)."""
    df = _fetch_ohlcv(ticker)
    if df is None:
        return {"error": f"no OHLCV for {ticker} — indicators dark"}
    frames = _indicator_frame(df)
    out = {}
    for name in INDICATORS:
        s = frames[name].tail(look_back).dropna()
        out[name] = {"latest": round(float(s.iloc[-1]), 2) if len(s) else None,
                     "series": [{"date": str(ix)[:10], "value": round(float(v), 2)}
                                for ix, v in s.items()]}
    return {"ticker": ticker, "indicators": out}


def get_fundamentals(ticker: str) -> dict:
    """The books, from the one Ticker read — the fields the report speaks."""
    import yfinance as yf
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception as e:
        return {"error": f"fundamentals dark for {ticker}: {e}"}
    keys = ["marketCap", "trailingPE", "forwardPE", "trailingPegRatio",
            "priceToBook", "grossMargins", "operatingMargins", "profitMargins",
            "totalRevenue", "revenueGrowth", "trailingEps", "forwardEps",
            "totalCash", "totalDebt", "currentRatio", "freeCashflow",
            "returnOnEquity", "sharesOutstanding", "dividendYield", "beta",
            "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "shortName", "sector",
            "industry", "longBusinessSummary"]
    got = {k: info.get(k) for k in keys if info.get(k) is not None}
    if not got:
        return {"error": f"fundamentals dark for {ticker} — empty info"}
    if isinstance(got.get("longBusinessSummary"), str):
        got["longBusinessSummary"] = got["longBusinessSummary"][:600]
    return {"ticker": ticker, "fundamentals": got}


def _statement(ticker: str, which: str) -> dict:
    import yfinance as yf
    try:
        t = yf.Ticker(ticker)
        df = {"balance_sheet": t.balance_sheet, "cashflow": t.cashflow,
              "income": t.income_stmt}[which]
        if df is None or df.empty:
            return {"error": f"{which} dark for {ticker}"}
        col = df.columns[0]
        rows = {str(k): float(v) for k, v in df[col].items()
                if v == v and abs(float(v)) > 0}          # NaN-safe, zeros dropped
        return {"ticker": ticker, "statement": which, "period": str(col)[:10],
                "rows": dict(list(rows.items())[:40])}
    except Exception as e:
        return {"error": f"{which} dark for {ticker}: {e}"}


def get_balance_sheet(ticker: str) -> dict:
    return _statement(ticker, "balance_sheet")


def get_cashflow(ticker: str) -> dict:
    return _statement(ticker, "cashflow")


def get_income_statement(ticker: str) -> dict:
    return _statement(ticker, "income")


def get_insider_transactions(ticker: str) -> dict:
    import yfinance as yf
    try:
        df = yf.Ticker(ticker).insider_transactions
        if df is None or df.empty:
            return {"ticker": ticker, "insider": [],
                    "note": "no insider rows in the window"}
        rows = df.head(12).to_dict("records")
        return {"ticker": ticker,
                "insider": [{str(k): (str(v)[:60]) for k, v in r.items()}
                            for r in rows]}
    except Exception as e:
        return {"error": f"insider dark for {ticker}: {e}"}


def get_chart_series(ticker: str) -> dict:
    """The bundle's charts: price last 35 sessions + the six indicator
    series over the same window — the exact shape the sample carries."""
    df = _fetch_ohlcv(ticker)
    if df is None:
        return {"error": f"no OHLCV for {ticker} — charts dark"}
    tail = df.tail(35)
    price = [{"date": str(ix)[:10], "open": float(r["open"]), "high": float(r["high"]),
              "low": float(r["low"]), "close": float(r["close"]),
              "volume": float(r["volume"])} for ix, r in tail.iterrows()]
    frames = _indicator_frame(df)
    ind = {}
    for name in INDICATORS:
        s = frames[name].tail(35)
        ind[name] = [{"date": str(ix)[:10],
                      "value": (round(float(v), 4) if v == v else None)}
                     for ix, v in s.items()]
    return {"price_series": price, "indicator_series": ind}


TOOLS = {
    "get_stock_data": get_stock_data,
    "get_indicators": get_indicators,
    "get_fundamentals": get_fundamentals,
    "get_balance_sheet": get_balance_sheet,
    "get_cashflow": get_cashflow,
    "get_income_statement": get_income_statement,
    "get_insider_transactions": get_insider_transactions,
    "get_chart_series": get_chart_series,
}
