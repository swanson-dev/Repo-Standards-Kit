# Architecture

The kit's architecture is conceptual — there is no runtime, no service, no deployment. What this document captures is **how the artifact types relate** and **how information flows** between them.

## Context diagram

```mermaid
flowchart LR
  Stakeholders[Stakeholders] -->|notes, requirements, use cases| Discovery
  Discovery[docs/discovery/<br/>early context notes]
  RFCs[docs/rfcs/<br/>investigations]
  Decisions[docs/decisions/<br/>ADRs - MADR 3.0]
  Numbered[docs/00–10/<br/>synthesized & durable]
  AI[ai/<br/>rolling context]
  Agents[AI Agents<br/>human + machine]

  Discovery -->|synthesize| RFCs
  Discovery -->|synthesize| Numbered
  RFCs -->|spawn| Decisions
  Decisions -->|inform| Numbered
  Numbered <-->|read & update| AI
  Agents -->|read AGENTS.md| AI
  Agents -->|read & update| Numbered
```

## Components

### `docs/discovery/`

**Responsibility:** Lightweight stakeholder, research, and reconnaissance notes that may later inform RFCs, ADRs, or numbered docs. Discovery notes are tracked markdown files directly under `docs/discovery/`; there is no capture/promote lifecycle.

**Depends on:** nothing structural. Stakeholders write in their own language; the team preserves it.

### `docs/rfcs/`

**Responsibility:** Time-boxed technical investigations with a question and a recommendation. Folder-per-RFC so artifacts can live alongside prose.

**Depends on:** the question being investigated, often drawn from `discovery/` or from open questions in `ai/open-questions.md`.

### `docs/decisions/`

**Responsibility:** Immutable records of material technical decisions in MADR 3.0 format.

**Depends on:** an RFC concluded with a recommendation, or a decision made in-line that's substantive enough to capture.

### `docs/00–10/<numbered>.md`

**Responsibility:** The synthesized, durable "answer" layer. Required-doc set varies by profile.

**Depends on:** earlier ADRs, RFCs, and discovery items as inputs. These are where the team's mental model lives in its most consumable form.

### `ai/`

**Responsibility:** Rolling session-to-session context: current state, next actions, open questions, and the most recent handoff.

**Depends on:** the numbered docs (as the durable backdrop) plus whatever the last session changed.

### `AGENTS.md` (root)

**Responsibility:** Single source of truth for the agent contract — canonical reading order and end-of-session contract. Tool-specific pointers (`CLAUDE.md`, `.github/copilot-instructions.md`) reference it.

## Data flow

For a typical change cycle in a downstream repo:

```mermaid
sequenceDiagram
  participant SH as Stakeholder
  participant Disc as docs/discovery/
  participant RFC as docs/rfcs/
  participant ADR as docs/decisions/
  participant Doc as docs/0X-*.md
  participant AI as ai/

  SH->>Disc: write tracked markdown discovery note
  Disc->>Doc: inform structured docs with source context
  Doc-->>Disc: link back to discovery note when useful
  Doc->>RFC: open RFC for technical question
  RFC->>ADR: spawn ADR with decision
  ADR-->>Doc: update numbered docs to reflect decision
  Doc-->>AI: update current-state.md, handoff.md
```

## Trust boundaries

- **Stakeholder content** (in `discovery/`) is preserved as context, not trusted as-is. Synthesis into numbered docs is the act of reconciliation with engineering reality.
- **ADRs once `Accepted` are inviolable.** Reversal is a new ADR, never an edit.

## Constraints

- Markdown only **in version control**. Discovery notes are tracked markdown; large binary source files should stay outside the repo and be linked from notes when needed.
- ISO 8601 dates everywhere.
- The kit ships **content**, not tooling. Tooling is queued for Slices 2 and 4.

## Trade-offs

- **Markdown only** (vs. structured-doc formats) — accepts that some queries against the corpus are harder; gains universal toolability. See ADR [0002](./decisions/0002-adopt-madr-3.md).
- **`ai/` committed** (vs. gitignored) — accepts PR diff noise; gains shared institutional memory. See ADR [0004](./decisions/0004-define-ai-directory-contract.md).
- **Separate `discovery/` and `rfcs/`** (vs. a single folder) — accepts an extra top-level folder; gains clean separation of *received* vs. *produced* material. See ADR [0005](./decisions/0005-split-discovery-and-rfcs.md).
- **`AGENTS.md` + thin pointers** (vs. full per-tool files) — accepts that each new AI tool needs a pointer file; gains a single source of truth. See ADR [0006](./decisions/0006-adopt-agents-md-pattern.md).
