# Team Repository Standards Kit

A versioned, opinionated set of documentation standards and templates that any repository on the team can adopt. The kit's goal is to keep documentation lean, durable, and useful for both humans and AI-assisted development workflows.

- **Distributed as:** the [`repo-standards-kit`](https://pypi.org/project/repo-standards-kit/) package on PyPI — a zero-dependency `standards` CLI.
- **Authoritative spec:** [`docs/STANDARDS.md`](./docs/STANDARDS.md)
- **Agent contract:** [`AGENTS.md`](./AGENTS.md)
- **Version history:** [`CHANGELOG.md`](./CHANGELOG.md)

## Installation

The kit installs as a command-line tool. Use whichever installer you prefer:

```sh
pipx install repo-standards-kit     # recommended (isolated install)
# or
uvx repo-standards-kit standards --version   # run without installing
# or
pip install repo-standards-kit
```

This puts a `standards` command on your PATH. Verify it:

```sh
standards --version
```

The runtime is **stdlib-only** (Python 3.9+) — no third-party dependencies.

## Quickstart

```sh
# Adopt the kit into a NEW or empty repo (greenfield):
standards init --profile library .

# Adopt into an EXISTING repo (non-destructive — keeps your files,
# writes <file>.kit-<version> sidecars on conflict):
standards adopt --profile application .

# Verify a repo against the standards (use in CI):
standards check .

# Pull in a newer kit version later (non-destructive reconcile):
standards update .
```

Pick the profile that fits the repo: `application` | `library` | `infra` | `data`. Each profile has its own Required / Expected / Optional / N/A doc matrix — see [`docs/STANDARDS.md`](./docs/STANDARDS.md).

- **`init`** is for blank/clean repos; it refuses if kit-owned files already exist with different content (it points you at `adopt`).
- **`adopt`** is for repos that already have their own README, docs, or CI; it never clobbers — it keeps your files, sidecars true conflicts, and appends/splices the kit's managed block into an existing `AGENTS.md`.
- Both write a `.standards-kit.json` marker so `standards update` can keep you current.

## What this kit gives you

1. A **standard folder layout** that scales across repo types.
2. Four **repo profiles** (application, library, infra, data) with explicit Required / Expected / Optional / N/A doc requirements.
3. A defined contract for the **`ai/` directory** — four files that carry session-to-session context.
4. **MADR 3.0 ADRs** with a defined lifecycle.
5. **RFCs** for time-boxed technical investigations (separate from raw discovery intake).
6. Lightweight conventions for **`docs/discovery/`** — meeting notes, requirement drafts, use cases — with a traceability flow to durable docs.
7. A **PR template** that asks the right questions about documentation, ADRs, AI context, and operational impact.
8. A **`STANDARDS-CHECKLIST.md`** with a waiver mechanism so absences are explicit, not silent.
9. A **CI check** (`standards check`) that enforces the structural minimum plus content-level lints.
10. **AI Skills + hooks** (Claude Code + Copilot) for ADRs, RFCs, discovery promotion, handoffs, and running the check.

## The information flow

```
docs/discovery/    →    docs/rfcs/        →    docs/decisions/    →    docs/0X-*.md
(raw intake)            (investigated)          (decided)               (synthesized & durable)
meetings, reqs,         time-boxed,             MADR 3.0 ADRs,          PRD, architecture,
use case drafts         spawn-or-abandon        immutable               runbook, etc.
```

## Adopting without the CLI

If you'd rather adopt by hand (or want the full detail of what the CLI does), the manual process is documented in [`docs/STANDARDS.md`](./docs/STANDARDS.md): copy `docs/templates/`, pick a profile, fill in `docs/STANDARDS.md` + `docs/STANDARDS-CHECKLIST.md`, seed `ai/*.md` from `docs/templates/ai-starters/`, adopt the `.github/` workflow + PR template, and point your AI tools at `AGENTS.md`.

## Documentation philosophy

Keep documentation lean but scalable. Add durable docs when they improve onboarding, implementation, review, operations, traceability, or decision quality. Do not create documents only because a structure exists — that's why the kit uses **Required / Expected / Optional** rather than a single rigid required-doc list.

## Roadmap

| Slice | Scope | Status |
|---|---|---|
| 1 | Templates + standards content | Shipped |
| 2 | AI Skills + Hooks (Claude Code, Copilot) | Shipped |
| 3 | Distribution — the `standards` CLI (`init` / `update`), PyPI, 3-class sync | Shipped |
| 4 | Deeper CI enforcement (content/link/placeholder lint, parity + coherence guards) | Shipped |
| 5 | Hardening — `standards check` subcommand + multi-profile CI-green `init` | Shipped |
| 6 | `standards adopt` — non-destructive adoption onto existing repos | Shipped |

The design rationale is captured as ADRs under [`docs/decisions/`](./docs/decisions/) and investigations under [`docs/rfcs/`](./docs/rfcs/).
