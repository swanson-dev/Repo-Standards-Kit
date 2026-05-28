---
written: 2026-05-28T18:30:00-05:00
written_by: josh (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Slice 1 is **complete and green**. All five phases landed: foundation, templates, bootstrap ADRs + folder READMEs, kit's own numbered docs + `ai/`, and the `.github/` + standards-check script. The structural lint runs locally and exits clean (`0 errors, 0 warnings`). `CHANGELOG.md` is started at v0.1.0. Next session can push, tag `v0.1.0`, and open Slice 2.

## Recently touched

- `scripts/standards-check/check.py` — stdlib-only Python implementing the v1 standards check. Runs locally with `python scripts/standards-check/check.py`.
- `.github/workflows/repo-standards.yml` — invokes the check on push and PR.
- `.github/pull_request_template.md` — Standards Impact block.
- `.github/copilot-instructions.md` — thin pointer to `AGENTS.md`.
- `CHANGELOG.md` — Keep-a-Changelog, v0.1.0 entry recording the Slice 1 release.
- `docs/STANDARDS-CHECKLIST.md` — CHANGELOG waiver removed (Q-3 resolved).
- `ai/open-questions.md` — Q-3 marked `answered`.

## Open threads

- **Tag and push v0.1.0** — `ai/next-actions.md` item 1.
- **Slice 2 design** queued — `ai/open-questions.md#q-1` is the Skill-selection question.
- **Slice 3 distribution** queued — `ai/open-questions.md#q-2`.

## Don't do

- **Don't edit `docs/decisions/0001`–`0006`.** They are `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`. This rule is enforced by `docs/STANDARDS.md` and applies to ourselves first.
- **Don't add Skills, Hooks, or distribution mechanics in Slice 1.** Those belong to Slices 2 and 3. Capture the want in `ai/open-questions.md` or open an RFC instead.
- **Don't create the kit's own `docs/01-prd.md`, `03-data-model.md`, `05-implementation-plan.md`, `06-runbook.md`, or `09-deployment.md`.** The library profile marks them N/A or Optional. The current `STANDARDS-CHECKLIST.md` already records this; creating them would contradict the kit's own standards.
- **Don't deepen the standards-check workflow beyond the v1 list** in `docs/STANDARDS.md` § "Standards check workflow (v1)". The deeper checks (content linting, link checking, freshness reports) are Slice 4 work and need their own design pass.
- **Don't squash the per-phase commits.** They serve as the kit's own demonstration of atomic-commit discipline.
- **Don't add a remote and push without confirming first.** The kit has no remote yet by design — pick a home (`team/repo-standards-kit` on GitHub or wherever) before pushing.
