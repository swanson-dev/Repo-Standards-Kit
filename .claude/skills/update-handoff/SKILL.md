---
name: update-handoff
description: Generate a draft ai/handoff.md from git state — frontmatter and "Recently touched" pre-filled; TL;DR, Open threads, and Don't do for the author.
---

# update-handoff

## When to invoke

Use when the user is about to end a session that produced meaningful change —
typically to satisfy the `AGENTS.md` end-of-session contract item "Write `ai/handoff.md`
for the next session", or because the `update-handoff` Stop hook surfaced a reminder
("N commits + M modified files since last handoff").

## How to invoke

Run from the repo root:

`python scripts/update-handoff/update_handoff.py`

Add `--force` to overwrite an existing handoff. The script:
- pre-fills frontmatter (`written:` now, `written_by:` from `git config user.name`),
- pre-fills "Recently touched" from `git log` since the prior handoff,
- leaves TL;DR, Open threads, and Don't do as placeholders for the author.

## After scaffolding

Open `ai/handoff.md`. Write the TL;DR in plain English (1–3 sentences). Replace
the Open threads and Don't do placeholders with the real items. Commit alongside
the slice's other end-of-session updates (`ai/current-state.md`, etc.).
