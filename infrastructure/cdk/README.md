# Orreth.ai — spectator demo infrastructure

A captured moment of the live universe, served static: S3 (private, OAC) +
CloudFront. No compute, no login, no origin to probe — the demo *cannot act*.

## Ship a moment

```bash
# 1. capture the moment (rig up: scripts/dev.sh start)
cd backend/conformance && uv run python snapshot_console.py 4500

# 2. preview locally
python3 -m http.server -d site 8080     # → http://localhost:8080

# 3. deploy (from infrastructure/cdk; needs a deploy-capable AWS profile)
export TMPDIR="$HOME/.orreth/tmp"        # macOS: jsii needs a writable tmp
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PATH=".venv/bin:$PATH" npx aws-cdk@latest deploy            # CloudFront URL
# with the domain (zone must exist in the account):
PATH=".venv/bin:$PATH" npx aws-cdk@latest deploy \
  -c demo_domain=demo.orreth.ai -c orreth_zone_id=ZXXXX -c orreth_zone_name=orreth.ai
```

Notes: the homebrew `cdk` CLI is older than aws-cdk-lib's schema — use
`npx aws-cdk@latest`. Re-running step 1 + 3 refreshes the captured moment
(BucketDeployment invalidates the edge cache). `site/` and `cdk.out/` are
generated — never committed.
