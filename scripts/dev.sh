#!/usr/bin/env bash
# Orreth dev universe — JB's one-command feedback rig (DOCKER-first).
#   scripts/dev.sh start     compose up the tree in Docker (pg + universe + eco + field)
#   scripts/dev.sh window    seed a biography and open the Window (field :4502)
#   scripts/dev.sh status    container + tier health          logs: scripts/dev.sh logs
#   scripts/dev.sh stop      compose down                     restart = down + up --build
set -euo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
# docker compose needs a WRITABLE temp dir; macOS fallbacks are sometimes root-owned
export TMPDIR="$HOME/.orreth/tmp"; mkdir -p "$TMPDIR"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$ROOT/backend/conformance"; COMPOSE="docker compose -f $ROOT/infrastructure/compose.yaml"

rootpub() {  # keep the seed and infrastructure/.env in lockstep, always
  RP=$(cd "$CONF" && uv run python smoke_orrethd.py root-pub)
  echo "ORRETH_ROOT_PUB=$RP" > "$ROOT/infrastructure/.env"
  echo "· root: ${RP:0:20}… (env synced)"
}

case "${1:-}" in
  start)   rootpub; $COMPOSE up --build -d; sleep 3; "$0" status ;;
  stop)    pkill -f console_worker.py 2>/dev/null || true; $COMPOSE down ;;
  restart) $COMPOSE down; rootpub; $COMPOSE up --build -d; sleep 3; "$0" status ;;
  status)  $COMPOSE ps --format '  {{.Name}}\t{{.Status}}' 2>/dev/null || true
           for p in 4500 4501 4502; do printf "  :%s  " "$p"
             curl -sf "http://127.0.0.1:$p/health" || printf dark; echo; done ;;
  logs)    $COMPOSE logs -f --tail 40 ;;
  window) pkill -f console_worker.py 2>/dev/null || true
           (cd "$CONF" && nohup uv run python console_worker.py 4502 >"$TMPDIR/worker.log" 2>&1 &)
           echo "· librarian worker started (Ask → memories); log: $TMPDIR/worker.log"
           (cd "$CONF" && uv run python demo_open_window.py 4502 4500) ;;
  *) echo "usage: scripts/dev.sh start|stop|restart|status|logs|window" ;;
esac
