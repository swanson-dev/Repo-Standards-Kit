---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0002. Adopt MADR 3.0 as the ADR format

## Context and Problem Statement

ADR [0001](./0001-record-architecture-decisions.md) commits the kit to recording decisions in `docs/decisions/` but doesn't fix the format. Several mature formats exist (MADR 3.0, Michael Nygard's classic, ADR-tools/npryce style). The choice affects how much structure each ADR carries, how easily AI agents can author them, and how quickly humans can scan a directory of them.

## Decision Drivers

- Explicit "considered alternatives" section (the most valuable historical record).
- Clear status lifecycle and immutability rules.
- Friendly to AI authoring (well-known by LLMs, regular structure).
- Modest ceremony — readable in 2 minutes, writeable in 20.

## Considered Options

- **Option A** — MADR 3.0 (Markdown ADR).
- **Option B** — Michael Nygard's classic four-section format.
- **Option C** — Custom lean MADR (drop optional sections).
- **Option D** — ADR-tools (npryce) CLI-driven format.

## Decision Outcome

Chosen option: **MADR 3.0**, because it is the best balance of structure and brevity, has explicit slots for decision drivers, considered options, and consequences, is widely recognized by AI tooling, and doesn't require any CLI to author.

### Consequences

- **Good:** Every ADR forces an explicit "Considered Options" section — the most useful historical record.
- **Good:** Format is regular enough that the standards CI workflow can lint filename and status automatically.
- **Bad:** Slightly heavier than Nygard's classic; the optional "Pros and Cons of the Options" can balloon if not curated.
- **Neutral:** Adopting MADR 3.0 means accepting its status vocabulary (`Proposed`, `Accepted`, `Deprecated`, `Superseded by NNNN`).

## Pros and Cons of the Options

### Option A — MADR 3.0
- Good: explicit drivers + options + consequences; standardized status lifecycle.
- Bad: a touch verbose for trivial decisions.

### Option B — Nygard classic
- Good: minimal ceremony (Title, Status, Context, Decision, Consequences).
- Bad: no explicit "considered alternatives" section — the most-cited weakness of the format.

### Option C — Custom lean MADR
- Good: tailored to team tolerance.
- Bad: bespoke; new contributors have to learn it; AI agents need extra context.

### Option D — ADR-tools (npryce)
- Good: tooling-driven; CLI handles numbering and supersession.
- Bad: introduces a tooling dependency that conflicts with the kit's "AI Skill drives ADR creation" trajectory (Slice 2).

## More Information

- Template: `docs/templates/adr-template.md`.
- Status lifecycle and immutability rules: `docs/STANDARDS.md` § "ADRs — MADR 3.0".
- MADR 3.0 reference: https://adr.github.io/madr/
