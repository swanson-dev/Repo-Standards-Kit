---
status: Accepted
date: 2026-05-29
deciders: swanson-dev
consulted: team
informed: team
---

# 0009. Distribute the kit as a PyPI standards CLI with vendored-copy sync

## Context and Problem Statement

Downstream repos need to both (a) initially adopt the kit and (b) stay current as it evolves. Three constraints shaped the choice: the deliverable was RFC-only; adoption and upgrade were weighted equally; tool-neutrality is a hard constraint — the engine must not require any single AI assistant, consistent with ADR-0007's wrappers-over-stdlib-scripts ethos. The team is all-Python.

The question: what mechanism lets a downstream repo adopt the kit in one command and upgrade it on demand, without imposing a non-Python toolchain or tying adoption to any particular AI assistant?

## Decision Drivers

- **Tool-neutrality.** The distribution engine must work from any terminal without a specific AI assistant installed.
- **Adoption and upgrade parity.** The same mechanism must serve both first-time init and subsequent updates.
- **Team stack alignment.** The team is all-Python; a Python-native solution minimizes onboarding friction.
- **Zero runtime dependencies.** The kit should ship without forcing downstream repos to manage a dependency graph.
- **Reproducibility.** Downstream repos must be able to pin to a specific kit version.

## Considered Options

- **Option A** — GitHub template repo (alone)
- **Option B** — Claude Code plugin
- **Option C** — npm/npx
- **Option D** — gh CLI convenience wrapper
- **Option E** — pipx/uvx via PyPI (chosen)

## Decision Outcome

Chosen option: **Option E — pipx/uvx via PyPI**, because it satisfies all decision drivers simultaneously: it is tool-neutral, covers both adoption and upgrade in a single `standards` CLI, stays in the team's Python ecosystem, and ships as a zero-dependency wheel.

The kit is distributed as a single zero-dependency Python package on PyPI named `repo-standards-kit`, run ephemerally via `pipx run` or `uvx`. It exposes a `standards` console CLI with two subcommands: `init` (adopt) and `update` (stay current). Kit content ships as package data inside the wheel; the PyPI package version IS the kit version.

Upgrades reconcile via a three-class ownership model:
- **kit-tracked** — kit owns the file; `update` overwrites it, hash-guarded.
- **scaffold-once** — downstream owns the file after init; `update` never touches it.
- **partial/managed-region** — shared; kit splices only its sentinel-delimited block.

A `.standards-kit.json` marker at the target repo root stores the kit version, profile, adoption date, and per-file sha256 hashes. Conflicts are handled non-destructively via `<path>.kit-<version>` sidecars. `git clone` remains the no-packaging fallback.

### Consequences

- **Good:** Single tool-neutral mechanism covers both adoption and upgrade; reproducible via version pinning; stays in the team's Python ecosystem; zero runtime dependencies.
- **Bad:** Requires `pipx` or `uv` installed once per machine; requires restructuring the kit into a packaged layout.
- **Neutral:** The marker file format is JSON (`.standards-kit.json`), not TOML — see correction note below. `standards update` and the partial/managed-region class are deferred to Plan 2; Plan 1 ships packaging and `init` with kit-tracked and scaffold-once only.

## More Information

- Durable decision recorded from: [`../rfcs/0001-what-is-the-kit-s-distribution-and-upgrade-mechanism/rfc.md`](../rfcs/0001-what-is-the-kit-s-distribution-and-upgrade-mechanism/rfc.md)
- Related ADRs: [0007](./0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md) — wrappers-over-stdlib-scripts ethos that informed the tool-neutrality constraint.
- **Important correction to RFC-0001:** The marker file is `.standards-kit.json`, not `.standards-kit.toml` as named in the RFC. Python's stdlib has `tomllib` (read-only, 3.11+) but no TOML writer, so TOML would force either a third-party dependency or a hand-rolled serializer. JSON has full stdlib read+write (`json` module) and preserves the zero-dependency stance.
- **Scope note:** `standards update` and the partial/managed-region ownership class are deferred to Plan 2. Plan 1 ships packaging and `standards init` with kit-tracked and scaffold-once only.
