# PROVENANCE: Fable 5 (claude-fable-5) — 0061 sp1, the declared shape · 2026-08-25
"""The Living Atlas (0061): the machine's schematic, declared as data.

The atlas leaves the paper: `docs/design/the-objective-atlas.md` kept the
interop map honest only by discipline; these declarations keep it honest by
LAW. The shape below plants as shelf craft (`atlas-governance-flow`,
`atlas-human-flow`) — the machine's own schematic is a governed, editable
part of the machine, tunable at the gates like the dictionary — and the
worker's /atlas door serves the LIVE heads first, genesis beneath, composed
with the topology and every installed capability's own manifest. The life
(edge lighting) is never declared: it is measured from real request
activity, so no edge ever glows that did not carry something.

Every label is first-contact surface — quinn-grade plain words only; the
canon terms it uses are dictionary words, and the glass makes them doors.

Node grammar:  id · label · sub (one plain line) · lane (human|organs|kernel)
               · door (what a click opens: res:<name> | view:<tab> |
                 parlor:<name>)
Edge grammar:  from · to · label · kinds (the REQUEST KINDS whose real
               activity lights this edge — empty means structural, lit dim)
"""

GOVERNANCE_FLOW = {
    "nodes": [
        {"id": "becky", "label": "becky", "lane": "organs",
         "sub": "signs everyone in — nothing joins without her word",
         "door": {"res": "becky"}},
        {"id": "vigil", "label": "vigil", "lane": "organs",
         "sub": "watches for tampering; can only raise a hand",
         "door": {"res": "vigil"}},
        {"id": "steward", "label": "the steward", "lane": "organs",
         "sub": "keeps memory healthy — the breath",
         "door": {"res": "steward"}},
        {"id": "grace", "label": "grace", "lane": "organs",
         "sub": "proposes better craft from the evidence",
         "door": {"res": "grace"}},
        {"id": "vera", "label": "vera", "lane": "organs",
         "sub": "grades finished work — flags, never acts",
         "door": {"res": "vera"}},
        {"id": "studio", "label": "the studio", "lane": "organs",
         "sub": "reads your ask and drafts the plan",
         "door": {"res": "studio"}},
        {"id": "librarian", "label": "the librarian", "lane": "organs",
         "sub": "finds and files knowledge — every answer cited",
         "door": {"parlor": "librarian"}},
        {"id": "ada", "label": "ada", "lane": "organs",
         "sub": "keeps the AI minds and their terms",
         "door": {"res": "ada"}},
        {"id": "charlotte", "label": "charlotte", "lane": "organs",
         "sub": "keeps the outside tools — tested and tracked",
         "door": {"res": "charlotte"}},
        # 0062 made these two flow-carriers — declared here on JB's find
        # (2026-08-27: "allen is a resident and is NOT in the Atlas?")
        {"id": "allen", "label": "allen", "lane": "organs",
         "sub": "grows what the universe needs — tool bodies and estates, "
                "every act a deed",
         "door": {"res": "allen"}},
        {"id": "quinn", "label": "quinn", "lane": "organs",
         "sub": "walks every room as a newcomer; what confuses her is "
                "filed for fixing",
         "door": {"view": "gov"}},
        {"id": "the-record", "label": "the signed record", "lane": "kernel",
         "sub": "everything that happens is filed here, forever",
         "door": {"view": "pulse"}},
        {"id": "the-plane", "label": "the model plane", "lane": "kernel",
         "sub": "every AI thought passes this metered door",
         "door": {"view": "stable"}},
        {"id": "the-farm-gate", "label": "the tool door", "lane": "kernel",
         "sub": "every outside tool call passes here, on the meter",
         "door": {"view": "farm"}},
        {"id": "the-epoch", "label": "the machine's names", "lane": "kernel",
         "sub": "a new exact name cut at every change of its parts",
         "door": {"view": "obs"}},
    ],
    "edges": [
        {"from": "becky", "to": "the-record",
         "label": "every join and lease, filed", "kinds": ["join", "field-join"]},
        {"from": "vigil", "to": "the-gates",
         "label": "raises drift or tampering to you", "kinds": ["drift", "witness"]},
        {"from": "steward", "to": "the-record",
         "label": "compresses the old, keeps what matters", "kinds": ["breath"]},
        {"from": "grace", "to": "the-gates",
         "label": "an improved version waits for your word",
         "kinds": ["improvement", "craft-edit", "design-change"]},
        {"from": "the-gates", "to": "the-epoch",
         "label": "an adopted release renames the machine",
         "kinds": ["release", "experiment"]},
        {"from": "vera", "to": "the-gates",
         "label": "her gradings wait at your gate", "kinds": ["assay", "calibration"]},
        {"from": "studio", "to": "the-gates",
         "label": "the drafted plan waits for your approval",
         "kinds": ["objective"]},
        {"from": "librarian", "to": "the-record",
         "label": "knowledge lands cited, untrusted until proven",
         "kinds": ["subscription", "commission"]},
        {"from": "ada", "to": "the-plane",
         "label": "pins each mind's terms; drift is caught", "kinds": ["dial"]},
        {"from": "charlotte", "to": "the-farm-gate",
         "label": "probes, pins, and tends each tool", "kinds": ["service"]},
        {"from": "allen", "to": "the-farm-gate",
         "label": "grows a tool's body; charlotte plants the wire",
         "kinds": ["service"]},
        {"from": "allen", "to": "the-record",
         "label": "every estate change a deed, start to finish",
         "kinds": ["estate-adopt"]},
        {"from": "quinn", "to": "the-gates",
         "label": "her walk's confusions wait as filed reports",
         "kinds": ["uat-report"]},
        {"from": "the-plane", "to": "the-record",
         "label": "every thought metered and filed", "kinds": []},
        {"from": "the-farm-gate", "to": "the-record",
         "label": "every tool call on the record", "kinds": []},
    ],
}

