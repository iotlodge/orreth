# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp5, the person · 2026-09-11
"""The person's laws (0070 §3.4): a name is never reissued, a person's
strokes are theirs alone, the anonymous portrait never leaks a person's
words — and a person's claim is signed under their OWN key."""
from orreth_sim import crypto, persons, profile
from orreth_sim.world import build


def test_names_have_a_shape():
    assert persons.valid_name("jb")
    assert persons.valid_name("maria-h_2")
    assert not persons.valid_name("J B")
    assert not persons.valid_name("x")
    assert not persons.valid_name("9lives")
    assert not persons.valid_name("")


def test_a_name_is_never_reissued():
    w = build()
    b = {"did": w.becky.did, "scope": "u:demo"}
    first = persons.make_person_record(b, w.becky.kp, "u:demo", "jb",
                                       "did:key:zFirstJB")
    w.universe.write(first)
    later = persons.make_person_record(b, w.becky.kp, "u:demo", "jb",
                                       "did:key:zImpostor")
    w.universe.write(later)
    reg = persons.registry(w.universe)
    assert reg["jb"]["did"] == "did:key:zFirstJB"     # the first owns it


def test_whose_portrait_a_stroke_belongs_to_is_one_law():
    a = ["profile", "creator", "person:jb"]
    b = ["profile", "creator", "person:guest"]
    c = ["profile", "creator"]
    w = ["profile", "withdrawn", "person:jb"]
    assert profile.stroke_visible(a, "jb") and not profile.stroke_visible(b, "jb")
    assert not profile.stroke_visible(c, "jb")        # anonymous is not yours
    assert profile.stroke_visible(c, "") and not profile.stroke_visible(a, "")
    assert profile.stroke_visible(w, "")              # withdrawals always count
    assert profile.stroke_visible(w, "jb")


def test_a_persons_claim_signs_under_their_own_key():
    """The debt itself: the record's AUTHOR is the person's did, verified
    under the person's own public key — not a floor seat's."""
    w = build()
    kp = crypto.KeyPair(seed=b"\x07" * 32)            # the custody's seed
    did = crypto.did_key_for(kp.public)
    w.becky.nanda.register(did, kp.public)
    rec = profile.make_claim({"did": did, "scope": "u:demo"}, kp, "u:demo",
                             "I toast with cocoa", asserted_by="human",
                             person="jb")
    assert rec["author"] == did
    assert "person:jb" in rec["tags"]
    w.universe.write(rec)     # the node verifies the person's OWN signature
    # ...and the same seed is the same self, forever (covenant rule 1)
    assert crypto.did_key_for(crypto.KeyPair(seed=b"\x07" * 32).public) == did
