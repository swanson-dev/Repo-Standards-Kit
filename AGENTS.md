# AGENTS.md

Single source of truth for AI agents working in this repository. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`) are thin pointers to this document.

## What this repo is

This is the **Team Repository Standards Kit** — a versioned set of documentation standards, templates, and (in later slices) AI Skills, Hooks, and CI checks that other repositories adopt.

- Kit version: **0.3.0** (Slice 2.5: `update-handoff` hook + slash command)
- Profile: **library** (this kit ships templates; it has no runtime, no deployment, no runbook)

## Canonical reading order

When you start a session in a repo that follows this kit, read in this order before taking action:

1. **`docs/00-overview.md`** — what this repo is, in 1 page.
2. **`ai/handoff.md`** — what the last session left for you. If `written` is older than 7 days, treat as "no handoff available".
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
- [ ] If you used content from `docs/discovery/`, flip its `status: raw` → `promoted` and set `promoted_to:`.

## How to author each artifact type

- **ADRs:** `docs/templates/adr-template.md`. Immutable once `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- **RFCs:** `docs/templates/rfc-template.md`. One folder per RFC under `docs/rfcs/NNNN-slug/`. Every RFC must either spawn an ADR, be `Abandoned` with reason, or its question must be tracked in `ai/open-questions.md`.
- **Discovery items:** `docs/templates/discovery-meeting-notes.md` or `discovery-use-case.md`. Filename: `YYYY-MM-DD-source-topic.md`. Place in the right subfolder. Optional but encouraged frontmatter (`source`, `date_captured`, `topic`, `status`, `promoted_to`).
- **Numbered docs:** see `docs/STANDARDS.md` for which docs are Required/Expected/Optional/N/A for this profile.

## Local conventions for this kit

- Date format everywhere: ISO 8601 (`YYYY-MM-DD`).
- Filename conventions: lowercase kebab-case for slugs.
- Don't edit files in `docs/decisions/` whose status is `Accepted` — write a superseding ADR instead.
- Don't create numbered docs marked **N/A** for this profile. If a doc is **Optional** and you skip it, no waiver is needed. If it's **Required** or **Expected** and you skip it, add a `**Waived:** <reason>` line in `docs/STANDARDS-CHECKLIST.md`.
- This kit follows itself. Every Slice 1 decision (profile model, ADR format, RFC format, ai/ contract, AGENTS.md pattern) is also captured as an ADR in `docs/decisions/`.

## What's out of scope right now (queued slices)

- **Slice 2.6:** AI Hook — `promote-discovery` (reminder for raw items in `docs/discovery/`). Slice 2.5 shipped `update-handoff`; this is the second hook, deferred to keep Slice 2.5 surgical.
- **Slice 3:** Distribution mechanism (template repo vs. Claude Code plugin vs. copy script).
- **Slice 4:** Deeper CI enforcement (content linting, doc freshness, link checking).

If you're tempted to add a distribution mechanism or deeper CI check while working on Slice 2.6 — don't. Open an RFC or an `ai/open-questions.md` entry instead.
