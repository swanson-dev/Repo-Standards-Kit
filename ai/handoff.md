---
written: 2026-05-28T22:45:00-05:00
written_by: josh (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Slice 2 is **complete and green**. Two scaffolding skills shipped (`new-adr`, `new-rfc`) with dual Claude `SKILL.md` + Copilot `prompt.md` wrappers over stdlib-only Python scripts; Q-1 resolved; ADR-0007 records the form-factor decision (produced via the very first dogfooded run of `new-adr.py`). All 24 tests pass (14 helpers + 10 CLI); structural check exits `0 errors, 0 warnings`; `CHANGELOG.md` records v0.2.0.

## Recently touched

- `scripts/_doc_lib/helpers.py`, `scripts/_doc_lib/__init__.py` — four pure helpers (`slugify`, `today_iso`, `next_nnnn`, `render_template`) used by both CLIs.
- `scripts/new-doc/new-adr.py`, `scripts/new-doc/new-rfc.py` — the two scaffolding CLIs (stdlib only).
- `scripts/new-doc/test_helpers.py`, `scripts/new-doc/test_cli.py` — stdlib `unittest` coverage (14 + 10 tests).
- `scripts/new-doc/README.md` — script directory contract: invocation, conventions, dogfooding rule.
- `.claude/skills/new-adr/SKILL.md`, `.claude/skills/new-rfc/SKILL.md` — Claude Code wrappers.
- `.github/prompts/new-adr.prompt.md`, `.github/prompts/new-rfc.prompt.md` — GitHub Copilot Chat wrappers (parity with SKILL.md).
- `docs/decisions/0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md` — ADR-0007, the form-factor decision (dogfooded smoke test produced this file).
- `docs/decisions/README.md` — index row appended for ADR-0007.
- `ai/open-questions.md` — Q-1 marked answered.
- `ai/current-state.md` — Slice 2 in What works; Slice 2.5 next.
- `AGENTS.md` — kit version bumped to 0.2.0; Slice 2.5 in queued slices.
- `CHANGELOG.md` — v0.2.0 entry recording Slice 2.

## Open threads

- **Tag v0.2.0** if the user wants to release on the existing remote (do not push or tag without explicit confirmation).
- **Slice 2.5 design** queued — Hooks: `update-handoff` (Stop hook), `promote-discovery` (reminder).
- **Slice 3 distribution** still queued at `ai/open-questions.md#q-2` — blocks `scaffold-new-repo`.
- The earlier handoff's "push v0.1.0" item — re-evaluate; v0.1.0 may or may not have been pushed during the gap. Confirm with user before any tag/push.

## Don't do

- **Don't edit ADR-0007.** It is `Accepted`. Reversal = new ADR + flip 0007 to `Superseded by NNNN`. Same rule that applies to 0001–0006.
- **Don't add a third doc-creation script (e.g., `new-discovery.py`) without lifting `next_folder_nnnn` into `scripts/_doc_lib/`.** Right now it's deliberately private to `new-rfc.py` per the YAGNI note in its docstring; a third script means the lift is justified.
- **Don't bypass the wrapper-parity rule.** The two wrappers per Skill (`SKILL.md` + `prompt.md`) must convey the same when/how/after content. Any drift is a bug; either fix the drift or open a follow-up to single-source them.
- **Don't extend `.gitignore` ad-hoc.** A pre-existing gap exists (`__pycache__/` is untracked) — log it as a follow-up if it bothers anyone; don't bundle it into a Slice 2.5 commit.
- **Don't push without confirming with the user first.** The kit's prior handoff established this rule; it still applies.
