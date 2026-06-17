---
status: Concluded
opened: 2026-06-16
closed: 2026-06-16
owner: codex
time_box: same-day implementation
---

# 0006. Should the kit add a documentation repo profile?

## Question

Should the kit add a first-class `documentation` repo profile for repositories whose primary deliverable is maintained documentation while implementation lives elsewhere?

## Why now

Some downstream repositories are not applications, libraries, infrastructure, or data pipelines. They own durable documentation, specifications, guides, or reference material while linking to implementation repositories. Forcing those repos into `library` hides the real source-of-truth boundary and creates poor defaults around deployment, runbooks, and API ownership.

## Approach

Compare the existing four-profile model against the documentation-only use case. Keep the universal core unchanged so documentation repos still get ADRs, RFCs, discovery notes, templates, AI continuity files, and standards checks. Add only the profile-specific matrix entries, profile extra, CLI/check plumbing, and generated readiness coverage needed to make the profile first-class.

## Findings

- The universal core already fits documentation repos and should remain unchanged.
- `library` is the closest existing profile, but it implies package distribution and public API ownership that documentation repos do not have.
- Documentation repos need a durable map to linked implementation repos, canonical references, sync cadence, and ownership boundaries.
- The profile model is hard-coded in CLI choices, structural checks, generated readiness fixtures, and profile placeholders, so adding the profile must update all of those surfaces together.

## Recommendation

Add a `documentation` profile. Give it a Required `04-api-and-integrations.md` reframed as linked source repos and reference contracts, Required `07-testing.md` focused on links/generated-docs/freshness, Expected PRD/architecture/implementation/security docs, and a documentation-profile extra `docs/source-map.md`.

## Follow-ups

- **ADR to write:** yes - [ADR-0021](../../decisions/0021-add-a-documentation-repo-profile.md)
- **Implementation plan changes:** update `docs/05-implementation-plan.md` with the shipped documentation-profile slice
- **New open questions:** none
- **Discovery to promote:** none
