---
last_updated: 2026-10-17
---

# Next Actions

1. **Finish M8, the automation engine (ADR-0023)** - built: the drift core and block-once Stop hook (`scripts/drift/drift.py`, wired into `.claude/settings.json`), the CI drift check (`standards check --drift-base`, run on PRs by `repo-standards.yml`), and the Copilot results: manual tests A–C in RFC-0007's `artifacts/spike-results.md` showed every Copilot host takes the top-level output, and on CI runners the hook now blocks once per session (test C2). Test B2 showed every Copilot host also reads `.claude/settings.json`, so `init`/`adopt --agents` (detected by default, recorded in `.standards-kit.json`) now ships one hook file per repo: Claude's, or `.github/hooks/standards.json` for Copilot-only teams. Left: test D (Codex's interactive trust flow). Shipping Codex hook config waits on RFC-0008's plugin.
2. **Run RFC-0008's checks** - cloud-agent plugin skills and `agentStop`, Codex marketplace-plugin hooks, and whether `.claude/skills` show as slash commands in VS Code and Copilot CLI. Then conclude RFC-0008 and write ADR-0024.
3. **Land the parked ADR-0022 branch** - open a PR for `feat/adr-0022-daily-changelog-grouping`. It also carries the managed `AGENTS.md` simplification; split it first if atomic history matters.
4. **Build M9, the setup wizard (RFC-0009 concluded, ADR-0025)** - bare `standards` menu, one non-destructive setup, the "what does this repo contain?" wizard, and four combinable profiles with `infra` merged into application (kept as an alias). Lift `setup_logic.py` from RFC-0009's `artifacts/prototype/` into `src/standards/`, put the matrix in code with a sync test against `docs/STANDARDS.md`, and update `docs/STANDARDS.md`, the templates' tier headers, and `structural.py`/`doctor.py`/`init.py`/`cli.py`. Then conclude RFC-0009 and write ADR-0025.
5. **Build RFC-0010 (retrospectives) after RFC-0007 to RFC-0009 conclude** - `docs/rfcs/0010-how-should-the-kit-turn-session-lessons-into-lasting-improvements/rfc.md`. Draft `standard-retro`, run one trial retro on a real session, conclude, and write ADR-0026.
6. **Validate the documentation profile in one real docs-only repo** - confirm the `source-map` extra and profile matrix fit a repo whose implementation lives elsewhere.
7. **Pilot `standards doctor --recommend` and `standard-get-session-context` in one real downstream repo** - capture whether recommendations and context summaries are useful, noisy, or missing important signals.
