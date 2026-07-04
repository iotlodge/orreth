#!/usr/bin/env bash
# Orreth dev universe — JB's one-command start/stop for feedback sessions.
#   scripts/dev.sh start     stand up a 3-tier local tree (universe 4700 · eco 4701 · field 4702)
#   scripts/dev.sh window    seed a biography and open the Window in your browser
#   scripts/dev.sh status    health of all three tiers
#   scripts/dev.sh stop      bring it all down          restart = stop + start
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN=/tmp/orreth-dev; mkdir -p "$RUN"
PLANE="$ROOT/backend/plane"; CONF="$ROOT/backend/conformance"

start() {
  echo "· building orrethd…"
  (cd "$PLANE" && cargo build -p orrethd --quiet)
  ROOT_PUB=$(cd "$CONF" && uv run python smoke_orrethd.py root-pub)
  echo "· root: ${ROOT_PUB:0:20}…"
  BIN="$PLANE/target/debug/orrethd"; PROF="$PLANE/profiles"; REG="$PLANE/profiles/model-registry.json"
  "$BIN" --profile "$PROF/demo-universe.json" --port 4700 --root-pub "$ROOT_PUB" \
      --store-dir "$RUN/apex-bodies"  --models "$REG" >"$RUN/universe.log" 2>&1 &
  sleep 1
  "$BIN" --profile "$PROF/demo-eco.json"      --port 4701 --root-pub "$ROOT_PUB" \
      --parent http://127.0.0.1:4700 --store-dir "$RUN/eco-bodies" --models "$REG" >"$RUN/eco.log" 2>&1 &
  sleep 1
  "$BIN" --profile "$PROF/demo-field.json"    --port 4702 --root-pub "$ROOT_PUB" \
      --parent http://127.0.0.1:4701 --store-dir "$RUN/field-bodies" --models "$REG" >"$RUN/field.log" 2>&1 &
  sleep 1
  status
  echo "· logs in $RUN/ — next: scripts/dev.sh window"
}

stop()   { pkill -f "orrethd --profile" 2>/dev/null && echo "· tree stopped" || echo "· nothing running"; }
status() { for p in 4700 4701 4702; do
             printf "  :%s  " "$p"; curl -sf "http://127.0.0.1:$p/health" || echo "dark"; echo; done; }
window() { (cd "$CONF" && uv run python demo_open_window.py 4702 4700); }

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  restart) stop; sleep 1; start ;;
  status) status ;;
  window) window ;;
  *) echo "usage: scripts/dev.sh start|stop|restart|status|window" ;;
esac
