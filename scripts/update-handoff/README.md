# `scripts/update-handoff/`

Stdlib-only Python script that generates a draft `ai/handoff.md` from git state,
captures a compact pre-compaction snapshot, or emits an advisory line on Claude
Code Stop events when work has accumulated.

## Two modes

| Invocation | Mode | What it does |
|---|---|---|
| `python scripts/update-handoff/update_handoff.py` | write | Creates/updates `ai/handoff.md`. Frontmatter + "Recently touched" pre-filled from git. Refuses to overwrite without `--force`. |
| `python scripts/update-handoff/update_handoff.py --force` | write | Same as above, overwriting an existing handoff. |
| `python scripts/update-handoff/update_handoff.py --compact-snapshot --force` | write | Writes a compact pre-compaction checkpoint to `ai/handoff.md`. |
| `python scripts/update-handoff/update_handoff.py --check` | hook | Silent if no commits and no modified files since last handoff. Otherwise prints one line to stderr. Always exits 0 (never breaks the session). |

## How "Recently touched" is computed

- If `ai/handoff.md` exists: `git log --since=<prior-written-ts> --pretty=format:"%s"` for commit subjects; same flag on `--name-only` for changed files.
- If absent: last 10 commits (a sensible cap so a long-history repo doesn't produce a multi-page first draft).

The prior `written:` timestamp is parsed verbatim from frontmatter and handed to `git log --since=` — git accepts the ISO 8601 string directly, no Python date parsing needed.

## Exit codes

| Mode | Exit | When |
|---|---|---|
| write | 0 | Handoff written |
| write | 2 | Not in a git repo, or `ai/handoff.md` exists without `--force` |
| `--check` | 0 | Always (hook mode must never break the session) |

## Invocation surfaces

| Surface | File |
|---|---|
| Claude Code Stop hook | `.claude/settings.json` |
| Claude Code slash command | `.claude/skills/standard-update-handoff/SKILL.md`, `.claude/skills/standard-compact-snapshot/SKILL.md` |
| GitHub Copilot Chat | `.github/prompts/standard-update-handoff.prompt.md`, `.github/prompts/standard-compact-snapshot.prompt.md` |
| Bash / Codex / manual | `python scripts/update-handoff/update_handoff.py` |

The Stop hook calls `--check` (advisory only); slash commands call write modes.
Both pathways converge on the same Python script. See **ADR-0008** for the
form-factor rationale and ADR-0020 for the AI continuity commands.

## Tests

```
python scripts/update-handoff/test_update_handoff.py
```

Stdlib `unittest` cases against temporary git repos. No third-party deps.
