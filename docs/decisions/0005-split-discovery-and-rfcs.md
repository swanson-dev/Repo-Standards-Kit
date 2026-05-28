---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0005. Split discovery and RFCs into separate folders

## Context and Problem Statement

The kit needs a home for two genuinely different artifact types:

1. **Raw intake** — stakeholder material the team *receives*: meeting notes, business requirements drafts, use case docs from stakeholders. Unstructured, unpredictable, often pre-engineering-language.
2. **Technical investigations** — work the team *produces* to answer a specific question before committing: RFCs, time-boxed spikes, evaluations. Highly structured, with a clear question and recommendation.

The original README placed both under `docs/discovery/`. Mixing them dilutes both — forcing structure on meeting notes kills the practice, while letting RFCs go unstructured discards their value as decision inputs.

## Decision Drivers

- Each artifact has a different lifecycle (received vs. produced).
- Each has different reviewers (stakeholder-facing vs. engineering-facing).
- Each has different output rules (discovery feeds many things; RFCs reach a single terminal state).
- AI Skills (Slice 2) need predictable, distinct folders to scaffold into.

## Considered Options

- **Option A** — Two sibling folders: `docs/discovery/` (raw intake) and `docs/rfcs/` (investigations).
- **Option B** — `docs/discovery/spikes/` as a subfolder, sharing the discovery folder.
- **Option C** — Single `docs/research/` covering both with mixed structure.

## Decision Outcome

Chosen option: **Option A**, because the two artifacts have opposite structural needs (loose vs. strict), different lifecycles, and different reviewers. Sibling folders make the boundary explicit and let each evolve without contaminating the other. The folder is named `rfcs/` (not `spikes/`) to align with established industry convention.

### Consequences

- **Good:** Discovery stays low-friction (no forced template body), so meeting notes actually land in the repo.
- **Good:** RFCs have a strict shape — every RFC has a question, a time-box, findings, and a recommendation.
- **Good:** Each folder gets its own README explaining the contract.
- **Bad:** One more top-level folder under `docs/`.
- **Neutral:** Each RFC lives in its own subfolder (`docs/rfcs/NNNN-slug/`) so benchmarks, screenshots, and prototype artifacts can live alongside the prose.

## More Information

- Discovery conventions: `docs/STANDARDS.md` § "Discovery folder".
- RFC structure and lifecycle: `docs/STANDARDS.md` § "RFCs".
- Templates: `docs/templates/discovery-meeting-notes.md`, `docs/templates/discovery-use-case.md`, `docs/templates/rfc-template.md`.
- Information flow: `docs/discovery/` → `docs/rfcs/` → `docs/decisions/` → numbered docs.
