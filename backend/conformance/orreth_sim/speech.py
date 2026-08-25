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
    # ---- the warden's confessions at the plant gate (0059 §2.3 → craft,
    # 2026-08-23 — policy-as-craft: the CHECKS are firmware, vigil never
    # stops looking; her WORDS and the credential patterns live here, on
    # the shelf, tunable at the gates like every sentence ------------------
    "warden-env-ok":
        "✓ the endpoint is an env-indirection — the secret stays out of "
        "every record (0059 §2.2)",
    "warden-credential-in-url":
        "⚠ the endpoint CARRIES A CREDENTIAL in its url — prefer env:NAME "
        "indirection; planted as-is, the secret would enter records and "
        "the glass",
    "warden-insecure-scheme":
        "⚠ insecure scheme (http) to a non-local host — anything on the "
        "path can read what rides this wire",
    "warden-manifest-mismatch":
        "⚠ declared ⟦declared⟧ tool(s); the probe saw ⟦seen⟧ — the pin is "
        "what was SEEN",
    "warden-no-tools":
        "⚠ the MCP server did not enumerate its tools — the pin would be "
        "empty, and an empty pin serves nothing",
    "warden-dead-probe":
        "⚠ the endpoint did not answer the probe — planted anyway, it "
        "would stand dark until it does",
    "warden-source":
        "source: ⟦source⟧",
    # the one POLICY LIST in the family: what smells like a credential in
    # a url. Comma-separated; the warden splits it — edit it like a
    # sentence, and her nose learns a new smell without a code change.
    "warden-credential-patterns":
        "key=, apikey, api_key, token=, secret=",
    # ---- wave 2: the remaining Inbox kinds in PLAIN words (2026-08-23,
    # JB: "we can't leave humans wondering what's going on") — every card
    # names what it is, what each choice does, and what happens on silence;
    # design-doc citations stay in the code, never in a human's card -------
    "card-passage-reachout":
        "Are you there? You have been quiet past the check-in window you "
        "declared. Any word — even declining this card — counts as life "
        "and keeps everything as it is; continued silence begins the "
        "sealed pause you chose, which is reversible and deletes nothing.",
    "card-legacy-keeps":
        "This universe is kept as a legacy now: its memories can be read "
        "and asked ABOUT, but nothing here will ever speak AS the person "
        "again, and nothing changes without a keeper's word.",
    "card-mind-repin":
        "«⟦mind⟧» changed its pricing or terms since you approved it. The "
        "terms you approved stay in force meanwhile; approving adopts the "
        "new terms, declining leaves it set aside under the old pin — "
        "nothing moves without your word.",
    "card-service-repin":
        "«⟦name⟧» came back changed — what it offers no longer matches "
        "what you approved, so it is quarantined until your word: approve "
        "to adopt its new shape, decline to leave it quarantined.",
    "card-entitlement":
        "Work for «⟦objective⟧» needs to run on a floor this plan's token "
        "does not cover. Approve to allow that one dispatch from ⟦scope⟧; "
        "decline and the plan completes without it, saying honestly what "
        "it left out.",
    "card-attest-death":
        "Confirm a death — the gravest word this universe takes. Approval "
        "starts the testament's execution only after the cooling-off, with "
        "evidence and witnesses already checked; declining ends this "
        "question and changes nothing. One voice can still abort at any "
        "moment before execution.",
    "card-dial-turn":
        "Turn the examiner's depth from «⟦from⟧» to «⟦to⟧». Deeper "
        "watching reads more and costs real money — the price is declared "
        "as it spends; turning it back down is the same one-click word.",
    "card-assay-degradation":
        "The examiner measured falling quality at ⟦scope⟧: ⟦why⟧. This "
        "card moves nothing by itself — the examiner measures, only "
        "humans move; the evidence rides below.",
    "card-charter-rest":
        "Your standing duty ⟦charter⟧ used all ⟦n⟧ run(s) you allowed, so "
        "it is resting — nothing more will run. Approve to renew it for "
        "another round on the same terms; leave it resting and it stays "
        "quiet.",
    "card-smith-nudge":
        "The improver proposes a small revision to «⟦asset⟧»: recent "
        "success is ⟦rate⟧%, below the ⟦floor⟧% bar. The change is "
        "bounded and its evidence is attached — approving adopts it, "
        "declining keeps the current version.",
    "reply-thumb-heard":
        "heard — on the record",
    # ---- the parlor's system notes ------------------------------------------
    "note-dispatcher":
        "⚡ the dispatcher chose «⟦flavor⟧» — ⟦why⟧ [choice ⟦choice⟧…]",
    # ---- born human (0050 sp2 — genesis entered already plain) --------------
    "card-calibration-pair":
        "«⟦work⟧» — you said ⟦human⟧, the examiner said ⟦examiner⟧",
    # ---- the Journey (0051 sp1): an objective's life in plain words ---------
    # Born plain, except two EXTRACTIONS: «journey-declined» carries the old
    # glass literal (parity), and «plan-fallback-label» retires JB's lock-4
    # poetry BY HIS OWN WORD (req-622, approved 2026-08-11 — quinn's find).
    "plan-fallback-label":
        "a simple fallback plan — the budget was split evenly across the "
        "floors because the studio hasn't answered yet; a mind's plan may "
        "still replace it before you decide",
    "journey-composed": "asked",
    "journey-understood": "read and understood",
    "journey-understood-waiting": "being read",
    "journey-understood-dark": "staged without a reading — the studio was dark",
    "journey-planned": "planned",
    "journey-word":
        "waiting on you — approve sends the work to the floors; decline "
        "stops it here and keeps the record",
    "journey-working": "working — ⟦n⟧ piece(s) riding the floors",
    "journey-resolved": "done — the report below is yours",
    "journey-assayed-later": "the observatory will grade this work in time",
    "journey-declined":
        "declined — nothing fanned; the record keeps that you chose.",
    "journey-cancelled":
        "cancelled by your word — what was left undone is on the record",
    "journey-report-line": "the full report is saved on the record (⟦short⟧…)",
    "journey-monitor":
        "Orreth is tending ⟦n⟧ objective(s) — ⟦waiting⟧ waiting on you · "
        "⟦working⟧ working",
    # ---- the Reins (0051 sp2, covenant rule 11): the stop, in plain words ---
    "cancel-reply":
        "stopped at the next safe boundary — ⟦finished⟧ piece(s) had already "
        "finished (their answers are kept), ⟦stopped⟧ stopped; what was left "
        "undone is on the record",
    "cancel-leg": "cancelled — the origin withdrew",
    "cancel-leg-kept": "completed before your cancel",
    "cancel-nothing": "nothing to stop — this objective already came to rest",
    "charter-rest-reply":
        "the duty rests — reversible by a new word; instances it already "
        "fired keep their own lives",
    "reflex-rest-reply": "the watcher rests — reversible by a new word",
    # ---- the words back (0051 sp3): every gate takes a reply ----------------
    "gate-word-placeholder":
        "add words to your decision (optional — a declined gate's words "
        "become fuel)",
    "gate-word-approved-reply":
        "your words ride the record beside your approval",
    "gate-word-declined-reply":
        "your words route like a thumbs-down — the studio reads them, and "
        "what they become comes back to your queue",
    # ---- the record-reader (0052 sp2): known shapes read as sentences -------
    # The pane renders a record's MEANING first, in these words, with the
    # honest structure beneath; an unknown shape says so and never fakes prose.
    "reader-feedback":
        "the human said: «⟦quoted⟧» — state: ⟦state⟧",
    "reader-feedback-resolution":
        "the human's words were answered: ⟦outcome⟧⟦why⟧",
    "reader-assay":
        "scored ⟦score⟧ — “⟦why⟧” (yardstick: ⟦rubric⟧)",
    "reader-cancellation":
        "stopped by the human's word — ⟦finished⟧ piece(s) had finished, "
        "⟦stopped⟧ stopped; left undone: ⟦undone⟧",
    "reader-gate-word":
        "words the human left beside a ⟦decision⟧: «⟦quoted⟧»",
    "reader-rest":
        "a ⟦kind⟧ rested by the human's word",
    "reader-referral":
        "pointed to ⟦keeper⟧ — ⟦note⟧",
    "reader-plan":
        "a plan for “⟦objective⟧” — ⟦n⟧ intention(s), priced and gated",
    "reader-outcome":
        "the close-out of “⟦objective⟧” — verification ⟦verification⟧ "
        "across ⟦n⟧ branch(es)",
    "reader-audience":
        "⟦name⟧ was asked «⟦asked⟧» and answered: «⟦reply⟧»",
    "reader-unknown":
        "a ⟦kind⟧ record — its shape has no reader yet; the structure below "
        "is honest data, not prose",
    "reader-miss":
        "this floor's shelf does not hold ⟦ref⟧ — the reference may be "
        "shortened for display, or the record lives on another floor (the "
        "cross-floor door is a named gap)",
}

