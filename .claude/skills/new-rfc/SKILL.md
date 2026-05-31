---
name: new-rfc
description: Scaffold a new RFC folder with rfc.md, the next NNNN, and today as `opened`.
---

# new-rfc

## When to invoke

Use when the user is about to open a time-boxed investigation that needs a written
record — typically to satisfy the `AGENTS.md` end-of-session contract item "If you ran
a time-boxed investigation, write or conclude an RFC", because a question can't be
resolved inside a single conversation and the team wants to track its approach,
findings, and recommendation.

## How to invoke

Run from the repo root:

`python scripts/new-doc/new-rfc.py "<Question being investigated>"`

The script creates `docs/rfcs/<NNNN>-<slug>/rfc.md` and prints the created path.
It does **not** create an `artifacts/` subfolder — add that yourself if the RFC
collects benchmarks, screenshots, or prototype code.

## After scaffolding

Open the created file. Fill `owner`, `time_box`, and the body sections. Every RFC
must eventually reach `status: Concluded` or `status: Abandoned`, or its question
must be moved to `ai/open-questions.md`. RFCs do not sit Open indefinitely.
