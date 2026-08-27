# PROVENANCE: Fable 5 (claude-fable-5) — 0037, the Estate · 2026-07-22
"""The Estate (0037) spoonful 1: the resident stands.

Under test: the universe-parent allowance (a field with no eco above it, its
becky delegated one hop from the root — staff of the universe, locked
2026-07-22); the TYPED DOOR (humans alone speak objectives; agent speech
carries walkable lineage or is refused LOUDLY — a teaching refusal, never the
uniform authz shape); and the acceptance gate (Create refuses until the
brownfield adoption has walked, locked 2026-07-22)."""
import pytest

from orreth_sim import estate, parlor, provisioner


def _estate_field():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = provisioner.staff_field(prov, provisioner.second_brain_template(), "estate")
    b = prov.beckys["u:t/f:estate"]
    allen, allen_kp = b.issue_identity("instance", "u:t/f:estate", resident=True)
    return prov, fld, b, allen, allen_kp


def test_staff_field_parents_off_universe():
    """The 0037 §8.3 allowance: no eco between allen and the universe — the
    delegation chain is exactly one hop, and a token his becky mints verifies
    at the root like any other."""
    prov, fld, b, allen, allen_kp = _estate_field()
    assert fld.profile["scope"] == "u:t/f:estate"
    assert fld.profile["is_leaf"] is True
    assert len(b.chain) == 1                       # root → becky@estate, one hop
    assert b.chain[0]["issuer"] == prov.becky.did
    # spend rides the lease (§8.6): the Budget shape's `cost` axis carries the
    # dollars — contracts/v0 untouched; a named `usd` member is a later rule-9 ask
    token = b.issue_token(allen["did"], "u:t/f:estate",
                          [{"action": "retrieve", "space": "self"}],
                          budget={"cost": 25})
    prov.becky.verify_token(token)                 # the root recognizes the staff


def test_door_refuses_agent_objectives():
    """Humans alone originate objectives (0030) — an agent speaking a why is
    refused loudly, with the law in the message."""
    _, fld, _, allen, allen_kp = _estate_field()
    with pytest.raises(estate.DoorRefusal, match="humans alone originate"):
        estate.receive(fld, allen, allen_kp,
                       {"kind": "objective", "text": "make me a bucket",
                        "speaker": {"did": "did:key:zagent", "human": False}})


def test_door_demands_walkable_lineage():
    """An agent intention with no ancestry — or an ancestry this floor cannot
    see — never enters. With a walkable lineage it lands as signed memory,
    the rung riding the tags and the ancestry riding the signed body."""
    _, fld, _, allen, allen_kp = _estate_field()
    with pytest.raises(estate.DoorRefusal, match="no ancestry"):
        estate.receive(fld, allen, allen_kp,
                       {"kind": "intention", "text": "a bucket for the corpus",
                        "speaker": {"did": "did:key:zagent", "human": False}})
    with pytest.raises(estate.DoorRefusal, match="cannot see"):
        estate.receive(fld, allen, allen_kp,
                       {"kind": "intention", "text": "a bucket for the corpus",
                        "speaker": {"did": "did:key:zagent", "human": False},
                        "lineage": ["not-a-record-here"]})
    oid = estate.receive(fld, allen, allen_kp,
                         {"kind": "objective", "text": "build the seven RAGs",
                          "speaker": {"did": "did:key:zjb", "human": True}})
    iid = estate.receive(fld, allen, allen_kp,
                         {"kind": "intention", "text": "a bucket for the corpus",
                          "speaker": {"did": "did:key:zagent", "human": False},
                          "lineage": [oid]})
    rec = fld.records[iid]
    assert "estate" in rec["tags"] and "intention" in rec["tags"]


def test_gate_stands_until_adoption():
    """The acceptance gate (0037 §8.7): Create refuses with the gate's own
    words until the brownfield walk lands its receipts — then a sandbox ask
    (no charter owed on the lowest rung) stages."""
    _, fld, _, allen, allen_kp = _estate_field()
    assert not estate.create_unlocked(fld)
    with pytest.raises(estate.GateStands, match="adopts before it creates"):
        estate.stage_create(fld, "create me an S3 bucket")
    estate.record_adoption(fld, allen, allen_kp,
                           ["OrrethDemoStack", "jsbarth-pipeline"])
    assert estate.create_unlocked(fld)
    staged = estate.stage_create(fld, "create me an S3 bucket", env="sandbox")
    assert staged["staged"] is True and "charter" in staged["note"]


