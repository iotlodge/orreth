# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (b): the desk's pure laws and the body's knock · 2026-09-26
"""THE MACHINE JOIN DESK — the reference's pure laws (the fixture measures them on both
kernels; these say WHY in words) and the body's side of the knock against a desk
played by a small door of this test's own: challenge → prove → the word → collect.
The desk's doors themselves live on the Rust kernel (`tests/desk.rs`)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from orreth_spine import desk, envelope as ev, seat
from orreth_spine.identity import Identity

KERNEL = Identity("kernel", bytes(range(32)), kind="kernel")
SCOUT = Identity("scout", bytes(range(32, 64)), kind="agent")
OTHER = Identity("other", bytes(range(64, 96)), kind="agent")
NONCE = "00" * 16


def test_a_settled_word_is_never_rewritten_and_proved_answers_only_a_challenge():
    assert desk.transition_legal("pending", "challenged")
    assert desk.transition_legal("challenged", "proved")
    assert desk.transition_legal("proved", "staged")
    assert desk.transition_legal("staged", "done") and desk.transition_legal("staged", "denied")
    assert desk.transition_legal("staged", "challenged"), "a restarted desk re-challenges rather than verifying blind"
    assert not desk.transition_legal("pending", "proved"), "no proof without a challenge"
    assert not desk.transition_legal("challenged", "done"), "no lease without a proof"
    for settled in ("done", "denied"):
        assert all(not desk.transition_legal(settled, to) for to in desk.STATUSES)
    assert not desk.transition_legal("challenged", "riding")


def test_the_proof_is_the_key_behind_the_did_over_the_desks_own_nonce():
    sig = desk.proof_of(SCOUT, NONCE)
    assert sig["alg"] == "ed25519" and sig["by"] == SCOUT.did
    assert desk.prove(SCOUT.did, SCOUT.verify_key_hex, NONCE, sig)
    assert not desk.prove(SCOUT.did, SCOUT.verify_key_hex, "11" * 16, sig), "the desk's nonce, never the echoed one"
    assert not desk.prove(SCOUT.did, OTHER.verify_key_hex, NONCE, sig), "a key that does not derive the DID"
    assert not desk.prove(SCOUT.did, SCOUT.verify_key_hex, NONCE, desk.proof_of(OTHER, NONCE)), "another key's signature"
    assert not desk.prove("did:orreth:person:jb", SCOUT.verify_key_hex, NONCE, sig), "a person has no key"
    svc = Identity("clock", bytes(range(32, 64)), kind="service")
    assert not desk.prove(svc.did, svc.verify_key_hex, NONCE, desk.proof_of(svc, NONCE)), "a service is the keeper's to register"
    jid = desk.join_id_of(SCOUT.did, NONCE)
    assert desk.collect_ok(SCOUT.did, SCOUT.verify_key_hex, jid, NONCE, desk.collect_sig(SCOUT, jid, NONCE))
    assert not desk.collect_ok(SCOUT.did, SCOUT.verify_key_hex, jid, NONCE, sig), "the challenge's proof does not collect"
    assert not desk.collect_ok(SCOUT.did, SCOUT.verify_key_hex, "join_0", NONCE, desk.collect_sig(SCOUT, jid, NONCE))


def test_the_lease_is_a_seat_shaped_token_with_the_fuel_clause_that_verifies_at_the_root():
    tok = desk.lease(KERNEL, did=SCOUT.did, scope="u:dev", expiry="2026-10-27T00:00:00.000Z", usd=1.0, renew_days=1)
    assert set(tok) == {"subject", "audience", "grants", "constraints", "chain", "sig"}
    assert tok["subject"] == SCOUT.did and tok["audience"] == "u:dev"
    assert tok["grants"] == [{"action": "retrieve", "space": "self"}, {"action": "write", "space": "self"}]
    assert tok["constraints"]["budget"] == {"cost": 1.0, "renew_days": 1}
    assert seat.verify(tok, root_did=KERNEL.did, root_key_hex=KERNEL.verify_key_hex, now="2026-10-01T00:00:00.000Z") == "ok"
    assert seat.verify(tok, root_did=KERNEL.did, root_key_hex=KERNEL.verify_key_hex, now="2026-10-28T00:00:00.000Z") == "expired"
    assert seat.verify(tok, root_did=OTHER.did, root_key_hex=OTHER.verify_key_hex, now="2026-10-01T00:00:00.000Z") == "foreign authority"
    assert not any(g["action"] == "govern" for g in tok["grants"]), "a lease never governs"
    assert desk.fuel_clause(2.5, 0) == {"cost": 2.5}, "0 days is the old lump"
    assert seat.seat_id(tok).startswith("seat_"), "a lease IS a seat on the ground"


def test_the_words_are_plain():
    assert desk.words("staged", "scout") == "scout proved its key — the door waits for a governing seat's yes"
    assert desk.words("done", "scout", "u:dev", desk.admitted_by(ticket=True)) == (
        "lease granted — welcome to u:dev, scout · admitted on the crew manifest — this kernel spawned this body")
    assert desk.admitted_by(welcome="join_abc") == "admitted on its standing welcome (join_abc) — the same self, the same world"
    assert desk.admitted_by(person="did:orreth:person:jb") == "admitted on jb's word"
    h = desk.hold_words("scout", "resident", "sha256:0123456789abcdef", 30)
    assert h.startswith("scout (a resident) asks to join this world — its key is proven, its template 01234567.")
    assert "Cancel is the default." in h
    assert desk.REFUSED == {"error": "join refused"}
    assert desk.name_ok("scout") and not desk.name_ok("Scout") and not desk.name_ok("a")


class _Desk(BaseHTTPRequestHandler):
    """A desk played for the body's side: challenge, verify against its OWN nonce, stage
    once (the human's word comes on the next look), then the lease on the right key."""
    state: dict = {}

    def log_message(self, *_a):
        pass

    def _send(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code); self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def do_GET(self):
        st = self.state
        if self.path == f"/join/{st['id']}":
            st["looks"] = st.get("looks", 0) + 1
            if st["status"] == "staged" and st["looks"] >= 2:
                st["status"] = "done"; st["admitted_by"] = desk.admitted_by(person="did:orreth:person:jb")
            return self._send(200, {"id": st["id"], "status": st["status"]})
        self._send(404, desk.REFUSED)

    def do_POST(self):
        st = self.state
        p = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)) or b"{}")
        if self.path == "/join":
            st.update(id=desk.join_id_of(p["did"], NONCE), did=p["did"], pk=p["public_key"], status="challenged",
                      asked=p, nonce=NONCE)
            return self._send(201, {"id": st["id"], "status": "challenged", "nonce": NONCE, "words": desk.words("challenged", "scout")})
        if self.path == "/join/prove":
            if not desk.prove(st["did"], st["pk"], st["nonce"], p["sig"]):
                st["status"] = "denied"; return self._send(200, {"id": st["id"], "status": "denied"})
            st["status"] = "staged"; return self._send(200, {"id": st["id"], "status": "staged", "ask": "ask_1"})
        if self.path == "/join/lease":
            if st["status"] != "done" or not desk.collect_ok(st["did"], st["pk"], st["id"], st["nonce"], p["sig"]):
                return self._send(403, {"error": "not confirmed"})
            tok = desk.lease(KERNEL, did=st["did"], scope="u:dev", expiry="2026-10-27T00:00:00.000Z", usd=1.0, renew_days=1)
            return self._send(200, {"id": st["id"], "status": "done", "lease": tok, "wire": seat.wire(tok),
                                    "lease_id": seat.seat_id(tok), "expiry": tok["constraints"]["expiry"],
                                    "admitted_by": st["admitted_by"]})
        self._send(404, desk.REFUSED)


