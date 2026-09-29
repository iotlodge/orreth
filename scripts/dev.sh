#!/usr/bin/env bash
# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: `shadow` seats the crew when it stands alone · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: `cell <name>` — a second universe on its own database and role · 2026-09-25
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp2: the Rust kernel `orrethd` is THE door on :4600 (`kernel`),
#          the Python Bridge is the `reference` on :4601, the old world's rig (`old` · `replant`) retired to the tag · 2026-09-29
#
# Orreth dev rig — JB's one-command feedback rig, DOCKER-first (canon 0002).
#   scripts/dev.sh up            the rig rises: ground (Postgres :5433) · invoke (RabbitMQ :5672 / :15672) ·
#                                events (Kafka :9092) · gateway (LiteLLM :4604); waits until all four are healthy
#   scripts/dev.sh down          the rig rests: compose STOP — never `down -v`; the ground's data survives
#   scripts/dev.sh status        compose ps · the kernel on :4600 · the reference on :4601 · the cells
#   scripts/dev.sh logs          follow the rig's logs
#   scripts/dev.sh kernel        light THE KERNEL — `orrethd` (Rust, orreth-spine) on :4600, a release build: it seats
#                                the crew as processes it governs (kill one: it comes back as the same self; three deaths
#                                in five minutes: it parks and says so); beside a lit reference it seats NONE (SPINE_BODIES
#                                honours an explicit word); log ~/.orreth/tmp/kernel.log, pid printed
#   scripts/dev.sh kernel stop   bring the kernel down whole (SIGINT — every body with it); confirms :4600 empty
#   scripts/dev.sh reference     light the PYTHON REFERENCE (the Bridge, `orreth_spine.glass`) on :4601 — the same ground,
#                                the same page; alone it seats the crew in-process (SPINE_MASTERS · the gateway on :4604
#                                from the environment / .env); log ~/.orreth/tmp/reference.log, pid printed
#   scripts/dev.sh reference stop   bring the reference down cleanly (SIGINT — it stops whole); confirms :4601 empty
#   scripts/dev.sh cell <name> [port]   P7 sp7: light a CELL — a second universe (u:<name>) with its OWN database
#                                (spine_<name>) and role (cell_<name>, reaching no other database), its own benches and
#                                topics (namespace <name>), its own kernel self and bodies' seeds (~/.orreth/cells/<name>),
#                                on :<port> (default 4601 + the count of cells lit, so the first is :4602); names its peers
#                                from SPINE_PEERS ("local=http://127.0.0.1:4600"); log ~/.orreth/tmp/cell-<name>.log
#   scripts/dev.sh cell <name> stop   bring that cell's kernel down whole; `cell <name> seal` only makes its role and database
#   scripts/dev.sh suite [args]  the spine suite to ~/.orreth/tmp/suite.log, tail printed (default: tests;
#                                pass a file or -k to narrow) — REFUSES while a kernel or the reference is lit (the stale-rig law)
#   scripts/dev.sh rust [rails]  cargo test in backend/plane (the whole workspace, hermetic) + the
#                                conformance report line; `rust rails` runs the rail tests on the rig, by name
#   scripts/dev.sh prune [ns]    the brokers' test residue pruned (topics · queues · empty test groups); a namespace to narrow
#   scripts/dev.sh walk          up + kernel — the human's word to open the glass (http://127.0.0.1:4600)
#   scripts/dev.sh replant       the OLD world's keeper's word (com.orreth.replant): nothing to replant here any more —
#                                says how to unload the keeper; the old rig lives at the tag main-v0.72-old-world
#
# HOUSE LAWS
#  · NEVER PIPE A WORKER-SPAWNING VERB — kernel · reference · walk · cell:
#    a pipe holds the spawned worker's stdout open and the verb never returns.
#  · The rig's `down` is compose stop and nothing more — the ground's volume is the universe's memory,
#    so `down -v` is never spoken here.
#  · DOCKER-RECYCLE: when compose wedges (a half-quit Desktop, a ghost engine), quit Docker Desktop whole and
#    open it again; ~/.orreth/tmp/replant.log is the OLD keeper's diary — we say whether it exists, never parse it.
#  · THE STALE-RIG LAW (2026-09-17 · 2026-09-25): a kernel older than the code on disk poisons every test
#    dispatcher, and a lit kernel on the SAME ground relays the suite's outbox rows to ITS topics — `suite`
#    refuses while :4600 or :4601 is held; relight (`kernel` · `reference`) after every code change.
#  · THE PORTS: 5433 · 5672 · 15672 · 9092 (the rig) · 4604 (the gateway) · 4600 (the kernel) · 4601 (the reference) ·
#    4602+ (the cells). The old world's 4500–4502 and 5432 are nobody's here.
set -euo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
# docker compose needs a WRITABLE temp dir; macOS fallbacks are sometimes root-owned
export TMPDIR="$HOME/.orreth/tmp"; mkdir -p "$TMPDIR"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPINE="$ROOT/spine"; PLANE="$ROOT/backend/plane"
RIG="docker compose -f $SPINE/compose.yaml"
RIG_BOXES="orreth-spine-ground orreth-spine-invoke orreth-spine-events orreth-spine-gateway"   # compose.yaml's container names
GATEWAY_PORT=4604   # P6.5 sp3: THE GATEWAY (LiteLLM), run and managed by Orreth — every mind thinks through it
KERNEL_PORT=4600; KERNEL_LOG="$TMPDIR/kernel.log"       # re-base sp2: THE door — orrethd, the Rust kernel
REF_PORT=4601;    REF_LOG="$TMPDIR/reference.log"       # the Python reference (the Bridge), beside or alone
SUITE_LOG="$TMPDIR/suite.log"; RUST_LOG="$TMPDIR/rust.log"
# the perf cure (2026-09-29): the walk kernel is a RELEASE build — every door number JB reads is the real one
# (a debug build ran 50–100× its own query cost); SPINE_PROFILE=debug keeps the quick build for a code loop
PROFILE_DIR="${SPINE_PROFILE:-release}"; CARGO_PROFILE=""; [ "$PROFILE_DIR" = release ] && CARGO_PROFILE="--release"

