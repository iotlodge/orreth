# PROVENANCE: Fable 5 (claude-fable-5) — 0037, the Estate · 2026-07-22
"""The Estate (0037): allen, the cloud architect — the first embodied tier.

allen IS a field: the tier's DID is his identity, its staff his control plane,
its incarnations his hands. This module is spoonful 1 — the resident stands:
the TYPED DOOR (the 0030 ladder enforced at his gateway) and the acceptance
gate (locked 2026-07-22: the estate adopts before it creates).

The door's law: humans alone originate Objectives; an agent speaks Intentions
or Observations, and every one carries lineage to a human Objective — or it is
refused, LOUDLY. This is a protocol refusal, deliberately not the uniform
authz shape (0002 §4 protects retrieval from probes; the door here TEACHES the
ladder to whoever knocks). Nobody builds infrastructure because a machine
wanted it.
"""
from __future__ import annotations

import json

from . import crypto, improver
from .identity import NOW
from .node import make_memory

SPEECH = ("objective", "intention", "observation")

# ---------------------------------------------------------------- the charter (0037 §3)
# The question set is a versioned ASSET (0031's shape, planted at genesis): grace
# may propose revisions from receipts, adoption rides the lanes, and the questions
# are DATA — a bare ask deployed literally is deployed incorrectly, so the answers
# below must exist before a prod plan may compile.
CHARTER_NAME = "charter-deployment"
CHARTER_GENESIS = {
    "version": "1",
    "questions": {
        "data_classification": "what class of data will this hold — public · "
                               "internal · confidential · regulated?",
        "rto": "recovery time objective — how long may this be down?",
        "rpo": "recovery point objective — how much data loss is survivable?",
        "interoperability": "who consumes this — which patterns (api · events · "
                            "files) and from where?",
        "caching": "what may be cached, and for how long?",
        "residency": "which region(s) may hold the bytes?",
        "retention": "how long must the data live — and when must it die?",
    },
    # the environment ladder (0013 applied): charter depth by rung — a sandbox
    # bucket needs almost nothing; prod demands the full charter
    "required": {"sandbox": [], "staging": ["data_classification", "retention"],
                 "prod": "all"},
}


class DoorRefusal(Exception):
    """The typed door, refusing loudly — the message names the missing rung."""


class GateStands(Exception):
    """The acceptance gate (0037 §8.7): Create waits for the brownfield walk."""


class CharterGaps(Exception):
    """Refused-at-compile (0037 §3): a plan with gaps cannot compile for this
    environment. Carries the open questions — they ARE the HITL card's text."""

    def __init__(self, env: str, questions: dict):
        self.env, self.questions = env, dict(questions)
        qs = " · ".join(f"{k}: {q}" for k, q in questions.items())
        super().__init__(f"the charter interrogates before a {env} plan compiles "
                         f"(0037 §3) — {len(questions)} question(s) stand open: {qs}")


def receive(node, allen: dict, allen_kp, speech: dict) -> str:
    """One utterance through allen's door. `speech` carries `kind` (a rung of the
    0030 ladder), `speaker` ({did, human}), `text`, and — for agents — `lineage`
    (the record ids walking back to a human Objective). Accepted speech lands as
    a signed memory record tagged with its rung; the ladder is stored so the
    spacetime window can WALK it: why does this bucket exist? is a query."""
    kind = str(speech.get("kind") or "")
    speaker = speech.get("speaker") or {}
    text = str(speech.get("text") or "").strip()
    lineage = [str(x) for x in speech.get("lineage") or []]
    if kind not in SPEECH:
        raise DoorRefusal(f"“{kind or '?'}” is not a rung — the ladder is "
                          "objective · intention · observation (0030)")
    if not text:
        raise DoorRefusal("empty speech — the door opens for words")
    if not speaker.get("human"):
        if kind == "objective":
            raise DoorRefusal("humans alone originate objectives (0030) — an "
                              "agent may speak an intention or an observation, "
                              "never a why")
        if not lineage:
            raise DoorRefusal("no ancestry — every agent ask descends from a "
                              "human objective; name the lineage or the door "
                              "stays shut")
        missing = [r for r in lineage if r not in node.records]
        if missing:
            raise DoorRefusal("lineage names records this floor cannot see — "
                              "an ancestry must be walkable, not merely claimed")
    elif kind != "objective":
        raise DoorRefusal("a human speaks objectives at this door — intentions "
                          "and observations are the agents' rungs; charter "
                          "answers ride the gate's card (0037 §3)")
    body = {"estate_speech": {"kind": kind, "speaker": speaker.get("did", ""),
                              "human": bool(speaker.get("human")), "text": text,
                              **({"lineage": lineage} if lineage else {}),
                              "at": NOW()}}
    # the lineage rides INSIDE the signed body — the ladder is data, walkable by
    # query; no unsigned top-level field to keep honest separately
    rec = make_memory(allen, allen_kp, node.scope, body, kind="episodic",
                      tags=["estate", kind])
    return node.write(rec)


