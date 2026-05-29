---
status: Accepted
date: 2026-05-29
deciders: swanson-dev
consulted: team
informed: team
---

# 0010. Managed-region sentinels for partially kit-owned files

## Context and Problem Statement

Some files in an adopting repository are partially owned — the kit provides a canonical core block (e.g., the agent contract in `AGENTS.md`, the pointer line in `CLAUDE.md`, the Copilot system-prompt pointer in `.github/copilot-instructions.md`), but the downstream repo is expected to add its own content around that core. These files cannot be treated as pure kit-owned (ADR-0009 class 1, full overwrite) nor as fully user-owned (class 2, never touched).

ADR-0009 named a third sync class — "partial / managed-region" — but deferred specifying the mechanism. This ADR fills that gap by defining the sentinel format, the update behavior, the drift-detection strategy, and the conflict-handling fallback for partially-owned files.

## Decision Drivers

- The kit must be able to keep its core content (agent contract, pointers) current across all adopters without clobbering downstream additions.
- Conflict handling must be non-destructive and consistent with the sidecar pattern already established in ADR-0009.
- The mechanism must be auditable: a downstream maintainer should be able to tell at a glance what the kit owns vs. what they own.
- Complexity must be minimal for v1; advanced cases (multi-block files) can be addressed in a future ADR.

## Considered Options

- **Option A** — HTML-comment sentinel markers delimiting one managed block per file (chosen).
- **Option B** — A separate companion file (e.g., `AGENTS.kit.md`) that the kit rewrites in full, with the downstream responsible for `include`-style references.
- **Option C** — Line-range annotations in `.standards-kit.json` that the update script uses to splice content by line number.

## Decision Outcome

Chosen option: **Option A — HTML-comment sentinel markers**, because it embeds ownership intent directly in the file (visible to any editor), reuses the existing sidecar conflict machinery from ADR-0009, and requires no structural change to how downstream maintainers consume these files.

### Sentinel format

Partially-owned files carry exactly ONE managed block delimited by:

```
<!-- BEGIN kit-managed: <id> (v<version>) -->
...kit-owned content...
<!-- END kit-managed: <id> -->
```

Defined block IDs for v1:

| File | Block ID |
|---|---|
| `AGENTS.md` | `agents-core` |
| `CLAUDE.md` | `claude-pointer` |
| `.github/copilot-instructions.md` | `copilot-pointer` |

### Update behavior

`standards update` rewrites ONLY the inner content of the managed block, preserving all content outside the sentinel markers — including the sentinel lines themselves — byte-for-byte. The `(v<version>)` tag in the opening sentinel is **informational**: it records the kit version that last *wrote* the block via `init` or a full-file migration, and is not rewritten by an inner-content splice, so it may lag the current version. The authoritative drift signal is the recorded hash (below), not the tag. (A pre-0.6.0 markerless file that was previously kit-tracked is migrated to this format by a full-file copy on the first `update`, which does bring the current sentinel version.)

### Drift detection

A sha256 hash of the inner block text (between the sentinel lines, exclusive) is recorded in `.standards-kit.json` under the `managed` table keyed by the file's repo-relative path (e.g. `"AGENTS.md"`). On each `update` run the script recomputes the hash of the on-disk inner content:

- Hash matches → downstream has not edited inside the block; safe to overwrite.
- Hash mismatch → downstream edited inside the block; degrade to sidecar (see below).

### Conflict handling

If any of the following conditions are true, `update` (and `init`) write a `<path>.kit-<version>` sidecar instead of modifying the original file — identical non-destructive behavior to ADR-0009's full-file conflict path:

1. The inner-block hash does not match the recorded value (downstream edited inside the block).
2. The opening or closing sentinel is missing or malformed.
3. There are multiple opening or closing sentinels (structural corruption).

The operator must resolve the sidecar manually.

### Consequences

- **Good:** The kit can keep the agent contract and pointer blocks current across all adopters without clobbering project-specific content that lives outside the markers.
- **Good:** Reuses the sentinel + sidecar machinery already designed in ADR-0009; no new conflict-handling concepts.
- **Good:** Ownership is self-documenting — any reader can see what the kit manages.
- **Bad:** Partially-owned files must be restructured so that kit-owned content is contiguous in one block. Files that interleave kit and project content cannot adopt this scheme without a one-time refactor.
- **Bad / accepted risk:** If a downstream maintainer deletes the sentinel markers, `update` has no managed block to target and degrades to a full-file sidecar. The operator must re-insert the markers to restore the managed-region workflow.
- **Neutral:** Multi-block support (more than one managed region per file) is deferred to a future ADR to keep v1 scope minimal.

## More Information

- Related ADR: [ADR-0009](./0009-distribute-the-kit-as-a-pypi-standards-cli-with-vendored-copy-sync.md)
- Design spec: [`../superpowers/specs/2026-05-29-standards-update-and-managed-regions-design.md`](../superpowers/specs/2026-05-29-standards-update-and-managed-regions-design.md)
