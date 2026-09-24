# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
"""A fake LiteLLM gateway for the suite: the management doors the Stable
uses (models · keys · spend) and the one chat door, on a local port, no
network, no spend — the WIRE proven (paths, bodies, headers, the 429 of a
drained key) without a provider. Prices come from a map the test sets;
every answer wears `x-litellm-response-cost` exactly as the real box does."""
from __future__ import annotations

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MASTER = "sk-fake-master"


class FakeLiteLLM:
    def __init__(self, prices: dict | None = None, reply: str = "pong", tokens: tuple[int, int] = (13, 5)):
        self.models: dict[str, dict] = {}            # id → {model_name, litellm_params}
        self.keys: dict[str, dict] = {}              # key → {alias, user_id, max_budget, budget_duration, spend, models}
        self.logs: list[dict] = []
        self.prices = dict(prices or {})             # route → (in_per_token, out_per_token)
        self.reply, self.tokens = reply, tokens
        self.calls: list[dict] = []
        self.dark = False
        self._srv = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.port = self._srv.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        threading.Thread(target=self._srv.serve_forever, daemon=True).start()

    def close(self):
        self._srv.shutdown(); self._srv.server_close()

    def price_of(self, route: str) -> tuple[float, float]:
        return self.prices.get(route) or (0.0, 0.0)

    def _handler(self):
        fake = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):          # quiet
                pass

            def _send(self, code, obj, headers=None):
                body = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("content-type", "application/json")
                for k, v in (headers or {}).items():
                    self.send_header(k, v)
                self.send_header("content-length", str(len(body)))
                self.end_headers(); self.wfile.write(body)

            def _body(self):
                n = int(self.headers.get("content-length") or 0)
                return json.loads(self.rfile.read(n) or b"{}") if n else {}

            def _auth(self):
                return (self.headers.get("Authorization") or "").replace("Bearer ", "", 1)

            def do_GET(self):
                if fake.dark:
                    self.connection.close(); return
                path, _, qs = self.path.partition("?")
                q = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
                if path in ("/health/readiness", "/health/liveliness"):
                    return self._send(200, {"status": "healthy"})
                if path == "/model/info":
                    data = []
                    for mid, m in fake.models.items():
                        ci, co = fake.price_of(m["litellm_params"]["model"])
                        data.append({"model_name": m["model_name"], "litellm_params": {"model": m["litellm_params"]["model"]},
                                     "model_info": {"id": mid, "base_model": (m.get("model_info") or {}).get("base_model"),
                                                    "input_cost_per_token": ci, "output_cost_per_token": co,
                                                    "max_input_tokens": 200000, "supports_function_calling": True,
                                                    "supports_vision": False}})
                    return self._send(200, {"data": data})
                if path == "/key/info":
                    k = fake.keys.get(q.get("key", ""))
                    if k is None:
                        return self._send(404, {"error": {"message": "no such key"}})
                    return self._send(200, {"key": q["key"], "info": dict(k, budget_reset_at="2099-01-01T00:00:00+00:00")})
                if path == "/spend/logs":
                    rows = [r for r in fake.logs if (not q.get("user_id") or r["user"] == q["user_id"])
                            and (not q.get("request_id") or r["request_id"] == q["request_id"])]
                    return self._send(200, rows)
                self._send(404, {"error": {"message": "no such door"}})

            def do_POST(self):
                if fake.dark:
                    self.connection.close(); return
                body = self._body(); key = self._auth()
                if self.path == "/model/new":
                    mid = str((body.get("model_info") or {}).get("id") or body["model_name"])
                    if mid in fake.models:
                        return self._send(500, {"error": {"message": "Failed to add model to db"}})
                    fake.models[mid] = {"model_name": body["model_name"], "litellm_params": body["litellm_params"],
                                        "model_info": body.get("model_info") or {}}
                    return self._send(200, {"model_id": mid})
                if self.path == "/model/delete":
                    fake.models.pop(body.get("id"), None)
                    return self._send(200, {"message": "deleted"})
                if self.path == "/key/generate":
                    k = "sk-fake-" + secrets.token_hex(6)
                    fake.keys[k] = {"key_alias": body.get("key_alias"), "user_id": body.get("user_id"),
                                    "max_budget": float(body.get("max_budget") or 0), "budget_duration": body.get("budget_duration"),
                                    "spend": 0.0, "models": body.get("models") or []}
                    return self._send(200, dict(fake.keys[k], key=k))
                if self.path == "/key/update":
                    k = fake.keys.get(body.get("key"))
                    if k is None:
                        return self._send(404, {"error": {"message": "no such key"}})
                    for f in ("max_budget", "models", "budget_duration"):
                        if f in body:
                            k[f] = body[f]
                    return self._send(200, dict(k, key=body["key"]))
                if self.path == "/key/delete":
                    for k in body.get("keys") or []:
                        fake.keys.pop(k, None)
                    return self._send(200, {"deleted_keys": body.get("keys") or []})
                if self.path == "/chat/completions":
                    k = fake.keys.get(key)
                    if k is None and key != MASTER:
                        return self._send(401, {"error": {"message": "invalid key", "type": "auth_error"}})
                    mid = body.get("model")
                    m = fake.models.get(mid)
                    if m is None:
                        return self._send(400, {"error": {"message": f"model {mid} not found", "type": "invalid_request"}})
                    if k is not None and k["models"] and mid not in k["models"]:
                        return self._send(401, {"error": {"message": "key not allowed this model", "type": "auth_error"}})
                    if k is not None and k["spend"] >= k["max_budget"]:
                        return self._send(429, {"error": {"message": f"Budget has been exceeded! Current cost: {k['spend']}, Max budget: {k['max_budget']}",
                                                          "type": "budget_exceeded", "code": "429"}})
                    ci, co = fake.price_of(m["litellm_params"]["model"])
                    tin, tout = fake.tokens
                    cost = round(tin * ci + tout * co, 10)
                    rid = "chatcmpl-" + secrets.token_hex(6)
                    fake.calls.append({"model": mid, "key": key, "body": body})
                    if k is not None:
                        k["spend"] = round(k["spend"] + cost, 10)
                    fake.logs.append({"request_id": rid, "model": m["litellm_params"]["model"], "model_group": mid,
                                      "spend": cost, "prompt_tokens": tin, "completion_tokens": tout,
                                      "user": (k or {}).get("user_id"), "api_key": key[-6:]})
                    tools = body.get("tools") or []
                    msg = {"role": "assistant", "content": fake.reply}
                    if tools and fake.reply.startswith("TOOL:"):        # "TOOL:name:{json}" → one tool call, then words
                        _, name, args = fake.reply.split(":", 2)
                        msg = {"role": "assistant", "content": None,
                               "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": name, "arguments": args}}]}
                        if any(mm.get("role") == "tool" for mm in body.get("messages") or []):
                            last = [mm for mm in body["messages"] if mm.get("role") == "tool"][-1]
                            msg = {"role": "assistant", "content": f"the tool said: {last.get('content')}"}
                    return self._send(200, {"id": rid, "choices": [{"message": msg, "finish_reason": "stop"}],
                                            "usage": {"prompt_tokens": tin, "completion_tokens": tout}},
                                      {"x-litellm-response-cost": repr(cost), "x-litellm-call-id": rid,
                                       "x-litellm-model-id": mid, "x-litellm-key-spend": repr((k or {}).get("spend", 0.0))})
                self._send(404, {"error": {"message": "no such door"}})
        return H
