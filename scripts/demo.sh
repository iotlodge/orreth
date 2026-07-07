#!/usr/bin/env bash
# PROVENANCE: Fable 5 (claude-fable-5) — the demo index · 2026-07-05
# Orreth demos — the growing reel. Each one tells a true story against the live rig.
# New demos land here as Orreth matures; when marketing time comes, this is the script.
#
#   scripts/demo.sh                 list the reel
#   scripts/demo.sh farm            0018 · a service's whole life: plant a REAL remote
#                                   MCP, then watch a rug pull get caught at the gate
#   scripts/demo.sh life            0002 · a digital life outlives process/machine/daemon
#   scripts/demo.sh spacetime       0002/0004 · one query, three tiers of deep time
#   scripts/demo.sh knowledge       0014 · admitted quarantined, promoted, recalled
#   scripts/demo.sh chassis         0015 · one governed thought through the fixed loop
#   scripts/demo.sh model           0016 · the model plane, metered end to end
#   scripts/demo.sh stable          0019 · a mind's whole life: saddled off the real
#                                   market, earned by canary, retired by appointment
#   scripts/demo.sh parlor          0020 · humans ask, residents fetch — audiences
#                                   with the residents, signed onto the window
#   scripts/demo.sh window          0008 · seed a biography and open the Console
#
# Most demos want the rig up first: scripts/dev.sh start
set -euo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$ROOT/backend/conformance"
FIELD=4502

run() { (cd "$CONF" && uv run python "$1" "${@:2}"); }

case "${1:-list}" in
  farm)      run demo_farm.py "$FIELD" ;;
  life)      run demo_digital_life.py ;;
  spacetime) run demo_spacetime_window.py ;;
  knowledge) run demo_knowledge_loop.py ;;
  chassis)   run demo_chassis.py ;;
  model)     run demo_model_plane.py ;;
  stable)    run demo_stable.py "$FIELD" ;;
  parlor)    run demo_parlor.py "$FIELD" ;;
  window)    "$ROOT/scripts/dev.sh" window ;;
  list|*)
    echo "the Orreth demo reel — scripts/demo.sh <name>   (rig first: scripts/dev.sh start)"
    echo
    echo "  farm        0018 · a service's whole life — real remote MCP planted live,"
    echo "              then a rug pull caught at the gate and read off its worldline"
    echo "  life        0002 · a digital life outlives the process, the machine, the daemon"
    echo "  spacetime   0002 · one query, three tiers of deep time"
    echo "  knowledge   0014 · admitted quarantined · promoted on receipts · recalled by lineage"
    echo "  chassis     0015 · one governed thought through the fixed loop"
    echo "  model       0016 · the model plane, metered end to end"
    echo "  stable      0019 · a mind's whole life — saddled off the real market,"
    echo "              earned by canary, expiring by appointment, swapped, remembered"
    echo "  parlor      0020 · humans ask, residents fetch — an audience with charlotte,"
    echo "              ada, and vigil, every exchange signed onto the window"
    echo "  window      0008 · seed a biography and open the Console"
    ;;
esac