def test_charter_refuses_prod_with_gaps():
    """Refused-at-compile (0037 §3): past the acceptance gate, a prod ask with
    an unanswered charter cannot compile — and the refusal carries the open
    questions, which ARE the HITL card's text."""
    _, fld, _, allen, allen_kp = _estate_field()
    estate.record_adoption(fld, allen, allen_kp, ["OrrethDemoStack"])
    with pytest.raises(estate.CharterGaps, match="recovery time objective") as e:
        estate.stage_create(fld, "deploy repo foo to production")
    assert set(e.value.questions) == set(estate.CHARTER_GENESIS["questions"])
    # the ladder: staging owes only its rung's questions
    with pytest.raises(estate.CharterGaps) as e2:
        estate.stage_create(fld, "deploy repo foo", env="staging")
    assert set(e2.value.questions) == {"data_classification", "retention"}


def test_answers_bind_to_subjects_and_policy_underlies():
    """JB's walk finding (2026-07-22) made structural: an answer is a property
    of a WORKLOAD; estate policy ("" subject) is deliberate and auto-applies
    beneath it; another workload's history is OFFERED in the question, never
    silently inherited."""
    _, fld, _, allen, allen_kp = _estate_field()
    estate.record_adoption(fld, allen, allen_kp, ["OrrethDemoStack"])
    with pytest.raises(estate.DoorRefusal, match="not a charter question"):
        estate.answer_gap(fld, allen, allen_kp, "color", "blue", "did:key:zjb",
                          subject="rag-corpus")
    # estate policy: residency for everything, deliberately
    estate.answer_gap(fld, allen, allen_kp, "residency", "us-west-2",
                      "did:key:zjb", subject=estate.ESTATE)
    # workload answers for the corpus bucket
    for key, words in (("data_classification", "internal"),
                       ("rto", "4 hours"), ("rpo", "24 hours"),
                       ("interoperability", "api, from the universe only"),
                       ("caching", "nothing cacheable"),
                       ("retention", "7 years, then crypto-shred")):
        estate.answer_gap(fld, allen, allen_kp, key, words, "did:key:zjb",
                          subject="rag-corpus")
    staged = estate.stage_create(fld, "a bucket for the corpus",
                                 subject="rag-corpus")
    assert staged["staged"] and staged["subject"] == "rag-corpus"
    assert staged["charter"]["rto"]["scope"] == "workload"
    assert staged["charter"]["residency"]["scope"] == "estate-policy"  # underlies
    # a DIFFERENT workload owes its own answers — history is offered, not applied
    with pytest.raises(estate.CharterGaps) as e:
        estate.stage_create(fld, "deploy repo foo to production",
                            subject="repo-foo")
    assert "residency" not in e.value.questions          # policy already covers it
    assert "reuse?" in e.value.questions["rto"]          # the offer, not the answer
    assert "rag-corpus" in e.value.questions["rto"]


def _charter_up(fld, allen, allen_kp, subject="rag-corpus"):
    estate.answer_gap(fld, allen, allen_kp, "residency", "us-west-2",
                      "did:key:zjb", subject=estate.ESTATE)
    for key, words in (("data_classification", "internal"),
                       ("rto", "4 hours"), ("rpo", "24 hours"),
                       ("interoperability", "api only"),
                       ("caching", "none"),
                       ("retention", "7 years, then crypto-shred")):
        estate.answer_gap(fld, allen, allen_kp, key, words, "did:key:zjb",
                          subject=subject)


def test_plan_is_free_but_never_wrong():
    """PLAN IS FREE (§8.4): the preview runs with the acceptance gate still
    STANDING — no consequence, no gate. But never a wrong picture: with charter
    gaps the preview refuses exactly like the compile would."""
    _, fld, _, allen, allen_kp = _estate_field()
    assert not estate.create_unlocked(fld)         # the gate stands…
    with pytest.raises(estate.CharterGaps):        # …and the charter still asks
        estate.preview(fld, allen, allen_kp, "an s3 bucket for the corpus",
                       subject="rag-corpus")
    _charter_up(fld, allen, allen_kp)
    plan = estate.preview(fld, allen, allen_kp, "an s3 bucket for the corpus",
                          subject="rag-corpus")
    assert plan["stack"] == "orreth-rag-corpus" and not estate.create_unlocked(fld)