HUMAN_FLOW = {
    "nodes": [
        {"id": "you", "label": "YOU", "lane": "human",
         "sub": "the origin — nothing big happens without you",
         "door": {"view": "inbox"}},
        {"id": "the-composer", "label": "your ask", "lane": "human",
         "sub": "Objectives — ask in your own words",
         "door": {"view": "obj"}},
        {"id": "the-gates", "label": "your Inbox", "lane": "human",
         "sub": "decisions wait here — silence never approves",
         "door": {"view": "inbox"}},
        {"id": "the-parlor", "label": "the parlor", "lane": "human",
         "sub": "talk to any resident; answers are cited and kept",
         "door": {"parlor": "librarian"}},
        {"id": "the-craft-door", "label": "the craft room", "lane": "human",
         "sub": "read and edit the words the machine runs on",
         "door": {"view": "gov"}},
        {"id": "the-bell", "label": "the bell", "lane": "human",
         "sub": "emails you when something needs you — even away",
         "door": {"view": "obs"}},
    ],
    "edges": [
        {"from": "you", "to": "the-composer",
         "label": "you ask; a plan comes back", "kinds": ["objective"]},
        {"from": "the-composer", "to": "studio",
         "label": "your words are read whole", "kinds": ["objective"]},
        {"from": "you", "to": "the-gates",
         "label": "you decide; the machine proceeds", "kinds": ["question"]},
        {"from": "you", "to": "the-parlor",
         "label": "you ask; the resident fetches", "kinds": ["parlor"]},
        {"from": "the-parlor", "to": "librarian",
         "label": "the lens of the universe's mind", "kinds": ["parlor"]},
        {"from": "you", "to": "the-craft-door",
         "label": "your edit lands as a new version", "kinds": ["craft-edit"]},
        {"from": "the-bell", "to": "you",
         "label": "one email, content-minimal, on the record", "kinds": ["ring"]},
    ],
}

FLOWS = {"atlas-governance-flow": GOVERNANCE_FLOW,
         "atlas-human-flow": HUMAN_FLOW}
