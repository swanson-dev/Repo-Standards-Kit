---
name: standard-update-handoff
description: Refresh ai/handoff.md at the end of meaningful work using the standard handoff script.
---

# standard-update-handoff

## When to invoke

Use when ending a session that produced meaningful change, especially when the
Stop hook reports work since the last handoff. This satisfies the AGENTS.md
end-of-session contract to write `ai/handoff.md`.

## How to invoke

Run from the repo root:

`python scripts/update-handoff/update_handoff.py --force`

The script writes `ai/handoff.md` with frontmatter and git-derived touched files.

## After running

Open `ai/handoff.md` and replace placeholders with a concise TL;DR, open
threads, and "Don't do" notes before finishing.
