---
mode: agent
description: Run the repo's standards checks and fix any findings before pushing or ending a session.
---

# standards-check

When finishing a session that touched docs, before pushing, or when CI's structural
lint is red, run this from the repo root:

`python scripts/standards-check/check.py`

For release notes or other docs where outbound URLs matter, opt in to networked
`http(s)` liveness checks:

`python scripts/standards-check/check.py --external-links`

For a current `ai/` freshness status report, opt in with:

`python scripts/standards-check/check.py --freshness-report`

Exit `1` with `ERROR` lines means there is work to fix; `WARN` lines are advisory.
Each finding is `[<check_id>] <file>:<line> <message>`.
For `external-links` findings, fix or replace the unreachable outbound URL.

Fix by check_id: `links` → correct the relative path / `#anchor`; `placeholder` → fill
`<…>`/`YYYY-MM-DD`/`NNNN` in the committed ADR/RFC; `changelog` → add a `## [x.y.z]`
section; `skill-format` → add the missing
frontmatter / `.github/prompts/<n>.prompt.md` twin / `AGENTS.md` index entry;
`structural` → add the missing file or a `**Waived:**` reason; `ai` freshness →
refresh the named `ai/` file. Re-run until `0 error(s)`.
