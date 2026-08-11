# PROVENANCE: Fable 5 (claude-fable-5) — 0050 sp1, the shelf · 2026-08-11
"""The machine's speech (0050): sentences as craft, facts as slots.

Wave 1 (JB's lock L3): the gate cards and the parlor's system notes. Each
genesis template mirrors the code literal it replaces BYTE-FOR-BYTE when
rendered (the parity law) — sp1 changes where the words LIVE, never what
they say; sp2 changes what they say, through the gates. Facts ride ⟦slots⟧
and an unfilled slot refuses to render, naming what it lacks — so an edited
sentence can never silently lie about data. Conditional FRAGMENTS (a ref
that may be absent, a why that may be empty) are their own tiny templates:
the deciding stays code, the words stay shelf.

The refusal family is deliberately ABSENT (0002 §4: refusal wears one face,
identical across causes — it enters the shelf later as a single guarded
object with that law encoded beside it, never piecemeal)."""
import re as _re

SENTENCES = {
    # ---- the gate cards — WAITING ON YOU ------------------------------------
    "card-calibration":
        "⚖ the human and the examiner disagree — ⟦pairs⟧ shared work(s), "
        "mean gap ⟦mean_gap⟧ (bar ⟦bar⟧): ⟦examples⟧",
    "card-calibration-held":
        "the yardsticks argue — a card, never a lever; the word is yours",
    "card-verify-blind":
        "👁 the standing verify cannot SEE /⟦path⟧ (⟦looks⟧ looks — last: "
        "⟦error⟧). The observer is blind, NOT the deed altered — check the "
        "wire; the watchman keeps looking.",
    "card-verify-blind-reply":
        "a note, never a lever — nothing is known to be wrong",
    "card-verify-tamper":
        "the standing verify found /⟦path⟧ altered — the walk-back waits "
        "for your word (0042 · 0044 sp3)",
    "card-feedback-closure":
        "💬 your 👎 was heard — ⟦outcome⟧",
    "card-feedback-closure-ref":                  # fragment: only when a ref exists
        " → ⟦ref⟧…",
    "card-feedback-closure-why":                  # fragment: only when words exist
        ": ⟦why⟧",
    "card-feedback-closure-reply":
        "the outcome, named back to your word",
    "card-reflex-escalation":
        "⚡ ⟦event⟧ — [⟦ref⟧…]",
    "card-reflex-escalation-held":
        "a reflex escalated — detection wears no levers; the word is yours",
    "reply-thumb-heard":
        "heard — on the record",
    # ---- the parlor's system notes ------------------------------------------
    "note-dispatcher":
        "⚡ the dispatcher chose «⟦flavor⟧» — ⟦why⟧ [choice ⟦choice⟧…]",
    # ---- born human (0050 sp2 — genesis entered already plain) --------------
    "card-calibration-pair":
        "«⟦work⟧» — you said ⟦human⟧, the examiner said ⟦examiner⟧",
}

# 0050 sp2 — how an outcome is SAID to the human who caused it: the routing's
# machine words (thumb.OUTCOME_FOR and kin) translated for the closure card.
# Total over thumb.OUTCOMES, suite-held — a new outcome without its sentence
# is a conformance failure, never a card mumbling machine-speak.
OUTCOME_SPOKEN = {
    "repair-staged": "a repair objective now waits for your approval",
    "commissioned": "Orreth is building the skill you found missing — "
                    "it will wait for your welcome",
    "evidenced": "your words were filed as evidence toward improving "
                 "that craft",
    "referred": "you were pointed to the keeper whose charter it is",
    "parked": "Orreth could not classify it yet — your words stay open, "
              "never dropped",
    "adopted": "the change you argued for was adopted",
    "repaired": "the repair completed",
    "declined": "it was declined, with the reason on the record",
}


def render(template: str, **slots) -> str:
    """The strict render: every ⟦slot⟧ filled or the sentence REFUSES,
    naming what it lacks — the machine's speech never guesses at facts."""
    out = str(template)
    for k, v in slots.items():
        out = out.replace(f"⟦{k}⟧", str(v))
    unfilled = sorted(set(_re.findall(r"⟦(\w+)⟧", out)))
    if unfilled:
        raise ValueError(f"unfilled slot(s): {', '.join(unfilled)}")
    return out
