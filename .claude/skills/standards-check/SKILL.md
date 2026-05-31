---
name: standards-check
description: Run the repo's standards checks and fix any findings before pushing or ending a session.
---

# standards-check

## When to invoke

Run before you finish a session that touched docs, before you push, or when CI's
"Structural lint" job is red. This satisfies the `AGENTS.md` end-of-session contract
item "Run `/standards-check` … before ending a session that touched docs."

## How to invoke

Run from the repo root:

`python scripts/standards-check/check.py`

Exit `1` with `ERROR` lines means there is work to fix. `WARN` lines are advisory and
do not fail CI. The output lists each finding as `[<check_id>] <file>:<line> <message>`.

## After running — how to fix, by check_id

- **`links`** — the relative link or `#anchor` doesn't resolve. Correct the path
  (relative to the linking file) or fix the fragment to match the target heading slug.
- **`placeholder`** — a committed ADR/RFC still has template scaffolding. Fill the
  `<…>`, `YYYY-MM-DD`, or `NNNN`.
- **`changelog`** — `CHANGELOG.md` has no `## [x.y.z]` version section; add one.
- **`discovery`** — a `status: promoted` item's `promoted_to:` path is missing or wrong.
- **`skill-format`** — a skill is missing frontmatter, its `.github/prompts/<n>.prompt.md`
  twin, or an entry in the `AGENTS.md` `## Available skills` index. Add the missing piece.
- **`structural`** — a core file is missing, a profile/waiver is unset, or an ADR/RFC
  filename/status is invalid. Add the file or a `**Waived:**` reason in `docs/STANDARDS-CHECKLIST.md`.
- **`ai` freshness (WARN)** — `ai/handoff.md`/`current-state.md` is stale. Run `/update-handoff`.

Re-run until `0 error(s)`. (Kit maintainers: version coherence is a separate kit-only
guard, `tools/check_version_coherence.py`, not covered by this skill.)
