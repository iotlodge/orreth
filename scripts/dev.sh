#!/usr/bin/env bash
# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
# (the OLD world's rig, unchanged, lives on below under `old` — its own provenance in its lines)
#
# Orreth dev rig — JB's one-command feedback rig, DOCKER-first (the NEW line: canon 0002).
#   scripts/dev.sh up            the spine rig rises: ground (Postgres :5433) · invoke (RabbitMQ
#                                :5672 / :15672) · events (Kafka :9092); waits until all three are healthy
#   scripts/dev.sh down          the rig rests: compose STOP — never `down -v`; the ground's data survives
#   scripts/dev.sh status        compose ps · the Bridge on :4600 · the harness door when the Bridge is lit
#   scripts/dev.sh logs          follow the rig's logs
#   scripts/dev.sh bridge        relight the Python Bridge on the host (SPINE_MASTERS · ANTHROPIC_API_KEY
#                                from the environment / .env), log ~/.orreth/tmp/bridge.log, print the pid
#   scripts/dev.sh bridge stop   bring the Bridge down cleanly (SIGINT — it stops whole); confirms :4600 empty
#   scripts/dev.sh shadow        light the RUST bridge (spine-bridge, P7 sp3) on :4601 in SHADOW beside the Python
#                                Bridge — same ground, same page; log ~/.orreth/tmp/shadow.log, pid printed
#   scripts/dev.sh shadow stop   bring the Rust bridge down (SIGINT — it stops whole); confirms :4601 empty
#   scripts/dev.sh suite [args]  the spine suite to ~/.orreth/tmp/suite.log, tail printed (default: tests;
#                                pass a file or -k to narrow) — REFUSES while a Bridge is lit (the stale-rig law)
#   scripts/dev.sh rust [rails]  cargo test in backend/plane (the whole workspace, hermetic) + the
#                                conformance report line; `rust rails` runs the rail tests on the rig, by name
#   scripts/dev.sh walk          up + bridge — the human's word to open the glass (http://127.0.0.1:4600)
#   scripts/dev.sh old <verb>    the OLD world's rig (universe :4500 · eco :4501 · field :4502), unchanged:
#                                start|stop|restart|replant|status|logs|window|clean|agent
#   scripts/dev.sh replant       = old replant — the launchd keeper's word (com.orreth.replant) stays here
#
# HOUSE LAWS (kept from the old rig; they hold on the new one)
#  · NEVER PIPE A WORKER-SPAWNING VERB — bridge · walk · old start · old replant · old window:
#    a pipe holds the spawned worker's stdout open and the verb never returns.
#  · THE RIG-LEVEL DOWN WORD (~/.orreth/shipyard/rig-down) is the OLD rig's: `old stop` writes it,
#    the keeper's replant honors it, `old start` lifts it. The new rig's `down` is compose stop and
#    nothing more — the ground's volume is the universe's memory, so `down -v` is never spoken here.
#  · DOCKER-RECYCLE: when compose wedges (a half-quit Desktop, a ghost engine), the cures live in
#    `old replant`'s comments; ~/.orreth/tmp/replant.log is the keeper's diary — we say whether it
#    exists, we never parse it.
#  · THE STALE-RIG LAW (2026-09-17): a Bridge older than the code on disk poisons every test
#    dispatcher — `suite` refuses while :4600 is held; relight (`bridge`) after every code change.
#  · The new rig and the old rig share no port: 5433 · 5672 · 15672 · 9092 · 4600 against
#    4500 · 4501 · 4502 · 5432 — both can stand at once, for the record.
set -euo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
# docker compose needs a WRITABLE temp dir; macOS fallbacks are sometimes root-owned
export TMPDIR="$HOME/.orreth/tmp"; mkdir -p "$TMPDIR"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPINE="$ROOT/spine"; PLANE="$ROOT/backend/plane"
RIG="docker compose -f $SPINE/compose.yaml"
RIG_BOXES="orreth-spine-ground orreth-spine-invoke orreth-spine-events"   # compose.yaml's container names
BRIDGE_PORT=4600; BRIDGE_LOG="$TMPDIR/bridge.log"; SUITE_LOG="$TMPDIR/suite.log"; RUST_LOG="$TMPDIR/rust.log"
SHADOW_PORT=4601; SHADOW_LOG="$TMPDIR/shadow.log"   # P7 sp3: the Rust bridge in SHADOW beside the Python Bridge

