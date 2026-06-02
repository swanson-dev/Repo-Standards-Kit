# Standards Checklist — Repo Standards Kit

**Profile:** library
**Kit version adopted:** 0.1.0
**Last reviewed:** 2026-05-28 by josh

## Universal core (Required for all profiles)

- [x] `README.md`
- [x] `CHANGELOG.md`
- [x] `AGENTS.md`
- [x] `CLAUDE.md`
- [x] `docs/STANDARDS.md`
- [x] `docs/STANDARDS-CHECKLIST.md` (this file)
- [x] `docs/00-overview.md`
- [x] `docs/10-glossary.md`
- [x] `docs/decisions/` (folder + README, ≥1 ADR)
- [x] `docs/discovery/` (folder + README)
- [x] `docs/rfcs/` (folder + README)
- [x] `docs/templates/` (kit-supplied templates)
- [x] `ai/current-state.md`
- [x] `ai/next-actions.md`
- [x] `ai/open-questions.md`
- [x] `ai/handoff.md`
- [x] `.github/copilot-instructions.md`
- [x] `.github/pull_request_template.md`
- [x] `.github/workflows/repo-standards.yml`

## Profile: library

### Required

- [x] `docs/04-api-and-integrations.md` — the kit's "API" is the templates surface + profile matrix; this doc enumerates it.
- [x] `docs/07-testing.md` — describes the structural and walkthrough verification model.
- [x] `docs/versioning-policy.md` — kit SemVer policy (mirrors `STANDARDS.md` §"Kit versioning" with more detail).

### Expected

- [x] `docs/02-architecture.md` — describes the kit's conceptual architecture (information flow, artifact lifecycles).
- [x] `docs/08-security-and-compliance.md` — minimal but present (kit has no runtime, no secrets, no PII; documents the threat model boundary).

### Optional

- [ ] `docs/01-prd.md` — Optional for library profile; the kit's "PRD" is the README + STANDARDS.md.
- [x] `docs/05-implementation-plan.md` — present: holds the kit's milestone roadmap + active-milestone slices (ADR-0016). Detailed working plans still live in `docs/rfcs/` and the local plans dir.

### N/A for library profile (not created)

- `docs/03-data-model.md`
- `docs/06-runbook.md`
- `docs/09-deployment.md`

## Per-PR (filled in PR description, not here)

Each PR confirms the Standards Impact checklist in `.github/pull_request_template.md`.
