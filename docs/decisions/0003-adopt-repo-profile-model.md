---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0003. Adopt a repo-profile model with tiered doc requirements

## Context and Problem Statement

The team builds four kinds of repositories — applications, libraries, infrastructure, and data — and they share little besides "they need documentation." A single rigid required-doc list either over-burdens libraries (which don't have a runbook) or under-serves applications (which need much more than libraries). Adoption of any standards kit collapses if it asks for docs that don't apply.

## Decision Drivers

- Each repo type has genuinely different durable-doc needs.
- The kit's own philosophy: "do not create documents only because a structure exists."
- Need for CI to enforce the standard automatically — which requires a machine-readable spec of what's required where.
- Avoid encouraging waivers as the default escape hatch.

## Considered Options

- **Option A** — Four repo profiles (application, library, infra, data) with a Required / Expected / Optional / N/A tier per numbered doc.
- **Option B** — Single core (every repo) + every other doc Optional, created on demand.
- **Option C** — Maturity tiers (Tier 1 skeleton / Tier 2 production / Tier 3 critical) independent of repo type.

## Decision Outcome

Chosen option: **Option A (repo profiles + tiered requirements)**, because the team's main source of repo variation is shape (application vs. library vs. infra vs. data), not maturity, and a tiered requirement model lets the kit be prescriptive where it matters while remaining honest about what genuinely doesn't apply.

### Consequences

- **Good:** Each profile has a sharp, defensible required-doc list.
- **Good:** CI can enforce mechanically.
- **Good:** The Expected/Waived mechanism creates a useful paper trail of "this was considered and skipped because…".
- **Bad:** New repo types may need a new profile via RFC (intentional friction).
- **Neutral:** Adopting this model means the kit's checklist is the source of truth for what to scaffold, not a free-form judgment per repo.

## More Information

- Tier semantics and full matrix: `docs/STANDARDS.md` § "Tier semantics" and § "Profile matrix".
- Waiver mechanism: `docs/STANDARDS.md` § "Waiver mechanism".
- Per-repo checklist template: `docs/templates/STANDARDS-CHECKLIST.md.template`.