def adopted(node) -> list[dict]:
    """The brownfield walk's receipts: every adoption record on this floor."""
    return [r for r in node.records.values() if "estate-adopted" in (r.get("tags") or [])]


def create_unlocked(node) -> bool:
    """The acceptance gate (locked 2026-07-22): greenfield Create is possible
    only after the read-only adoption walk has landed its receipts."""
    return bool(adopted(node))


def record_adoption(node, allen: dict, allen_kp, stacks: list[str]) -> str:
    """The adoption walk's landing — observed stacks, read-only, attested by
    allen's key. Spoonful 4 drives this against the real estate (OrrethDemoStack,
    the pipeline); the mechanism stands now so the gate is real, not rhetorical."""
    if not stacks:
        raise DoorRefusal("an adoption names what it observed — no stacks, no walk")
    body = {"estate_adoption": {"stacks": sorted(stacks), "posture": "read-only",
                                "at": NOW()}}
    rec = make_memory(allen, allen_kp, node.scope, body, kind="semantic",
                      tags=["estate", "estate-adopted"])
    return node.write(rec)


def plant_charter(node, allen: dict, allen_kp) -> str:
    """Genesis: the charter enters the shelf as a versioned asset (0031's shape)
    under allen's own signature — from here a question change is a proposal that
    rides the lanes, never an edit to code."""
    rec = improver.make_asset(allen, allen_kp, node.scope, name=CHARTER_NAME,
                              profile=CHARTER_GENESIS)
    return node.write(rec)


def charter_profile(node) -> dict:
    """The ACTIVE charter's questions and ladder — the genesis shape until a
    planted version stands, then always the shelf's word."""
    row = improver.active_asset(node, CHARTER_NAME)
    if row is None:
        return CHARTER_GENESIS
    prof = improver._profile_of(row[1])
    return prof if prof.get("questions") else CHARTER_GENESIS


def required_keys(node, env: str) -> list[str]:
    prof = charter_profile(node)
    req = (prof.get("required") or {}).get(env, "all")
    return list(prof["questions"]) if req == "all" else [k for k in req
                                                         if k in prof["questions"]]


ESTATE = ""                # the subject meaning "policy for everything I build"


def charter_answers(node) -> dict:
    """Recalled from memory — every (question, subject)'s newest record, with
    who answered. An answer is a property of a WORKLOAD (the bucket, the repo),
    never of the universe; subject ESTATE ("") is deliberate estate-wide policy,
    spoken as such (JB's walk finding, 2026-07-22: subject-less answers read as
    homework and silently over-apply — the flattening is the bug)."""
    out: dict = {}
    rows = sorted((r for r in node.records.values()
                   if "estate-charter" in (r.get("tags") or [])),
                  key=lambda r: r["received_at"])
    for r in rows:
        b = json.loads(crypto._b64d(r["body"]).decode()).get("charter_answer") or {}
        if b.get("key"):
            out[(b["key"], b.get("subject", ESTATE))] = {
                "answer": b.get("answer", ""), "by": b.get("by", ""),
                "subject": b.get("subject", ESTATE), "id": r["id"]}
    return out


def answer_gap(node, allen: dict, allen_kp, key: str, answer: str, by: str, *,
               subject: str) -> str:
    """The human seat answers a question FOR a subject (locked 2026-07-22) —
    a workload's name, or ESTATE ("") for deliberate everything-policy. The
    answer lands signed with the question and who spoke, and is recalled: the
    workload's own word first, estate policy beneath it, history as offers."""
    prof = charter_profile(node)
    if key not in prof["questions"]:
        raise DoorRefusal(f"“{key}” is not a charter question — the charter asks: "
                          + " · ".join(prof["questions"]))
    if not (answer or "").strip():
        raise DoorRefusal("an answer needs words — the charter records substance, "
                          "not acknowledgement")
    body = {"charter_answer": {"key": key, "question": prof["questions"][key],
                               "answer": answer.strip(), "by": by,
                               "subject": (subject or ESTATE).strip().lower(),
                               "at": NOW()}}
    rec = make_memory(allen, allen_kp, node.scope, body, kind="semantic",
                      tags=["estate", "estate-charter", key])
    return node.write(rec)


