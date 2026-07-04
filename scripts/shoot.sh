#!/usr/bin/env bash
# Self-review harness: stand up a seeded daemon, mint the Console URL, and let
# headless Chrome capture what a human would see. Claude's own eyes on the UI.
#   scripts/shoot.sh [outfile.png] [view]   view = pulse|window|req|ask (default pulse)
set -euo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
export TMPDIR="$HOME/.orreth/tmp"; mkdir -p "$TMPDIR"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$ROOT/backend/conformance"; PLANE="$ROOT/backend/plane"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="${1:-$TMPDIR/console.png}"; SHOT_TMP="$TMPDIR/shot"
PORT=4970

pkill -f "orrethd --profile.*$PORT" 2>/dev/null || true; sleep 0.5
(cd "$PLANE" && cargo build -q -p orrethd)
ROOT_PUB=$(cd "$CONF" && uv run python smoke_orrethd.py root-pub)
"$PLANE/target/debug/orrethd" --profile "$PLANE/profiles/demo-field.json" --port $PORT \
  --root-pub "$ROOT_PUB" --store-dir "$TMPDIR/shot-bodies" \
  --models "$PLANE/profiles/model-registry.json" >"$TMPDIR/shot-daemon.log" 2>&1 &
DPID=$!; sleep 1.2

# seed a biography + roster life + a couple asks so every view has something to show
URL=$(cd "$CONF" && SHOOT=1 uv run python - "$PORT" <<'PY'
import base64, json, sys, urllib.request
from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda, NOW
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair
port=sys.argv[1]; SCOPE="u:demo/e:cloud/f:prod"; B=f"http://127.0.0.1:{port}"
def post(p,d):
    r=urllib.request.Request(B+p,method="POST",data=json.dumps(d).encode(),headers={"Content-Type":"application/json"})
    try: urllib.request.urlopen(r).read()
    except Exception: pass
kp=crypto.KeyPair(); ag={"did":crypto.did_key_for(kp.public),"scope":SCOPE}
def ago(d):
    from datetime import datetime,timedelta,timezone
    return (datetime.now(timezone.utc)-timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%SZ")
for c,d,pc in [("the founding season",420,"ingested-archive"),("the championship",180,"ingested-archive"),
               ("spring training",45,"ingested-archive"),("yesterday's win",0.01,"lived")]:
    post("/records", make_memory(ag,kp,SCOPE,{"chapter":c},occurred_at=ago(d),provenance_class=pc))
st=crypto.KeyPair(); sd=crypto.did_key_for(st.public)
for i,(oc,sc) in enumerate([("partial",0.0),("success",1.0),("success",1.0)]):
    run={"id":crypto.content_hash({"c":i,"t":NOW()}),"agent":ag["did"],"scope":SCOPE,
         "goal_hash":"sha256:demo","occurred_at":NOW(),"outcome":oc,
         "scores":[{"objective":"objective-met","score":sc}],"cost":{"tokens":48+i},"author":sd}
    run["sig"]=st.sign(sd,{k:run[k] for k in ("id","agent","scope","goal_hash","occurred_at")})
    post("/runs",run)
post("/requests",{"kind":"gather","text":"build strategies for cold-weather architecture"})
post("/requests",{"kind":"gather","text":"PCI-DSS controls for payment services"})
nanda=Nanda(); root=Becky("u:demo",nanda,universe_name="demo",kp=root_keypair())
tok=root.issue_token(ag["did"],"u:demo",[{"action":"retrieve","space":"self"}])
cfg={"token":tok,"requester":ag["did"],"requester_scope":SCOPE,
     "tiers":[SCOPE,"u:demo/e:cloud","u:demo"]}
print(f"{B}/window#t={base64.b64encode(json.dumps(cfg).encode()).decode()}")
PY
)

VIEW="${2:-pulse}"
PROF=$(mktemp -d "$TMPDIR/chrome.XXXXXX")     # unique profile per shot — no lock collisions
"$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --no-first-run --no-default-browser-check \
  --window-size=1600,1000 --virtual-time-budget=6500 \
  --user-data-dir="$PROF" --screenshot="$OUT" "${URL}&v=${VIEW}" >/dev/null 2>&1 || true
rm -rf "$PROF"
kill $DPID 2>/dev/null || true; rm -f "$CONF/.smoke-root-seed"
echo "shot: $OUT   (view=$VIEW)"
