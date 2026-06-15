# AGENTS.md

<!-- BEGIN kit-managed: agents-core (v0.18.0) -->
Single source of truth for AI agents working in this repository. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`) are thin pointers to this document.

- Kit version: **0.18.0**

## Canonical reading order

When you start a session in a repo that follows this kit, read in this order before taking action:

1. **`docs/00-overview.md`** — what this repo is, in 1 page.
2. **`ai/handoff.md`** — what the last session left for you. If `written` is older than 5 days, treat as "no handoff available".
3. **`ai/current-state.md`** — the current truth about what works, what's in progress, what's blocked.
4. **`docs/STANDARDS.md`** — which profile this repo follows and any local deviations.
5. **`ai/next-actions.md`** — the next 1–7 things on deck.
6. **`ai/open-questions.md`** — unresolved questions you may need to factor in.

Only after that, dive into the code or the user's specific request.

## End-of-session contract

Before you finish a session that produced meaningful change:

- [ ] Update `ai/current-state.md` if any of the four sections changed (What works · What's in progress · What's blocked · Active environments).
- [ ] Write `ai/handoff.md` for the next session — TL;DR, recently touched, open threads, and **Don't do** (dead-ends to spare the next session).
- [ ] If you opened a new question while working, add it to `ai/open-questions.md` with a unique anchor (`#q-N`).
- [ ] If you closed an `ai/open-questions.md` entry, flip status to `answered` and link the ADR (if one was produced) or the resolution.
- [ ] If you made a material technical decision, write an ADR in `docs/decisions/` (MADR 3.0 format — see `docs/templates/adr-template.md`).
- [ ] If you ran a time-boxed investigation, write or conclude an RFC in `docs/rfcs/<NNNN-slug>/rfc.md`.
- [ ] Run `/standards-check` (or `python scripts/standards-check/check.py`) and fix any findings before ending a session that touched docs.

## How to author each artifact type

- **ADRs:** `docs/templates/adr-template.md`. Immutable once `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- **RFCs:** `docs/templates/rfc-template.md`. One folder per RFC under `docs/rfcs/NNNN-slug/`. Every RFC must either spawn an ADR, be `Abandoned` with reason, or its question must be tracked in `ai/open-questions.md`.
- **Discovery items:** lightweight stakeholder, research, and reconnaissance notes live directly under `docs/discovery/` as tracked markdown. Templates: `docs/templates/discovery-meeting-notes.md` / `discovery-use-case.md`. Filename: `YYYY-MM-DD-source-topic.md`. Optional frontmatter (`source`, `date`, `topic`).
- **Skills:** `docs/templates/skill-template.md` (Claude) + `docs/templates/skill-prompt-template.md` (Copilot). Name must equal the skill's directory; add a row to the `## Available skills` index.
- **Numbered docs:** see `docs/STANDARDS.md` for which docs are Required/Expected/Optional/N/A for this profile.

## Standard conventions

- Date format everywhere: ISO 8601 (`YYYY-MM-DD`).
- Filename conventions: lowercase kebab-case for slugs.
- Don't edit files in `docs/decisions/` whose status is `Accepted` — write a superseding ADR instead.
- Don't create numbered docs marked **N/A** for this profile. If a doc is **Optional** and you skip it, no waiver is needed. If it's **Required** or **Expected** and you skip it, add a `**Waived:** <reason>` line in `docs/STANDARDS-CHECKLIST.md`.
<!-- END kit-managed: agents-core -->

## Available skills

| Skill | When to use |
|---|---|
| `new-adr` | Recording a material architecture decision |
| `new-rfc` | Starting a time-boxed investigation |
| `update-handoff` | Writing the end-of-session handoff |
| `standards-check` | Running the standards checks + fixing findings before pushing |

## About this repository

This is the **Team Repository Standards Kit** — a versioned set of documentation standards, templates, AI Skills + a `standards` CLI, and CI checks that other repositories adopt.

- Profile: **library** (this kit ships templates; it has no runtime, no deployment, no runbook)

### Local conventions

- This kit follows itself. Every Slice 1 decision (profile model, ADR format, RFC format, `ai/` contract, AGENTS.md pattern) is captured as an ADR in `docs/decisions/`.

### Roadmap

The active milestone and forward plan live in
`docs/05-implementation-plan.md`. Genuinely-future work
(open an RFC or `ai/open-questions.md` entry before starting): a `new-skill` scaffolder.
