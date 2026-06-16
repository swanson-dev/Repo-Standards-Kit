---
status: Accepted
date: 2026-06-16
deciders: swanson-dev, codex
consulted: docs/rfcs/0004-should-the-kit-add-post-v1-adoption-assistant-commands-and-optional-knowledge-lanes/rfc.md
informed: downstream repo adopters
---

# 0019. Add post-v1 adoption assistant commands and optional knowledge lanes

## Context and Problem Statement

The v1.0.0 kit release established a stable SemVer baseline and generated downstream readiness gate. The remaining product confidence gap is how well teams operate the kit in real repos after initial adoption: diagnosing drift, finding the right command, adding AI skill surfaces, and capturing useful knowledge without turning every repo into a heavy documentation warehouse.

The question is which public CLI and template surface should ship first after v1.0.0.

## Decision Drivers

- Keep the default adopted repo lean.
- Make the next action obvious for adopters when something is missing, stale, or conflicted.
- Reuse existing stdlib scripts and the packaged payload model.
- Keep recommendations advisory, read-only, deterministic, and offline by default.
- Avoid normalizing raw binary artifact storage in git.

## Considered Options

- **Option A** - Ship only `standards new-skill`.
- **Option B** - Ship only `standards doctor`.
- **Option C** - Ship `doctor`, `new-skill`, command discovery, and optional knowledge-lane templates together.

## Decision Outcome

Chosen option: **Option C**, because the commands reinforce each other: `doctor` identifies adopter health and useful optional lanes, `new-skill` exposes an existing authoring workflow through the public CLI, and command discovery makes the expanded surface easier to use.

### Consequences

- **Good:** Adopters get a read-only health check, clearer command discovery, and a packaged path for skill scaffolding.
- **Good:** Optional discovery, design, and support lanes become available without becoming universal requirements.
- **Bad:** The public CLI surface is larger and needs command-level tests and documentation.
- **Neutral:** `doctor --recommend` suggests lanes from repo state; agent/session guidance can suggest lanes from work context, but neither creates files automatically.

## More Information

- Related ADRs: ADR-0009, ADR-0010, ADR-0012, ADR-0017, ADR-0018
- Related RFC: `docs/rfcs/0004-should-the-kit-add-post-v1-adoption-assistant-commands-and-optional-knowledge-lanes/`
- Open questions spawned: none
