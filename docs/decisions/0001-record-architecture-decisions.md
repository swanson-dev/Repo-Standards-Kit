---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0001. Record architecture decisions

## Context and Problem Statement

The Repo Standards Kit (and every repo that adopts it) needs a durable way to capture material technical decisions: why a structure was chosen, what alternatives were considered, what consequences were accepted. Decisions made in chat, in PR comments, or in ad-hoc docs vanish; future contributors and AI agents re-litigate the same questions without the historical context.

## Decision Drivers

- Traceability of "why we chose X" over time.
- Low ceremony so the practice is actually used.
- Format that AI agents can author and read reliably.
- Immutability of decisions once accepted, so the historical record stays trustworthy.

## Considered Options

- **Option A** — Record decisions in ADR files under `docs/decisions/` using a standardized format.
- **Option B** — Use only PR descriptions and commit messages.
- **Option C** — Use a wiki external to the repo.

## Decision Outcome

Chosen option: **Option A (ADR files in `docs/decisions/`)**, because decisions live alongside the code they govern, survive repo migrations, are review-able as part of PRs, and can be authored consistently by humans and AI agents.

### Consequences

- **Good:** Every material decision has a durable, citable home.
- **Good:** Future readers can trace why the current shape exists.
- **Bad:** Adds a small documentation burden per material decision.
- **Neutral:** The exact format is fixed by a separate ADR ([0002](./0002-adopt-madr-3.md)).

## More Information

- ADR format: see ADR [0002](./0002-adopt-madr-3.md).
- Authoring guidance: `docs/STANDARDS.md` § "ADRs — MADR 3.0".
- Template: `docs/templates/adr-template.md`.