kernel_pid() { lsof -nP -iTCP:$KERNEL_PORT -sTCP:LISTEN -t 2>/dev/null | head -1 || true; }
ref_pid()    { lsof -nP -iTCP:$REF_PORT -sTCP:LISTEN -t 2>/dev/null | head -1 || true; }
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
    [ "$n" = 4 ] && return 0
    sleep 2
  done
  return 1
}

load_env() {  # keys live in .env and the process env only, never in any record (the env-secrets law)
  [ -f "$ROOT/.env" ] && { set -a; . "$ROOT/.env"; set +a; }
  # W57 (walk #15): every clock a human reads is the HUMAN'S — the machine's own zone unless a dial says otherwise
  # (the kernel's default, America/Denver, read 12:28 beside a Mac on America/Phoenix that read 11:28)
  if [ -z "${SPINE_HUMAN_ZONE:-}" ]; then
    z=$(readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||'); [ -n "$z" ] && export SPINE_HUMAN_ZONE="$z"
  fi
  true
}

gateway_db() {  # P6.5 sp3: the gateway keeps its ledger in its own database on the ground — made once, kept forever
  have=$(docker exec orreth-spine-ground psql -U orreth -d spine -tAc "SELECT 1 FROM pg_database WHERE datname='litellm'" 2>/dev/null || true)
  [ "$have" = 1 ] && return 0
  docker exec orreth-spine-ground createdb -U orreth litellm >/dev/null 2>&1 && echo "· the gateway's ledger database made on the ground (litellm)"
}

gateway_up() { curl -sf -m 3 "http://127.0.0.1:$GATEWAY_PORT/health/liveliness" >/dev/null 2>&1; }

build_kernel() {  # one build for the kernel and the cells: orrethd, feature bridge, the chosen profile
  echo "· building orrethd (cargo, feature bridge, $PROFILE_DIR) …"
  (cd "$PLANE" && cargo build --quiet -p orreth-spine --features bridge --bin orrethd $CARGO_PROFILE) || { echo "· the build refused — read the errors above"; return 1; }
}

stop_whole() {  # $1 the pid · $2 the port · $3 the name: SIGINT (Ctrl+C's law — it stops whole), then SIGTERM, then the human
  pid="$1"; port="$2"; name="$3"
  kill -INT "$pid" 2>/dev/null || true
  for i in $(seq 120); do [ -z "$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | head -1)" ] && break; sleep 0.5; done   # a whole stop can take ~30 s (consumers leave their groups)
  if [ -n "$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | head -1)" ]; then
    echo "· $name did not stop whole in 60 s — terminating (SIGTERM; its consumer groups may hold ghosts for a while)"; kill -TERM "$pid" 2>/dev/null || true
    for i in $(seq 20); do [ -z "$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | head -1)" ] && break; sleep 0.5; done
  fi
  [ -n "$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | head -1)" ] && { echo "· :$port is STILL held — kill it by hand"; return 1; }
  echo "· $name is dark — :$port empty"
}

kernel_light() {  # re-base sp2: THE KERNEL — orrethd on :4600, the crew its own processes
  pid=$(kernel_pid)
  [ -n "$pid" ] && { echo "· the kernel is already lit on :$KERNEL_PORT (pid $pid) — \`kernel stop\` first to relight"; return 0; }
  ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first"; return 1; }
  load_env
  build_kernel || return 1
  # P7 sp6: whose bodies serve? Beside a lit reference the kernel seats NONE (one crew, never doubled);
  # alone it seats the crew as processes it governs (SPINE_BODIES honours an explicit setting).
  bodies="${SPINE_BODIES:-}"
  if [ -z "$bodies" ]; then [ -n "$(ref_pid)" ] && bodies=none || bodies=crew; fi
  mind="a fake mind (the gateway on :$GATEWAY_PORT is dark — run scripts/dev.sh up)"; gateway_up && mind="every mind through the gateway on :$GATEWAY_PORT"
  (cd "$PLANE" && SPINE_BRIDGE_PORT=$KERNEL_PORT SPINE_BODIES="$bodies" nohup "$PLANE/target/$PROFILE_DIR/orrethd" >"$KERNEL_LOG" 2>&1 &)
  for i in $(seq 60); do [ -n "$(kernel_pid)" ] && break; sleep 0.5; done
  pid=$(kernel_pid)
  [ -z "$pid" ] && { echo "· the kernel never took :$KERNEL_PORT in 30 s — read $KERNEL_LOG"; tail -5 "$KERNEL_LOG"; return 1; }
  echo "· the kernel is lit: http://127.0.0.1:$KERNEL_PORT/  (orrethd · pid $pid · bodies: $bodies · $mind) — log: $KERNEL_LOG"
  [ "$bodies" = crew ] && echo "· the crew is the kernel's: every seat a process it spawns and governs (kill one: it comes back as the same self; kill it three times in five minutes: it parks and says so)" || echo "· the kernel seats no bodies — the reference's serve (SPINE_BODIES=none)"
}

kernel_stop() {
  pid=$(kernel_pid)
  [ -z "$pid" ] && { echo "· no kernel holds :$KERNEL_PORT — nothing to stop"; return 0; }
  echo "· asking the kernel (pid $pid) to stop whole (SIGINT — every body with it, the benches left clean)"
  stop_whole "$pid" "$KERNEL_PORT" "the kernel"
}

reference_light() {  # the Python reference — the Bridge (orreth_spine.glass) on :4601
  pid=$(ref_pid)
  [ -n "$pid" ] && { echo "· the reference is already lit on :$REF_PORT (pid $pid) — \`reference stop\` first to relight"; return 0; }
  ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first"; return 1; }
  load_env
  masters="${SPINE_MASTERS:-}"; n=0; [ -n "$masters" ] && n=$(echo "$masters" | tr ',' '\n' | grep -c . || true)
  mind="a fake mind (the gateway on :$GATEWAY_PORT is dark — run scripts/dev.sh up)"; gateway_up && mind="every mind through the gateway on :$GATEWAY_PORT"
  # nohup + & + a subshell: the worker outlives this verb; its stdout is the log, never our pipe.
  # A background child of a non-interactive shell inherits SIGINT IGNORED (POSIX), and Python
  # then never installs KeyboardInterrupt — so `reference stop`'s SIGINT would fall on deaf ears
  # (found live 2026-09-22: 60 s of silence, then a SIGTERM). The shim restores the default
  # SIGINT handler before the Bridge runs, so Ctrl+C's law holds: it stops WHOLE. -u: the log
  # tells the truth as it happens (block-buffered, it once showed nothing until the kill).
  (cd "$SPINE" && SPINE_BRIDGE_PORT=$REF_PORT nohup uv run --quiet python -u -c \
     "import signal, runpy; signal.signal(signal.SIGINT, signal.default_int_handler); runpy.run_module('orreth_spine.glass', run_name='__main__')" \
     >"$REF_LOG" 2>&1 &)
  for i in $(seq 120); do [ -n "$(ref_pid)" ] && break; sleep 0.5; done
  pid=$(ref_pid)
  [ -z "$pid" ] && { echo "· the reference never took :$REF_PORT in 60 s — read $REF_LOG"; tail -5 "$REF_LOG"; return 1; }
  echo "· the reference is lit: http://127.0.0.1:$REF_PORT/  (the Python Bridge · pid $pid · $mind · masters: $n named) — log: $REF_LOG"
  [ -n "$(kernel_pid)" ] && echo "· the kernel on :$KERNEL_PORT was lit first and seats the crew — the reference's own residents serve beside them from the same benches (one crew per ground is the law: relight the kernel with SPINE_BODIES=none, or run one of the two)"
  true
}

reference_stop() {
  pid=$(ref_pid)
  [ -z "$pid" ] && { echo "· no reference holds :$REF_PORT — nothing to stop"; return 0; }
  echo "· asking the reference (pid $pid) to stop whole (SIGINT — every thread joined, the benches left clean)"
  stop_whole "$pid" "$REF_PORT" "the reference"
}

cell_seal() {  # P7 sp7: a cell's ground — its own database and a role that reaches no other (M8's isolation, the dev profile)
  name="$1"; db="spine_$name"; role="cell_$name"; pw="cell-$name-dev"
  PSQL="docker exec orreth-spine-ground psql -U orreth -d spine -tAqc"
  have=$($PSQL "SELECT 1 FROM pg_roles WHERE rolname='$role'" 2>/dev/null || true)
  [ "$have" = 1 ] || { $PSQL "CREATE ROLE $role LOGIN PASSWORD '$pw'" >/dev/null && echo "· the role $role made"; }
  have=$($PSQL "SELECT 1 FROM pg_database WHERE datname='$db'" 2>/dev/null || true)
  [ "$have" = 1 ] || { docker exec orreth-spine-ground createdb -U orreth -O "$role" "$db" >/dev/null && echo "· the database $db made, owned by $role"; }
  # the seal: PUBLIC may enter no database of ours; each cell's role enters only its own (the owner role, orreth, enters all — the dev profile, said by the tenth check)
  for d in spine litellm postgres "$db"; do $PSQL "REVOKE CONNECT ON DATABASE $d FROM PUBLIC" >/dev/null 2>&1 || true; done
  $PSQL "GRANT CONNECT ON DATABASE $db TO $role" >/dev/null
  $PSQL "REVOKE CONNECT ON DATABASE $db FROM $role; GRANT CONNECT ON DATABASE $db TO $role" >/dev/null   # idempotent
  echo "· cell $name is sealed: the role $role reaches only $db"
}

cell_home() { echo "$HOME/.orreth/cells/$1"; }
cell_pid()  { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1 || true; }
cell_port() { # the port a lit cell holds, remembered beside its seeds (a number, or nothing)
  [ -f "$(cell_home "$1")/port" ] && grep -E '^[0-9]+$' "$(cell_home "$1")/port" || true; }

cell_light() {  # P7 sp7: a second universe beside u:dev — its own kernel on its own database, sealed
  name="$1"; port="${2:-}"
  case "$port" in ""|*[!0-9]*) [ -n "$port" ] && { echo "· a port is a number (got '$port') — scripts/dev.sh cell $name [port|stop|seal]"; return 2; } ;; esac   # W59: never write a word into the port file
  case "$name" in local|"") echo "· 'local' is the first cell (u:dev on :$KERNEL_PORT) — light it with scripts/dev.sh kernel"; return 2 ;; esac
  echo "$name" | grep -Eq '^[a-z0-9_-]+$' || { echo "· a cell's name is lower-case letters, digits, - and _"; return 2; }
  ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first"; return 1; }
  home=$(cell_home "$name"); mkdir -p "$home"
  if [ -z "$port" ]; then port=$(cell_port "$name"); fi
  if [ -z "$port" ]; then n=$(ls -d "$HOME"/.orreth/cells/*/ 2>/dev/null | wc -l | tr -d ' '); port=$((REF_PORT + n)); fi   # the first cell :4602
  pid=$(cell_pid "$port")
  [ -n "$pid" ] && { echo "· :$port is already held (pid $pid) — \`cell $name stop\` first, or name another port"; return 0; }
  cell_seal "$name"
  load_env
  build_kernel || return 1
  echo "$port" >"$home/port"
  log="$TMPDIR/cell-$name.log"
  peers="${SPINE_PEERS:-local=http://127.0.0.1:$KERNEL_PORT}"
  (cd "$PLANE" && ORRETH_HOME="$home" SPINE_PG="postgresql://cell_$name:cell-$name-dev@localhost:5433/spine_$name" \
     SPINE_SCOPE="u:$name" SPINE_CELL="$name" SPINE_QUEUE_NS="$name" SPINE_BRIDGE_PORT="$port" SPINE_BODIES=crew \
     SPINE_PEERS="$peers" nohup "$PLANE/target/$PROFILE_DIR/orrethd" >"$log" 2>&1 &)
  for i in $(seq 60); do [ -n "$(cell_pid "$port")" ] && break; sleep 0.5; done
  pid=$(cell_pid "$port")
  [ -z "$pid" ] && { echo "· cell $name never took :$port in 30 s — read $log"; tail -5 "$log"; return 1; }
  echo "· cell $name is lit: http://127.0.0.1:$port/  (u:$name on spine_$name as cell_$name · benches and topics '$name' · seeds in $home · peers: $peers · pid $pid) — log: $log"
  echo "· say \"librarian@$name, hello\" on :$KERNEL_PORT to route an ask home to this cell; stop it with scripts/dev.sh cell $name stop"
}

cell_stop() {
  name="$1"; port=$(cell_port "$name")
  [ -z "$port" ] && { echo "· no cell named $name was ever lit here (no $(cell_home "$name")/port)"; return 0; }
  pid=$(cell_pid "$port")
  [ -z "$pid" ] && { echo "· cell $name is dark — :$port empty"; return 0; }
  kill -INT "$pid" 2>/dev/null || true       # Ctrl+C's law: it stops whole, its bodies with it
  for i in $(seq 60); do [ -z "$(cell_pid "$port")" ] && break; sleep 0.5; done
  [ -n "$(cell_pid "$port")" ] && { kill "$pid" 2>/dev/null || true; for i in $(seq 20); do [ -z "$(cell_pid "$port")" ] && break; sleep 0.5; done; }
  [ -n "$(cell_pid "$port")" ] && { echo "· :$port is STILL held by $(cell_pid "$port") — kill it by hand"; return 1; }
  echo "· cell $name is dark — :$port empty"
}

rig_status() {
  echo "the spine rig (spine/compose.yaml):"
  $RIG ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "  (compose is not answering — is Docker up?)"
  rig_health
  pid=$(kernel_pid)
  if [ -n "$pid" ]; then
    echo "  kernel: LIT on :$KERNEL_PORT (orrethd · pid $pid) — log $KERNEL_LOG"
    h=$(curl -sf -m 4 "http://127.0.0.1:$KERNEL_PORT/health" 2>/dev/null || true)
    [ -n "$h" ] && echo "  health: $(echo "$h" | head -c 300)" || echo "  health: no answer on /health"
  else
    echo "  kernel: dark — scripts/dev.sh kernel (or walk) lights orrethd on :$KERNEL_PORT"
  fi
  rpid=$(ref_pid)
  [ -n "$rpid" ] && echo "  reference: the Python Bridge LIT on :$REF_PORT (pid $rpid) — log $REF_LOG" \
                 || echo "  reference: dark — scripts/dev.sh reference lights the Python Bridge on :$REF_PORT"
  for d in "$HOME"/.orreth/cells/*/; do
    [ -d "$d" ] || continue; n=$(basename "$d"); p=$(cell_port "$n"); [ -n "$p" ] || continue
    [ -n "$(cell_pid "$p")" ] && echo "  cell $n: LIT on :$p — log $TMPDIR/cell-$n.log" || echo "  cell $n: dark (:$p)"
  done
  [ -f "$TMPDIR/replant.log" ] && echo "  the old keeper's diary: $TMPDIR/replant.log exists (the old world's; not parsed)" || true
}

