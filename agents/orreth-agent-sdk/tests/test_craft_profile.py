# PROVENANCE: Fable 5 (claude-fable-5) — 0050 sp3 · 2026-08-11
"""The supply line learns the persona shelf: a chronicle asset whose profile
IS a template renders exactly like firmware — the tester is craft too."""
from orreth_agent.craft import ResolvedCraft


def test_a_chronicle_template_renders_like_firmware():
    rc = ResolvedCraft({"name": "uat-persona-quinn", "ref": "sha256:x",
                        "version": 3, "lifecycle": "chronicle",
                        "profile": {"template": "hello ⟦who⟧"}})
    assert rc.render(who="quinn") == "hello quinn"


def test_a_dict_profile_without_template_stays_unrenderable():
    rc = ResolvedCraft({"name": "fingertip-default", "ref": "sha256:y",
                        "version": 1, "lifecycle": "chronicle",
                        "profile": {"max_cycles": 3}})
    assert rc.text is None and rc.render() == ""


def test_a_leased_acquire_rides_the_post_lane(tmp_path):
    # 0045 law 8 (2026-08-23): a citizen presents the SAME becky-chained
    # lease that fuels its thoughts — the token is a JSON blob, so the
    # leased ask rides POST; the reply's own fields confess the posture
    import http.server
    import json as _json
    import threading

    from orreth_agent.craft import acquire

    seen = {}

    class Door(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("content-length", 0)))
            seen.update(_json.loads(raw))
            out = _json.dumps({"name": "resident-voice", "ref": "sha256:z",
                               "version": 2, "lifecycle": "chronicle",
                               "text": "hello", "leased": True}).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), Door)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        tok = {"subject": "did:key:zme", "chain": ["hop"]}
        rc = acquire("resident-voice", did="did:key:zme",
                     base=f"http://127.0.0.1:{srv.server_port}",
                     token=tok, cache_home=str(tmp_path))
        assert rc.text == "hello"
        # the door received the whole lease beside the claimant's name
        assert seen["token"] == tok and seen["did"] == "did:key:zme"
    finally:
        srv.shutdown()
