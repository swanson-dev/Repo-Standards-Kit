---
written: 2026-06-16T17:09:44-05:00
written_by: codex
for: next-session
---

# Handoff

## TL;DR

Published v1.1.0 after implementing the adoption-assistant and AI-continuity slice: `standards doctor [--recommend]`, `standards new-skill`, `standards commands`, optional discovery/design/support templates, `standard-update-handoff`, `standard-get-session-context`, `standard-compact-snapshot`, and an advisory read-only SessionStart context hook. The `v1.1.0` tag deployed through GitHub Actions, published to PyPI, created the GitHub Release, and passed the clean installed-package smoke.

## Recently touched

- `src/standards/cli.py` and `src/standards/doctor.py` add the new public CLI commands and read-only diagnostics.
- `scripts/session-context/session_context.py` adds the read-only AI context brief used by the SessionStart hook and `standard-get-session-context`.
- `scripts/update-handoff/update_handoff.py` adds `--compact-snapshot` for explicit pre-compaction handoff checkpoints.
- `docs/templates/` adds optional lane templates for discovery notes, meetings, artifact indexes, design, incidents, troubleshooting, and guides.
- `docs/STANDARDS.md`, `README.md`, `docs/04-api-and-integrations.md`, and `docs/discovery/README.md` document optional lanes and the pointer-first artifact policy.
- `docs/rfcs/0004-.../rfc.md`, `docs/decisions/0019-...md`, RFC-0005, and ADR-0020 record the public CLI, optional-lane, and AI-continuity decisions.
- `CHANGELOG.md`, `ai/current-state.md`, and `ai/next-actions.md` now describe v1.1.0 as published.

## Open threads

- Merge/reconcile `codex/release-v1.1.0` into `main` if you want `main` to carry the release commit and post-release changelog link.
- Pilot `standards doctor --recommend` in a real downstream repo to tune recommendation noise.
- Pilot the SessionStart context brief in real work to tune summary noise.

## Don't do

- Do not make optional knowledge lanes required or scaffold them by default.
- Do not make the SessionStart hook blocking or mutating.
- Do not store raw discovery binaries in git by default; use markdown artifact indexes that point to deliberate external storage.
- Do not reintroduce the old capture/promote discovery lifecycle without a superseding ADR.
