---
last_updated: 2026-10-20
---

# Next Actions

1. **Release M9 as v1.5.0 (ADR-0025)** - all three slices are built on `feat/m9-setup-wizard`: four profiles with `infra` kept as an alias, combinable profiles with setup creating and ticking their docs, and the bare `standards` menu with the setup wizard and `standards change`. The terminal path is verified by a pseudo-terminal test (`MenuInATerminalTests`, run in CI on Linux and skipped on Windows); one look at the menu yourself is optional. Then prepare the release (version, changelog section, roadmap, `AGENTS.md` kit version), open the PR, merge, and tag `v1.5.0`.
2. **Close out M8 (shipped in v1.4.0)** - test D (Codex's interactive trust flow) is still a manual run; the steps are in RFC-0007's `artifacts/spike-results.md`. Shipping Codex hook config waits on RFC-0008's plugin.
3. **Run RFC-0008's checks** - cloud-agent plugin skills and `agentStop`, Codex marketplace-plugin hooks, and whether `.claude/skills` show as slash commands in VS Code and Copilot CLI. Then conclude RFC-0008 and write ADR-0024.
4. **Land the parked ADR-0022 branch** - open a PR for `feat/adr-0022-daily-changelog-grouping`. It also carries the managed `AGENTS.md` simplification; split it first if atomic history matters.
5. **Build RFC-0010 (retrospectives) after RFC-0007 to RFC-0009 conclude** - `docs/rfcs/0010-how-should-the-kit-turn-session-lessons-into-lasting-improvements/rfc.md`. Draft `standard-retro`, run one trial retro on a real session, conclude, and write ADR-0026.
6. **Validate the documentation profile in one real docs-only repo** - confirm the `source-map` extra and profile matrix fit a repo whose implementation lives elsewhere.
7. **Pilot `standards doctor --recommend` and `standard-get-session-context` in one real downstream repo** - capture whether recommendations and context summaries are useful, noisy, or missing important signals.
