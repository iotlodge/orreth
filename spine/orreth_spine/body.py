# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
"""THE SDK-SIDE BODY (canon 0004 · 0008's end shape · 0005 P7 sp6, THE BODIES'
SEAM).

0008: a resident's brain is a LangGraph process the kernel starts, meters and
stops. This module is that process. `python -m orreth_spine.body --template
<path> [--binding <path>] [--policy <path>]` stands ONE body — the same
`Resident` the Python Bridge seats in-process — as its own process: it loads
its template, its binding and the covenant policy (no policy, no join — AG-3),
joins this world as the SAME self every life (rule 1: its seed under the
agents' home), keeps its lease while it serves its benches (the shared
any-body bench and its own), streams its words as they form to the kernel
that spawned it through the kernel's local door (glass-bound, never the
rail), and stops WHOLE on SIGINT or SIGTERM — its lease lapses, the roster
reads dormant in seconds, nothing is deleted.

The kernel GOVERNS the bodies it spawns (the Rust kernel, `bodies.rs`; the
Python Bridge seats its crew in-process as the reference and simulator):
spawn at light, restart a body that died after a backoff (`backoff_s`), PARK
a body that dies `PARK_STRIKES` times inside `PARK_WINDOW_S` — visibly, as a
fact (`orreth.body.parked.v1`) carrying its last words, its seat and its self
standing — and stop every body whole at dark, none left running. A body
refused at birth (placement: the ground cannot seat it, P6 sp4) exits
`EXIT_REFUSED` and is never restarted — the refusal is already a recorded
fact; a body without a policy exits `EXIT_NO_POLICY` the same way.

The crew a kernel seats is ONE manifest (`spine/crew.v0.json`, `crew()`),
read by both spines: one crew, one truth. The pure laws here are the
fixture's (`spine/conformance/bodies-v0.json`).
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from . import envelope as ev

SPINE = Path(__file__).resolve().parents[1]
CREW_MANIFEST = SPINE / "crew.v0.json"
CREW_FORMAT = "orreth-crew/1"

PARKED = "orreth.body.parked.v1"                  # the kernel stopped restarting a body — a fact, with its evidence
KERNEL = "the kernel"

EXIT_STOPPED = 0                                  # stopped whole on the kernel's word
EXIT_REFUSED = 3                                  # refused at birth (placement) — terminal, never restarted
EXIT_NO_POLICY = 4                                # no covenant policy — terminal (AG-3)

PARK_STRIKES = 3                                  # deaths inside the window that park a body
PARK_WINDOW_S = 300                               # the window
BACKOFF_CAP_S = 30.0                              # the longest wait before a restart
KERNEL_DOOR_DIAL = "SPINE_KERNEL_DOOR"            # where a spawned body streams its words (http://127.0.0.1:<port>)
EPHEMERAL_DIAL = "SPINE_BODY_EPHEMERAL"           # tests only: an ephemeral self (home=None)


# ---- the pure laws (fixture bodies-v0) ------------------------------------------------------------

def backoff_s(deaths: int) -> float:
    """The wait before the n-th restart: 1 s after the first death, doubling,
    capped at BACKOFF_CAP_S — a body that keeps dying is not hammered back."""
    n = int(deaths)
    if n <= 0:
        return 0.0
    return float(min(BACKOFF_CAP_S, 2 ** (n - 1)))


def _iso(s: str) -> datetime:
    at = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return at if at.tzinfo else at.replace(tzinfo=timezone.utc)


def park_rule(exits: list[str], now: str, window_s: int = PARK_WINDOW_S, strikes: int = PARK_STRIKES) -> dict:
    """The park law: the deaths inside the window (an exit at or after
    now - window), counted; at `strikes` the kernel stops restarting —
    PARKED. Otherwise the wait before the next restart is the backoff for
    the deaths counted. {parked, deaths, wait_s}."""
    t = _iso(now)
    n = sum(1 for e in exits if (t - _iso(e)).total_seconds() <= float(window_s))
    if n >= int(strikes):
        return {"parked": True, "deaths": n, "wait_s": None}
    return {"parked": False, "deaths": n, "wait_s": backoff_s(n)}


def window_words(window_s: int) -> str:
    s = int(window_s)
    if s % 3600 == 0:
        h = s // 3600
        return f"{h} hour{'s' if h != 1 else ''}"
    if s % 60 == 0:
        m = s // 60
        return f"{m} minute{'s' if m != 1 else ''}"
    return f"{s} second{'s' if s != 1 else ''}"


def parked_words(name: str, deaths: int, window_s: int, last_words: str | None) -> str:
    """The plain words of a parked body (rule 13 · rule 11): what happened,
    what stands, and the human's lever."""
    said = " ".join(str(last_words or "").split())
    tail = f" Its last words: “{said[:200]}”." if said else " It left no words."
    n = int(deaths)
    return (f"{name} is PARKED — it died {n} time{'s' if n != 1 else ''} in {window_words(window_s)}, so the kernel "
            f"stopped restarting it.{tail} Nothing is deleted: its seat, its self and its record stand. "
            f"Say “restart the {name} body” to try again.")


