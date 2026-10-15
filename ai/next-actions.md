---
last_updated: 2026-10-15
---

# Next Actions

1. **Run the manual hook tests (owner)** - tests A–D in `docs/rfcs/0007-how-should-the-kit-make-documentation-and-continuity-upkeep-automatic-instead-of-advisory/artifacts/spike-results.md`: Copilot in VS Code, Copilot CLI, the Copilot cloud agent, and Codex's interactive trust flow. Test A decides whether VS Code needs its own output variant. Then conclude RFC-0007 and write ADR-0023.
2. **Run RFC-0008's checks** - cloud-agent plugin skills and `agentStop`, Codex marketplace-plugin hooks, and whether `.claude/skills` show as slash commands in VS Code and Copilot CLI; decide where the marketplace lives. Then conclude RFC-0008 and write ADR-0024.
3. **Land the parked ADR-0022 branch** - open a PR for `feat/adr-0022-daily-changelog-grouping`. It also carries the managed `AGENTS.md` simplification; split it first if atomic history matters.
4. **Draft RFC-0009: setup wizard and composable profiles** - bare `standards` opens a menu; setup asks "what does this repo contain?" (multi-select, docs-only means no picks) and picks init vs adopt automatically. The setup flow may live in the plugin (RFC-0008). Also fix `new-rfc.py --help` creating an RFC titled "help".
5. **Validate the documentation profile in one real docs-only repo** - confirm the `source-map` extra and profile matrix fit a repo whose implementation lives elsewhere.
6. **Pilot `standards doctor --recommend` and `standard-get-session-context` in one real downstream repo** - capture whether recommendations and context summaries are useful, noisy, or missing important signals.
