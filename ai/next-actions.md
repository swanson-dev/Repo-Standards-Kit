---
last_updated: 2026-10-20
---

# Next Actions

1. **Release v1.5.0 (M9, ADR-0025)** - prepared on `feat/m9-setup-wizard` (`chore(release): prepare v1.5.0`), and the release PR to `main` is open. Once CI passes and the owner merges it, tag `v1.5.0` on `main` (its `release.yml` publishes to PyPI and creates the GitHub Release), then point the CHANGELOG `[1.5.0]` link at the release tag (`docs/RELEASING.md` step 3) and run the published-package smoke.
2. **Close out M8 (shipped in v1.4.0)** - test D (Codex's interactive trust flow) is still a manual run; the steps are in RFC-0007's `artifacts/spike-results.md`. Shipping Codex hook config waits on RFC-0008's plugin.
3. **Run RFC-0008's checks** - cloud-agent plugin skills and `agentStop`, Codex marketplace-plugin hooks, and whether `.claude/skills` show as slash commands in VS Code and Copilot CLI. Then conclude RFC-0008 and write ADR-0024.
4. **Land the parked ADR-0022 branch** - open a PR for `feat/adr-0022-daily-changelog-grouping`. It also carries the managed `AGENTS.md` simplification; split it first if atomic history matters.
5. **Build RFC-0010 (retrospectives) after RFC-0007 to RFC-0009 conclude** - `docs/rfcs/0010-how-should-the-kit-turn-session-lessons-into-lasting-improvements/rfc.md`. Draft `standard-retro`, run one trial retro on a real session, conclude, and write ADR-0026.
6. **Validate the documentation profile in one real docs-only repo** - confirm the `source-map` extra and profile matrix fit a repo whose implementation lives elsewhere.
7. **Pilot `standards doctor --recommend` and `standard-get-session-context` in one real downstream repo** - capture whether recommendations and context summaries are useful, noisy, or missing important signals.
