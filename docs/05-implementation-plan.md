# Implementation Plan

## Roadmap

> Active milestone: **M4 — Release and reporting hygiene** (sliced below)

| Milestone                        | Outcome                                                                                  | Target   | Status  |
|----------------------------------|------------------------------------------------------------------------------------------|----------|---------|
| M1 — Foundation                  | Templates → AI skills → `standards` CLI → CI enforcement → hardening → non-destructive `adopt` | →v0.15.0 | shipped |
| M2 — Roadmap & planning surface  | A standard home for the longitudinal roadmap (this doc + the template `## Roadmap` section) | v0.16.0  | shipped |
| M3 — Workflow simplification & AI readiness | Flat discovery notes, clearer CLI help, local skill scaffolding, and stronger agent-surface checks | v0.17.0 | shipped |
| M4 — Release and reporting hygiene | GitHub Release consistency, external-link liveness, and richer doc-freshness reporting    | TBD      | active  |

### Shipped slices (M1 — Foundation)

| Slice | Scope | Status |
|---|---|---|
| 1 | Templates + standards content | Shipped |
| 2 | AI Skills + Hooks (Claude Code, Copilot) | Shipped |
| 3 | Distribution — the `standards` CLI (`init` / `update`), PyPI, 3-class sync | Shipped |
| 4 | Deeper CI enforcement (content/link/placeholder lint, parity + coherence guards) | Shipped |
| 5 | Hardening — `standards check` subcommand + multi-profile CI-green `init` | Shipped |
| 6 | `standards adopt` — non-destructive adoption onto existing repos | Shipped |

### Shipped slices (M2 — Roadmap & planning surface)

| Slice | Scope | Status |
|---|---|---|
| 1 | Roadmap section in the implementation-plan template | Shipped |
| 2 | Dogfood the kit's own roadmap in `docs/05-implementation-plan.md` | Shipped |

## Approach

M4 closes the quality gaps that appear around releases and long-lived docs: release pages should
exist when changelog links point at them, external links should not silently rot, and `ai/`
freshness should be easier to report on than a simple stale/not-stale warning.

## Slices

### Slice 1: GitHub Release consistency

- **Goal:** make `v0.17.0` and future tag releases visible as GitHub Releases with attached artifacts.
- **Includes:** create the missing `v0.17.0` GitHub Release; update `release.yml` to create/update releases after PyPI publish; update release docs and AI state.
- **Excludes:** backfilling every older missing GitHub Release.
- **Owner:** codex
- **Verification:** `gh release view v0.17.0`; `python scripts/standards-check/check.py`; `python tools/run_tests.py`; `python tools/check_version_coherence.py`.

### Slice 2: External-link liveness

- **Goal:** catch stale external links such as changelog release URLs before they ship.
- **Includes:** a standards-check liveness mode with conservative defaults and tests.
- **Excludes:** flaky network-hard CI by default; networked checks should be opt-in or warn-first.
- **Owner:** swanson-dev
- **Verification:** targeted tests with mocked URL results plus standards-check.

### Slice 3: Richer doc-freshness reporting

- **Goal:** make `ai/` drift visible as an actionable report instead of only stale-threshold warnings.
- **Includes:** clearer age/status output for `ai/current-state.md`, `ai/next-actions.md`, and `ai/handoff.md`.
- **Excludes:** turning freshness warnings into hard adopter errors by default.
- **Owner:** swanson-dev
- **Verification:** standards-check freshness tests plus current repo check.

## Sequencing

```mermaid
flowchart LR
  S1[Slice 1: release consistency] --> S2[Slice 2: external links]
  S2 --> S3[Slice 3: freshness reporting]
```

## Verification per slice

Release/reporting hygiene work is verified with focused tests and the full local gates:
- `python scripts/standards-check/check.py` — links/placeholders/structure.
- `python tools/run_tests.py` — payload/manifest/CLI suite unaffected.
- `python tools/check_version_coherence.py` — version strings stay coherent.

## Open questions blocking the plan

- None. A section-presence lint for the `## Roadmap` block is deferred as YAGNI (RFC-0003).