def test_the_bodys_knock_walks_the_desk_and_collects_its_lease():
    _Desk.state = {}
    srv = HTTPServer(("127.0.0.1", 0), _Desk)
    t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    try:
        said = []
        got = desk.knock(f"http://127.0.0.1:{srv.server_port}", SCOUT, name="scout", kind="resident",
                         template_hash="sha256:abc", policy_hash="sha256:def", ticket="t0", wait_s=10, poll_s=0.05,
                         say=said.append)
        assert got is not None, said
        assert got["lease"]["subject"] == SCOUT.did and got["lease_id"].startswith("seat_")
        assert seat.unwire(got["wire"]) == got["lease"]
        assert got["admitted_by"] == "admitted on jb's word"
        assert _Desk.state["asked"]["role"] == "resident" and _Desk.state["asked"]["ticket"] == "t0"
        assert _Desk.state["asked"]["public_key"] == SCOUT.verify_key_hex
        assert any("waiting at the door" in w for w in said), said
        # an imposter wearing scout's DID never collects: the desk verifies against the key it was given
        _Desk.state = {}
        got = desk.knock(f"http://127.0.0.1:{srv.server_port}", OTHER, name="scout", kind="resident",
                         template_hash="", policy_hash="", wait_s=2, poll_s=0.05, say=said.append)
        assert got is not None and got["lease"]["subject"] == OTHER.did, "its own self, never another's"
    finally:
        srv.shutdown(); srv.server_close()


def test_the_body_signs_the_bytes_the_old_sdk_signed():
    assert ev.canonical(desk.challenge_payload("did:x", "n")) == b'{"did":"did:x","join_nonce":"n"}'
