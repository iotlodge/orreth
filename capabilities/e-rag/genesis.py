# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0072 sp1, the grammar grows · 2026-09-11
"""E-RAG — One Place (0072): the first tenant of the kernel's rich rooms.

THE L1 LAW, lived: this file brings NO application and NO code the glass
will run — it brings a DECLARATION. «Give me a chat room wired to the ask
door; give me a sources room over the estate.» The kernel renders; this
capability configures. The 0055 law survives whole: declarations never
code, foreign JavaScript never loads, and every world that ever declares a
chat inherits the same room.

(The folder-install era this file still lives in is the KCR-0002 wound —
sp4 of this same dive replaces the road with the signed box; the
declaration below is exactly what that box will carry.)
"""

CRAFT = {}   # E-RAG's words already live on the shelf (personas, routing
             # standards, guardrails — planted by their own dives)

# the eleven, as the ask door's menu speaks them (variants.MENU is the one
# truth; the suite holds this list to it so the selector can never drift)
VARIANTS = ["auto", "naive", "advanced", "hierarchical", "multimodal",
            "multi-agent", "reasoning-first", "memory-augmented", "graph",
            "hybrid", "hyde", "corrective"]

MANIFEST = {
    "key": "e-rag",
    "name": "E-RAG · One Place",
    "emoji": "🎯",
    "resident": "librarian",
    "floor": "u:demo/e:rag",
    "port": 4513,
    "law": ("one place: ask in your own words, watch the answer wear its "
            "thinking, and see exactly what the machine may read — every "
            "byte through the governed doors, never a side channel"),
    "door": "e-rag",
    "group": "One Place",
    "floors": [{"scope": "u:demo/e:rag", "shared": True}],
    "crew": [],          # no new processes — the estate already stands
    "view": [
        {"kind": "chat",
         "label": "the chat canvas",
         "ask_port": 4500,
         "placeholder": "ask across everything E-RAG holds…",
         "selector": VARIANTS},
        {"kind": "workspace",
         "label": "the workspace — tune the eleven",
         "ask_port": 4500,
         "ws_port": 4500},
        {"kind": "sources",
         "label": "the estate — what E-RAG can read",
         "farm_port": 4500},
    ],
}
