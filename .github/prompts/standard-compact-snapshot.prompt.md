---
mode: agent
description: Capture a compact pre-compaction checkpoint into ai/handoff.md.
---

# standard-compact-snapshot

Run `python scripts/update-handoff/update_handoff.py --compact-snapshot --force`
from the repo root. Then fill the compact checkpoint placeholders in
`ai/handoff.md` with the current goal, status, touched files, tests, decisions,
blockers, "Don't redo", and next exact action.
