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

_No ADRs yet. The `new-adr` script prints the index row to paste here when you create one._
