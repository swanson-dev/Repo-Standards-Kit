---
written: 2026-05-28T23:49:19-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Slice 2.6 is complete and green. `promote-discovery` ships as the kit's second hook-backed Skill — same ADR-0008 pattern as `update-handoff`, applied to the SessionStart event. The script has two subcommands: `list` (verbose + `--check` for hook mode) and `promote <path> --to <target>` (monotonic flip from raw → promoted). No new ADR — Slice 2.6 is the proof that the pattern survives reuse. All 51 tests pass (14 + 12 + 10 + 15); standards-check exits clean; CHANGELOG records v0.4.0.

## Recently touched

- docs(slice-2.6): record v0.4.0 in CHANGELOG
- docs(slice-2.6): record Slice 2.6 in current-state; bump AGENTS to 0.4.0; drop Slice 2.6 from queued
- docs(slice-2.6): document scripts/promote-discovery/ contract and subcommands
- feat(slice-2.6): add promote-discovery Claude Skill and Copilot prompt wrappers
- feat(slice-2.6): wire promote-discovery SessionStart hook in .claude/settings.json
- feat(slice-2.6): add promote-discovery script (list + promote subcommands) with tests
- docs(slice-2.5): correct test count in CHANGELOG and update-handoff README (9 to 10)
- docs(slice-2.5): write Slice 2.5 handoff via dogfooded update-handoff

Files changed:
  - `CHANGELOG.md`
  - `AGENTS.md`
  - `ai/current-state.md`
  - `scripts/promote-discovery/README.md`
  - `.claude/skills/promote-discovery/SKILL.md`
  - `.github/prompts/promote-discovery.prompt.md`
  - `.claude/settings.json`
  - `scripts/promote-discovery/promote_discovery.py`
  - `scripts/promote-discovery/test_promote_discovery.py`
  - `scripts/update-handoff/README.md`
  - `ai/handoff.md`

## Open threads

- Branch pushed to `origin/ai-skills-implementation`; tags `v0.2.0`, `v0.3.0`, `v0.4.0` pushed (closed the CHANGELOG↔git-tag gap that prior slices left). Remote is `https://github.com/swanson-dev/Repo-Standards-Kit.git`. Working tree clean; nothing pending to push.
- **Slice 3 distribution** still queued at `ai/open-questions.md#q-2` — blocks `scaffold-new-repo`. Three credible options (template repo, plugin, copy script); next session likely starts here per user's stated direction.
- Slice 4 (deeper CI: content linting, doc freshness, link checking, wrapper-parity lint, every-`promoted_to:`-resolves) still queued.
- `strip_leading_html_comment` is now duplicated across `new-adr.py`, `new-rfc.py`, and `promote_discovery.py` — kit's "third caller = lift" rule fires. Worth lifting to `_doc_lib/helpers.py` as a chore commit before or alongside Slice 3.
- Spec reviewer flagged the live `promote-discovery list` against a real raw discovery item was deferred (kit's own `docs/discovery/` is empty). First real discovery file someone creates will be the proper smoke test.

## Don't do

- Don't edit ADRs 0001–0008. All are `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- Don't add a write-mode auto-trigger to the `promote-discovery` SessionStart hook. ADR-0008 explicitly chose advisory-only for hook surfaces.
- Don't bypass the wrapper-parity rule. `promote-discovery`'s SKILL.md and prompt.md must convey the same content; documented asymmetry is the Copilot-can't-auto-trigger note.
- Don't add `reviewed` → `promoted` transition to the `promote` subcommand without first asking whether `reviewed` is a real state in usage. The kit allows it in frontmatter but no script flips it yet.
- Don't push without confirming with the user first.
