---
mode: agent
description: List raw items in docs/discovery/, or flip a specific item from status raw to promoted with a promoted_to target.
---

# promote-discovery

When the user wants to see the inventory of raw discovery items, or has just synthesized
a discovery item's content into a structured doc and wants to flip its status, run one
of these from the repo root:

**List raw items:** `python scripts/promote-discovery/promote_discovery.py list`

**Promote a specific item:** `python scripts/promote-discovery/promote_discovery.py promote <path> --to <target>`

Both `<path>` and `--to <target>` are required for the promote subcommand. `<target>` must
be a relative repo path (no absolute paths, no `..`). The script does not require the
target file to exist yet.

After promoting, verify the diff in the file's frontmatter and commit alongside the
synthesized target doc. Promotion is monotonic — the script refuses to re-promote.

**Note for Copilot users:** Claude Code's SessionStart hook auto-pings when raw items
exist at session open; Copilot Chat has no equivalent. Remember to run `list` periodically
to check the inventory yourself.
