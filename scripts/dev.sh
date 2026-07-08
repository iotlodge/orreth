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
  echo "ORRETH_ROOT_PUB=$RP" > "$ROOT/infrastructure/.env"
  echo "· root: ${RP:0:20}… (env synced)"
}

joindoor() {  # becky answers joins + the librarian answers Asks — the floor's cognition
  pkill -f "console_worker.py $FIELD" 2>/dev/null || true; sleep 0.3
  (cd "$CONF" && nohup uv run python console_worker.py "$FIELD" >"$TMPDIR/worker.log" 2>&1 &)
  echo "· becky's join door open on :$FIELD — agents may join; log: $TMPDIR/worker.log"
}

case "${1:-}" in
  start)   rootpub; $COMPOSE up --build -d; sleep 3; joindoor; "$0" status ;;
  stop)    pkill -f console_worker.py 2>/dev/null || true
           # dynamic hulls (the Shipyard) ride the rig's network — down together;
           # the worker's replant relaunches them from ~/.orreth/shipyard on start
           docker ps -aq --filter name=orreth-dyn- | xargs docker rm -f 2>/dev/null || true
           $COMPOSE down ;;
  restart) "$0" stop; rootpub; $COMPOSE up --build -d; sleep 3; joindoor; "$0" status ;;
  status)  $COMPOSE ps --format '  {{.Name}}\t{{.Status}}' 2>/dev/null || true
           dyn=""; [ -f "$HOME/.orreth/shipyard/floors.json" ] && \
             dyn=$(python3 -c 'import json,sys;print(" ".join(sorted(json.load(open(sys.argv[1])))))' "$HOME/.orreth/shipyard/floors.json" 2>/dev/null)
           for p in 4500 4501 4502 $dyn; do printf "  :%s  " "$p"
             curl -sf "http://127.0.0.1:$p/health" || printf dark; echo; done
           pgrep -f "console_worker.py $FIELD" >/dev/null \
             && echo "  join door: OPEN (:$FIELD)" || echo "  join door: CLOSED — run scripts/dev.sh start" ;;
  logs)    $COMPOSE logs -f --tail 40 ;;
  window)  joindoor; (cd "$CONF" && uv run python demo_open_window.py "$FIELD" 4500) ;;
  agent)   flavor="${2:-01-prototype}"; mode="${3:---once}"
           case "$flavor" in 1|01|prototype) d=01-prototype;; 2|02|langgraph) d=02-langgraph;;
             3|03|sentinel|security) d=03-agentfield-sentinel;; *) d="$flavor";; esac
           echo "· running $d against :$FIELD ($mode)"
           (cd "$ROOT/agents/flavors/$d" && \
             uv run --with pyyaml --with langgraph --with cryptography \
               python run.py --field "http://127.0.0.1:$FIELD" "$mode") ;;
  *) echo "usage: scripts/dev.sh start|stop|restart|status|logs|window|agent [flavor] [--once|--forever]" ;;
esac