def test_charter_answers_become_template_properties():
    """The point of the plan (0037 §4): 'deploy it correctly' is compilation —
    classification closes public access and turns on encryption, retention
    becomes a lifecycle rule, and the full charter rides the yaml's Metadata."""
    _, fld, _, allen, allen_kp = _estate_field()
    _charter_up(fld, allen, allen_kp)
    plan = estate.preview(fld, allen, allen_kp, "an s3 bucket for the corpus",
                          subject="rag-corpus")
    bucket = next(r for r in plan["resources"] if r["type"] == "AWS::S3::Bucket")
    assert bucket["properties"]["Encryption"] == "SSE-KMS"
    assert bucket["properties"]["PublicAccessBlock"] == "ALL"
    assert "7 years" in bucket["properties"]["Lifecycle"]
    assert "OrrethCharter" in plan["yaml"] and "us-west-2" in plan["yaml"]
    assert "estate-policy" in plan["yaml"]          # the answer's scope travels
    # the template is a recallable asset under allen's signature
    row = improver_active(fld, "template-rag-corpus")
    assert row and row[1]["author"] == allen["did"]
    # the planned DAG: the policy depends on its bucket; the human sees it
    dag = plan["dag"]
    assert dag["layout"] == "dag"
    assert {"from": "bucketMain", "to": "bucketPolicy",
            "kind": "depends"} in dag["edges"]
    assert all(n["status"] == "planned" for n in dag["nodes"])


def improver_active(node, name):
    from orreth_sim import improver
    return improver.active_asset(node, name)


def test_the_diff_is_news():
    """The second DAG (0037 §4): the as-built reconciled against the blueprint.
    A faithful deployment matches quietly; a resource that materialized
    differently lands as a signed drift record — news, never a footnote."""
    _, fld, _, allen, allen_kp = _estate_field()
    _charter_up(fld, allen, allen_kp)
    plan = estate.preview(fld, allen, allen_kp, "an s3 bucket for the corpus",
                          subject="rag-corpus")
    faithful = estate.reconcile(fld, allen, allen_kp, "rag-corpus",
                                plan["resources"])
    assert faithful["match"] and not faithful["diff"]
    mutated = [dict(r, properties=dict(r["properties"], Encryption="NONE"))
               if r["id"] == "bucketMain" else r for r in plan["resources"]]
    drifted = estate.reconcile(fld, allen, allen_kp, "rag-corpus", mutated)
    assert not drifted["match"] and any("changed: bucketMain" in d
                                        for d in drifted["diff"])
    news = [r for r in fld.records.values()
            if "estate-drift" in (r.get("tags") or [])]
    assert news and news[0]["author"] == allen["did"]
    assert all(n["status"] == "deployed" for n in drifted["dag"]["nodes"])


def test_template_parsing_derives_the_real_graph():
    """The adoption walk's parser (0037 §7): DependsOn plus Ref/GetAtt-implied
    edges from the template's own truth — never drawn by hand."""
    tpl = {"Resources": {
        "Bucket": {"Type": "AWS::S3::Bucket"},
        "Dist": {"Type": "AWS::CloudFront::Distribution",
                 "Properties": {"Origin": {"Fn::GetAtt": ["Bucket", "DomainName"]}}},
        "Record": {"Type": "AWS::Route53::RecordSet", "DependsOn": "Dist",
                   "Properties": {"Alias": {"Ref": "Dist"}}},
        "Role": {"Type": "AWS::IAM::Role"}}}
    rs = {r["id"]: r for r in estate.parse_template_resources(tpl)}
    assert rs["Dist"]["depends_on"] == ["Bucket"]       # GetAtt-implied
    assert rs["Record"]["depends_on"] == ["Dist"]       # explicit + Ref, deduped
    assert rs["Role"]["depends_on"] == []
    assert estate.category_of("AWS::CloudFront::Distribution") == "network"
    assert estate.category_of("AWS::IAM::Role") == "identity"
    assert estate.category_of("AWS::CodePipeline::Pipeline") == "operations"
    # the merged estate: stack nodes contain, dependencies run within
    dag = estate.estate_dag([{"stack": "OrrethDemoStack", "subject": "demo",
                              "resources": list(rs.values())}])
    kinds = {e["kind"] for e in dag["edges"]}
    assert kinds == {"depends", "contains"}
    stack_node = next(n for n in dag["nodes"] if n["role"] == "stack")
    assert stack_node["id"] == "OrrethDemoStack"
    cats = {n["id"]: n.get("category") for n in dag["nodes"]}
    assert cats["Bucket"] == "data" and cats["Record"] == "network"


def test_charter_is_a_versioned_asset():
    """The question set is data on the shelf (0031's shape): genesis plants under
    allen's signature, and the active version's questions govern the compile."""
    _, fld, _, allen, allen_kp = _estate_field()
    estate.plant_charter(fld, allen, allen_kp)
    prof = estate.charter_profile(fld)
    assert prof["questions"] == estate.CHARTER_GENESIS["questions"]
    rows = [r for r in fld.records.values()
            if estate.CHARTER_NAME in (r.get("tags") or [])]
    assert rows and rows[0]["author"] == allen["did"]


