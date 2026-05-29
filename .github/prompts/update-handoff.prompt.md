---
mode: agent
description: Generate a draft ai/handoff.md from git state — frontmatter and "Recently touched" pre-filled; TL;DR, Open threads, and Don't do for the author.
---

# update-handoff

When the user is about to end a session that produced meaningful change, run this
from the repo root:

`python scripts/update-handoff/update_handoff.py`

(Add `--force` to overwrite an existing handoff.) The script pre-fills the handoff
frontmatter and "Recently touched" section from git state, leaving TL;DR, Open
threads, and Don't do as placeholders for the author.

After scaffolding, open `ai/handoff.md` and write the TL;DR in plain English (1–3
sentences). Replace the Open threads and Don't do placeholders with the real
items. Commit alongside the slice's other end-of-session updates.

**Note for Copilot users:** Claude Code's `update-handoff` Stop hook auto-reminds
when work has accumulated; Copilot Chat has no equivalent. Remember to invoke
this slash command yourself before ending a meaningful session.
