---
status: Concluded
opened: 2026-06-16
closed: 2026-06-16
owner: codex
time_box: same-day implementation
---

# 0005. Should the kit add advisory AI continuity hooks and standard slash commands?

## Question

Should the kit add optional AI continuity hooks and standard slash-command surfaces for session context, compact snapshots, and handoff refreshes?

## Why now

The v1.1.0 adoption-assistant slice improves downstream repo diagnostics, but long AI sessions still have two fragile moments: session start and context compaction. The canonical reading order already names `ai/handoff.md`, `ai/current-state.md`, `ai/next-actions.md`, and `ai/open-questions.md`; the missing piece is a thin tool surface that makes those files easy to consult or refresh at the right time.

## Approach

Follow the existing wrapper-over-stdlib-scripts pattern. Add a read-only session-context script for advisory SessionStart use, extend the handoff script with an explicit compact snapshot write mode, and expose all three user-invokable actions through paired Claude/Copilot command surfaces. Keep hooks non-blocking and non-mutating.

## Findings

- The existing `update-handoff` script already owns git/status collection and handoff writes, so compact snapshot belongs there as an explicit write mode.
- Session-start context should be a separate read-only script so hook mode cannot accidentally mutate files.
- The repo's skill parity and hook-path checks can validate the new command surfaces and hook references.
- The selected `standard-*` names align with the repo's lowercase kebab-case skill convention while adding the requested prefix.

## Recommendation

Add `standard-update-handoff`, `standard-get-session-context`, and `standard-compact-snapshot` as paired Claude/Copilot command surfaces. Add an optional advisory Claude SessionStart hook that invokes the read-only context script, keep the existing Stop hook, and do not add any required `ai/compact-snapshot.md` file.

## Follow-ups

- **ADR to write:** yes - [ADR-0020](../../decisions/0020-add-advisory-ai-continuity-hooks-and-standard-slash-commands.md)
- **Implementation plan changes:** update `docs/05-implementation-plan.md` with the AI continuity slice
- **New open questions:** none
- **Discovery to promote:** none