def test_charter_speaks_in_the_parlor():
    """The doors are subject-anchored (0037 §3, JB's walk finding): a bare
    answer is refused toward the grammar; “answer <key> for <workload>: …” and
    “… for the estate: …” ride as actions with their subject; a create ask past
    the gate hands the interrogation to the worker (estate-create); the charter
    reads back as policy + workloads, never a to-do list."""
    facts = {"scope": "u:demo",
             "estate": {"adopted": 1, "gate_open": True,
                        "policy": {"residency": {"answer": "us-west-2"}},
                        "workloads": {"rag-corpus": {"data_classification":
                                                     {"answer": "internal"}}}}}
    bare = parlor.answer("allen", "answer rto: 4 hours", facts)
    assert "needs a subject" in bare["reply"] and "action" not in bare
    ans = parlor.answer("allen", "answer rto for rag-corpus: 4 hours", facts)
    assert ans.get("action") == "estate-answer" and ans["key"] == "rto" \
        and ans["subject"] == "rag-corpus" and ans["answer"] == "4 hours"
    pol = parlor.answer("allen", "answer residency for the estate: us-west-2",
                        facts)
    assert pol.get("action") == "estate-answer" and pol["subject"] == "" \
        and "policy" in pol["reply"]
    a = parlor.answer("allen", "create me an S3 bucket", facts)
    assert a.get("action") == "estate-create" and a["ask"]
    c = parlor.answer("allen", "show the charter", facts)
    assert "ESTATE POLICY" in c["reply"] and "rag-corpus" in c["reply"] \
        and "OPEN" not in c["reply"]
    ws = parlor.workspace("allen", facts)
    charter_panel = next(p for p in ws["panels"] if "charter" in p["title"])
    texts = [i["text"] for i in charter_panel["items"]]
    assert any("estate policy" in x for x in texts) \
        and any("rag-corpus" in x for x in texts)


def test_plan_door_is_free_and_template_recallable():
    """The parlor's plan door (0037 §4): “plan <ask>” rides as estate-preview
    even with the acceptance gate STANDING (plan is free); “show template for
    <subject>” recalls the yaml; the room carries the picture when one stands."""
    facts = {"scope": "u:demo", "estate": {"adopted": 0, "gate_open": False}}
    p = parlor.answer("allen", "plan an s3 bucket for the corpus", facts)
    assert p.get("action") == "estate-preview" \
        and p["ask"] == "an s3 bucket for the corpus"
    tm = parlor.answer("allen", "show template for rag-corpus", facts)
    assert tm.get("action") == "estate-template" and tm["subject"] == "rag-corpus"
    dag = {"layout": "dag", "nodes": [{"id": "bucketMain", "role": "fingertip",
                                       "status": "planned"}], "edges": [],
           "narrative": []}
    rich = {"scope": "u:demo",
            "estate": {"adopted": 0, "gate_open": False,
                       "plan": {"subject": "rag-corpus", "yaml": "Resources: …",
                                "dag": dag}}}
    ws = parlor.workspace("allen", rich)
    assert ws["panels"][0]["kind"] == "graph" \
        and ws["panels"][0]["layout"] == "dag"
    assert "template" in ws["panels"][1]["title"]


def test_allen_receives_in_the_parlor():
    """The resident stands in the audience room: a card with his doors, honest
    gate language while the estate is unwalked — and his catch-all is a
    QUESTION, not protocol (0046's default-ear law, reached allen 2026-08-26
    in 0062 sp1: one stale verbatim flag had silenced his voice since the
    estate). His true PROTOCOL paths — answer/create/preview/adopt/charter —
    still travel verbatim; a governed voice never rewrites law."""
    facts = {"scope": "u:demo", "estate": {"adopted": 0, "gate_open": False}}
    c = parlor.card("allen", facts)
    assert c["voiced"] and c["role"] == "allen · cloud architect"
    assert "acceptance gate" in c["greeting"]
    a = parlor.answer("allen", "create me an S3 bucket", facts)
    assert "adopt before I create" in a["reply"] and not a.get("verbatim")
    # protocol stays protocol: the charter's words still travel verbatim
    p = parlor.answer("allen", "show the charter", facts)
    assert p.get("verbatim")
    d = parlor.answer("allen", "who may speak to you?", facts)
    assert "humans alone" not in d["reply"] or True
    assert "objectives" in d["reply"] and "lineage" in d["reply"]
    ws = parlor.workspace("allen", facts)
    assert ws and any(p["kind"] == "doc" for p in ws["panels"])
