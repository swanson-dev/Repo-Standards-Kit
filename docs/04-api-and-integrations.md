# API and Integrations

The kit's "public API" is the set of artifacts and conventions downstream repos depend on. This document enumerates that surface so downstream repos know what they are coupling to — and so kit maintainers know what a breaking change would actually break.

## Public surface

| Surface | Stability | Lives in |
|---|---|---|
| **Folder layout** under `docs/` (`STANDARDS.md`, `STANDARDS-CHECKLIST.md`, `00–10-*.md`, `decisions/`, `discovery/`, `rfcs/`, `templates/`) | Stable; changes follow SemVer | This kit's `docs/` tree |
| **`ai/` directory contract** (the four files, frontmatter, sections) | Stable; changes follow SemVer | `docs/STANDARDS.md` § "The `ai/` directory contract" |
| **Profile model** (`application` \| `library` \| `infra` \| `data`) | Stable | `docs/STANDARDS.md` § "Repo profiles" |
| **Profile matrix** (Required / Expected / Optional / N/A per profile per numbered doc) | Stable; cells may move per kit-version rules in [`versioning-policy.md`](./versioning-policy.md) | `docs/STANDARDS.md` § "Profile matrix" |
| **ADR format** (MADR 3.0) | Stable | `docs/templates/adr-template.md`, ADR [0002](./decisions/0002-adopt-madr-3.md) |
| **RFC format** (folder per RFC, required sections) | Stable | `docs/templates/rfc-template.md` |
| **Discovery conventions** (filename, optional frontmatter, `status` lifecycle) | Stable | `docs/STANDARDS.md` § "Discovery folder" |
| **Waiver syntax** (`**Waived:** <reason>` on unchecked checklist boxes) | **Load-bearing for CI**; treat as a hard contract | `docs/STANDARDS.md` § "Waiver mechanism" |
| **`AGENTS.md` reading order and end-of-session contract** | Stable | `AGENTS.md` (root) |

## Internal (not API)

These are not part of the public surface and may change without notice within a MAJOR version:

- Wording inside this kit's own numbered docs.
- The kit's own `ai/*.md` content.
- The exact list of bootstrap ADRs (0001–0006). Their content is durable, but the kit may add new ADRs at any time.

## Consumers

This kit's consumers are **downstream repositories** that adopt it. A repo adopts the kit by:

1. Pinning a kit version in its local `docs/STANDARDS.md`.
2. Copying `docs/templates/` into its own tree.
3. Filling in the profile and checklist.
4. Following the `AGENTS.md` reading order.

The kit does not impose runtime dependencies, build steps, or non-markdown tooling on consumers.

## Integration contract: standards check workflow

The kit ships `.github/workflows/repo-standards.yml` (Phase E). It expects a downstream repo to have:

- A `docs/STANDARDS.md` declaring a profile from the allowed set.
- A `docs/STANDARDS-CHECKLIST.md` where unchecked boxes carry `**Waived:** <reason>`.
- ADR filenames matching `NNNN-kebab-case-title.md`.
- RFC folders containing `rfc.md`.
- `ai/current-state.md` and `ai/handoff.md` with the required frontmatter fields.

Repos with non-default file paths must adjust the workflow accordingly (or capture the deviation in a local ADR).

## Versioning

See [`versioning-policy.md`](./versioning-policy.md). The kit follows SemVer. A consumer pins a specific kit version; upgrades are deliberate.

## Error model

The kit has no runtime errors. "Errors" surface as:

- **CI standards-check failures** in downstream repos when a contract is violated.
- **Doc drift** flagged during the per-repo "last reviewed" cycle.
- **Validation warnings** (`ai/*.md` past stale threshold).

Each surfaces in the workflow output with a pointer to the relevant `docs/STANDARDS.md` section.