def parked_payload(name: str, did: str | None, deaths: int, window_s: int, last_words: str | None) -> dict:
    """The parked fact's payload: pointer + the evidence (the words cut, never a stack whole)."""
    said = " ".join(str(last_words or "").split())[:600]
    return {"ref": name, "hash": ev.content_hash(said), "did": did, "deaths": int(deaths),
            "window_s": int(window_s), "last_words": said}


def parked_fact(name: str, did: str | None, deaths: int, window_s: int, last_words: str | None,
                scope: str | None = None) -> dict:
    """`orreth.body.parked.v1` — the kernel's own fact (its chain, an
    observation marker under no parent: the kernel keeps the crew)."""
    sc = scope or ev.scope()
    return ev.make_envelope(kind="event", type=PARKED, universe_id=sc, scope_path=sc,
                            payload=parked_payload(name, did, deaths, window_s, last_words),
                            correlation_id=name, authority_chain=[KERNEL])


# ---- the crew: one manifest, both spines -------------------------------------------------------------

def crew_seats(manifest: dict) -> list[dict]:
    """The manifest's seats, checked: {template, binding|None} each, in order."""
    if not isinstance(manifest, dict) or manifest.get("format") != CREW_FORMAT:
        raise ValueError(f"not a crew manifest: {manifest.get('format') if isinstance(manifest, dict) else manifest!r}")
    out = []
    for s in manifest.get("seats") or []:
        t = str(s.get("template") or "").strip()
        if not t:
            raise ValueError("a seat names its template")
        out.append({"template": t, "binding": (str(s["binding"]).strip() if s.get("binding") else None)})
    if not out:
        raise ValueError("a crew has at least one seat")
    return out


CREW_DIAL = "SPINE_CREW"                          # a manifest other than crew.v0.json (a proof's two-seat crew) — a path


def crew(spine: str | os.PathLike | None = None) -> list[dict]:
    """The seats with their paths resolved against the spine home (the
    manifest `SPINE_CREW` names, else `crew.v0.json`)."""
    base = Path(spine or SPINE)
    manifest = Path(os.environ.get(CREW_DIAL) or (base / "crew.v0.json"))
    seats = crew_seats(json.loads(manifest.read_text("utf-8")))
    return [{"template": base / s["template"], "binding": (base / s["binding"]) if s["binding"] else None}
            for s in seats]


# ---- the words as they form: to the kernel's door, coalesced ----------------------------------------------

