---
last_updated: 2026-10-19
---

# Next Actions

1. **Build M9, the setup wizard (ADR-0025)** - slice 1 is built on `feat/m9-setup-wizard`: four profiles, with `infra` merged into application and kept as an alias in `--profile`, markers, and checklists. Next, slice 2: combinable profiles. Put the matrix in code with a sync test against `docs/STANDARDS.md`, let `--profile` take a comma list, write `"profiles": [...]` to the marker with `profile` as the first entry, join the checklist header with ` + `, and have setup create and tick the docs the profiles need. Then the bare `standards` menu and the setup wizard; lift `setup_logic.py` from RFC-0009's `artifacts/prototype/`. Ships as v1.5.0.
2. **Close out M8 (shipped in v1.4.0)** - test D (Codex's interactive trust flow) is still a manual run; the steps are in RFC-0007's `artifacts/spike-results.md`. Shipping Codex hook config waits on RFC-0008's plugin.
3. **Run RFC-0008's checks** - cloud-agent plugin skills and `agentStop`, Codex marketplace-plugin hooks, and whether `.claude/skills` show as slash commands in VS Code and Copilot CLI. Then conclude RFC-0008 and write ADR-0024.
4. **Land the parked ADR-0022 branch** - open a PR for `feat/adr-0022-daily-changelog-grouping`. It also carries the managed `AGENTS.md` simplification; split it first if atomic history matters.
5. **Build RFC-0010 (retrospectives) after RFC-0007 to RFC-0009 conclude** - `docs/rfcs/0010-how-should-the-kit-turn-session-lessons-into-lasting-improvements/rfc.md`. Draft `standard-retro`, run one trial retro on a real session, conclude, and write ADR-0026.
6. **Validate the documentation profile in one real docs-only repo** - confirm the `source-map` extra and profile matrix fit a repo whose implementation lives elsewhere.
7. **Pilot `standards doctor --recommend` and `standard-get-session-context` in one real downstream repo** - capture whether recommendations and context summaries are useful, noisy, or missing important signals.
