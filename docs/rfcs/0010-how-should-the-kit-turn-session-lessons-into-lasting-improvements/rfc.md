---
status: Open
opened: 2026-10-15
closed:
owner: Josh Swanson
time_box: 1 day (draft the skill, run one trial retro, review)
---

# 0010. How should the kit turn session lessons into lasting improvements?

## Question

How should the kit turn what goes wrong in a session into lasting, shared improvements, such as checks, rules, and docs, without bloating agent instructions or letting agents rewrite their own rules unreviewed?

## Why now

The kit's loop has three steps, and only two exist:

1. **Record what happened:** the handoff, changelog, and ADRs.
2. **Make sure it gets recorded:** the enforce-once hooks in [RFC-0007](../0007-how-should-the-kit-make-documentation-and-continuity-upkeep-automatic-instead-of-advisory/rfc.md).
3. **Learn, so the same problem doesn't come back:** nothing does this today. The handoff's "Don't do" list comes closest, but it is rewritten every session.

The owner proposed a retrospective feature modeled on Matt Pocock's `retro` skill. This RFC follows RFC-0007, RFC-0008, and RFC-0009: a retro's findings become drift-map rules (RFC-0007), and the skill would ship in the plugin (RFC-0008). It is drafted now so the design is not lost, not to be built before those conclude.

## Approach

- Review Matt Pocock's `retro` skill.
- Test the idea against this repo's own session of 2026-10-14 and 2026-10-15.
- Map each kind of finding onto an artifact the kit already has.

Remaining before this RFC concludes:

- **Trial run.** Draft the skill and run one retro on a real session. Check that the findings cite evidence and land in the right place.
- **Promotion threshold.** Decide how often a lesson must recur before it moves from the handoff's "Don't do" list into `AGENTS.md`.
- **Past sessions.** Decide whether the retro may also read Claude Code's local transcripts, which no other host offers in the same form, or stays with inputs every host has.

## Findings

### What Matt Pocock's retro does

- **You run it by hand.** It is marked `disable-model-invocation: true`, so the model never starts it on its own.
- **It reads one session's transcript** and looks for improvements in seven areas: finding files, automated checks, coding standards, trimming `AGENTS.md`, wasteful tool use, instructions that change nothing, and missing information.
- **It presents a ranked list of proposals.** As written, it does not edit files itself.
- **Its bias:** use `AGENTS.md` "incredibly sparingly," give mechanical mistakes deterministic checks instead of more instructions, and delete instructions that don't change behavior.

Source: [mattpocock/skills, `engineering/retro`](https://github.com/mattpocock/skills/tree/main/skills/engineering/retro).

### What a retro on this repo's own session would have found

The session that produced RFC-0007 through RFC-0009 is a fair test:

- **No `.gitattributes`.** With `core.autocrlf=true`, files check out with Windows line endings. A scripted changelog split failed on them and had to be redone. One file fixes this for everyone. *(automated guardrail)*
- **Bugs found by reading, not by checks.** `standards update` dropped adopter keys from `.standards-kit.json`, and the session brief listed answered questions as open. Both have tests now; the finding is that nothing caught them before. *(missing guardrail)*
- **A wrong claim from not looking first.** The agent called the discovery templates unused, but the payload manifest and the tests said otherwise. A pointer to check `src/standards/manifest.py` and the tests first would have prevented it. *(finding things)*
- **A personal preference that must not reach the repo.** The owner declined `rm` commands. That belongs in the owner's own agent memory, not in a file every teammate's agent reads. *(boundary)*

### Boundaries

- **Shared, not personal.** The kit's retro writes only to artifacts in git, so every agent and teammate benefits. Personal lessons belong in personal memory tools, such as the `remember` plugin or Claude Code's own memory.
- **Self-improving, not self-healing.** Fixing out-of-date docs right now is RFC-0007's job: its hooks make the agent repair docs before finishing. Changing the rules so a problem doesn't come back is this RFC's job.
- **Outside the kit's section of `AGENTS.md`.** The kit owns a protected section of `AGENTS.md`. Retro edits must land outside it, or `standards update` will report a conflict.

### Risks

- **Rule bloat.** Self-improving agents tend to add a rule every time, until `AGENTS.md` is a wall of contradictions.
- **Unreviewed self-editing.** An agent rewriting its own rules drifts over time.
- **Grading its own homework.** The agent that made a mistake may explain it away.
- **Different hosts keep sessions differently.** Claude Code stores readable transcripts locally; Codex and Copilot do not offer them in the same form.

## Proposed design

### 1. A skill you run

A `standard-retro` skill that the user runs, plus one line in the end-of-session checklist in `AGENTS.md`: "after a rough session, run `standard-retro`." No hook runs it every session, because of the token cost and the noise. Automate the trigger later only if it proves useful.

### 2. Findings need evidence

Inputs that every host has: the current conversation, the session's `git log` and diff, and check and test results. Each finding cites its evidence: a failed check, a reverted or redone commit, a declined command, or a correction from the user. Findings without evidence are dropped. When a second agent is available, it reviews the list, matching the owner's cross-review rule.

### 3. Proposals only

Findings are ranked by severity. The user approves each one, and the agent applies only the approved ones. Nothing changes without approval.

### 4. Each finding goes to a place the kit already has

| Finding | Where it goes |
|---|---|
| A mistake a script could catch | a standards check or a test |
| Docs fell out of date | a drift-map rule (RFC-0007) |
| A decision was made | an ADR |
| An unresolved disagreement | `ai/open-questions.md` |
| A dead end that keeps coming back | the handoff's "Don't do" list, then `AGENTS.md` if it keeps happening |
| An out-of-date or useless instruction | deleted |
| Something was hard to find | a pointer in `docs/00-overview.md` |
| A personal preference | not written to the repo; suggested for the user's own memory |
| A bug in the kit itself | an issue or a fix in the kit's repo |

### 5. Guarding against bloat

- Prefer a check or a deletion over new text.
- Move a lesson into `AGENTS.md` only when it keeps recurring.
- Every retro also looks for instructions to remove.

## Recommendation

Add a `standard-retro` skill that the user runs. It turns evidence-backed session lessons into ranked proposals, sends each to an artifact the kit already has, and changes nothing without approval. Keep its output shared through git, prefer checks and deletions over new rules, and build it after RFC-0007 through RFC-0009 conclude. Conclude this RFC after a trial retro on a real session.

## Follow-ups

- **ADR to write:** yes. ADR-0026 records the retro design; ADR-0022 to ADR-0025 are already reserved.
- **Implementation plan changes:** on conclusion, add a "Retrospectives" milestone to `docs/05-implementation-plan.md` after the setup wizard (RFC-0009).
- **New open questions:** none; the remaining items are tracked under Approach until this RFC concludes.
- **Discovery to promote:** none