class DeltaSink:
    """A spawned body's streaming words go to the kernel that spawned it —
    `POST <door>/delta {ref, text}` — coalesced every ~80 ms on a thread of
    their own, so a slow door never slows a thought; display only (glass-
    bound): a miss is dropped in silence, the durable truth is the reply."""

    def __init__(self, door: str, every_s: float = 0.08):
        self.door = door.rstrip("/")
        self.every_s = every_s
        self._q: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def __call__(self, ref: str, text: str) -> None:
        self._q.put((ref, text))

    def _run(self) -> None:
        import http.client
        from urllib.parse import urlsplit
        u = urlsplit(self.door)
        conn = None
        while not self._stop.is_set():
            batch: dict[str, list[str]] = {}
            try:
                ref, text = self._q.get(timeout=self.every_s)
                batch.setdefault(ref, []).append(text)
                deadline = time.monotonic() + self.every_s
                while time.monotonic() < deadline:
                    try:
                        ref, text = self._q.get_nowait()
                        batch.setdefault(ref, []).append(text)
                    except queue.Empty:
                        break
            except queue.Empty:
                continue
            for ref, parts in batch.items():
                body = json.dumps({"ref": ref, "text": "".join(parts)}).encode()
                for _attempt in range(2):
                    try:
                        if conn is None:
                            conn = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=2.0)
                        conn.request("POST", "/delta", body, {"content-type": "application/json"})
                        r = conn.getresponse()
                        r.read()
                        break
                    except Exception:                       # noqa: BLE001 — display only, never a stack
                        try:
                            if conn is not None:
                                conn.close()
                        except Exception:                   # noqa: BLE001
                            pass
                        conn = None

    def close(self) -> None:
        self._stop.set()


# ---- the process -------------------------------------------------------------------------------------

def _gateway():
    """The lane every mind thinks through: the LiteLLM gateway when the box
    answers, else the fake mind that says so — the Bridge's own law."""
    from . import stable as _stable
    if _stable.Gateway().ready():
        from .gateway import LiteLLMGateway
        return LiteLLMGateway(), f"every mind through the gateway at {_stable.Gateway().base}"
    from .gateway import FakeGateway
    return (FakeGateway(reply="I am the fake mind — the gateway is dark; run scripts/dev.sh up "
                              "and restart me to think for real."),
            f"a fake mind (the gateway at {_stable.Gateway().base} is dark)")


def _home():
    if os.environ.get(EPHEMERAL_DIAL):
        return None
    return Path(os.environ.get("ORRETH_HOME", Path.home() / ".orreth")) / "agents"


def _say(words: str) -> None:
    print(words, file=sys.stderr, flush=True)


def seed_shelf(conn, gateway, home) -> None:
    """The kernel's boot rite, in the reference's own words (P6.5 sp1 · sp2):
    the built-ins on the shelf (their schemas live in tools.py — the Rust
    kernel asks this rite to run once at light, until sp8 moves the tool
    door), each probed once; the reference clock by the dial."""
    from . import mcp, services
    made = services.seed(conn, gateway=gateway, home=home)
    for line in made["refused"]:
        _say(f"the shelf refused a built-in: {line}")
    checked = services.check_all(conn, gateway=gateway)
    bad = [c["name"] for c in checked if c["ok"] is False]
    _say(f"the shelf: {len(checked)} services probed"
         + (f", registered now: {', '.join(made['registered'])}" if made["registered"] else "")
         + (f", re-pinned (their words changed): {', '.join(made['versioned'])}" if made.get("versioned") else "")
         + (f", UNHEALTHY: {', '.join(bad)}" if bad else ""))
    if mcp.ref_on():
        try:
            ref = mcp.seed_ref(conn, home=home)
            t = ref["tools"]
            _say(f"the shelf: the reference clock server registered at {mcp.locator_words(mcp.ref_locator())}"
                 f" — tools {', '.join(t['new'] + t['present'] + t['versioned']) or 'none'}")
        except Exception as e:                                  # noqa: BLE001 — the rig runs on
            _say(f"the reference clock could not be registered: {type(e).__name__}: {e}")


