---
status: Concluded
opened: 2026-06-16
closed: 2026-06-16
owner: codex
time_box: same-day implementation
---

# 0004. Should the kit add post-v1 adoption-assistant commands and optional knowledge lanes?

## Question

Should the first post-v1 milestone add adoption-assistant CLI commands and optional knowledge-lane templates without making the default repository scaffold heavier?

## Why now

The v1.0.0 release proved generated downstream repos can pass the public adoption path, but the next product risk is operating the kit in real repos after adoption. `ai/next-actions.md` named the public CLI choice as the next milestone: `standards new-skill`, `standards doctor`, or command discovery. The implementation request chooses all three and adds optional discovery, design, and support lanes.

## Approach

Use the existing CLI shape and shipped script architecture. Keep the default scaffold lean, expose existing skill scaffolding through the packaged CLI, add a read-only diagnostic command, and add optional templates for richer capture paths. Avoid background watchers, mandatory folders, network access, or automatic file creation for recommendations.

## Findings

- The existing `standards` CLI is a single stdlib `argparse` entrypoint, so adding `doctor`, `new-skill`, and `commands` is an incremental public-surface change.
- The repo already has `scripts/new-doc/new-skill.py`; exposing it through the packaged CLI mainly requires command wiring and ensuring its helper package ships in the payload.
- `doctor` can reuse the bundled standards check as a subprocess, then add marker, sidecar, and managed-region diagnostics without mutating files.
- Optional knowledge lanes are best shipped as templates and documented conventions. Creating every optional folder during `init` would dilute the lean default.
- Discovery artifacts need a pointer-first policy: markdown index files should point to external binaries unless a repo explicitly chooses Git LFS, release assets, object storage, or another deliberate storage mechanism.

## Recommendation

Add `standards doctor`, `standards new-skill`, and `standards commands` as the post-v1 adoption-assistant milestone. Ship optional templates for discovery notes, meetings, artifact indexes, design notes, incidents, troubleshooting, and guides. Keep all lanes optional, recommend them through `doctor --recommend` and agent guidance, and do not create optional folders by default.

## Follow-ups

- **ADR to write:** yes - [ADR-0019](../../decisions/0019-add-post-v1-adoption-assistant-commands-and-optional-knowledge-lanes.md)
- **Implementation plan changes:** update `docs/05-implementation-plan.md` with the shipped post-v1 milestone
- **New open questions:** none
- **Discovery to promote:** none