case "${1:-}" in
  up)      # compose recreates a box whose config hash drifted (seen 2026-09-22: ground + invoke
           # recreated, events kept); a RECREATE carries the named volume over (P6.5 sp1: the ground's
           # data lives on `orreth-spine-ground`) — only `down -v`/`rm` would drop it.
           # P6.5 sp3: the gateway rises LAST — its ledger database must stand on the ground first,
           # and its provider keys ride in from THIS shell's environment (load_env; never a file of ours)
           load_env
           echo "· the spine rig rises (ground · invoke · events · gateway)"
           $RIG up -d ground invoke events 2>&1 | tail -3
           for i in $(seq 60); do [ "$(docker inspect -f '{{.State.Health.Status}}' orreth-spine-ground 2>/dev/null)" = healthy ] && break; sleep 2; done
           gateway_db
           $RIG up -d gateway 2>&1 | tail -2
           if wait_healthy; then echo "· all four boxes healthy"; else echo "· NOT all healthy after 3 min — see below and \`logs\`"; fi
           rig_status ;;
  down)    [ -n "$(kernel_pid)" ] && kernel_stop
           [ -n "$(ref_pid)" ] && reference_stop
           echo "· the rig rests (compose stop — the ground's data survives; never down -v)"
           $RIG stop 2>&1 | tail -3
           rig_health ;;
  status)  rig_status ;;
  logs)    $RIG logs -f --tail 40 ;;
  kernel)  case "${2:-}" in stop) kernel_stop ;; ""|start) kernel_light ;;
             *) echo "usage: scripts/dev.sh kernel [stop]"; exit 2 ;; esac ;;
  reference) case "${2:-}" in stop) reference_stop ;; ""|start) reference_light ;;
             *) echo "usage: scripts/dev.sh reference [stop]"; exit 2 ;; esac ;;
  bridge|shadow)   # the P7 names, kept as signposts for a hand that remembers them
           echo "· \`$1\` was the P7 rig's word — since re-base sp2 the Rust kernel is THE door: scripts/dev.sh kernel [stop] (:4600); the Python Bridge is scripts/dev.sh reference [stop] (:4601)"; exit 2 ;;
  cell)    case "${3:-}" in stop) cell_stop "${2:-}" ;; seal) cell_seal "${2:-}" ;;   # P7 sp7: a second universe, sealed
             ""|start) cell_light "${2:-}" ;; *) cell_light "${2:-}" "${3:-}" ;; esac ;;
  suite)   pid=$(kernel_pid)   # the stale-rig law: a lit kernel on the SAME ground relays the suite's rows to ITS topics (found 2026-09-25)
           [ -n "$pid" ] && { echo "· the kernel is lit on :$KERNEL_PORT (pid $pid) — the stale-rig law: a live kernel poisons every test dispatcher. \`scripts/dev.sh kernel stop\` first."; exit 1; }
           rpid=$(ref_pid)
           [ -n "$rpid" ] && { echo "· the reference is lit on :$REF_PORT (pid $rpid) — the stale-rig law: a live rig poisons every test dispatcher. \`scripts/dev.sh reference stop\` first."; exit 1; }
           ground_up || { echo "· the ground is dark on :5433 — run scripts/dev.sh up first (the suite needs the rails)"; exit 1; }
           shift; args=("$@"); [ ${#args[@]} -eq 0 ] && args=(tests)
           echo "· the spine suite → $SUITE_LOG  (pytest -q ${args[*]})"
           rc=0; (cd "$SPINE" && uv run --quiet pytest -q "${args[@]}" >"$SUITE_LOG" 2>&1) || rc=$?
           tail -12 "$SUITE_LOG"
           [ "$rc" = 0 ] && echo "· suite green" || echo "· suite NOT green (pytest exit $rc) — read $SUITE_LOG"
           exit $rc ;;
  rust)    if [ "${2:-}" = rails ]; then
             ground_up || echo "· the ground is dark on :5433 — the rail tests will skip BY NAME (run scripts/dev.sh up)"
             [ -n "$(kernel_pid)" ] || [ -n "$(ref_pid)" ] && echo "· a kernel or the reference is lit — the shadow proof will refuse to run beside it"
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
  prune)   # the perf cure (2026-09-29): the brokers' TEST RESIDUE — every test-shaped namespace's topics and queues,
           # the empty test-prefixed groups; a person's namespaces (two · perf · the dev world) are never touched
           ground_up || { echo "· the rig is dark — run scripts/dev.sh up first"; exit 1; }
           (cd "$SPINE" && uv run --quiet python -m orreth_spine.prune "${2:-}") ;;
  walk)    "$0" up; kernel_light
           echo "· open the glass: http://127.0.0.1:$KERNEL_PORT/" ;;
  replant) # the OLD world's launchd keeper (com.orreth.replant) still says this word every five minutes on a Mac
           # that loaded it; the old rig it healed rests at the tag main-v0.72-old-world. Nothing to replant: say so, exit clean.
           echo "· the old world rests at the tag main-v0.72-old-world — nothing to replant; unload the keeper with:"
           echo "    launchctl bootout gui/\$(id -u)/com.orreth.replant   (the plist lived at infrastructure/com.orreth.replant.plist, now at the tag)"
           exit 0 ;;
  old)     echo "· the old world's rig (universe :4500 · eco :4501 · field :4502) rests at the tag main-v0.72-old-world — \`git switch old-world/main-v0.72\` to run it"; exit 2 ;;
  stop)    # W55 (walk #15): "stop two" / "two stop" — a hand reaches for these; they mean `cell two stop`
           [ -n "${2:-}" ] && [ -f "$(cell_home "$2")/port" ] && { cell_stop "$2"; exit $?; }
           echo "usage: scripts/dev.sh cell <name> stop   (cells lit here: $(ls "$HOME"/.orreth/cells 2>/dev/null | tr '\n' ' '))"; exit 2 ;;
  *) if [ -n "${1:-}" ] && [ -f "$(cell_home "$1")/port" ]; then      # a cell's bare name: `two` lights it, `two stop` darkens it
       case "${2:-}" in stop) cell_stop "$1" ;; ""|start) cell_light "$1" ;; *) echo "usage: scripts/dev.sh cell $1 [port|stop|seal]"; exit 2 ;; esac
     else
       echo "usage: scripts/dev.sh up|down|status|logs|kernel [stop]|reference [stop]|cell <name> [port|stop|seal]|suite [pytest args]|rust [rails]|prune [ns]|walk|replant"
     fi ;;
esac
