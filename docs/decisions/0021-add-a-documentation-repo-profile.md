---
status: Accepted
date: 2026-06-16
deciders: swanson-dev, codex
consulted: docs/rfcs/0006-should-the-kit-add-a-documentation-repo-profile/rfc.md
informed: downstream repo adopters
---

# 0021. Add a documentation repo profile

## Context and Problem Statement

The kit's profile model covers applications, libraries, infrastructure, and data repos. Some downstream repos instead exist to maintain documentation, specifications, guides, or knowledge artifacts while the code lives in one or more linked repositories.

Those repos should keep the same universal governance core as every other adopted repo, but their profile-specific requirements should not imply a runtime, package distribution surface, or operational runbook unless the documentation itself is published as an operated site.

## Decision Drivers

- Documentation repos must keep the universal core: ADRs, RFCs, discovery, templates, AI continuity files, agent files, checklist, and standards workflow.
- The profile must make linked implementation repositories and source-of-truth boundaries explicit.
- The profile should avoid requiring runtime/deployment docs when no runtime exists.
- The generated profile readiness gate must validate the profile through `init`, `check`, `update`, and `check`.
- The addition should remain a minor-version feature because it adds a new public profile and template surface.

## Considered Options

- **Option A** - Keep using `library` plus local deviations.
- **Option B** - Add a generic `knowledge-base` profile.
- **Option C** - Add a specific `documentation` profile with a source-map extra.

## Decision Outcome

Chosen option: **Option C**, because it names the real repo shape without making the profile too broad. A source map gives documentation repos the missing contract: which implementation repos they reference, who owns them, what reference policy is canonical, and how freshness is reviewed.

### Consequences

- **Good:** Documentation-only repos get accurate profile defaults without losing the universal governance structure.
- **Good:** Generated readiness fixtures now cover documentation repos alongside the existing profiles.
- **Bad:** The profile list is public surface area, so CLI help, checks, docs, templates, and tests all need to stay synchronized.
- **Neutral:** Existing repos keep their current profile until they intentionally adopt or migrate to `documentation`.

## More Information

- Related ADRs: ADR-0003, ADR-0018
- Related RFC: `docs/rfcs/0006-should-the-kit-add-a-documentation-repo-profile/`
- Open questions spawned: none