bridge_pid() { lsof -nP -iTCP:$BRIDGE_PORT -sTCP:LISTEN -t 2>/dev/null | head -1 || true; }
shadow_pid() { lsof -nP -iTCP:$SHADOW_PORT -sTCP:LISTEN -t 2>/dev/null | head -1 || true; }
ground_up()  { nc -z 127.0.0.1 5433 >/dev/null 2>&1; }

rig_health() {  # one word per box: healthy · starting · unhealthy · stopped · dark (no such box)
  for b in $RIG_BOXES; do
    h=$(docker inspect -f '{{if .State.Running}}{{.State.Health.Status}}{{else}}stopped{{end}}' "$b" 2>/dev/null || echo dark)
    printf "  %-22s %s\n" "$b" "${h:-dark}"
  done
}

wait_healthy() {  # up to ~3 minutes; the events rail (Kafka) is the slow riser
  for i in $(seq 90); do
    n=0; for b in $RIG_BOXES; do
      [ "$(docker inspect -f '{{.State.Health.Status}}' "$b" 2>/dev/null || true)" = healthy ] && n=$((n+1)); done
    [ "$n" = 3 ] && return 0
    sleep 2
  done
  return 1
}

load_env() {  # keys live in .env and the process env only, never in any record (the env-secrets law, 0059)
  [ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }; true
}

bridge_stop() {
  pid=$(bridge_pid)
  [ -z "$pid" ] && { echo "· no Bridge holds :$BRIDGE_PORT — nothing to stop"; return 0; }
  echo "· asking the Bridge (pid $pid) to stop whole (SIGINT — every thread joined, the benches left clean)"
  kill -INT "$pid" 2>/dev/null || true
  for i in $(seq 120); do [ -z "$(bridge_pid)" ] && break; sleep 0.5; done   # a whole stop can take ~30 s (consumers leave their groups)
  if [ -n "$(bridge_pid)" ]; then
    echo "· the Bridge did not stop whole in 60 s — terminating (SIGTERM; its consumer groups may hold ghosts for a while)"; kill -TERM "$pid" 2>/dev/null || true
    for i in $(seq 20); do [ -z "$(bridge_pid)" ] && break; sleep 0.5; done
  fi
  [ -n "$(bridge_pid)" ] && { echo "· :$BRIDGE_PORT is STILL held by $(bridge_pid) — kill it by hand"; return 1; }
  echo "· the Bridge is dark — :$BRIDGE_PORT empty"
}

bridge_light() {
  pid=$(bridge_pid)
  [ -n "$pid" ] && { echo "· the Bridge is already lit on :$BRIDGE_PORT (pid $pid) — \`bridge stop\` first to relight"; return 0; }
  ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first"; return 1; }
  load_env
  masters="${SPINE_MASTERS:-}"; n=0; [ -n "$masters" ] && n=$(echo "$masters" | tr ',' '\n' | grep -c . || true)
  mind="a fake mind (no ANTHROPIC_API_KEY)"; [ -n "${ANTHROPIC_API_KEY:-}" ] && mind="the librarian, thinking for real"
  # nohup + & + a subshell: the worker outlives this verb; its stdout is the log, never our pipe.
  # A background child of a non-interactive shell inherits SIGINT IGNORED (POSIX), and Python
  # then never installs KeyboardInterrupt — so `bridge stop`'s SIGINT would fall on deaf ears
  # (found live 2026-09-22: 60 s of silence, then a SIGTERM). The shim restores the default
  # SIGINT handler before the Bridge runs, so Ctrl+C's law holds: it stops WHOLE. -u: the log
  # tells the truth as it happens (block-buffered, it once showed nothing until the kill).
  (cd "$SPINE" && nohup uv run --quiet python -u -c \
     "import signal, runpy; signal.signal(signal.SIGINT, signal.default_int_handler); runpy.run_module('orreth_spine.glass', run_name='__main__')" \
     >"$BRIDGE_LOG" 2>&1 &)
  for i in $(seq 120); do [ -n "$(bridge_pid)" ] && break; sleep 0.5; done
  pid=$(bridge_pid)
  [ -z "$pid" ] && { echo "· the Bridge never took :$BRIDGE_PORT in 60 s — read $BRIDGE_LOG"; tail -5 "$BRIDGE_LOG"; return 1; }
  echo "· the Bridge is lit: http://127.0.0.1:$BRIDGE_PORT/  (pid $pid · $mind · masters: $n named) — log: $BRIDGE_LOG"
}

