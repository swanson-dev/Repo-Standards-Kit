---
name: standard-compact-snapshot
description: Capture a compact pre-compaction checkpoint into ai/handoff.md.
---

# standard-compact-snapshot

## When to invoke

Use immediately before context compaction or a long interruption when preserving
the exact working state matters more than a polished end-of-session handoff.

## How to invoke

Run from the repo root:

`python scripts/update-handoff/update_handoff.py --compact-snapshot --force`

The script writes `ai/handoff.md` with compact checkpoint sections for goal,
status, touched files, tests, decisions, blockers, "Don't redo", and next action.

## After running

Fill the placeholders with the current working context before compaction
continues.
