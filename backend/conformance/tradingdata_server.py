# PROVENANCE: Fable 5 (claude-fable-5) — 0054 sp2, the desk's data stall · 2026-08-12
"""tradingdata server — the desk's stall in the Farm (0054 sp2).

A local HTTP hull around orreth_sim/tradingdata.py so the Farm can govern
it like any service: GET answers the keeper's heartbeat probes (probation
earns serving on live beats, 0018), POST /call {tool, args} executes one
of the eight declared tools — the same names the pinned manifest carries.
The stall holds no keys and writes no records; the worker's /tool door
meters every call at the plane before a byte moves.

    uv run --with yfinance --with pandas python tradingdata_server.py 4570
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from orreth_sim import tradingdata

SERVICE = "local.desk/tradingdata"


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        out = json.dumps({"ok": True, "service": SERVICE,
                          "tools": sorted(tradingdata.TOOLS)}).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(out)

    def do_POST(self):
        ln = int(self.headers.get("content-length") or 0)
        try:
            data = json.loads(self.rfile.read(ln) or b"{}")
            fn = tradingdata.TOOLS.get(str(data.get("tool") or ""))
            out = (fn(**(data.get("args") or {})) if fn
                   else {"error": "no such tool on this stall"})
        except Exception as e:
            out = {"error": f"the stall stumbled: {str(e)[:120]}"}
        body = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):                  # the stall is quiet
        pass

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass              # a caller hung up mid-answer — quiet, not broken


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4570
    print(f"· the tradingdata stall opens on :{port} — "
          f"{len(tradingdata.TOOLS)} tools, no keys held")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