shadow_light() {  # P7 sp3: the Rust bridge (spine-bridge) on :4601, the same ground, the same page
  pid=$(shadow_pid)
  [ -n "$pid" ] && { echo "· the Rust bridge is already lit on :$SHADOW_PORT (pid $pid) — \`shadow stop\` first to relight"; return 0; }
  ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first"; return 1; }
  load_env
  echo "· building spine-bridge (cargo, feature bridge) …"
  (cd "$PLANE" && cargo build --quiet -p orreth-spine --features bridge --bin spine-bridge) || { echo "· the build refused — read the errors above"; return 1; }
  (cd "$PLANE" && SPINE_BRIDGE_PORT=$SHADOW_PORT nohup "$PLANE/target/debug/spine-bridge" >"$SHADOW_LOG" 2>&1 &)
  for i in $(seq 60); do [ -n "$(shadow_pid)" ] && break; sleep 0.5; done
  pid=$(shadow_pid)
  [ -z "$pid" ] && { echo "· the Rust bridge never took :$SHADOW_PORT in 30 s — read $SHADOW_LOG"; tail -5 "$SHADOW_LOG"; return 1; }
  echo "· the Rust bridge is lit: http://127.0.0.1:$SHADOW_PORT/  (pid $pid · in SHADOW beside :$BRIDGE_PORT — the Python Bridge's residents serve) — log: $SHADOW_LOG"
}

shadow_stop() {
  pid=$(shadow_pid)
  [ -z "$pid" ] && { echo "· no Rust bridge on :$SHADOW_PORT — nothing to stop"; return 0; }
  kill -INT "$pid" 2>/dev/null || true       # Ctrl+C's law: it stops whole
  for i in $(seq 60); do [ -z "$(shadow_pid)" ] && break; sleep 0.5; done
  [ -n "$(shadow_pid)" ] && { kill "$pid" 2>/dev/null || true; for i in $(seq 20); do [ -z "$(shadow_pid)" ] && break; sleep 0.5; done; }
  [ -n "$(shadow_pid)" ] && { echo "· :$SHADOW_PORT is STILL held by $(shadow_pid) — kill it by hand"; return 1; }
  echo "· the Rust bridge is dark — :$SHADOW_PORT empty"
}

new_status() {
  echo "the spine rig (spine/compose.yaml):"
  $RIG ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "  (compose is not answering — is Docker up?)"
  rig_health
  pid=$(bridge_pid)
  if [ -n "$pid" ]; then
    echo "  bridge: LIT on :$BRIDGE_PORT (pid $pid) — log $BRIDGE_LOG"
    h=$(curl -sf -m 4 "http://127.0.0.1:$BRIDGE_PORT/harness" 2>/dev/null || true)
    if [ -n "$h" ]; then
      if command -v jq >/dev/null 2>&1; then
        echo "  harness: $(echo "$h" | jq -c '[.checks[]? | {(.name // .check // "check"): (.ok // .status // .)}] | add // .' 2>/dev/null | head -c 400)"
      else echo "  harness: $(echo "$h" | head -c 300)"; fi
    else echo "  harness: no answer on /harness"; fi
  else
    echo "  bridge: dark — scripts/dev.sh bridge (or walk) lights it"
  fi
  spid=$(shadow_pid)
  [ -n "$spid" ] && echo "  shadow: the Rust bridge LIT on :$SHADOW_PORT (pid $spid) — log $SHADOW_LOG" \
                 || echo "  shadow: dark — scripts/dev.sh shadow lights the Rust bridge on :$SHADOW_PORT"
  [ -f "$TMPDIR/replant.log" ] && echo "  keeper's diary: $TMPDIR/replant.log exists (the old rig's; not parsed)" \
                                || echo "  keeper's diary: none yet"
}

