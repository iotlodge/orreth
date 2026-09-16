# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P0 sp2, the old world measured (M0) · 2026-09-16
"""M0 — baseline the old world without changing it (canon 0005 sp2).

Measures the polling rig exactly as it runs: per-floor door costs (the
unit the worker pays every 2 seconds per floor, and the unit the glass
and SDK pay while waiting), the true ask path the glass walks (POST
/requests, then poll the WHOLE queue until done), and the arithmetic
idle-load ladder those unit costs imply at production floor counts.

Stdlib only. Run with the old rig + worker up:

    python3 spine/baseline/measure_m0.py

Prints a plain-words report and writes m0-results.json beside itself.
"""
from __future__ import annotations

import json
import statistics
import time
import urllib.request
from pathlib import Path

HOST = "127.0.0.1"
PORT_SCAN = range(4500, 4521)
ASK_PORT_PREFERENCE = (4502, 4500)
ASKS = 6
ASK_TIMEOUT_S = 300.0
ASK_POLL_S = 1.0
QUESTIONS = [
    "What is Orreth in one sentence?",
    "Which residents live on this floor?",
    "What does the librarian keep?",
    "Name one governed dial and what it does.",
    "What happened most recently in this world?",
    "What is a capability in this universe?",
]


def _get(url: str, timeout: float = 15.0) -> tuple[float, bytes]:
    t0 = time.perf_counter()
    with urllib.request.urlopen(url, timeout=timeout) as r:
        body = r.read()
    return (time.perf_counter() - t0) * 1000.0, body


def _post(url: str, obj: dict, timeout: float = 15.0) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(obj).encode(),
        headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def discover_floors() -> list[dict]:
    floors = []
    for port in PORT_SCAN:
        try:
            ms, body = _get(f"http://{HOST}:{port}/health", timeout=2.0)
            h = json.loads(body)
            floors.append({"port": port, "scope": h.get("scope", "?"),
                           "records": h.get("records", 0),
                           "health_ms": round(ms, 1)})
        except Exception:
            continue
    return floors


def poll_cost(floors: list[dict], samples: int = 3) -> list[dict]:
    """GET /requests per floor — the poll the worker pays per floor every
    2 s, and the poll the glass/SDK pay every second while waiting."""
    out = []
    for f in floors:
        lats, sizes = [], []
        for _ in range(samples):
            try:
                ms, body = _get(f"http://{HOST}:{f['port']}/requests")
                lats.append(ms)
                sizes.append(len(body))
            except Exception as e:
                out.append({**f, "error": f"{type(e).__name__}: {e}"[:100]})
                break
        else:
            out.append({**f, "poll_ms": round(statistics.median(lats), 1),
                        "poll_bytes": max(sizes),
                        "queue_rows": _queue_rows(f["port"])})
    return out


def _queue_rows(port: int) -> int:
    try:
        _, body = _get(f"http://{HOST}:{port}/requests")
        return len(json.loads(body).get("requests", []))
    except Exception:
        return -1


def ask_walk(port: int) -> list[dict]:
    """The glass's exact ask path: POST an unsigned ask, then poll the
    WHOLE queue once a second until the row says done — measuring both the
    human's wait and the bytes the wait itself costs."""
    walks = []
    for i, q in enumerate(QUESTIONS[:ASKS]):
        t0 = time.perf_counter()
        try:
            filed = _post(f"http://{HOST}:{port}/requests",
                          {"kind": "ask", "text": q, "thread": "new"})
            rid = filed.get("id")
        except Exception as e:
            walks.append({"ask": i + 1, "error": str(e)[:120]})
            continue
        polls, poll_bytes, status = 0, 0, "timeout"
        deadline = time.monotonic() + ASK_TIMEOUT_S
        while time.monotonic() < deadline:
            time.sleep(ASK_POLL_S)
            try:
                _, body = _get(f"http://{HOST}:{port}/requests")
            except Exception:
                continue
            polls += 1
            poll_bytes += len(body)
            row = next((x for x in json.loads(body).get("requests", [])
                        if x.get("id") == rid), None)
            if row and row.get("status") in ("done", "denied"):
                status = row["status"]
                break
        walks.append({
            "ask": i + 1, "question": q, "status": status,
            "seconds": round(time.perf_counter() - t0, 1),
            "polls": polls, "poll_bytes": poll_bytes})
        print(f"  ask {i+1}: {status} in {walks[-1]['seconds']}s "
              f"({polls} whole-queue polls, {poll_bytes:,} bytes read to wait)")
    return walks


def ladder(per_poll_bytes: float, per_poll_ms: float) -> list[dict]:
    """SOL M0's workload ladder, priced with today's measured unit costs:
    the worker polls every active floor's whole queue every 2 s and posts a
    pulse besides — idle work proportional to floors, not to work."""
    rows = []
    for floors in (26, 110, 1100, 10100):
        rps = floors * 2 / 2.0          # 1 poll + 1 pulse per floor / 2 s
        mb_s = floors * per_poll_bytes / 2.0 / 1e6
        busy_workers = floors * per_poll_ms / 2000.0
        rows.append({"floors": floors, "idle_req_s": round(rps, 0),
                     "idle_MB_s": round(mb_s, 2),
                     "worker_threads_saturated": round(busy_workers, 1)})
    return rows


def main() -> int:
    print("M0 — the old world, measured as it runs\n")
    floors = discover_floors()
    print(f"floors alive: {len(floors)} "
          f"({', '.join(str(f['port']) for f in floors)})")
    costs = poll_cost(floors)
    ok = [c for c in costs if "poll_ms" in c]
    for c in ok:
        print(f"  :{c['port']} {c['scope']:<24} /requests "
              f"{c['poll_ms']:7.1f} ms  {c['poll_bytes']:>8,} B  "
              f"({c['queue_rows']} rows retained)  records={c['records']:,}")
    med_bytes = statistics.median([c["poll_bytes"] for c in ok]) if ok else 0
    med_ms = statistics.median([c["poll_ms"] for c in ok]) if ok else 0

    ask_port = next((p for p in ASK_PORT_PREFERENCE
                     if any(f["port"] == p for f in floors)),
                    floors[0]["port"] if floors else 0)
    print(f"\nthe ask walk (the glass's own path, port {ask_port}, "
          f"{ASKS} asks, sequential):")
    walks = ask_walk(ask_port)
    done = [w["seconds"] for w in walks if w.get("status") == "done"]
    if done:
        srt = sorted(done)
        p50 = srt[len(srt) // 2]
        print(f"  answered {len(done)}/{len(walks)} · p50 {p50:.1f}s · "
              f"worst {max(done):.1f}s · first (boot-lap window) "
              f"{walks[0].get('seconds', '—')}s")

    print("\nthe idle-load ladder (arithmetic from measured unit costs — "
          "a projection, not a benchmark):")
    lad = ladder(med_bytes, med_ms)
    for r in lad:
        print(f"  {r['floors']:>6,} floors → {r['idle_req_s']:>7,.0f} req/s "
              f"idle · {r['idle_MB_s']:>8.2f} MB/s idle · "
              f"{r['worker_threads_saturated']:>7.1f} worker-threads just polling")

    out = {"measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "floors": costs, "ask_port": ask_port, "asks": walks,
           "median_poll_bytes": med_bytes, "median_poll_ms": med_ms,
           "ladder": lad}
    path = Path(__file__).with_name("m0-results.json")
    path.write_text(json.dumps(out, indent=1))
    print(f"\nresults written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
