---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0006. Adopt the AGENTS.md pattern with thin tool-specific pointers

## Context and Problem Statement

Multiple AI coding tools (Claude Code, GitHub Copilot, Cursor, Aider, Codex, others) each look for their own per-tool instruction file at the repo root: `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules`, `AGENTS.md`, and so on. Maintaining the same content across three or four near-identical files invites drift — and when they drift, agents behave inconsistently inside the same repo.

## Decision Drivers

- Single source of truth for agent guidance.
- Each tool must still find the door it's looking for.
- Tool-specific notes (which Skills exist, which Hooks fire) must have a home without polluting the shared contract.
- The pattern needs to keep working as new AI tools enter the picture.

## Considered Options

- **Option A** — `AGENTS.md` at repo root as canonical, plus thin pointers in `CLAUDE.md`, `.github/copilot-instructions.md`, and any other tool-specific files.
- **Option B** — Maintain full content in each tool-specific file independently.
- **Option C** — Maintain only one tool-specific file (e.g., `CLAUDE.md`) and point everything else at it.
- **Option D** — No file; rely entirely on `docs/STANDARDS.md`.

## Decision Outcome

Chosen option: **Option A**, because it provides one source of truth (`AGENTS.md`) while letting every tool find its expected door (`CLAUDE.md`, `.github/copilot-instructions.md`, etc.), and lets tool-specific notes live in the tool-specific pointer files without bleeding into the shared contract.

### Consequences

- **Good:** Updating the agent contract is one edit (`AGENTS.md`).
- **Good:** Aligns with the emerging cross-tool `AGENTS.md` convention.
- **Good:** Each tool-specific pointer file stays small (~5–10 lines), so it can carry tool-specific notes without becoming a maintenance burden.
- **Bad:** A new tool ecosystem may use a non-`AGENTS.md` filename; a pointer file must be added.
- **Neutral:** `AGENTS.md` lives at the repo root, not under `docs/`, because agents scan the root by default.

## More Information

- `AGENTS.md` shape: see this kit's own `AGENTS.md` and `docs/STANDARDS.md` § "AGENTS.md pattern".
- Tool-specific pointers in this kit: `CLAUDE.md`, `.github/copilot-instructions.md`.
- Future Skills (Slice 2) may reference `AGENTS.md` § "End-of-session contract" as the spec they enforce.
