---
name: standard-update-changelog
description: Review meaningful repository changes and draft a Keep-a-Changelog entry.
---

# standard-update-changelog

## When to invoke

Use near the end of meaningful work, especially when the Stop hook reports that
`CHANGELOG.md` may need an entry.

## How to invoke

From the repo root, inspect the current work:

`git status --short`

Then review the relevant diff and recent commits. Update `CHANGELOG.md` under
`[Unreleased]` when that section exists; otherwise add the smallest appropriate
Keep-a-Changelog section for the repository.

## After running

Keep the entry factual and user-facing. Do not invent issue numbers, release
dates, or validation that did not happen.

