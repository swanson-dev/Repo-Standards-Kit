---
status: Concluded
opened: 2026-06-01
closed: 2026-06-01
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

- The reconcile primitives already do the hard part. The sidecar-on-conflict and managed-block
  splice logic from `run_update` (and the scaffold-once "seed only when absent" rule) are
  exactly what retrofit needs. The blocking piece was purely `init`'s pre-flight guard, which
  treated any differing pre-existing kit file as a hard stop rather than a reconcile input.
- A retrofit does NOT need a marker to reconcile. `run_update` reads the marker to distinguish
  "untouched since last sync" from "edited downstream"; on a first-run adopt there is no prior
  baseline, so every differing file is simply adopter-owned → keep it + sidecar. That makes
  `adopt` simpler than `update`, not a special case of it.
- The one real decision was the blockless partial file (an existing hand-written `AGENTS.md`
  with no kit-managed block). There is nothing to splice into, so the choice was append the
  kit block (installs the contract, non-destructive) vs. sidecar (conservative, leaves the
  file untouched). Appending was chosen: it is the designed purpose of managed regions and
  removes nothing.

## Recommendation

**Concluded → Option A.** Implemented `standards adopt` as a dedicated non-destructive
subcommand (not `init --merge`), reconciling each file by ownership class: copy-if-absent;
keep-and-sidecar a differing kit-tracked file; splice an existing managed block or append the
kit block to a blockless partial file; seed scaffold-once only when absent; then write the
marker so the repo is `update`-ready. `init`'s collision error now points at `adopt`. The
decision and per-class behavior are recorded in **ADR-0013**. Out of scope (unchanged): the
kit never rewrites prose it does not own.

## Follow-ups

- **ADR to write:** yes — [`docs/decisions/0013-standards-adopt-for-non-destructive-adoption-onto-existing-repos.md`](../../decisions/0013-standards-adopt-for-non-destructive-adoption-onto-existing-repos.md).
- **Implementation plan changes:** shipped in v0.11.0 (`run_adopt` + `adopt` subcommand + `tests/test_adopt.py`); no separate plan doc.
- **New open questions:** none.
- **Discovery to promote:** none.
