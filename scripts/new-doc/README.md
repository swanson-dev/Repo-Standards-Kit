# `scripts/new-doc/`

Two stdlib-only Python scripts for scaffolding numbered repo documents.

| Script | Creates | Template source |
|---|---|---|
| `new-adr.py "Title"` | `docs/decisions/<NNNN>-<slug>.md` | `docs/templates/adr-template.md` |
| `new-rfc.py "Question"` | `docs/rfcs/<NNNN>-<slug>/rfc.md` | `docs/templates/rfc-template.md` |

## How they work

1. Walk up from the current working directory to find `.git` — establishes the repo root.
2. Read the matching template under `docs/templates/`.
3. Compute the next zero-padded `NNNN` by scanning the target directory.
4. Slugify the title (lowercase, kebab-case, alnum only).
5. Substitute today's ISO 8601 date and the `NNNN. Title` heading. **All other `<...>` placeholders are left intact** — scaffolding ≠ authoring.
6. Write the file (or folder for RFC). Refuse to overwrite existing artifacts.
7. Print the created path. For ADRs, also print a paste-ready row for the manual index in `docs/decisions/README.md`.

## Exit codes

- `0` — file/folder created successfully.
- `2` — precondition failure (no git repo, missing template, missing target dir, empty/invalid title, file already exists). Single-line message on stderr.

## How to invoke from AI tools

| Tool | Wrapper |
|---|---|
| Claude Code | `.claude/skills/new-adr/SKILL.md`, `.claude/skills/new-rfc/SKILL.md` |
| GitHub Copilot Chat | `.github/prompts/new-adr.prompt.md`, `.github/prompts/new-rfc.prompt.md` |
| Anything else (bash, Codex, manual) | `python scripts/new-doc/new-adr.py "<title>"` |

The wrappers are documentation-grade. All behavior lives in the Python scripts — see ADR-0007 for the form-factor rationale.

## Tests

```
python scripts/new-doc/test_helpers.py     # unit tests for _doc_lib helpers
python scripts/new-doc/test_cli.py         # subprocess E2E tests for both CLIs
```

Both use stdlib `unittest`; no third-party dependencies.