old_rig() {  # ======== THE OLD WORLD'S RIG — verbatim, for the record (universe :4500 · eco :4501 · field :4502) ========
  # Orreth dev universe — JB's one-command feedback rig (DOCKER-first).
  #   scripts/dev.sh old start     compose up the tree + open becky's join door (agents can join)
  #   scripts/dev.sh old window    seed a biography and open the Console (field :4502)
  #   scripts/dev.sh old status    the honest inventory: spine + grown floors + tool bodies + doors
  #   scripts/dev.sh old stop      the WHOLE rig rests (spine, hulls, bodies) and the keeper
  #                                honors the word until start lifts it     restart = stop + start
  #   scripts/dev.sh old agent [flavor] [--once|--forever]   run a lifeforce agent into the field
  CONF="$ROOT/backend/conformance"; COMPOSE="docker compose -f $ROOT/infrastructure/compose.yaml"
  FIELD=4502
  # the rig-level down word (rule 11, paid 2026-08-28): stop writes it, the
  # keeper's replant honors it, start lifts it — down.json speaks per-floor,
  # this file speaks for the whole rig
  RIGDOWN="$HOME/.orreth/shipyard/rig-down"

  rootpub() {  # keep the seed and infrastructure/.env in lockstep, always
    RP=$(cd "$CONF" && uv run python smoke_orrethd.py root-pub)
    # the version: era (VERSION file, bumped reflectively) . commit-count + short
    # hash — climbs with every push on its own, honest provenance in the glass
    OV="v$(cat "$ROOT/VERSION" 2>/dev/null || echo 0.0).$(git -C "$ROOT" rev-list --count HEAD 2>/dev/null || echo 0)+$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo dev)"
    { echo "ORRETH_ROOT_PUB=$RP"; echo "ORRETH_VERSION=$OV"; } > "$ROOT/infrastructure/.env"
    export ORRETH_VERSION="$OV"
    echo "· root: ${RP:0:20}… (env synced) · $OV"
  }

  joindoor() {  # becky answers joins + the librarian answers Asks — the floor's cognition
    pkill -f "console_worker.py $FIELD" 2>/dev/null || true; sleep 0.3
    # the keeper's context carries no login profile (launchd): the repo's own
    # .env fuels the worker — keys live in the file and the process env only,
    # never in any record (the env-secrets law, 0059)
    [ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }
    (cd "$CONF" && ORRETH_JOIN_LEASE_TOKENS="${ORRETH_JOIN_LEASE_TOKENS:-400000}" \
      ORRETH_MODE="${ORRETH_MODE:-dev}" \
      nohup uv run python console_worker.py "$FIELD" >"$TMPDIR/worker.log" 2>&1 &)
    echo "· becky's join door open on :$FIELD — agents may join; log: $TMPDIR/worker.log"
  }

  case "${1:-}" in
    start)   rm -f "$RIGDOWN"   # the human's word: rise
             rootpub; $COMPOSE up --build -d
             docker image prune -f >/dev/null 2>&1 || true   # superseded layers die quietly (the jsbarth disk fire's lesson)
             # wake the tool bodies the last stop rested — start, never re-run:
             # their fetched packages live in the container, and nothing replants
             # a removed body (~/.orreth/bodies.json only allocates ports).
             # compose down killed their network, so each body's stale endpoint
             # is force-cut and re-tied to the fresh net before it rises
             # (RIG_NET in console_worker.py — the one street every hull shares)
             for b in $(docker ps -a --filter name=orreth-body- --filter status=exited --format '{{.Names}}'); do
               docker network disconnect -f orreth-demo-universe_default "$b" 2>/dev/null || true
               docker network connect orreth-demo-universe_default "$b" 2>/dev/null || true
               docker start "$b" >/dev/null 2>&1 && echo "· body wakes: $b" || echo "· body would not wake: $b"
             done
             sleep 3; joindoor; "$0" old status ;;
    stop)    # the rig-level down word lands FIRST, so a keeper tick mid-stop
             # cannot resurrect what the human is darkening
             mkdir -p "$(dirname "$RIGDOWN")"
             date -u +%Y-%m-%dT%H:%M:%SZ > "$RIGDOWN"
             pkill -f console_worker.py 2>/dev/null || true
             pkill -f tradingdata_server.py 2>/dev/null || true
             pkill -f "05-desk/run.py" 2>/dev/null || true
             # dynamic hulls (the Shipyard) ride the rig's network — down together;
             # the worker's replant relaunches them from ~/.orreth/shipyard on start
             docker ps -aq --filter name=orreth-dyn- --filter name=orreth-field- \
               | xargs docker rm -f 2>/dev/null || true
             # tool bodies REST, never removed — docker stop is the operator's
             # word unless-stopped respects; start wakes them with their souls
             docker ps -q --filter name=orreth-body- \
               | xargs docker stop 2>/dev/null || true
             $COMPOSE down ;;
    restart) "$0" old stop; "$0" old start ;;
    clean)   # deliberate deep clean (2026-07-30, after the jsbarth 100%-disk fire):
             # dangling images + build cache trimmed to a warm 15GB. NEVER volumes
             # (pg holds the universe's memory) and NEVER -a image prunes here —
             # this laptop hosts other projects whose stopped images would vanish.
             docker image prune -f
             docker builder prune -f --keep-storage=15GB
             docker buildx prune -f --keep-storage=15GB   # Desktop keeps a second builder
             docker system df ;;
    status)  # the honest inventory (2026-08-28): every container family the rig
             # owns, each beside the ledger that governs it — no invisible parts
             [ -f "$RIGDOWN" ] && \
               echo "  ■ RIG DOWN by the human's word ($(cat "$RIGDOWN")) — scripts/dev.sh start lifts it"
             echo "  spine (infrastructure/compose.yaml):"
             $COMPOSE ps --format '    {{.Name}}\t{{.Status}}' 2>/dev/null || true
             echo "  grown floors (~/.orreth/shipyard/floors.json — the worker replants):"
             docker ps -a --filter name=orreth-dyn- --filter name=orreth-field- \
               --format '    {{.Names}}\t{{.Status}}' 2>/dev/null | sort || true
             echo "  tool bodies (~/.orreth/bodies.json — stop rests them, start wakes them):"
             docker ps -a --filter name=orreth-body- \
               --format '    {{.Names}}\t{{.Status}}' 2>/dev/null | sort || true
             dyn=""; [ -f "$HOME/.orreth/shipyard/floors.json" ] && \
               dyn=$(python3 -c 'import json,sys;print(" ".join(sorted(json.load(open(sys.argv[1])))))' "$HOME/.orreth/shipyard/floors.json" 2>/dev/null)
             for p in 4500 4501 4502 $dyn; do printf "  :%s  " "$p"
               curl -sf "http://127.0.0.1:$p/health" || printf dark; echo; done
             pgrep -f "console_worker.py $FIELD" >/dev/null \
               && echo "  join door: OPEN (:$FIELD)" || echo "  join door: CLOSED — run scripts/dev.sh start"
             # no -q: under pipefail, grep -q's early exit SIGPIPEs launchctl
             # and a loaded keeper reads as NOT LOADED (caught live 2026-08-28)
             launchctl list 2>/dev/null | grep com.orreth.replant >/dev/null \
               && echo "  keeper: loaded — heals every 5 min, honors the down words" \
               || echo "  keeper: NOT LOADED — no self-healing (infrastructure/com.orreth.replant.plist)"
             echo "  capabilities: discovered + crewed by the worker at boot (capabilities/*/genesis.py)" ;;
    logs)    $COMPOSE logs -f --tail 40 ;;
    replant) # the down-ledger-honoring self-replant (2026-08-26, the morning the
             # rig would not rise): HEAL QUIETLY, NEVER REBUILD, NEVER RESURRECT
             # a floor the human darkened. Whole rig healthy → say so and leave.
             # Docker dead → open the Desktop and wait, bounded. Then compose up
             # WITHOUT --build (heal is not a build) and re-open the join door if
             # closed. Hulls rise by their own unless-stopped policy, and the
             # worker's boot replant tends the rest from the shipyard ledger —
             # down.json's dark words honored (chad, charlene, the probe grave).
             # The rig-level word outranks the healer (2026-08-28, the morning
             # stop would not stick): a whole-rig stop is the human's, not a wound.
             [ -f "$RIGDOWN" ] && {
               echo "· the rig rests by the human's word ($(cat "$RIGDOWN")) — not replanting"
               exit 0; }
             if curl -sf -m 4 "http://127.0.0.1:4500/health" >/dev/null 2>&1 \
                && pgrep -f "console_worker.py $FIELD" >/dev/null; then
               echo "· whole — nothing to replant"; exit 0; fi
             if ! docker info >/dev/null 2>&1; then
               echo "· docker is down — opening the Desktop"
               # the REAL app nests inside the wrapper (found live 2026-08-26:
               # after a quit, `open -a Docker` no-ops against the wrapper's
               # ghost while the inner Desktop stays down) — open the inner
               # app first, the wrapper only as a fallback
               open "/Applications/Docker.app/Contents/MacOS/Docker Desktop.app" 2>/dev/null \
                 || open -a Docker 2>/dev/null || true
               for i in $(seq 75); do
                 docker info >/dev/null 2>&1 && break
                 # a Desktop still tearing down swallows the first open — knock
                 # again mid-wait until the inner app's processes stand; the VM
                 # engine itself can take a couple of minutes after that
                 pgrep -f "Docker Desktop.app" >/dev/null \
                   || open "/Applications/Docker.app/Contents/MacOS/Docker Desktop.app" 2>/dev/null || true
                 sleep 4
               done
             fi
             docker info >/dev/null 2>&1 || {
               echo "· docker never rose — replant refused"
               # the stuck-Desktop reflex (found live 2026-08-26): a half-quit
               # can leave the UI standing with a backend that never starts its
               # VM — every later knock then no-ops against the standing ghost.
               # Clear it, so the NEXT replant tick opens clean.
               if pgrep -f "Docker Desktop.app" >/dev/null; then
                 echo "· a stuck Desktop stands without its engine — clearing it for the next tick"
                 pkill -f "Docker Desktop" 2>/dev/null || true
                 pkill -f "com.docker.backend" 2>/dev/null || true
               fi
               exit 1; }
             $COMPOSE up -d 2>&1 | tail -2
             sleep 3
             pgrep -f "console_worker.py $FIELD" >/dev/null || joindoor
             echo "· replanted $(date '+%Y-%m-%d %H:%M:%S') — the dark words stay dark"
             "$0" old status ;;
    window)  joindoor; (cd "$CONF" && uv run python demo_open_window.py "$FIELD" 4500) ;;
    agent)   flavor="${2:-01-prototype}"; mode="${3:---once}"
             case "$flavor" in 1|01|prototype) d=01-prototype;; 2|02|langgraph) d=02-langgraph;;
               3|03|sentinel|security) d=03-agentfield-sentinel;; *) d="$flavor";; esac
             echo "· running $d against :$FIELD ($mode)"
             (cd "$ROOT/agents/flavors/$d" && \
               uv run --with pyyaml --with langgraph --with cryptography \
                 python run.py --field "http://127.0.0.1:$FIELD" "$mode") ;;
    *) echo "usage: scripts/dev.sh old start|stop|restart|replant|status|logs|window|clean|agent [flavor] [--once|--forever]" ;;
  esac
}

