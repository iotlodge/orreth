#!/usr/bin/env bash
# Orreth dev universe — JB's one-command feedback rig (DOCKER-first).
#   scripts/dev.sh start     compose up the tree + open becky's join door (agents can join)
#   scripts/dev.sh window    seed a biography and open the Console (field :4502)
#   scripts/dev.sh status    container + tier health + join door
#   scripts/dev.sh stop      compose down                     restart = down + up --build
#   scripts/dev.sh agent [flavor] [--once|--forever]   run a lifeforce agent into the field
set -euo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
# docker compose needs a WRITABLE temp dir; macOS fallbacks are sometimes root-owned
export TMPDIR="$HOME/.orreth/tmp"; mkdir -p "$TMPDIR"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$ROOT/backend/conformance"; COMPOSE="docker compose -f $ROOT/infrastructure/compose.yaml"
FIELD=4502

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
  (cd "$CONF" && ORRETH_JOIN_LEASE_TOKENS="${ORRETH_JOIN_LEASE_TOKENS:-250000}"     nohup uv run python console_worker.py "$FIELD" >"$TMPDIR/worker.log" 2>&1 &)
  echo "· becky's join door open on :$FIELD — agents may join; log: $TMPDIR/worker.log"
}

deskcrew() {  # 0054: the Trading desk's standing crew — the data stall + charles tending
  pkill -f "tradingdata_server.py" 2>/dev/null || true
  pkill -f "05-desk/run.py" 2>/dev/null || true; sleep 0.3
  (cd "$CONF" && nohup uv run --with yfinance --with pandas     python -u tradingdata_server.py 4570 >"$TMPDIR/tradingdata.log" 2>&1 &)
  (cd "$ROOT" && nohup uv run --with litellm --with cryptography     python -u agents/flavors/05-desk/run.py --tend >"$TMPDIR/charles.log" 2>&1 &)
  echo "· the desk crew stands: stall :4570 + charles --tend (logs: $TMPDIR/{tradingdata,charles}.log)"
  echo "  ⚠ charles waits at his join gate after every start — welcome him in the Inbox (f:charles)"
}

case "${1:-}" in
  start)   rootpub; $COMPOSE up --build -d
           docker image prune -f >/dev/null 2>&1 || true   # superseded layers die quietly (the jsbarth disk fire's lesson)
           sleep 3; joindoor; deskcrew; "$0" status ;;
  stop)    pkill -f console_worker.py 2>/dev/null || true
           pkill -f tradingdata_server.py 2>/dev/null || true
           pkill -f "05-desk/run.py" 2>/dev/null || true
           # dynamic hulls (the Shipyard) ride the rig's network — down together;
           # the worker's replant relaunches them from ~/.orreth/shipyard on start
           docker ps -aq --filter name=orreth-dyn- --filter name=orreth-field- \
             | xargs docker rm -f 2>/dev/null || true
           $COMPOSE down ;;
  restart) "$0" stop; rootpub; $COMPOSE up --build -d
           docker image prune -f >/dev/null 2>&1 || true
           sleep 3; joindoor; deskcrew; "$0" status ;;
  clean)   # deliberate deep clean (2026-07-30, after the jsbarth 100%-disk fire):
           # dangling images + build cache trimmed to a warm 15GB. NEVER volumes
           # (pg holds the universe's memory) and NEVER -a image prunes here —
           # this laptop hosts other projects whose stopped images would vanish.
           docker image prune -f
           docker builder prune -f --keep-storage=15GB
           docker buildx prune -f --keep-storage=15GB   # Desktop keeps a second builder
           docker system df ;;
  status)  $COMPOSE ps --format '  {{.Name}}\t{{.Status}}' 2>/dev/null || true
           dyn=""; [ -f "$HOME/.orreth/shipyard/floors.json" ] && \
             dyn=$(python3 -c 'import json,sys;print(" ".join(sorted(json.load(open(sys.argv[1])))))' "$HOME/.orreth/shipyard/floors.json" 2>/dev/null)
           for p in 4500 4501 4502 $dyn; do printf "  :%s  " "$p"
             curl -sf "http://127.0.0.1:$p/health" || printf dark; echo; done
           pgrep -f "console_worker.py $FIELD" >/dev/null \
             && echo "  join door: OPEN (:$FIELD)" || echo "  join door: CLOSED — run scripts/dev.sh start"
           pgrep -f "tradingdata_server.py" >/dev/null \
             && echo "  desk stall: SERVING (:4570)" || echo "  desk stall: DARK"
           pgrep -f "05-desk/run.py" >/dev/null \
             && echo "  charles: TENDING (walks at the close; asks anytime)" \
             || echo "  charles: RESTING — run scripts/dev.sh start" ;;
  logs)    $COMPOSE logs -f --tail 40 ;;
  window)  joindoor; (cd "$CONF" && uv run python demo_open_window.py "$FIELD" 4500) ;;
  agent)   flavor="${2:-01-prototype}"; mode="${3:---once}"
           case "$flavor" in 1|01|prototype) d=01-prototype;; 2|02|langgraph) d=02-langgraph;;
             3|03|sentinel|security) d=03-agentfield-sentinel;; *) d="$flavor";; esac
           echo "· running $d against :$FIELD ($mode)"
           (cd "$ROOT/agents/flavors/$d" && \
             uv run --with pyyaml --with langgraph --with cryptography \
               python run.py --field "http://127.0.0.1:$FIELD" "$mode") ;;
  *) echo "usage: scripts/dev.sh start|stop|restart|status|logs|window|clean|agent [flavor] [--once|--forever]" ;;
esac
