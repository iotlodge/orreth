# Seed — ML Over the Operating State (the fourth loop)

**Status: SEED (JB, 2026-09-16, late-session riff — "keep me real").**
Deep dive slots AFTER embedded-graded-learning; mostly V2, but the
substrate cost is nearly zero, which is why it's worth holding now.

## JB's idea, faithfully

Machine learning over the SCHEDULED work of agents: an automated
observation made by an agent every minute — anything in the request —
creates an **agent-observation-dataset** whose format and values the
agent itself crafts. That feeds a **Machine Learning Agent** that can
create any type of ML model for the kernel, agents, services, and apps
in cloud production (any stream of data). Agents never sleep → rules
and patterns over recurrence → threat-detection uplift → "the ability
to machine learn a self-tuning and adaptive kernel."

## What's REAL (the substrate already does the hard part)

- **The dataset factory exists.** Every scheduled job already emits
  committed, signed, timestamped, schema'd events on the rail. An
  observation dataset = a topic family + a DECLARED, VERSIONED dataset
  schema (a craft artifact — "the agent crafts the format" becomes
  governed, not ad hoc).
- **Point-in-time training sets, free.** Replay + immutable lineage =
  reproducible datasets AS OF any moment, provenance on every row — the
  thing ML teams build feature stores to fake. Temporal honesty also
  kills label leakage.
- **Models are craft.** The ML Agent (an identity, MITL's sibling)
  trains models that land as versioned artifacts wearing their hash AND
  their training-set ref — model → dataset → records: the supply chain
  of article 12, extended to weights. Deployment through gates + the
  harness; inference through the meter.
- **The honest "self-tuning kernel":** models PROPOSE turns of the
  governed dials that already exist, inside pre-approved bounds;
  permanence rides the two-speed law; rule 11's stop lever covers the
  whole loop. Autonomic computing WITH receipts — powerful, and never
  a kernel rewriting itself.
- **Threat detection is the right first target**: refusals, gate
  denials, fencing rejections, verdict floods are structured,
  labeled-ish signals — classical anomaly methods genuinely work there.

## The KEEP-IT-REAL list (named before anyone dreams)

1. **Volume and cold start:** per-minute = ~525k rows/stream/year —
   plenty for anomaly detection, thin for deep models. Law: every model
   must BEAT THE DUMB BASELINE (threshold/EWMA) in the harness before
   deployment. Most won't at first; that's honest, not failure.
2. **The loop can chase its own tail:** a model that tunes the system
   changes the data the next model learns from (quota tightens → more
   refusals → "threat" → tightens more). Cures: bounded actuation
   (dial min/max), change-rate budgets, drift monitoring ON the models,
   the human stop.
3. **Anomaly ≠ threat.** False-positive floods destroy trust faster
   than misses. Uplift comes from provenance context (the chain shows
   WHY), never from alert volume.
4. **The observation stream is an attack surface** — article 12's law
   extends: ONLY SIGNED OBSERVATIONS TRAIN. Dataset poisoning is the
   new feedback poisoning.
5. **Never-sleeping observation is metered work**: cadence is a dial,
   cost rides showback.

## The ladder, complete

L1 in-graph self-critique · L2 the offline A/B harness · L3 near-live
graded lessons (context) · **L4 learned models over the Operating
State's own streams (weights — governed, provenanced, bounded).**
