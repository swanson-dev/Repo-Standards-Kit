# `docs/decisions/`

Architecture Decision Records (ADRs) — the durable record of **why** the current shape exists.

## Format

[MADR 3.0](https://adr.github.io/madr/). Template: [`../templates/adr-template.md`](../templates/adr-template.md).

## Filename

`NNNN-kebab-case-title.md` — zero-padded 4 digits, monotonically increasing.

## Lifecycle

```
Proposed  →  Accepted  →  Deprecated
                       ↘  Superseded by NNNN
```

**Once `Accepted`, the body is not edited.** To change an accepted decision, write a new ADR with the new decision and flip the old ADR's status to `Superseded by <new-NNNN>`. This preserves the historical record.

## When to write an ADR

Any time the team makes a material technical decision: a structural choice, a library adoption, a protocol commitment, a process change with engineering impact. If you find yourself writing "the reason we did X is…" in a PR comment that's longer than two sentences, that's the signal — write an ADR.

If a decision is the result of an RFC, the RFC's `Follow-ups → ADR to write` field should link the new ADR.

## Index

| ADR | Title |
|---|---|
| [0001](./0001-record-architecture-decisions.md) | Record architecture decisions |
| [0002](./0002-adopt-madr-3.md) | Adopt MADR 3.0 as the ADR format |
| [0003](./0003-adopt-repo-profile-model.md) | Adopt a repo-profile model with tiered doc requirements |
| [0004](./0004-define-ai-directory-contract.md) | Define the ai/ directory as committed, shared, rolling state |
| [0005](./0005-split-discovery-and-rfcs.md) | Split discovery and RFCs into separate folders |
| [0006](./0006-adopt-agents-md-pattern.md) | Adopt the AGENTS.md pattern with thin tool-specific pointers |
| [0007](./0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md) | Author AI-tool wrappers as thin shells over stdlib Python scripts |
| [0008](./0008-hooks-invoke-script-in-check-mode-behavior-writes-via-slash-command.md) | Hooks invoke script in check mode; behavior writes via slash command |
| [0009](./0009-distribute-the-kit-as-a-pypi-standards-cli-with-vendored-copy-sync.md) | Distribute the kit as a PyPI `standards` CLI with vendored-copy sync |
| [0010](./0010-managed-region-sentinels-for-partially-kit-owned-files.md) | Managed-region sentinels for partially kit-owned files |
| [0011](./0011-publish-to-pypi-via-github-actions-trusted-publishing.md) | Publish to PyPI via GitHub Actions Trusted Publishing |
| [0012](./0012-expose-standards-check-by-subprocessing-the-bundled-check.md) | Expose standards check by subprocessing the bundled check |
| [0013](./0013-standards-adopt-for-non-destructive-adoption-onto-existing-repos.md) | standards adopt for non-destructive adoption onto existing repos |
| [0014](./0014-capture-stage-for-discovery-gitignore-raw-intake-track-synthesized-markdown.md) | Capture stage for discovery: gitignore raw intake, track synthesized markdown |
| [0015](./0015-promote-discovery-defaults-to-interactive-decision-shaping-the-cli-stays-a-plain-flip.md) | promote-discovery defaults to interactive decision-shaping; the CLI stays a plain flip |
| [0016](./0016-add-roadmap-section-to-implementation-plan.md) | Add a milestone roadmap section to the implementation-plan template |
| [0017](./0017-simplify-discovery-to-tracked-markdown-notes.md) | Simplify discovery to tracked markdown notes |
| [0018](./0018-validate-v1-readiness-with-generated-profile-fixtures.md) | Validate v1 readiness with generated profile fixtures |
| [0019](./0019-add-post-v1-adoption-assistant-commands-and-optional-knowledge-lanes.md) | Add post-v1 adoption assistant commands and optional knowledge lanes |
| [0020](./0020-add-advisory-ai-continuity-hooks-and-standard-slash-commands.md) | Add advisory AI continuity hooks and standard slash commands |

(Index is maintained manually for now; Slice 4 may automate it.)
