---
mode: agent
description: Scaffold a new MADR 3.0 ADR with the next NNNN, today's date, and the title filled in.
---

# new-adr

When the user asks to record an architecture decision, run this from the repo root:

`python scripts/new-doc/new-adr.py "<Title of the decision>"`

The script creates `docs/decisions/<NNNN>-<slug>.md`, prints the created path, and
prints a paste-ready row for the manual index in `docs/decisions/README.md`.

After scaffolding, open the created file. Fill `deciders`, `consulted`, `informed`,
the body sections, and paste the printed index row into `docs/decisions/README.md`.
Leave `status: Proposed` until the decision is accepted. Once `status: Accepted`,
the body is immutable — reversal is a new ADR.
