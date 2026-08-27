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
  start)   rootpub; $COMPOSE up --build -d
           docker image prune -f >/dev/null 2>&1 || true   # superseded layers die quietly (the jsbarth disk fire's lesson)
           sleep 3; joindoor; "$0" status ;;
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
           sleep 3; joindoor; "$0" status ;;
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
           "$0" status ;;
  window)  joindoor; (cd "$CONF" && uv run python demo_open_window.py "$FIELD" 4500) ;;
  agent)   flavor="${2:-01-prototype}"; mode="${3:---once}"
           case "$flavor" in 1|01|prototype) d=01-prototype;; 2|02|langgraph) d=02-langgraph;;
             3|03|sentinel|security) d=03-agentfield-sentinel;; *) d="$flavor";; esac
           echo "· running $d against :$FIELD ($mode)"
           (cd "$ROOT/agents/flavors/$d" && \
             uv run --with pyyaml --with langgraph --with cryptography \
               python run.py --field "http://127.0.0.1:$FIELD" "$mode") ;;
  *) echo "usage: scripts/dev.sh start|stop|restart|replant|status|logs|window|clean|agent [flavor] [--once|--forever]" ;;
esac
