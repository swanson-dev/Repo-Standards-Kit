---
written: 2026-06-14T00:00:00-05:00
written_by: codex
for: next-session
---

# Handoff

## TL;DR

Release prep for v0.17.0 is in place locally. The post-0.16 cleanup now has coherent
version metadata, changelog, roadmap/current-state/next-actions, and ignored local
`.agents/` / `.codex/` surfaces so they do not accidentally ship. Gates were rerun
after the cleanup; push/tag/publish is the remaining maintainer action.

## Recently touched

- Release metadata: `src/standards/__about__.py`, `AGENTS.md`, `docs/STANDARDS.md`, `docs/STANDARDS-CHECKLIST.md`, `CHANGELOG.md` now target v0.17.0.
- Release coordination: `README.md`, `docs/05-implementation-plan.md`, `ai/current-state.md`, `ai/next-actions.md`, and this handoff now reflect that v0.16.0 already landed and v0.17.0 is the next release.
- Local tool surfaces: `.gitignore` now ignores `.agents/` and `.codex/`; the tracked shipped surface remains `AGENTS.md`, `.claude/`, and `.github/`.
- Existing post-0.16 changes remain the release payload: discovery simplification, CLI help polish, paired skill scaffolding, and stronger agent-surface checks.

## Open threads

- Push the local commit to `main`, create/push `v0.17.0`, and verify the release workflow publishes to PyPI.
- Historical changelog entries, prior ADR bodies, RFCs, and superpowers plans still mention capture/promote because they describe past design work.
- No `commands`, `doctor`, interactive CLI prompting, or `standards new-skill` subcommand was added; keep that scope for a separate design pass if wanted.

## Don't do

- Do not resurrect `/capture-discovery`, `/promote-discovery`, `docs/discovery/captured/`, or `promoted_to` unless a new ADR supersedes ADR-0017.
- Do not edit the bodies of Accepted/Superseded ADRs; write a new ADR for reversals.
- Keep discovery notes simple: tracked markdown under `docs/discovery/`, linked from structured docs when they matter.
- Do not commit `.agents/` or `.codex/`; they are local tool surfaces, not the shipped kit contract.