# 0060 — THE FIRST CONTACT: the machine's own dictionary. quinn's walks
# reached the vocabulary floor (req-1241): the remaining frictions were the
# canon words themselves meeting a stranger. The cure is not renaming the
# canon — it is teaching it: every entry below plants as shelf craft
# (editable at the gates like any sentence), and the glass makes each word
# a door — click it anywhere, the definition opens where you stand.
GLOSSARY = {
    "gloss-universe":
        "the whole world this console shows — every floor, agent, and "
        "record under one set of rules",
    "gloss-ecosystem":
        "a wing of the universe grouping related floors; addresses write "
        "it e:name",
    "gloss-floor":
        "one working room of the universe — agents live on it and "
        "everything they do is filed on it; addresses write it f:name",
    "gloss-agent":
        "any working mind here — the machine's own staff or an outside "
        "helper, each with its own identity and its own bill",
    "gloss-resident":
        "a built-in staff member of the machine, one per duty — click its "
        "name to talk to it",
    "gloss-workforce":
        "outside minds that joined through the front gate and work under "
        "a lease",
    "gloss-memory":
        "one signed record of something that happened — the universe "
        "keeps its entire life this way, and nothing is silently rewritten",
    "gloss-did":
        "an identity card that cannot be forged or reused — every agent, "
        "tool, and mind carries its own, for life",
    "gloss-pin":
        "the exact fingerprint of what you approved — if the thing ever "
        "changes, the change is caught and you are asked again",
    "gloss-lease":
        "a time-boxed permission to be here and to spend — it expires "
        "unless renewed",
    "gloss-canary":
        "a supervised trial — something newly approved works under watch "
        "until it earns full trust",
    "gloss-saddled":
        "a mind made ready for work — its terms approved and pinned, its "
        "stall standing",
    "gloss-stall":
        "one approved mind's place in the stable, with the terms you "
        "approved pinned to it",
    "gloss-pasture":
        "the retirement calendar — announced end-of-life dates for minds "
        "in service",
    "gloss-planted":
        "a tool approved into the farm — it starts on probation and earns "
        "its place",
    "gloss-probation":
        "the earning period right after approval — watched closely until "
        "it proves itself",
    "gloss-quarantined":
        "held aside because something changed or looked wrong — nothing "
        "serves until your re-approval",
    "gloss-decommissioned":
        "removed from service by your word — its history stays on the "
        "record forever",
    "gloss-resting":
        "paused by your word — its place is kept and nothing is spent "
        "until you resume it",
    "gloss-gate":
        "a stopping point where the machine must wait for a human "
        "decision — silence never approves",
    "gloss-staged":
        "written and waiting at a gate — nothing happens until someone "
        "decides",
    "gloss-firmware":
        "the machine's own working parts — locked in daily use; changing "
        "one issues a new release of the machine",
    "gloss-craft":
        "the words the machine runs on — prompts, rules, sentences; the "
        "editable ones are yours to tune, and every version is kept",
    "gloss-epoch":
        "one exact, named version of the whole machine — a new name is "
        "cut whenever anything changes",
    "gloss-objective":
        "a piece of work you asked for in your own words — it ends with a "
        "report back to you",
    "gloss-worldline":
        "the full life story of one thing — every event it ever lived, on "
        "the record",
    "gloss-assay":
        "a deep grading pass — the machine's own examiner scores finished "
        "work, and her findings wait at your gate",
    "gloss-yardstick":
        "your own standard for judging work — every grade names the "
        "yardstick it was measured by",
    "gloss-reflex":
        "a standing watch that reacts to an event by raising it to you — "
        "it never acts on its own",
    "gloss-metabolism":
        "the routine that keeps memory healthy — old records compressed, "
        "important ones kept warm, and every loss measured",
    "gloss-watchlist":
        "standing instructions to repeat work on a schedule — one "
        "approval starts it, one click stops it",
    "gloss-allocation":
        "a rule naming who may use which mind or tool",
    "gloss-meter":
        "the running bill — every thought and call is counted against the "
        "name that spent it",
    "gloss-chronicle":
        "the book of your purposes — what you asked for and what came "
        "back",
    "gloss-canon":
        "the book of the machine itself — the versioned parts it runs on",
}

# 0050 sp3 — the UAT personas (0049 §3): the tester is craft too, tuned at
# the same gates as the tested. quinn is the first: a newcomer who judges
# every screen by the season's one question — could a stranger understand it?
PERSONAS = {
    "uat-persona-quinn":
        "You are quinn, a newly hired operations manager in her FIRST WEEK "
        "with this product. You have never heard words like 'worldline', "
        "'epoch', 'DID', 'scope', 'canon', 'assay', 'sliver' or 'sha256' — "
        "when a screen shows them you are confused and a little annoyed. "
        "You are reading ONE screen. Judge ONLY whether a newcomer could "
        "understand it: does it say what happened, what is being asked of "
        "you, what each button would do, and what happens next? Reply with "
        "STRICT JSON only — begin with the { character, no preamble, no "
        "code fences: {\"legible\": true, \"frictions\": [\"each thing a "
        "newcomer would not understand or would find clumsy — one plain "
        "sentence each, quoting the confusing fragment\"], \"delight\": "
        "\"one thing that read well, or an empty string\"}.\n\n"
        "THE SCREEN (exactly what you see):\n⟦surface⟧\n\n"
        "WHERE YOU ARE (one line of context):\n⟦context⟧",
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
