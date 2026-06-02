---
name: promote-discovery
description: Promote a captured discovery note into structured docs — by default interview the user and draft Proposed ADR(s)/RFC(s) from the note, then flip status raw→promoted; or just flip a note to an existing target (the plain CLI behavior).
---

# promote-discovery

## When to invoke

Use when:
- The SessionStart hook surfaced an "N raw items" reminder and you want to act on the inventory.
- A captured discovery note (`docs/discovery/captured/*.md`, `status: raw`) holds a decision or an
  open question that should become a durable doc.
- You just used a discovery note's content in a structured doc and need to record the trace.

## The default: interactive decision-shaping (ADR-0015)

When **you (an AI agent)** promote a raw note, **default to drafting the structured docs**, not just
flipping a link. Raw notes rarely contain an ADR's rationale (drivers, options, the *why*) — so you
must *elicit* it. Run this flow:

**1. Pick the note.**
`python scripts/promote-discovery/promote_discovery.py list` → choose a `status: raw` note and read it.

**2. Identify candidates, then confirm.** From the note, decide what it implies:
- a **decision already made / that needs making** → an **ADR**;
- an **open, time-boxed investigation** (a question with no answer yet) → an **RFC**;
- a note may imply **several**, or **none** (→ go to the plain-flip fallback).

Use `AskUserQuestion` to confirm the candidate list with the user *before* drafting — never invent
ADRs the user didn't intend.

**3. Interview — only the gaps the template needs.** For each confirmed candidate, ask the user
(via `AskUserQuestion`, one focused question at a time) for what the note doesn't already answer:
- **ADR** → Context/problem · Decision Drivers · Considered Options · Decision Outcome **and the
  rationale (the "because")** · Consequences (good/bad/neutral).
- **RFC** → the exact question · time-box · approach/method · what a good answer looks like.

**4. Scaffold** (don't hand-write the skeleton):
- ADR → `python scripts/new-doc/new-adr.py "<decision title>"`
- RFC → `python scripts/new-doc/new-rfc.py "<question>"`

Capture the **created path** the script prints (and the ADR index row it prints).

**5. Draft the body** of the scaffolded file from the note + interview answers. Leave ADRs at
`status: Proposed` (the user accepts later; an Accepted ADR is immutable). Paste the printed ADR
index row into `docs/decisions/README.md`.

**6. Promote** — flip the note and record the trace, once per target:
`python scripts/promote-discovery/promote_discovery.py promote <note-path> --to <new-doc-path>`

`<note-path>` and `--to <target>` are both required; `<target>` must be a relative repo path (no
absolute, no `..`). If a note fed **multiple** docs, set `promoted_to:` to the primary one and
reference the others in that doc.

## Plain-flip fallback (the CLI standard)

If the user just wants to record a link (the note's content already went into an existing doc), or
the note implies no decision, skip the interview and run the flip directly — this is the unchanged
CLI behavior:

`python scripts/promote-discovery/promote_discovery.py promote <path> --to <target>`

The script never drafts anything; it only rewrites two frontmatter lines. The SessionStart `--check`
hook calls `list --check` only (silent, read-only) — the interview never runs in the hook.

## After promoting

- Verify the note's frontmatter diff (`status: promoted`, `promoted_to:` set; everything else
  preserved). Commit the flipped note **alongside** the drafted ADR/RFC so the trace target exists —
  the `discovery` standards check fails if `promoted_to:` points at a missing file.
- Promotion is **monotonic** — the script refuses to re-promote an already-`promoted` note. To
  un-promote, hand-edit the file and explain why in the commit message.
