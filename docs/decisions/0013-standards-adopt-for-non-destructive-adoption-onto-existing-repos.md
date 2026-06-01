---
status: Accepted
date: 2026-06-01
deciders: swanson-dev
consulted: —
informed: kit adopters
---

# 0013. standards adopt for non-destructive adoption onto existing repos

## Context and Problem Statement

`standards init` is greenfield-oriented: its pre-flight guard refuses when any kit-owned file
already exists with differing content, and `--force` overwrites bluntly. Existing repos —
which already have their own `README`, `AGENTS.md`, `docs/`, and CI — therefore had no clean
adoption path (RFC-0002). The kit's whole premise is non-destructive adoption, so the gap was
a correctness hole, not just a missing convenience.

How should the kit adopt onto an existing, non-blank repository without clobbering local work?

## Decision Drivers

- Never clobber adopter content (the kit's core invariant; ADR-0009/0010).
- Reuse the existing ownership model (kit-tracked / scaffold-once / partial managed-region)
  and primitives rather than inventing a parallel mechanism.
- Keep runtime stdlib-only; keep the command surface small and predictable.
- Leave the repo adopted (a valid marker) so subsequent `standards update` works normally.

## Considered Options

- **Option A** — a new `standards adopt` subcommand: a non-destructive "first-run" that
  reconciles each file by ownership class.
- **Option B** — extend `init` with a `--merge` flag.
- **Option C** — a read-only `standards diff` that only reports the gap for manual adoption.

## Decision Outcome

Chosen option: **Option A**, a dedicated `standards adopt` subcommand (RFC-0002 leaned this
way). It keeps `init`'s tested "refuse on collision" contract intact while giving existing
repos their own non-destructive path. Per-file behavior by ownership class:

- **kit-tracked, absent** → copy it (recorded as tracked).
- **kit-tracked, present & identical** → record, no-op.
- **kit-tracked, present & differing** → keep the adopter's file; write the kit copy as a
  `<rel>.kit-<version>` sidecar; record the kit's hash as the tracked baseline so a later
  `update` continues to treat the adopter's file as edited (sidecars again, never clobbers).
- **partial (managed-region), absent** → copy it.
- **partial, present with the kit block** → splice the kit's current block inner in (the kit
  owns that region by definition; the adopter's content outside the block is untouched).
- **partial, present with NO block** → append the kit's managed block to the end of the file,
  preserving all existing content above it. This installs the kit contract via the
  managed-region mechanism (its designed purpose) and is non-destructive (nothing removed).
- **partial, malformed/duplicate markers** → don't guess; sidecar.
- **scaffold-once, absent** → seed (shared with `init`, CI-green transforms applied);
  **present** → leave it (adopter owns it).

`init` and `adopt` share the scaffold-once seeding and marker write; `init`'s collision error
now points the user at `adopt`.

### Consequences

- **Good:** existing repos adopt without losing work; one ownership model and one set of
  primitives serve both init/update/adopt; the repo ends adopted and `update`-ready.
- **Bad:** `adopt` mutates a hand-written `AGENTS.md`/`CLAUDE.md` by appending the kit block
  (chosen over a sidecar so adoption actually installs the contract); a noisy repo can produce
  several `.kit-<version>` sidecars the adopter must merge by hand.
- **Neutral:** two adoption verbs now exist (`init` for blank/clean, `adopt` for existing);
  the distinction is surfaced in `init`'s error message and help text.

## Pros and Cons of the Options

### Option A (new `standards adopt`)
- Good: keeps `init` semantics intact; clear, discoverable verb; reuses the reconcile model.
- Bad: a second adoption command to document.
- Neutral: append-block behavior for blockless partial files is a deliberate, reported action.

### Option B (`init --merge`)
- Good: one command.
- Bad: overloads `init`'s contract and its tests; a flag is less discoverable than a verb.

### Option C (`standards diff` only)
- Good: zero risk; purely advisory.
- Bad: doesn't actually adopt — the human does all the work; fails the "adopt onto existing"
  goal.

## More Information

- Related: RFC-0002 (the investigation this concludes), ADR-0009 (sync model), ADR-0010
  (managed-region sentinels), ADR-0012 (Slice 5 CI-green init).
- Implementation: `src/standards/init.py` (`run_adopt`, shared `_seed_scaffold_once`),
  `src/standards/managed.py` (`extract_block`, `has_begin_marker`), `src/standards/cli.py`
  (`adopt` subcommand). Tests: `tests/test_adopt.py`.
