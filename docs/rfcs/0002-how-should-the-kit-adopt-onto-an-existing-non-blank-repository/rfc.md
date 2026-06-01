---
status: Open
opened: 2026-06-01
closed:
owner: swanson-dev
time_box: 2 days
---

# 0002. How should the kit adopt onto an existing non-blank repository

## Question

How should `standards init` adopt the kit onto a repository that already has its own
README, docs, and CI, without clobbering existing work or refusing outright?

## Why now

`standards init` is greenfield-oriented. Its pre-flight guard (`src/standards/init.py`)
raises `FileExistsError` when any kit-tracked file already exists with differing content,
unless `--force` is passed — and `--force` overwrites bluntly. There is no path between
"blank repo → init" and "already-adopted repo → update". But the common real case is a
repository that already exists: it has a `README.md`, a `CHANGELOG.md`, maybe a partial
`docs/` tree, and existing `.github/` CI. Today such a repo can only adopt by either
emptying conflicting files first or running `--force` and losing local content.

This is more than a feature gap — it is an untested assumption. The kit's own
`ai/next-actions.md` listed "walk one downstream repo per profile through adoption" as a
step that was never completed, so retrofit adoption has never been exercised against a real
repository. Slice 5 hardened the greenfield path (the multi-profile dogfood gate now proves
`init` yields a CI-green repo); this RFC investigates the retrofit path that remains.

## Approach

1. Enumerate the conflict classes a real repo presents: (a) adopter already owns a file the
   kit also ships (e.g. `README.md`, `.github/pull_request_template.md`); (b) adopter has a
   partial file the kit partially owns (`AGENTS.md` with no kit-managed block yet); (c)
   adopter has a directory the kit seeds into (`docs/` with some numbered docs already
   present).
2. Map each class onto the existing three-class ownership model (kit-tracked / scaffold-once
   / managed-region) and the reconcile engine in `src/standards/update.py`, to see how much
   of retrofit is already solved by `run_update`'s hash-guarded splice + sidecar logic.
3. Prototype option (a) below against two real repos (one per representative profile) and
   record what conflicts arise and whether the sidecar/managed-block resolution is
   acceptable to a human reviewer.

## Findings

To be completed by the investigation. Initial framing only:

- The reconcile engine already does the hard part. `run_update` already handles "file exists,
  hash differs → write `.kit-<version>` sidecar, keep adopter's copy" and "managed block
  matches → splice". A retrofit is conceptually an update applied from a baseline of "no
  marker / version none".
- The blocking piece is purely the init pre-flight guard, which treats any differing
  pre-existing kit file as a hard stop rather than a reconcile input.
- `scaffold-once` already does the right thing for retrofit (it only seeds when absent), so
  an adopter's existing `ai/` or `docs/00-overview.md` would be preserved automatically.

## Recommendation

Leaning toward **Option A — `standards adopt` as a "first-run update"**: introduce an adopt
mode that reuses `run_update`'s reconcile engine instead of the blunt init guard. For each
kit-tracked file already present and differing, write a sidecar and keep the adopter's copy
(never clobber); for partial files, splice the managed block into the existing file; for
scaffold-once, seed only when absent; then write the marker. This maximizes reuse of tested
code and makes adoption non-destructive by construction. Two alternatives remain on the
table for the investigation to rule out: **Option B** — extend `init` with a `--merge` flag
rather than a new subcommand; **Option C** — ship a read-only `standards diff` that reports
the gap and lets a human adopt incrementally. Explicitly out of scope: auto-rewriting an
adopter's existing README/doc prose — the kit reconciles ownership, it does not edit content
it does not own.

## Follow-ups

- **ADR to write:** yes (expected) — record the chosen retrofit mechanism once concluded.
- **Implementation plan changes:** a future Slice 6 plan implements the chosen option; none yet.
- **New open questions:** none yet; any unresolved sub-question moves to `ai/open-questions.md` on conclusion.
- **Discovery to promote:** none.
