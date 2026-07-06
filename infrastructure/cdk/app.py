#!/usr/bin/env python3
# PROVENANCE: Fable 5 (claude-fable-5) — 0019 demo, the spectator site · 2026-07-06
"""Orreth.ai CDK application — the spectator demo (static snapshot).

Build the snapshot first (rig up):
    cd backend/conformance && uv run python snapshot_console.py 4500

Deploy (CloudFront URL only):
    cdk deploy
Deploy on demo.orreth.ai (zone must exist in the account):
    cdk deploy -c demo_domain=demo.orreth.ai -c orreth_zone_id=ZXXXX \
               -c orreth_zone_name=orreth.ai
"""
from pathlib import Path

import aws_cdk as cdk

from stacks.orreth_demo_stack import OrrethDemoStack

app = cdk.App()

site_dir = str((Path(__file__).resolve().parents[2] / "site"))

OrrethDemoStack(
    app,
    "OrrethDemoStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account") or "824106896658",
        region=app.node.try_get_context("region") or "us-east-1",
    ),
    site_dir=site_dir,
    demo_domain=app.node.try_get_context("demo_domain"),
    zone_id=app.node.try_get_context("orreth_zone_id"),
    zone_name=app.node.try_get_context("orreth_zone_name"),
)

app.synth()
