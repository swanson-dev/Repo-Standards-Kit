---
written: 2026-06-02T13:45:52-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**Milestone roadmap** is built and verified on `feat/roadmap-milestones` (**PR #18** open into
`main`, not yet merged). It standardizes the longitudinal roadmap the kit was improvising in the
README table + AGENTS.md "queued slices": the `05-implementation-plan` **template** gains a
`## Roadmap` milestone table (status `planned | active | shipped | dropped`, exactly-one-`active`
invariant) above `## Approach`, and the existing `## Slices` is scoped to the active milestone.
Decision in **ADR-0016**, investigation in **RFC-0003**. The kit dogfoods it in the new
`docs/05-implementation-plan.md`; README + AGENTS now point there.

No version bump — only a CHANGELOG `[Unreleased]` entry. The **v0.16.0 release cut is deferred**
to the next session. This session also fixed stale `0.1.0` version strings in `docs/STANDARDS.md`
and `docs/STANDARDS-CHECKLIST.md` (→ 0.15.0) and refreshed the `ai/` files.

`standards-check` 0/0; version coherence OK (0.15.0); **26/26** suites.

## Recently touched

- **New:** `docs/rfcs/0003-how-should-the-kit-standardize-a-milestone-roadmap/rfc.md`, `docs/decisions/0016-add-roadmap-section-to-implementation-plan.md`, `docs/05-implementation-plan.md`.
- **Template (ships to adopters):** `docs/templates/implementation-plan-template.md` (`## Roadmap` section).
- **Pointers / dogfood:** `README.md`, `AGENTS.md` (repo-owned `### Roadmap`, code-span not link), `docs/decisions/README.md` (index), `docs/STANDARDS-CHECKLIST.md` (05 box flipped + version), `CHANGELOG.md` (`[Unreleased]` Added).
- **Staleness fix:** `docs/STANDARDS.md` + `docs/STANDARDS-CHECKLIST.md` version 0.1.0 → 0.15.0; `ai/*` refreshed.

## Open threads

- **PR #18** — review + merge → `main`, then **cut v0.16.0** (see `ai/next-actions.md` step 2; remember to bump the unguarded STANDARDS.md/CHECKLIST versions too).
- **Node 24 CI chore** (`6497ffd`) rides on this branch/PR; split onto its own branch if an atomic PR is preferred.
- The local impl plan is at `~/.claude/plans/2026-06-02-roadmap-milestones.md` (its T6 = the deferred release-cut task).

## Don't do

- **Don't put repo-specific markdown links in files that ship verbatim** (`AGENTS.md`, `docs/STANDARDS.md` — both in the payload). They break the multi-profile scaffold gate when the target (e.g. `docs/05-implementation-plan.md`) doesn't exist in a fresh adopter repo. Use **code spans**. `README.md` is NOT in the payload, so links there are fine. Run `python tools/run_tests.py` (not just the standards-check) after editing `AGENTS.md`/`STANDARDS.md`.
- Don't tag off a feature branch — tag the `main` merge commit (matches v0.9.0/v0.11.0/v0.13.0/v0.15.0).
- Don't push to `main` directly; don't add runtime deps; don't edit Accepted ADRs (0001–0016).
- Don't run a single `pytest` — `python tools/run_tests.py` is canonical (duplicate `test_cli.py` basenames). Keep `from __future__ import annotations` (3.9 matrix).
