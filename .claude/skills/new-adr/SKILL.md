---
name: new-adr
description: Scaffold a new MADR 3.0 ADR with the next NNNN, today's date, and the title filled in.
---

# new-adr

## When to invoke

Use when the user is about to record an architecture decision — typically because the
`AGENTS.md` end-of-session contract requires an ADR for a material technical decision,
or because an RFC's `Follow-ups → ADR to write` field points to a new ADR.

## How to invoke

Run from the repo root:

`python scripts/new-doc/new-adr.py "<Title of the decision>"`

The script creates `docs/decisions/<NNNN>-<slug>.md`, prints the created path, and
prints a paste-ready row for the manual index in `docs/decisions/README.md`.

## After scaffolding

Open the created file. Fill `deciders`, `consulted`, `informed`, the body sections,
and paste the printed index row into `docs/decisions/README.md`. Leave
`status: Proposed` until the decision is accepted. Once `status: Accepted`,
the body is immutable — reversal is a new ADR.