def gap_analysis(node, env: str, subject: str) -> dict:
    """Every ask enters here before anything else happens (0037 §3), anchored
    to its SUBJECT. Resolution per question: the workload's own answer wins;
    estate policy applies beneath it (deliberate, so it auto-applies); anything
    else is a gap — carrying an OFFERED default when history holds one ("last
    time: internal — reuse?"), never a silent inheritance."""
    have = charter_answers(node)
    need = required_keys(node, env)
    qs = charter_profile(node)["questions"]
    subject = (subject or "").strip().lower()
    answers: dict = {}
    gaps: dict = {}
    for k in need:
        own = have.get((k, subject))
        policy = have.get((k, ESTATE))
        if own:
            answers[k] = {**own, "scope": "workload"}
        elif policy:
            answers[k] = {**policy, "scope": "estate-policy"}
        else:
            prior = [v for (kk, s), v in have.items() if kk == k and s != ESTATE]
            offer = (f' (last time: “{prior[-1]["answer"]}” for '
                     f'«{prior[-1]["subject"]}» — reuse?)') if prior else ""
            gaps[k] = qs[k] + offer
    return {"env": env, "subject": subject, "required": need,
            "gaps": list(gaps), "questions": gaps, "answers": answers}


# ---------------------------------------------------------------- the planner (0037 §4)
# v0 shapes the planner recognizes — CloudFormation grammar, grown by evidence.
# The point of the plan: THE CHARTER ANSWERS BECOME TEMPLATE PROPERTIES —
# "deploy it correctly" is not advice, it is compilation.
_CATALOG = (
    (("s3", "bucket", "corpus", "store", "object"), "AWS::S3::Bucket", "bucket"),
    (("queue", "sqs"), "AWS::SQS::Queue", "queue"),
    (("table", "dynamo", "database"), "AWS::DynamoDB::Table", "table"),
    (("api", "service", "endpoint"), "AWS::ApiGateway::RestApi", "api"),
)


def _slug(s: str) -> str:
    import re as _re
    return _re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:48] or "workload"


def _resources_for(ask: str, charter: dict) -> list[dict]:
    """The ask's shapes, dressed by the charter: classification closes public
    access and turns on encryption; retention becomes a lifecycle rule;
    residency rides as the region. Unrecognized asks get one generic stack
    member — honest, and the catalog grows from evidence."""
    low = (ask or "").lower()
    kinds = [(t, short) for words, t, short in _CATALOG
             if any(w in low for w in words)] or [("AWS::CloudFormation::Stack",
                                                   "stack")]
    cls = (charter.get("data_classification") or {}).get("answer", "")
    keep = (charter.get("retention") or {}).get("answer", "")
    out: list[dict] = []
    for t, short in kinds:
        rid = f"{short}Main"
        out.append({"id": rid, "type": t, "depends_on": [],
                    "properties": {
                        **({"PublicAccessBlock": "ALL", "Encryption": "SSE-KMS"}
                           if t == "AWS::S3::Bucket" and "public" not in cls.lower()
                           else {}),
                        **({"Lifecycle": keep} if keep and t == "AWS::S3::Bucket"
                           else {})}})
        if t == "AWS::S3::Bucket":
            out.append({"id": f"{short}Policy", "type": "AWS::S3::BucketPolicy",
                        "depends_on": [rid],
                        "properties": {"Classification": cls or "unclassified"}})
    return out


def _yaml_for(stack: str, resources: list[dict], charter: dict,
              subject: str) -> str:
    """The template, recallable by a human forever — CloudFormation yaml with
    the charter pinned in Metadata: the answers travel WITH the artifact."""
    lines = [f"# {stack} — planned by allen (0037 §4); the charter rides below",
             "AWSTemplateFormatVersion: '2010-09-09'",
             f"Description: {subject} — every property below traces to a "
             "charter answer or the ask itself",
             "Metadata:",
             "  OrrethCharter:"]
    for k, v in sorted(charter.items()):
        lines.append(f"    {k}: \"{v.get('answer', '')}\"  # {v.get('scope', '?')}")
    lines.append("Resources:")
    for r in resources:
        lines.append(f"  {r['id']}:")
        lines.append(f"    Type: {r['type']}")
        if r.get("depends_on"):
            lines.append(f"    DependsOn: [{', '.join(r['depends_on'])}]")
        if r.get("properties"):
            lines.append("    Properties:")
            for pk, pv in sorted(r["properties"].items()):
                lines.append(f"      {pk}: \"{pv}\"")
    return "\n".join(lines) + "\n"


