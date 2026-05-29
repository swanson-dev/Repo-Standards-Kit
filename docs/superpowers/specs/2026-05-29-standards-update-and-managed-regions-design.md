# Plan 2 Design — `standards update` + Partial/Managed-Region Ownership

**Status:** Approved (brainstorming, 2026-05-29)
**Upstream:** RFC-0001 (distribution mechanism) and ADR-0009 (PyPI standards-CLI + three-class vendored sync). This spec elaborates the *implementation specifics* of the two pieces deferred from Plan 1; it does not change the decided model.
**Builds on:** Plan 1 (`docs/superpowers/plans/2026-05-29-distribution-build-1-packaging-and-init.md`), now on `main`.

## Goal

Realize the upgrade half of the distribution mechanism: a `standards update` command that reconciles a vendored kit against a newer version, and the **partial/managed-region** ownership class (the third class from ADR-0009) so the kit can own a canonical block inside files the downstream also edits (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`). Also closes the deferred first-init data-loss gap (Copilot, PR #2) by reusing `update`'s conflict mechanism.

One plan, **two phases**.

## Decisions (from brainstorming)

1. **AGENTS.md managed boundary:** the managed block holds the generic agent contract; repo-specifics move to a downstream-owned `## About this repository` section. This restructures the kit's own `AGENTS.md`.
2. **Scope:** one plan, two phases (Phase A = partial class + restructure; Phase B = `update` + first-init guard).
3. **`update` interaction model:** apply changes then report, plus a `--dry-run` flag that previews the same report read-only. Non-interactive (no y/N prompt) — consistent with the kit's scriptable-hooks stance.

## Phase A — Partial / managed-region ownership class

### A1. `src/standards/managed.py` (new — single responsibility: sentinel handling)

Sentinel format (HTML comments, **one block per file** for v1):
```
<!-- BEGIN kit-managed: <id> (v<version>) -->
…kit-owned canonical content…
<!-- END kit-managed: <id> -->
```
Block IDs: `agents-core`, `claude-pointer`, `copilot-pointer`. The `(v<version>)` in the BEGIN marker is informational; the marker file's `managed` hash is the source of truth for drift.

Functions:
- `find_block(text) -> tuple[int, int, str] | None` — locate the single managed block; return `(inner_start, inner_end, inner_text)` or `None` if markers absent/corrupt (exactly one BEGIN and one matching END required).
- `splice_block(text, new_inner) -> str` — replace only the inner content between the markers, preserving everything outside byte-for-byte. Raises if no block found.
- `block_hash(text) -> str | None` — sha256 of the inner block bytes (the drift anchor); `None` if no block.

Edge cases: missing/duplicate/unterminated markers → `find_block` returns `None` (caller treats as "can't splice" → sidecar). The marker `<id>` is matched literally so a stray comment doesn't collide.

### A2. `manifest.py` — add the partial class

- `PARTIAL_FILES: frozenset[str] = frozenset({"AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"})`.
- `classify(rel)` returns `"partial"` for those, `"scaffold-once-source"` for scaffold sources, else `"kit-tracked"`.
- Partial files leave the kit-tracked verbatim-copy/overwrite path.

### A3. Restructure the kit's own three files (also the payload)

- **`AGENTS.md`** — wrap the generic contract in the `agents-core` block: intro line, `Kit version`, canonical reading order, end-of-session contract, how-to-author, and the *standard* conventions (ISO dates, kebab-case slugs, don't-edit-Accepted-ADRs, the Required/Expected waiver rule). Below the block, a downstream-owned `## About this repository` section: what-this-repo-is, **Profile**, kit-specific conventions ("this kit follows itself"), and the "out of scope / queued slices" notes.
- **`CLAUDE.md`** / **`.github/copilot-instructions.md`** — wrap the one-line pointer to `AGENTS.md` in the `claude-pointer` / `copilot-pointer` block; leave the `## X-specific notes` section downstream-owned.
- The kit's restructured files must still pass `standards-check` 0/0 (they are this repo's real agent files).

### A4. `init.py` — handle partial files

For partial-class payload files: copy verbatim (the payload already carries the sentinels) and record `block_hash` of the managed block in `marker["managed"][rel]`. (The splice path is only exercised by `update`.)

## Phase B — `standards update` + first-init guard

### B1. `src/standards/update.py` (new — the reconciliation engine)

`run_update(target, *, dry_run=False) -> UpdateReport`. Reads the target's marker; resolves `payload_root()`; for each enumerated payload file, dispatches on `classify(rel)`:

- **kit-tracked:** compute current downstream hash; if it equals `marker["tracked"][rel]` → overwrite with payload content + refresh recorded hash (`updated`); if it differs → write `<rel>.kit-<new_version>` sidecar, leave the file, flag `conflict`. New payload file not in target → add it (`added`). A `tracked` entry whose payload file no longer exists → `removed` (report only, never auto-delete).
- **scaffold-once:** never touched.
- **partial:** compute `block_hash(current_file)`; if it equals `marker["managed"][rel]` → `splice_block` the payload's managed-block content into the current file + refresh recorded hash (`spliced`); if it differs → full-file `<rel>.kit-<ver>` sidecar + `conflict`; if `find_block` returns `None` (markers gone) → skip + sidecar + `conflict`.

Cross-cutting:
- **Leap-safe:** all comparisons are content/hash based, never version-delta replay — skipping versions is fine.
- **Breaking-change surfacing:** if the target's `kit_version` < the payload version and the CHANGELOG marks intervening entries, print the relevant CHANGELOG section(s) so the human sees what may break.
- On a real (non-dry-run) apply, rewrite the marker with refreshed `kit_version`, `tracked`, and `managed`.
- `dry_run=True` performs every comparison and builds the same report but writes nothing (no file copy, no sidecar, no marker rewrite).

### B2. First-init guard (`init.py`)

`run_init` gains a pre-flight: collect kit-tracked **and** partial destinations that already exist with content differing from the payload (for partial files, compare the managed-block hash). If any exist and `force` is False → raise `FileExistsError` listing them (cap the list, give the count) and copy nothing. Greenfield init is unaffected; scaffold-once is already copy-if-absent. The hash-compare helper is shared with `update.py` (one conflict-detection path).

### B3. `cli.py` — `update` subcommand

`standards update [target] [--dry-run]`. Prints a report: `updated / unchanged / spliced / conflicts (sidecars written) / added / removed`, plus a reminder to run `standards-check` afterward. Exit 0 on success; non-zero only on hard errors (e.g., no marker found → "not a kit-adopted repo; run `init` first").

### B4. ADR-0010

Dogfood `new-adr` to record the **managed-region sentinel convention** (the durable decision: HTML-comment sentinels, one block per file, hash-in-marker drift detection, sidecar-on-conflict). Companion to ADR-0009.

## Components & files

| File | Phase | Responsibility |
|---|---|---|
| `src/standards/managed.py` (new) | A | Sentinel find/splice/hash. |
| `src/standards/manifest.py` (modify) | A | `PARTIAL_FILES`; `classify` → `"partial"`. |
| `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` (modify) | A | Insert sentinels; restructure AGENTS.md (contract in block, repo-specifics in `## About this repository`). |
| `src/standards/init.py` (modify) | A, B | Record `managed` hashes for partial files (A); first-init guard (B). |
| `src/standards/update.py` (new) | B | Reconciliation engine. |
| `src/standards/cli.py` (modify) | B | `update` subcommand + `--dry-run`. |
| `docs/decisions/0010-*.md` (new) | B | ADR-0010 sentinel convention. |
| `tests/test_managed.py`, `tests/test_update.py`, `tests/test_init.py` (+cases), `tests/test_cli.py` (+cases), `tests/test_manifest.py` (+cases) | A, B | Coverage. |
| `CHANGELOG.md` (modify) | B | `## [0.6.0]`. |

## Testing strategy

- `managed.py`: splice preserves outside-block bytes; `block_hash` stable; missing/duplicate/unterminated markers → `None`.
- `update.py` per class: kit-tracked unchanged→overwrite, differs→sidecar, added, removed; partial unchanged→splice, differs→sidecar, markers-gone→sidecar; scaffold-once untouched; leap across ≥2 versions; `--dry-run` writes nothing.
- `init` guard: differing kit-tracked/partial collision without `--force` raises and copies nothing; `--force` proceeds; greenfield unaffected.
- Integration: `init` then mutate the marker to an older `kit_version`, then `update` → reconciles cleanly; the kit's own restructured files pass `standards-check` 0/0.

## Out of scope (later)

- Multi-block managed regions (v1 = one block per file).
- `standards set-profile` (profile change after adoption).
- Slice 4 CI lint of marker/sentinel integrity.
- PyPI release workflow + CI test wiring + version tagging (Plan 3).

## Version

Ships as **0.6.0** (new feature: `update` + partial class).
