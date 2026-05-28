# Team Repository Standards Kit

A versioned, opinionated set of documentation standards and templates that any repository on the team can adopt. The kit's goal is to keep documentation lean, durable, and useful for both humans and AI-assisted development workflows.

- **Status:** Slice 1 — Templates + Standards Content
- **Version:** 0.1.0
- **Authoritative spec:** [`docs/STANDARDS.md`](./docs/STANDARDS.md)
- **Agent contract:** [`AGENTS.md`](./AGENTS.md)

## What this kit gives you

1. A **standard folder layout** that scales across repo types.
2. Four **repo profiles** (application, library, infra, data) with explicit Required / Expected / Optional / N/A doc requirements.
3. A defined contract for the **`ai/` directory** — four files that carry session-to-session context.
4. **MADR 3.0 ADRs** with a defined lifecycle.
5. **RFCs** for time-boxed technical investigations (separate from raw discovery intake).
6. Lightweight conventions for **`docs/discovery/`** — meeting notes, requirement drafts, use cases — with a traceability flow to durable docs.
7. A **PR template** that asks the right questions about documentation, ADRs, AI context, and operational impact.
8. A **`STANDARDS-CHECKLIST.md`** with a waiver mechanism so absences are explicit, not silent.
9. A v1 CI check that enforces the structural minimum.

## The information flow

```
docs/discovery/    →    docs/rfcs/        →    docs/decisions/    →    docs/0X-*.md
(raw intake)            (investigated)          (decided)               (synthesized & durable)
meetings, reqs,         time-boxed,             MADR 3.0 ADRs,          PRD, architecture,
use case drafts         spawn-or-abandon        immutable               runbook, etc.
```

## How to adopt the kit in a new repo

This is documented in [`docs/STANDARDS.md`](./docs/STANDARDS.md). Short version:

1. Copy `docs/templates/` into your repo.
2. Pick a profile (`application` | `library` | `infra` | `data`).
3. Fill in `docs/STANDARDS.md` (declare profile + any deviations).
4. Fill in `docs/STANDARDS-CHECKLIST.md` (check off what exists, waive what doesn't).
5. Seed `ai/*.md` from `docs/templates/ai-starters/`.
6. Adopt `.github/pull_request_template.md` and `.github/workflows/repo-standards.yml`.
7. Point your AI tools at `AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`.

A Skill that automates this is queued in Slice 2.

## Documentation philosophy

Keep documentation lean but scalable. Add durable docs when they improve onboarding, implementation, review, operations, traceability, or decision quality. Do not create documents only because a structure exists — that's why the kit uses **Required / Expected / Optional** rather than a single rigid required-doc list.

## Roadmap

| Slice | Scope | Status |
|---|---|---|
| 1 | Templates + standards content (this slice) | In progress |
| 2 | AI Skills + Hooks (Claude Code, Copilot) | Designed only |
| 3 | Distribution mechanism (template repo vs. plugin vs. copy script) | Not started |
| 4 | Deeper CI enforcement (linting, freshness, link checking) | Not started |

The full design rationale for Slice 1 is captured in ADRs `0001`–`0006` under [`docs/decisions/`](./docs/decisions/).