def serve(template, binding, policy, *, stop: threading.Event, ready: threading.Event | None = None) -> int:
    """One body's whole life: born, joined, serving on its lease until the
    stop; the exit code says how it ended."""
    import psycopg
    from . import ground, mitl, presence, services, tools as _tools
    from .rails import PG_DSN
    from .resident import PlacementRefused, PolicyRefused, Resident

    home = _home()
    gateway, mind = _gateway()
    _tools.GATEWAY = gateway                               # the keepers' checks ping through the lane
    services.HOME = services.services_home(home)           # the services' seeds beside the agents'
    r = Resident(template, gateway=gateway, home=home, binding=binding)
    if policy is None:
        return EXIT_NO_POLICY
    try:
        r.load_policy(policy)
    except (OSError, ValueError, KeyError) as e:                # no policy, no join (AG-3) — terminal
        _say(f"{r.name} wears no covenant policy ({type(e).__name__}: {e}) — it never joins")
        return EXIT_NO_POLICY
    door = os.environ.get(KERNEL_DOOR_DIAL)
    sink = DeltaSink(door) if door else None
    if sink is not None:
        r.on_delta = sink
    with psycopg.connect(PG_DSN, autocommit=True) as conn:
        joined = None
        for _attempt in range(20):                          # birth retries: a schema race or a slow
            try:                                            # ground never kills a body before it lives
                ground.ensure_all(conn)
                joined = r.join(conn)
                break
            except PlacementRefused as e:                   # P6 sp4: the ground cannot seat this body —
                _say(f"{r.name} refused at birth — " + "; ".join(e.reasons) + " (recorded; never started)")
                return EXIT_REFUSED                         # terminal: the kernel never restarts a refusal
            except PolicyRefused as e:
                _say(str(e))
                return EXIT_NO_POLICY
            except Exception as e:                          # noqa: BLE001
                if _attempt == 19:
                    _say(f"{r.name} could not join: {type(e).__name__}: {e}")
                    return 1
                time.sleep(0.3)
        _say(f"{r.name} is alive: {r.identity.did} · life {joined['life']} · {r.kind}"
             + (f" ({r.function})" if r.function else "") + f" · {mind}"
             + (f" · words to {door}" if door else ""))
        if r.name == mitl.NAME:                             # P6 sp3: MITL wears the canon from birth
            try:
                made = mitl.acquire_ontology(conn, r)
                if made["acquired"] or made["missing"]:
                    _say(f"mitl wears the Orreth ontology v0: {made['acquired']} passages acquired from "
                         f"{made['files']} files" + (f"; missing {made['missing']}" if made["missing"] else ""))
            except Exception as e:                          # noqa: BLE001
                _say(f"mitl could not acquire the ontology: {type(e).__name__}: {e}")
        if ready is not None:
            ready.set()
        while not stop.is_set():
            try:
                presence.renew(conn, r.identity.did, r.name, r.kind)     # M2: alive while I serve
                r.serve_once(conn, idle_s=1.0, max_commands=50)
            except Exception as e:                          # noqa: BLE001 — a rail's hiccup never kills a body
                if not stop.is_set():
                    _say(f"{r.name}'s serve stumbled: {type(e).__name__}: {str(e)[:200]}")
                    time.sleep(0.5)
    if sink is not None:
        sink.close()
    _say(f"{r.name} stopped whole.")
    return EXIT_STOPPED


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m orreth_spine.body",
                                 description="One body as its own process (P7 sp6, the bodies' seam).")
    ap.add_argument("--template", help="the resident template (orreth-resident-template/1)")
    ap.add_argument("--binding", help="a workspace binding (bindings/<pull>.v0.json)")
    ap.add_argument("--policy", default=str(SPINE / "policy" / "covenant-policy.v1.json"),
                    help="the covenant policy the body wears (no policy, no join)")
    ap.add_argument("--seed-shelf", action="store_true",
                    help="the kernel's boot rite, once: the built-ins on the shelf, probed; then exit")
    a = ap.parse_args(argv)
    stop = threading.Event()

    def _on_signal(signum, _frame):
        stop.set()
    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    if a.seed_shelf:
        import psycopg
        from . import ground
        from .rails import PG_DSN
        home = _home()
        gateway, _mind = _gateway()
        with psycopg.connect(PG_DSN, autocommit=True) as conn:
            ground.ensure_all(conn)
            seed_shelf(conn, gateway, services_home(home))
        return EXIT_STOPPED
    if not a.template:
        ap.error("--template is required (or --seed-shelf)")
    return serve(a.template, a.binding, a.policy, stop=stop)


def services_home(home):
    from . import services
    return services.services_home(home)


if __name__ == "__main__":
    raise SystemExit(main())
