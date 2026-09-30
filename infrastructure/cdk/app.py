#!/usr/bin/env python3
# PROVENANCE: Fable 5 (claude-fable-5) — 0019 demo, the spectator site · 2026-07-06
# Amended: Claude Fable 5.1 (claude-fable-5-1) — re-homed from archive/0.72 for THE PANEL's photograph
#          (the refresh season's step 3, 2026-09-30): the site is scripts/snapshot_glass.py's output
"""Orreth.ai CDK application — the spectator demo (a static photograph of THE PANEL).

Capture the moment first (a kernel up, a real seat in hand):
    ORRETH_SEAT=<the seat's wire> python3 scripts/snapshot_glass.py

Deploy (CloudFront URL only):
    cdk deploy
Deploy on demo.orreth.ai (the zone must exist in the account):
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
