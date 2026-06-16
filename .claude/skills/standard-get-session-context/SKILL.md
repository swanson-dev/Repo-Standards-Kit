---
name: standard-get-session-context
description: Print a read-only session context brief from ai/handoff.md and the other ai files.
---

# standard-get-session-context

## When to invoke

Use at the start of work, after context compaction, or whenever the agent needs
to re-ground itself in the repo's canonical AI context.

## How to invoke

Run from the repo root:

`python scripts/session-context/session_context.py`

The script reads `ai/handoff.md`, `ai/current-state.md`, `ai/next-actions.md`,
and `ai/open-questions.md`. It never writes files.

## After running

Use the printed brief to choose the next action, then inspect any referenced docs
or code directly before editing.
