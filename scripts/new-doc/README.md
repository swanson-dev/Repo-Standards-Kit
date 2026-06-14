# `scripts/new-doc/`

Stdlib-only Python scripts for scaffolding repo documents and AI skill surfaces.

| Script | Creates | Template source |
|---|---|---|
| `new-adr.py "Title"` | `docs/decisions/<NNNN>-<slug>.md` | `docs/templates/adr-template.md` |
| `new-rfc.py "Question"` | `docs/rfcs/<NNNN>-<slug>/rfc.md` | `docs/templates/rfc-template.md` |
| `new-skill.py "skill-name" "Description"` | `.claude/skills/<skill-name>/SKILL.md`, `.github/prompts/<skill-name>.prompt.md`, and the `AGENTS.md` skills row | `docs/templates/skill-template.md`, `docs/templates/skill-prompt-template.md` |

## How they work

1. Walk up from the current working directory to find `.git` and establish the repo root.
2. Read the matching template under `docs/templates/`.
3. Compute any required target name: ADR/RFC scripts allocate the next zero-padded `NNNN`; `new-skill.py` validates a kebab-case skill name.
4. Substitute the known fields for that artifact. Numbered docs get today's ISO 8601 date and the `NNNN. Title` heading; skills get the name and description.
5. Write the file or folder. Refuse to overwrite existing artifacts.
6. Print the created path. For ADRs, also print a paste-ready row for the manual index in `docs/decisions/README.md`; for skills, update the `AGENTS.md` skills index.

## Exit codes

- `0` - artifact created successfully.
- `2` - precondition failure (no git repo, missing template, missing target dir or section, invalid input, artifact already exists). Single-line message on stderr.

## How to invoke from AI tools

| Tool | Wrapper |
|---|---|
| Claude Code | `.claude/skills/new-adr/SKILL.md`, `.claude/skills/new-rfc/SKILL.md` |
| GitHub Copilot Chat | `.github/prompts/new-adr.prompt.md`, `.github/prompts/new-rfc.prompt.md` |
| Anything else (bash, Codex, manual) | `python scripts/new-doc/new-adr.py "<title>"`, `python scripts/new-doc/new-skill.py "<skill-name>" "<description>"` |

The wrappers are documentation-grade. All behavior lives in the Python scripts; see ADR-0007 for the form-factor rationale.

## Tests

```sh
python scripts/new-doc/test_helpers.py
python scripts/new-doc/test_cli.py
python scripts/new-doc/test_new_skill.py
```

All tests use stdlib `unittest`; no third-party dependencies.
