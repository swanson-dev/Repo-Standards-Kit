---
name: promote-discovery
description: List raw items in docs/discovery/, or flip a specific item from status raw to promoted with a promoted_to target.
---

# promote-discovery

## When to invoke

Use when:
- The SessionStart hook surfaced a "N raw items" reminder and you want to see the inventory.
- You just synthesized a discovery item's content into a PRD, ADR, RFC, or other structured
  doc — to satisfy the `AGENTS.md` end-of-session contract item "If you used content from
  `docs/discovery/`, flip its `status: raw` → `promoted`" so the audit trail stays accurate.

## How to invoke

**List raw items** (default verbose mode) from the repo root:

`python scripts/promote-discovery/promote_discovery.py list`

**Promote a specific item** (flip status: raw → promoted; set promoted_to):

`python scripts/promote-discovery/promote_discovery.py promote <path> --to <target>`

Both `<path>` and `--to <target>` are required. `<target>` must be a relative repo path
(no absolute paths, no `..`). The script does not require `<target>` to exist yet — you
often promote during the act of writing the target.

## After scaffolding

Verify the diff in the promoted file's frontmatter (`status:` line and `promoted_to:`
line; everything else preserved). Commit alongside the synthesized target doc.

Promotion is monotonic — once a discovery item is `promoted`, the script refuses to
re-promote it. If you genuinely need to un-promote, hand-edit the file and explain why
in the commit message.
