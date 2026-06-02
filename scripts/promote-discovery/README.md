# `scripts/promote-discovery/`

Stdlib-only Python script that audits `docs/discovery/` tracked notes for unpromoted items, or flips a specific item from `status: raw` to `status: promoted` with a `promoted_to:` target. (Capture of raw source material into notes is a separate step — see `scripts/capture-discovery/`.)

## Subcommands

| Invocation | Mode | What it does |
|---|---|---|
| `python scripts/promote-discovery/promote_discovery.py list` | verbose | Prints a table of all `status: raw` items in `docs/discovery/`. Default subcommand. |
| `python scripts/promote-discovery/promote_discovery.py list --check` | hook | Silent if zero raw items. Otherwise prints one line to stderr. Always exits 0 (never breaks the session). |
| `python scripts/promote-discovery/promote_discovery.py promote <path> --to <target>` | write | Flips `<path>`'s frontmatter: `status: raw` → `status: promoted` and sets `promoted_to: <target>`. Both args required. Monotonic — no `--force`. |

## How discovery items are identified

The script walks `docs/discovery/**/*.md`, skipping `README.md`, any path containing a `templates/` component, and the gitignored raw-intake folders (`meetings/`, `requirements/`, `use-cases/`, `notes/`) — so only tracked notes (`captured/` and any top-level item) are inventoried (ADR-0014). For each file it parses leading frontmatter (between the first two `---` fences; a leading `<!-- ... -->` HTML comment block is stripped first, since the discovery templates carry one). Files without frontmatter are skipped silently.

An item is "raw" if its `status:` value equals exactly `raw`. Items with `status: reviewed`, `status: promoted`, or no `status:` field are ignored.

## Exit codes

| Mode | Exit | When |
|---|---|---|
| `list` | 0 | Always (verbose mode, even with zero items) |
| `list` | 2 | Not in a git repo |
| `list --check` | 0 | Always (hook mode must never break the session) |
| `promote` | 0 | Item flipped successfully |
| `promote` | 2 | Not in git, file missing, not under `docs/discovery/`, no frontmatter, no `status:`, status not `raw`, `--to` missing/absolute/contains `..` |

## Invocation surfaces

| Surface | File |
|---|---|
| Claude Code SessionStart hook | `.claude/settings.json` (the SessionStart array) |
| Claude Code slash command | `.claude/skills/promote-discovery/SKILL.md` |
| GitHub Copilot Chat | `.github/prompts/promote-discovery.prompt.md` |
| Bash / Codex / manual | `python scripts/promote-discovery/promote_discovery.py <subcommand>` |

The hook calls `list --check` (advisory only); the slash commands call `list` or `promote`. All pathways converge on the same Python script. See **ADR-0008** for the form-factor rationale — this script is the second concrete application of that pattern (the first was `update-handoff` in Slice 2.5).

## Tests

```
python scripts/promote-discovery/test_promote_discovery.py
```

17 stdlib `unittest` cases against `tmp_path` git repos. No third-party deps.
