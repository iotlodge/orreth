# Orreth.ai — the spectator demo's infrastructure

[demo.orreth.ai](https://demo.orreth.ai) is a **photograph of THE PANEL**: a kernel that
really ran, read through every one of its doors at one moment, served static — S3
(private, OAC) + CloudFront. No compute, no login, no origin to probe: the demo *cannot
act*. In the page, every read is a captured answer, every write is refused with one face,
and the feed's captured minutes replay on a loop.

Re-homed 2026-09-30 from `archive/0.72/infrastructure/cdk` (the 0.72 Console's demo)
for the kernel's panel; the stack is unchanged but for the cache words.

## Ship a moment

```bash
# 1. capture the moment (a kernel up on :4600 — scripts/dev.sh up; a REAL seat in hand:
#    take yours in the glass, then copy localStorage["orreth.seat"] from the browser)
ORRETH_SEAT='<the seat wire>' python3 scripts/snapshot_glass.py        # → site/

# 2. preview it
python3 -m http.server -d site 8080                                     # → http://localhost:8080

# 3. deploy (from infrastructure/cdk; a deploy-capable AWS profile)
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN   # static keys outrank the profile
export TMPDIR="$HOME/.orreth/tmp" AWS_PROFILE=jb_support           # macOS: jsii needs a writable tmp
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PATH=".venv/bin:$PATH" npx aws-cdk@latest diff \
  -c demo_domain=demo.orreth.ai -c orreth_zone_id=Z0336720KR9EO6MDNHDA -c orreth_zone_name=orreth.ai
PATH=".venv/bin:$PATH" npx aws-cdk@latest deploy --require-approval never \
  -c demo_domain=demo.orreth.ai -c orreth_zone_id=Z0336720KR9EO6MDNHDA -c orreth_zone_name=orreth.ai
```

The laws, each learned live:

- **Diff first, and BOTH diff and deploy carry the three `-c` flags.** A bare synth
  silently drops the certificate and the alias — the tell is `[-] Output DemoUrl` in the
  diff. Never deploy a synth whose diff removes `DemoUrl`.
- **Unset the static keys.** A scoped-down key in the environment outranks `AWS_PROFILE`
  and fails on `iam:PassRole` as the wrong user.
- `npx aws-cdk@latest` — the homebrew `cdk` is older than `aws-cdk-lib`'s schema.
- `TMPDIR` must be a literal path (`$HOME/…`, never `~`): jsii chokes on the tilde.
- `/deeds/` and `/media/` in the bucket are published out-of-band and **excluded** from
  the deployment, so a refresh never prunes them (the 0042 deed is a live proof).
- Every file ships `Cache-Control: public, max-age=0, must-revalidate`, and the deployment
  invalidates `/*` — a browser that held the old moment sees the new one on its next visit.

`site/`, `cdk.out/` and `.venv/` are generated — never committed (`.gitignore`).

Stack `OrrethDemoStack` · us-east-1 · CloudFront `EYH0DGXRO7C0Q` · zone `Z0336720KR9EO6MDNHDA`.
