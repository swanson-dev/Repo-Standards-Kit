# Testing

The kit has no runtime, so there are no unit tests in the traditional sense. Verification is **structural** (does the artifact set match the spec?) and **walkthrough** (does adopting the kit actually work for the four profiles?).

## Test pyramid for this repo

| Layer | What it catches | Tooling |
|---|---|---|
| Structural lint | Filename conventions, status vocabulary, frontmatter presence | `.github/workflows/repo-standards.yml` (Phase E) |
| Self-application check | Does the kit conform to its own library-profile requirements? | The kit's own `STANDARDS-CHECKLIST.md` parsed by the same workflow |
| Walkthrough | Can a contributor adopt the kit in ≤30 minutes for an empty repo of each profile? | Manual, recorded in `docs/discovery/` of a real downstream repo |
| Cross-tool agent check | Do Claude Code, Copilot, and one other tool all land on `AGENTS.md` and follow the canonical reading order? | Manual, per release |

## Coverage targets

- **Structural lint:** 100% of files matched by the workflow rules.
- **Self-application:** every Required and Expected doc for the `library` profile present (or waived) in this kit.
- **Walkthrough:** at least one downstream repo per profile (4 total) before the kit cuts a 1.0.0.

## How to run locally

The standards check workflow can be run manually once Phase E lands:

```
gh workflow run repo-standards.yml
```

Or run the underlying script locally (Phase E adds the script under `scripts/`).

## CI

`.github/workflows/repo-standards.yml` runs the structural lint and self-application check on every push and PR to `main`. Phase E adds the workflow file.

## Flaky-test policy

Structural lint should never be flaky — it's deterministic markdown parsing. If a check goes red intermittently, treat it as a real bug (likely a parser ambiguity or a frontmatter edge case) rather than a transient.

## Test data

The kit is its own test data — the structural lint runs against this very repo's files. The kit therefore must always pass its own standards check before a release tag is cut.
