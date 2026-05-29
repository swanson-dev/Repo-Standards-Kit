---
mode: agent
description: Scaffold a new RFC folder with rfc.md, the next NNNN, and today as `opened`.
---

# new-rfc

When the user asks to open a time-boxed investigation that needs a written record,
run this from the repo root:

`python scripts/new-doc/new-rfc.py "<Question being investigated>"`

The script creates `docs/rfcs/<NNNN>-<slug>/rfc.md` and prints the created path.
It does **not** create an `artifacts/` subfolder — add that yourself if the RFC
collects benchmarks, screenshots, or prototype code.

After scaffolding, open the created file. Fill `owner`, `time_box`, and the body
sections. Every RFC must eventually reach `status: Concluded` or `status: Abandoned`,
or its question must be moved to `ai/open-questions.md`. RFCs do not sit Open
indefinitely.
