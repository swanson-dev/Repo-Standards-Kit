---
status: Concluded
opened: 2026-05-29
closed: 2026-05-29
owner: swanson-dev
time_box: 1 session (brainstorming)
---

# 0001. What is the kit's distribution and upgrade mechanism?

## Question

How should downstream repositories both initially adopt the Repo-Standards-Kit and stay current as it evolves?

## Why now

Resolving this unblocks **Slice 3** in full and is recorded as **Q-2** in [`ai/open-questions.md`](../../../ai/open-questions.md). It also gates the deferred **`scaffold-new-repo`** capability (Q-1's resolution explicitly parked it "on Slice 3 distribution") and decides whether `docs/templates/` stays colocated or splits into a separate distributable. Until the mechanism is chosen, no adoption or upgrade path can be built and the kit cannot leave its own repo.

**Scope of this RFC:** decision + rationale only. It selects the mechanism and the upgrade model; it does **not** build them. Implementation (packaging restructure, the `standards` CLI, the sync engine) is a later slice.

## Approach

Worked the decision as a structured brainstorming session rather than a benchmark — the question is a design choice among known options, not an empirical unknown. Three constraints were elicited and then used to filter the candidate mechanisms from Q-2:

1. **Deliverable scope** — RFC only (this document); no distribution code in Slice 3.
2. **Adoption vs. upgrade weighting** — *both matter equally*. A mechanism that nails one-shot adoption but has a weak upgrade story (the original Q-2 concern) does not clear the bar.
3. **Tool-neutrality (hard constraint)** — the engine must not require any single **AI assistant**, consistent with [ADR-0007](../../decisions/0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md) (wrappers over stdlib scripts). This rules out a Claude Code plugin *as the mechanism*; assistant wrappers may only be optional sugar over a neutral core. (Language runtimes and general dev tools like `git`/`gh` are *not* AI assistants and do not violate this constraint.)

Candidate channels considered: GitHub template repo, Claude Code plugin, `degit`/copy script, `gh` CLI, `npm`/`npx`, `pipx`/`uvx` (PyPI). Each was evaluated against the three constraints and against the kit's existing reality: a **pure Python stdlib** codebase with zero runtime dependencies.

## Findings

### Channel evaluation

| Channel | Verdict | Reason |
|---|---|---|
| GitHub template repo (alone) | Rejected as *the* answer | One-click adoption, but the upgrade story is "read CHANGELOG, hand-copy" — fails the equal-weight bar. Kept as the rejected baseline. |
| Claude Code plugin | Rejected | Ties distribution to one AI assistant — fails the tool-neutral constraint. |
| `npm` / `npx` | Rejected (revisit later) | Best bootstrap ubiquity, but the kit's engine is Python stdlib. npm forces either a JS rewrite (abandons the stdlib engine and form-factor parity with `update-handoff`/`promote-discovery`) or a Node-shells-to-Python wrapper (requires two runtimes). Cost outweighs gain for a Python-only team. |
| `gh` CLI (`repo create --template`, `release download`) | Optional convenience | Useful for greenfield (`gh repo create --template`) and pinned fetch (`gh release download <tag>`, leveraging the pushed `v0.x.0` tags), but `--template` only serves *new* repos, not adoption into *existing* ones, and requires `gh` installed + authed. Documented fallback, not the engine. |
| **`pipx` / `uvx` via PyPI** | **Selected** | The `npx` *model* (zero-install, single command, runs latest, pinnable) realized in the kit's own ecosystem. One runtime, no language split, no extra dependency for the Python/Go/data repos the kit targets. The whole team is Python. |

### Selected mechanism: a single tool-neutral `standards` CLI on PyPI

One stdlib Python package (working name `repo-standards-kit`, console entry point `standards`), distributed on PyPI and run ephemerally:

```
pipx run repo-standards-kit init --profile library .              # adopt into a repo (greenfield or existing)
pipx run repo-standards-kit==0.5.0 init --profile library .       # pinned, reproducible
pipx run repo-standards-kit update .                              # stay current (Plan 2)
uvx repo-standards-kit init --profile library .                   # identical UX via uv — same package, zero extra work
```

Two subcommands cover both jobs Q-2 weighted equally:

- `init --profile <application|library|infra|data> [target]` — copy kit content into the target, record the profile, write a version marker. (`--profile` is required.)
- `update [target]` — reconcile the target against a newer kit version (see sync model).

**Key payoff:** the kit ships its content (STANDARDS.md reference, the 22 templates, the scripts, the standards-check workflow) as **package data inside the wheel**, and the **PyPI package version *is* the kit version.** That collapses the version anchor and the distributable into one object — no separate template repo, no release-tarball fetch inside the CLI, full reproducibility via `==<version>`. The package stays **zero-dependency / pure stdlib**; pipx/uvx is only the delivery vehicle.

**Bootstrap cost (accepted):** `pipx`/`uv` is not always preinstalled, so there is a one-time, machine-level install before first use — smaller and rarer than a per-repo clone. `git clone` remains the no-packaging fallback.

### Sync model: three ownership classes

Because the package delivers a *vendored copy*, `update` must classify every file. A manifest bundled in the package assigns each path exactly one class:

| Class | Who owns it | Examples | `update` behavior |
|---|---|---|---|
| **kit-tracked** | kit | `docs/templates/*`, `scripts/*`, `_doc_lib/helpers.py`, `standards-check`, standards-check workflow, the authoritative `docs/STANDARDS.md` reference | overwrite, **hash-guarded** |
| **scaffold-once** | downstream | `ai/*` starters, the per-repo `STANDARDS.md` (profile + waivers), `STANDARDS-CHECKLIST.md`, filled `docs/NN-*.md`, downstream ADRs/RFCs | **never touched** after `init` |
| **partial / managed-region** | shared | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | splice the kit-owned block only, **hash-guarded** |

Classifying principle: *if a downstream is expected to edit it, it is scaffold-once; if the kit owns a canonical block within a file the downstream also edits, it is partial; everything else is kit-tracked.*

**Version marker** — `init` writes a stdlib-readable `.standards-kit.toml` at the repo root:

```toml
kit_version = "0.4.0"      # = the PyPI package version last synced
profile     = "library"
adopted     = "2026-05-29"
[tracked]                   # sha256 of each kit-tracked file as last written by the kit
"docs/templates/adr-template.md" = "9f2c…"
[managed]                   # sha256 of each managed-region block as last written
"AGENTS.md" = "a1b8…"
```

**Hash guard + conflict handling (all classes, agreed):**
- Unchanged downstream (hash matches) → overwrite (kit-tracked) or splice block (partial); update recorded hash.
- Edited downstream (hash differs) → **never clobber.** Write the new version beside it as `<path>.kit-<version>` and report a conflict for manual reconciliation. Non-interactive sidecar — scriptable and CI-friendly (no blocking prompt, no abort).
- New upstream file → add it. Removed upstream file → report only, never auto-delete (conservative).

**Managed-region mechanism (partial class)** — HTML-comment sentinels delimit the kit's canonical block; `update` rewrites only what's between them:

```markdown
<!-- BEGIN kit-managed: agents-core (v0.4.0) -->
…canonical agent contract — kit owns this…
<!-- END kit-managed: agents-core -->

## Project-specific
…downstream owns everything outside the markers — never touched…
```

If markers are missing/corrupted, `update` skips the splice, reports, and writes a full sidecar. **v1 constraint: one managed block per file** (multi-block noted as a future extension).

**Properties:** all three classes are stdlib-implementable (`hashlib`, `pathlib`, `re`, `tomllib`/`json`); `update` is **advisory and non-destructive on conflict** — the same instinct as [ADR-0008](../../decisions/0008-hooks-invoke-script-in-check-mode-behavior-writes-via-slash-command.md)'s check-mode hooks. Content comparison (not version-delta replay) makes `update` **leap-safe** across skipped versions, and `update` prints the relevant CHANGELOG section so pre-1.0 breaking changes (allowed by [`versioning-policy.md`](../../versioning-policy.md)) are surfaced before they bite.

### Deliberately out of scope

- Profile change after adoption (a future `standards set-profile`).
- Multi-block managed regions.
- `gh`-extension packaging (`gh standards …`).
- npm/npx (revisit only if a non-Python audience emerges).
- Slice 4 CI lint of marker integrity.

## Recommendation

**Distribute the kit as a single zero-dependency Python package on PyPI**, run ephemerally via `pipx run` / `uvx`, exposing a `standards` CLI with `init` (adopt) and `update` (stay current). The PyPI package version is the kit version; kit content ships as package data. **Reconcile upgrades with a three-class ownership model** (kit-tracked / scaffold-once / partial managed-region), a `.standards-kit.toml` version-and-hash marker, and **non-destructive sidecar conflict handling**. Keep `git clone` as the no-packaging fallback; record `gh`, npm/npx, template-repo, and Claude-plugin channels as considered-and-deferred. This satisfies all three constraints: it is RFC-decidable now, weights adoption and upgrade equally, and keeps the engine AI-assistant-neutral while staying in the team's Python ecosystem.

## Follow-ups

- **ADR to write:** yes — record the durable decision ("We distribute via a PyPI `standards` CLI with a three-class vendored-sync model") as the next ADR (`docs/decisions/0009-…md`) when Slice 3 implementation begins. This RFC is the working record of *how* the decision was reached; the ADR is the lasting *what*.
- **Implementation plan changes:** Slice 3 build work — packaging restructure (`scripts/` → packaged layout with entry point + package-data bundling), the `standards init`/`update` CLI, the ownership manifest, the `.standards-kit.toml` marker, and the PyPI Trusted-Publishing (OIDC) release workflow on tag-push. `scaffold-new-repo` (Q-1 deferral) is subsumed by `standards init`.
- **New open questions:** none — Q-2 is answered by this RFC and should be marked `answered` with a pointer here.
- **Discovery to promote:** none.