case "${1:-}" in
  up)      # compose recreates a box whose config hash drifted (seen 2026-09-22: ground + invoke
           # recreated, events kept); a RECREATE carries the anonymous volumes over — verified:
           # 16k outbox rows from 2026-09-17 still there — only `down -v`/`rm` would drop them.
           # A NAMED volume for the ground would make this a law instead of a behaviour (JB's call).
           echo "· the spine rig rises (ground · invoke · events)"
           $RIG up -d 2>&1 | tail -3
           if wait_healthy; then echo "· all three rails healthy"; else echo "· NOT all healthy after 3 min — see below and \`logs\`"; fi
           new_status ;;
  down)    [ -n "$(bridge_pid)" ] && bridge_stop
           echo "· the rig rests (compose stop — the ground's data survives; never down -v)"
           $RIG stop 2>&1 | tail -3
           rig_health ;;
  status)  new_status ;;
  logs)    $RIG logs -f --tail 40 ;;
  bridge)  case "${2:-}" in stop) bridge_stop ;; ""|start) bridge_light ;;
             *) echo "usage: scripts/dev.sh bridge [stop]"; exit 2 ;; esac ;;
  shadow)  case "${2:-}" in stop) shadow_stop ;; ""|start) shadow_light ;;   # P7 sp3: the Rust bridge on :4601
             *) echo "usage: scripts/dev.sh shadow [stop]"; exit 2 ;; esac ;;
  suite)   pid=$(bridge_pid)
           [ -n "$pid" ] && { echo "· a Bridge is lit on :$BRIDGE_PORT (pid $pid) — the stale-rig law: a live rig poisons every test dispatcher. \`scripts/dev.sh bridge stop\` first."; exit 1; }
           ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first (the suite needs the rails)"; exit 1; }
           shift; args=("$@"); [ ${#args[@]} -eq 0 ] && args=(tests)
           echo "· the spine suite → $SUITE_LOG  (pytest -q ${args[*]})"
           rc=0; (cd "$SPINE" && uv run --quiet pytest -q "${args[@]}" >"$SUITE_LOG" 2>&1) || rc=$?
           tail -12 "$SUITE_LOG"
           [ "$rc" = 0 ] && echo "· suite green" || echo "· suite NOT green (pytest exit $rc) — read $SUITE_LOG"
           exit $rc ;;
  rust)    if [ "${2:-}" = rails ]; then
             ground_up || echo "· the ground is dark on :5433 — the rail tests will skip BY NAME (run scripts/dev.sh up)"
             [ -n "$(bridge_pid)" ] && echo "· a Bridge is lit on :$BRIDGE_PORT — the shadow proof will refuse to run beside it"
             echo "· the rail tests on the rig → $RUST_LOG"
             rc=0; (cd "$PLANE" && cargo test -p orreth-spine --features rails --test rails -- --nocapture --test-threads=2 >"$RUST_LOG" 2>&1) || rc=$?
             grep -E "^rails · |skipped by name|refuses to run|^test result|panicked" "$RUST_LOG" || tail -20 "$RUST_LOG"
             exit $rc
           fi
           echo "· cargo test, the whole plane (hermetic: no rig needed) → $RUST_LOG"
           rc=0; (cd "$PLANE" && cargo test >"$RUST_LOG" 2>&1) || rc=$?
           grep -E "^test result|^error|FAILED|panicked" "$RUST_LOG" | sort | uniq -c | sed 's/^/  /'
           (cd "$PLANE" && cargo test -p orreth-spine --test conformance -- --nocapture 2>/dev/null | grep "conformance —" | sed 's/^/  /') || true
           [ "$rc" = 0 ] && echo "· plane green" || echo "· plane NOT green (cargo exit $rc) — read $RUST_LOG"
           exit $rc ;;
  walk)    "$0" up; bridge_light
           echo "· open the glass: http://127.0.0.1:$BRIDGE_PORT/" ;;
  old)     shift; old_rig "$@" ;;
  replant) old_rig replant ;;     # the launchd keeper's word — unchanged, at the top level
  *) echo "usage: scripts/dev.sh up|down|status|logs|bridge [stop]|shadow [stop]|suite [pytest args]|rust [rails]|walk|old <verb>|replant" ;;
esac
