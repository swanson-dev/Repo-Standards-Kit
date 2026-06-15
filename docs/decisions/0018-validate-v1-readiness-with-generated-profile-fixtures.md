---
status: Accepted
date: 2026-06-15
deciders: swanson-dev, codex
consulted: docs/versioning-policy.md
informed: downstream repo adopters
---

# 0018. Validate v1 readiness with generated profile fixtures

## Context and Problem Statement

The kit's pre-1.0 policy required evidence that all four profiles can be adopted
successfully before cutting v1.0.0. Waiting for four named real downstream repos
would make the release depend on repository selection and access rather than on a
repeatable engineering gate.

The question is what evidence should count for v1.0.0 readiness.

## Decision Drivers

- The gate must be reproducible locally and in CI.
- The gate must exercise the public adopter path, not internal-only helpers.
- The release should not depend on private repository access.

## Considered Options

- **Option A** - Require four real downstream repositories before v1.0.0.
- **Option B** - Use generated downstream fixture repos for all four profiles.
- **Option C** - Cut v1.0.0 based only on the existing self-application tests.

## Decision Outcome

Chosen option: **Option B**, because generated fixture repos provide repeatable
evidence across `application`, `library`, `infra`, and `data` without coupling the
release to external repo availability.

### Consequences

- **Good:** v1 readiness can be checked by `python tools/check_v1_readiness.py`
  in local gates, CI, and the release workflow.
- **Bad:** generated fixtures do not replace the qualitative signal from real
  downstream adoption.
- **Neutral:** real downstream walkthroughs remain useful post-v1 evidence, but
  they are not a v1.0.0 release blocker.
