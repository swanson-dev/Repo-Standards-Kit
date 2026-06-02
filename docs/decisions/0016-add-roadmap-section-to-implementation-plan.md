---
status: Accepted
date: 2026-06-02
deciders: swanson-dev
consulted: —
informed: kit adopters
---

# 0016. Add a milestone roadmap section to the implementation-plan template

## Context and Problem Statement

The kit standardizes the artifacts teams otherwise improvise — yet it improvised its own
roadmap in two drifting places: the roadmap table in `README.md` and the "queued slices" prose
in `AGENTS.md`. Adopting repos likewise had no standard home for the longitudinal question
"where is this repo headed over the next several milestones." The two planning surfaces that
exist cover other horizons: `ai/next-actions.md` is capped at 7 tactical steps, and
`docs/05-implementation-plan.md` slices a single build effort.

Where should the longitudinal milestone roadmap live, given `05-implementation-plan.md` already
provides per-effort slicing and sequencing?

## Decision Drivers

- Keep the kit lean (its own rule: do not create documents only because a structure exists).
- Do not duplicate the sequencing machinery `05-implementation-plan.md` already ships.
- Work across all four profiles and for downstream teams, not just this repo.
- Minimize SemVer and adopter-cognitive cost.

## Considered Options

- **Option A** — Extend `05-implementation-plan.md` with a `## Roadmap` section (no new file).
- **Option B** — A new standalone roadmap doc above `05-implementation-plan.md`.
- **Option C** — A minimal root `ROADMAP.md`, peer of `CHANGELOG.md`, universal across profiles.

## Decision Outcome

Chosen option: **Option A**, extend `05-implementation-plan.md`. A new artifact (B/C) would
duplicate most of `05-plan`'s machinery to add one table, cost a profile-matrix row and a
likely new CI check, and add adopter-cognitive load. Extending the template is a single
template-structure change — a Minor bump — and needs zero new profile gating, because `05-plan`
is already tiered (Expected for application/infra/data, Optional for library).

The section is shaped as a **hybrid**: a milestone table (status `planned | active | shipped |
dropped`) is the slow strategic layer at the top, and the existing `## Slices` section is bound
to the single milestone marked `active`. An **exactly-one-`active` invariant** makes that
binding unambiguous, so the two horizons cannot silently drift inside one file — a structural
fix rather than a discipline rule.

### Consequences

- **Good:** one planning doc, two horizons, no new artifact/check/profile-gating; the kit can
  now dogfood its own roadmap; ships to adopters automatically via the bundled template.
- **Bad:** a long-lived doc carries both a slow table and a fast slice list; mitigated by the
  one-`active`-milestone invariant.
- **Neutral:** the invariant is documented in the template comment, not enforced by CI
  (section-presence linting is deferred as YAGNI — RFC-0003).

## More Information

- Investigation: [`../rfcs/0003-how-should-the-kit-standardize-a-milestone-roadmap/rfc.md`](../rfcs/0003-how-should-the-kit-standardize-a-milestone-roadmap/rfc.md).
- Related: ADR-0003 (repo-profile model / tiers), ADR-0009 (payload sync — the template ships DRY from `docs/templates/`).