def _dag_for(subject: str, resources: list[dict], status: str) -> dict:
    """The picture (0037 §4): layout `dag` — the glass lays columns by
    dependency depth. Every node is a resource; the human approves what they
    can SEE."""
    nodes = [{"id": r["id"], "role": "fingertip", "altitude": r["id"],
              "status": status} for r in resources]
    edges = [{"from": d, "to": r["id"]} for r in resources
             for d in r.get("depends_on") or []]
    return {"layout": "dag", "subject": subject, "nodes": nodes, "edges": edges,
            "narrative": [{"text": f"«{subject}» — {len(nodes)} resource(s), "
                                   f"{status}; every property traces to the "
                                   "charter or the ask",
                           "nodes": [n["id"] for n in nodes],
                           "edges": [f"{e['from']}→{e['to']}" for e in edges]}]}


def preview(node, allen: dict, allen_kp, ask: str, *, env: str = "prod",
            subject: str | None = None) -> dict:
    """PLAN IS FREE (§8.4): no gate, no consequence — but never a wrong picture:
    the charter still interrogates, because a plan without its answers would be
    the incorrect deployment drawn confidently. A clean preview compiles the
    resources, the yaml (registered as a recallable template asset under
    allen's signature), and the planned DAG."""
    subject = _slug(subject or ask)
    ga = gap_analysis(node, env, subject)
    if ga["gaps"]:
        raise CharterGaps(env, ga["questions"])
    resources = _resources_for(ask, ga["answers"])
    stack = f"orreth-{subject}"
    yaml = _yaml_for(stack, resources, ga["answers"], subject)
    asset = improver.make_asset(allen, allen_kp, node.scope,
                                name=f"template-{subject}",
                                profile={"yaml": yaml, "stack": stack,
                                         "subject": subject, "env": env,
                                         "resources": resources})
    node.write(asset)
    return {"subject": subject, "env": env, "ask": (ask or "").strip(),
            "stack": stack, "resources": resources, "yaml": yaml,
            "template_ref": asset["id"], "charter": ga["answers"],
            "dag": _dag_for(subject, resources, "planned")}


def stage_create(node, ask: str, *, env: str = "prod",
                 subject: str | None = None) -> dict:
    """A greenfield Create, asked — the CONSEQUENCE path. Behind the acceptance
    gate it refuses with the gate's own words; past the gate the preview
    compiles (charter-interrogated) and the plan stages toward 0012 with the
    answers and the picture PINNED — you approve what you can see."""
    if not create_unlocked(node):
        raise GateStands("the acceptance gate stands (0037 §8.7): the estate "
                         "adopts before it creates — the brownfield walk has "
                         "not completed")
    subject = _slug(subject or ask)
    ga = gap_analysis(node, env, subject)
    if ga["gaps"]:
        raise CharterGaps(env, ga["questions"])
    return {"staged": True, "ask": (ask or "").strip(), "env": env,
            "subject": subject, "charter": ga["answers"],
            "note": "the charter is satisfied — consequence waits at the gate "
                    "(0012); the plan carries its answers pinned (0037 §3)"}


def reconcile(node, allen: dict, allen_kp, subject: str,
              deployed: list[dict]) -> dict:
    """The second DAG (0037 §4): the as-built against the blueprint. THE DIFF
    IS NEWS — a resource that materialized differently than approved lands as
    a signed record wearing the medium marker's weight, never a footnote."""
    subject = _slug(subject)
    row = improver.active_asset(node, f"template-{subject}")
    planned = (improver._profile_of(row[1]) if row else {}).get("resources") or []
    p_ids = {r["id"]: r for r in planned}
    d_ids = {r["id"]: r for r in deployed}
    diff = ([f"missing: {i}" for i in p_ids if i not in d_ids]
            + [f"unplanned: {i}" for i in d_ids if i not in p_ids]
            + [f"changed: {i}" for i in p_ids
               if i in d_ids and (p_ids[i].get("type") != d_ids[i].get("type")
                                  or p_ids[i].get("properties") !=
                                  d_ids[i].get("properties"))])
    if diff:
        node.write(make_memory(
            allen, allen_kp, node.scope,
            {"estate_drift": {"subject": subject, "diff": diff,
                              "severity": "medium", "at": NOW()}},
            kind="episodic", tags=["estate", "estate-drift", subject]))
    return {"subject": subject, "match": not diff, "diff": diff,
            "dag": _dag_for(subject, deployed, "deployed")}
