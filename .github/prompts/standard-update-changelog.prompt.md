---
mode: agent
description: Review meaningful repository changes and draft a Keep-a-Changelog entry.
---

# standard-update-changelog

Run `git status --short`, then review the relevant diff and recent commits.
Update `CHANGELOG.md` under `[Unreleased]` when that section exists; otherwise
add the smallest appropriate Keep-a-Changelog section for the repository.

Keep the entry factual and user-facing. Do not invent issue numbers, release
dates, or validation that did not happen.

