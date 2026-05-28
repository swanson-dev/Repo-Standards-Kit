---
written: 2026-05-28T16:45:00-05:00
written_by: josh (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Slice 1 is ~85% complete. Phases A–D landed (foundation, templates, bootstrap ADRs + folder READMEs, kit's own numbered docs + `ai/`). Phase E (`.github/` files: copilot-instructions, PR template, repo-standards.yml workflow) is the last step before tagging `v0.1.0`. The kit applies its own `library` profile to itself and the structural shape is consistent.

## Recently touched

- `docs/STANDARDS.md` — the authoritative spec. Source of truth for profiles, matrix, ai/ contract, ADR/RFC/discovery rules, waiver mechanism.
- `docs/decisions/0001`–`0006` — bootstrap ADRs capturing every Slice 1 design decision in MADR 3.0.
- `docs/00-overview.md`, `02-architecture.md`, `04-api-and-integrations.md`, `07-testing.md`, `08-security-and-compliance.md`, `10-glossary.md`, `versioning-policy.md` — the kit's own numbered docs, written to its own library-profile spec.
- `docs/templates/*` — 21 templates; HTML-comment authoring guidance throughout.
- `AGENTS.md` and `CLAUDE.md` at root; tool-specific pointer pattern established.

## Open threads

- **Phase E (`.github/`) not yet written** — resume at the plan file (`C:\Users\CodeAssassin\.claude\plans\i-want-to-create-replicated-reef.md`) "Files to create" items 15 and 16.
- **CHANGELOG.md is waived in `STANDARDS-CHECKLIST.md`** but `ai/open-questions.md#q-3` argues for starting it now — decide before tagging v0.1.0.
- **Slice 2 design** queued — see `ai/open-questions.md#q-1` for the Skill-selection question.

## Don't do

- **Don't edit `docs/decisions/0001`–`0006`.** They are `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`. This rule is enforced by `docs/STANDARDS.md` and applies to ourselves first.
- **Don't add Skills, Hooks, or distribution mechanics in Slice 1.** Those belong to Slices 2 and 3. Capture the want in `ai/open-questions.md` or open an RFC instead.
- **Don't create the kit's own `docs/01-prd.md`, `03-data-model.md`, `05-implementation-plan.md`, `06-runbook.md`, or `09-deployment.md`.** The library profile marks them N/A or Optional. The current `STANDARDS-CHECKLIST.md` already records this; creating them would contradict the kit's own standards.
- **Don't deepen the standards-check workflow beyond the v1 list** in `docs/STANDARDS.md` § "Standards check workflow (v1)". The deeper checks (content linting, link checking, freshness reports) are Slice 4 work and need their own design pass.
- **Don't squash the per-phase commits.** They serve as the kit's own demonstration of atomic-commit discipline.
