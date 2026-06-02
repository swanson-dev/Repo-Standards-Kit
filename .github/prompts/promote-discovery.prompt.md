---
mode: agent
description: Promote a captured discovery note into structured docs — by default interview the user and draft Proposed ADR(s)/RFC(s) from the note, then flip status raw→promoted; or just flip a note to an existing target (the plain CLI behavior).
---

# promote-discovery

When the user promotes a captured discovery note (`docs/discovery/captured/*.md`, `status: raw`),
**default to drafting the structured docs**, not just flipping a link — raw notes rarely contain an
ADR's rationale (drivers, options, the *why*), so you must elicit it (ADR-0015).

**1. Pick the note:** `python scripts/promote-discovery/promote_discovery.py list` → read the chosen note.

**2. Identify candidates, then confirm.** From the note, decide what it implies — a **decision**
(→ ADR), an **open time-boxed investigation** (→ RFC), several, or none. Ask the user to confirm the
candidate list before drafting; never invent ADRs they didn't intend. (None → plain flip below.)

**3. Interview** conversationally for the gaps the template needs — ask a few focused questions, one
topic at a time:
- ADR → context/problem · decision drivers · options considered · the decision **and why** · consequences.
- RFC → the exact question · time-box · approach · what a good answer looks like.

**4. Scaffold:** `python scripts/new-doc/new-adr.py "<title>"` or
`python scripts/new-doc/new-rfc.py "<question>"`. Note the created path it prints (and the ADR index row).

**5. Draft the body** from the note + answers (ADRs stay `status: Proposed`); paste the ADR index row
into `docs/decisions/README.md`.

**6. Promote:** `python scripts/promote-discovery/promote_discovery.py promote <note-path> --to <new-doc-path>`.
Both args required; `<target>` must be a relative repo path (no absolute, no `..`).

**Plain-flip fallback (the CLI standard):** if the user just wants to record a link, or the note
implies no decision, skip the interview and run the flip directly:
`python scripts/promote-discovery/promote_discovery.py promote <path> --to <target>`. The script only
rewrites two frontmatter lines — it never drafts anything.

After promoting, verify the frontmatter diff and commit the flipped note alongside the drafted
ADR/RFC so the `promoted_to:` target exists (the `discovery` check fails otherwise). Promotion is
monotonic — the script refuses to re-promote.

**Note for Copilot users:** Claude Code's SessionStart hook auto-pings when raw items exist at session
open; Copilot Chat has no equivalent. Run `list` periodically to check the inventory yourself.
