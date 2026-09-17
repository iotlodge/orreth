# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P3 sp3, the words form live · 2026-09-17
"""The streaming laws (canon 0002's deferred design, landed): deltas
flow glass→human only — the words form live in the chat, at least a few
frames before completion; their concatenation matches the reply; and
the durable truth is STILL the full reply behind the door (the stream
is a sketch, the door is the record). The broker never carries a delta
— structurally: deltas never touch the outbox or a topic."""
import json
import os
import secrets
import time
import urllib.request

import pytest

from orreth_spine import gateway, glass

from tests.test_bridgefeed import SSEClient  # noqa: E402
from tests.test_mind import _rails_up  # noqa: E402

rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


@rails
def test_the_words_form_live_and_the_door_keeps_the_truth(pg, rig):
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    reply = f"alpha beta gamma delta {tok} end"
    rig.resident.gateway = gateway.FakeGateway(reply=reply)
    if True:
        client = SSEClient(rig.port)
        req = urllib.request.Request(
            f"http://127.0.0.1:{rig.port}/ask",
            data=json.dumps({"text": f"stream it (marker {tok})",
                             "to": ["librarian"]}).encode(),
            headers={"content-type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            ask_id = json.loads(r.read())["ids"][0]
        deltas, saw_reply = [], False
        end = time.monotonic() + 45
        while time.monotonic() < end and not saw_reply:
            got = client.next_event(deadline_s=20)
            if got is None:
                continue
            event, data, _id = got
            if event == "delta" and data["ref"] == ask_id:
                deltas.append(data["text"])
            elif event == "message" and data.get("ref") == ask_id and \
                    "reply" in data.get("kind", ""):
                saw_reply = True
        client.close()
        assert saw_reply, "the completion notice never arrived"
        assert len(deltas) >= 4          # the words formed LIVE, word by word
        assert "".join(deltas).strip() == reply
        # the door still serves the whole truth
        with urllib.request.urlopen(
                f"http://127.0.0.1:{rig.port}/ask/{ask_id}",
                timeout=10) as r:
            assert json.loads(r.read())["reply"] == reply
