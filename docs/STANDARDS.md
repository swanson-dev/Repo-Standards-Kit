# Team Repository Standards

**Kit version:** 0.1.0
**Slice:** 1 (Templates + standards content)
**Source of truth:** this file. Per-repo copies should be lightweight pointers (see `docs/templates/STANDARDS.md.template`).

## Purpose and precedence

This document is the authoritative spec for how repositories on the team document themselves. It exists so:

- New contributors and AI agents know **where to look**.
- Reviewers know **what to expect**.
- Decisions, investigations, and stakeholder context are **traceable**.
- Each repo can be **lean** without losing the things that matter.

### Precedence

1. **Per-repo deviations** explicitly recorded in the repo's local `docs/STANDARDS.md` (and justified by an ADR).
2. **This kit document** (the team-wide default).
3. **Implicit conventions** — never. If it isn't written here or in a per-repo deviation, it isn't a standard.

## Repo profiles

Each repo declares exactly one profile. The profile determines which numbered docs are Required / Expected / Optional / N/A.

| Profile | What it describes |
|---|---|
| **application** | Backend services, web apps, mobile apps, APIs. Have a runtime, an environment, secrets, an on-call story. |
| **library** | Internal packages (npm, NuGet, PyPI, Go modules). Distribute via registry; no environment of their own. |
| **infra** | Terraform, Bicep, Kubernetes manifests, IaC repos. Care about environments, drift, change windows. |
| **data** | ETL pipelines, dbt projects, analytics notebooks. Care about data contracts, lineage, freshness. |

If your repo doesn't fit, **pick the closest profile** and record any deviations in the local `STANDARDS.md`. Don't invent new profiles in-repo; propose one via RFC.

## Tier semantics

| Tier | Meaning | What CI does |
|---|---|---|
| **Required** | Must exist. The doc may be short, but the file must be present. | Fails the build if missing. |
| **Expected** | Present by default. May be skipped, but only with an explicit waiver. | Fails the build if missing *and* no waiver line. |
| **Optional** | Template exists; create when relevant. | Ignored. |
| **N/A** | Not applicable for this profile. Don't create. | Ignored. |

## Universal core (every profile, every repo)

| File | Purpose |
|---|---|
| `README.md` | Entry point. What is this repo, who uses it, where to go next. |
| `CHANGELOG.md` | History of meaningful change. Keep-a-Changelog style. |
| `AGENTS.md` | Canonical agent contract — reading order + end-of-session contract. |
| `CLAUDE.md` | Thin pointer to `AGENTS.md` + Claude-specific notes. |
| `docs/STANDARDS.md` | Per-repo pointer to this kit version + profile + deviations. |
| `docs/STANDARDS-CHECKLIST.md` | Per-repo checklist with waivers. |
| `docs/00-overview.md` | What this repo is, in 1 page. |
| `docs/10-glossary.md` | Project-specific terminology. |
| `docs/decisions/` | ADRs (folder + README, even if empty). |
| `docs/discovery/` | Raw intake folder (folder + README). |
| `docs/rfcs/` | RFC folder (folder + README). |
| `docs/templates/` | Starter templates (kit-supplied). |
| `ai/current-state.md` | Living snapshot of repo state. |
| `ai/next-actions.md` | Ordered, scoped next steps. |
| `ai/open-questions.md` | Anchored unresolved questions. |
| `ai/handoff.md` | End-of-session context for the next agent. |
| `.github/copilot-instructions.md` | Thin pointer to `AGENTS.md`. |
| `.github/pull_request_template.md` | PR gates including Standards Impact. |
| `.github/workflows/repo-standards.yml` | v1 standards check (see below). |

## Profile matrix (numbered docs)

| Doc | application | library | infra | data |
|---|---|---|---|---|
| `01-prd.md` | Required | Optional | Optional | Expected |
| `02-architecture.md` | Required | Expected | Required | Required |
| `03-data-model.md` | Expected (if state-bearing) | N/A | Optional | Required |
| `04-api-and-integrations.md` | Required | Required (public API contract) | Expected | Required (sources/sinks) |
| `05-implementation-plan.md` | Expected | Optional | Expected | Expected |
| `06-runbook.md` | Required | N/A | Required | Required |
| `07-testing.md` | Required | Required | Expected (drift/preview) | Required (data quality) |
| `08-security-and-compliance.md` | Required | Expected | Required | Required |
| `09-deployment.md` | Required | N/A (publishing policy in CHANGELOG) | Required | Required (orchestration) |

### Profile-specific extras

| Profile | Adds |
|---|---|
| `library` | `docs/versioning-policy.md` (SemVer commitments, deprecation cadence, support window) |
| `infra` | `docs/environments.md` (dev/stage/prod topology + change windows) |
| `data` | `docs/data-contracts/` (per-dataset contracts: schema, owner, freshness SLO, lineage) |

## The `ai/` directory contract

`ai/*.md` is **committed**, **shared**, and **rolling** — it always reflects current truth, not history.

### `ai/current-state.md`

Snapshot. Not a log.

Frontmatter: `last_updated`, `last_updated_by`.

Sections:
- **What works** — capabilities currently demonstrable in `main`.
- **What's in progress** — active feature, branch, owner, target.
- **What's blocked** — blocker, owner of the unblock, link to `ai/open-questions.md` entry.
- **Active environments** — env → URL/identifier → health.

Update trigger: end of any working session that changed one of the four sections.
Stale threshold: **14 days** (CI warning).

### `ai/next-actions.md`

Ordered, scoped, executable. Not a backlog.

Frontmatter: `last_updated`.

Body: ordered list, **maximum 7 entries**. Overflow belongs in an issue tracker.

Each entry:
- Imperative verb phrase ("Migrate users table to UUID PKs").
- One-sentence why.
- Link to relevant `docs/rfcs/`, `docs/decisions/`, or `ai/open-questions.md` entry.

Stale threshold: **14 days**.

### `ai/open-questions.md`

Anchored questions other docs can link to (`#q-N`).

Per question:
- **Status:** `open` | `answered` | `obsolete`.
- **Blocking:** what waits on this.
- **Context:** one paragraph.
- **Candidate answers:** bullets.
- **Resolution:** filled when answered; link the ADR if one was produced.

Lifecycle: answered questions remain (institutional memory). Move to `ai/open-questions-archive.md` once the live file gets long (>50 entries).

### `ai/handoff.md`

Most ephemeral. Designed as the *first* thing a new AI session reads.

Frontmatter: `written` (timestamp), `written_by`, `for: next-session`.

Sections:
- **TL;DR** — 3–5 sentences.
- **Recently touched** — files/areas with one-line why.
- **Open threads** — thread → status → where to resume.
- **Don't do** — recent dead-ends or rejected approaches the next session shouldn't re-walk.

Stale threshold: **5 days** (if older, treat as "no handoff written").

### Ownership and update cadence

| File | Primary owner | Update cadence | Stale threshold |
|---|---|---|---|
| `current-state.md` | Whoever last shipped | After any state-changing PR | 14 days |
| `next-actions.md` | Tech lead / on-deck dev | When priorities shift | 14 days |
| `open-questions.md` | Author of the question | When opens/closes | None |
| `handoff.md` | End of session | Every meaningful session | 5 days |

## ADRs — MADR 3.0

ADRs live in `docs/decisions/`. They are **immutable once Accepted**.

### Filename

`NNNN-kebab-case-title.md`. Zero-padded 4 digits, monotonically increasing.

### Status lifecycle

`Proposed` → `Accepted` → (`Deprecated` | `Superseded by NNNN`)

To change an accepted decision, write a new ADR with the new decision and flip the old ADR's status to `Superseded by <new-NNNN>`. **Do not edit the body of an Accepted ADR.**

### Required structure

See `docs/templates/adr-template.md`. The mandatory sections are:

- Frontmatter: `status`, `date`, `deciders`, `consulted`, `informed`.
- **Context and Problem Statement**
- **Decision Drivers**
- **Considered Options**
- **Decision Outcome** (chosen option + because + Consequences)

Optional sections: **Pros and Cons of the Options**, **More Information**.

## RFCs

RFCs live in `docs/rfcs/NNNN-slug/` — one **folder** per RFC so artifacts (benchmarks, screenshots, prototypes) live alongside the prose.

### Filename and structure

```
docs/rfcs/0003-evaluate-graphql-vs-rest/
├── rfc.md
└── artifacts/
```

### `rfc.md` shape

See `docs/templates/rfc-template.md`. Mandatory sections:

- Frontmatter: `status` (`Open` | `Concluded` | `Abandoned`), `opened`, `closed`, `owner`, `time_box`.
- **Question** — one sentence.
- **Why now** — what's downstream of the answer.
- **Approach** — how we'll investigate.
- **Findings** — what we learned.
- **Recommendation** — one paragraph.
- **Follow-ups** — ADR to write? Implementation plan changes? New open questions?

### Lifecycle rule

Every RFC must reach one of three terminal states:

1. **Concluded** — spawned an ADR (or explicitly noted "no ADR needed; recommendation is informational").
2. **Abandoned** — with a one-sentence reason in the frontmatter.
3. **Open question carried forward** — the central question is moved into `ai/open-questions.md` and the RFC is `Abandoned` with a reason linking to the open question.

RFCs do not sit `Open` indefinitely.

## Discovery folder

`docs/discovery/` is the **raw intake folder** for unstructured stakeholder material — meeting notes, requirements drafts, use case docs, anything pre-structured.

### Subfolders

- `meetings/` — meeting notes.
- `requirements/` — business requirements drafts received from stakeholders.
- `use-cases/` — use case documents (often stakeholder-authored).
- `notes/` — anything else pre-structured.

### Filename convention

`YYYY-MM-DD-source-topic.md`

Examples:
- `meetings/2026-05-12-acme-corp-kickoff.md`
- `requirements/2026-04-30-procurement-requirements-draft.md`
- `use-cases/2026-05-02-claims-adjuster-use-case.md`

### Optional frontmatter (encouraged for traceability)

```yaml
source: <person, meeting, doc URL>
date_captured: 2026-05-12
topic: <free text>
status: raw | reviewed | promoted
promoted_to: docs/01-prd.md   # filled when status flips to promoted
```

### Traceability flow

When content from a discovery file is synthesized into a structured doc (PRD, architecture, ADR, etc.), flip `status: promoted` and set `promoted_to:`. This turns the folder from a write-only graveyard into a traceable feeder system.

### What does NOT belong in `docs/discovery/`

- Technical investigations with a question and recommendation → those are **RFCs** under `docs/rfcs/`.
- Decisions → those are **ADRs** under `docs/decisions/`.

## AGENTS.md pattern

The kit uses a single root **`AGENTS.md`** as the canonical agent contract. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`) are short pointers (≤10 lines) that link back to `AGENTS.md` and add only tool-specific notes.

**Why:** maintaining three near-identical agent files invites drift. One source of truth + thin pointers = consistent behavior across Claude, Copilot, Cursor, Aider, etc.

`AGENTS.md` must include:

1. Kit version + profile.
2. Canonical reading order (`docs/00-overview` → `ai/handoff` → `ai/current-state` → `docs/STANDARDS` → `ai/next-actions` → `ai/open-questions`).
3. End-of-session contract (what to update before exiting a session).
4. Pointers to the templates for each artifact type.
5. Local conventions (date format, naming, etc.).

## Waiver mechanism

A waiver records an explicit, justified absence of a Required or Expected doc.

### Where to record

In `docs/STANDARDS-CHECKLIST.md`, on the same line as the unchecked box:

```markdown
- [ ] docs/03-data-model.md — **Waived:** repo is a stateless reverse proxy; has no domain entities.
```

### CI enforcement

The standards workflow parses unchecked boxes. A line without `**Waived:** <reason>` fails the build. A line with a waiver passes.

### Review

Waivers are reviewed during the doc's review cycle (recorded in `docs/STANDARDS.md` `Last reviewed` field). If a waiver no longer applies, the doc should be created.

## Adopting the kit in a new repo

1. Copy `docs/templates/` from this kit into your repo (eventually a Skill in Slice 2 will do this).
2. Decide the profile.
3. Create `AGENTS.md` and `CLAUDE.md` from the kit's root copies (rewrite the "What this repo is" and "Local conventions" sections).
4. Fill `docs/STANDARDS.md` from `docs/templates/STANDARDS.md.template`.
5. Fill `docs/STANDARDS-CHECKLIST.md` from `docs/templates/STANDARDS-CHECKLIST.md.template`.
6. Seed `ai/*.md` from `docs/templates/ai-starters/`.
7. Create the profile-required numbered docs from their templates. Leave Expected docs as stubs to be filled in (or waive them).
8. Adopt `.github/pull_request_template.md` and `.github/workflows/repo-standards.yml`.
9. Run the CI check locally if possible; commit when green.

## Kit versioning

The kit follows SemVer.

| Change | Bump |
|---|---|
| New optional artifact, new profile-specific extra | Minor |
| New Required or Expected doc, change to existing template structure | Minor (downstream repos opt-in) |
| Removed artifact, changed tier (e.g., Optional → Required), incompatible folder rename | Major |
| Typo fixes, clarifications, new examples | Patch |

Each repo records the kit version it adopted in its local `docs/STANDARDS.md`. Upgrading is a deliberate per-repo action, not automatic.

## Standards check workflow (v1)

`.github/workflows/repo-standards.yml` checks:

1. **Universal core present** — all files listed under "Universal core".
2. **Profile declared** — `docs/STANDARDS.md` declares a profile from the allowed set.
3. **Waiver completeness** — every unchecked box in `docs/STANDARDS-CHECKLIST.md` has `**Waived:** <reason>`.
4. **`ai/` freshness** — `ai/current-state.md` and `ai/handoff.md` have required frontmatter; warn if `last_updated` / `written` is older than the stale threshold.
5. **ADR filename + status** — filenames match `NNNN-kebab-case.md`; status is `Proposed` | `Accepted` | `Deprecated` | `Superseded by NNNN`.
6. **RFC structure + status** — `docs/rfcs/NNNN-slug/rfc.md` exists; status is `Open` | `Concluded` | `Abandoned`.

Link checking, placeholder/content linting, and skill-format linting now ship as the v2 content checks (see below). Deeper checks still ahead — external-link liveness and richer doc-freshness reporting — remain future work.

The kit's own release is guarded by `tools/check_version_coherence.py` (run in `kit-guards.yml` and `release.yml`): `src/standards/__about__.py`, the CHANGELOG top entry, and the `AGENTS.md` Kit-version must agree, and a release tag must match the version. This guard is kit-internal and is not shipped to adopters.

## Content checks (v2)

Beyond the structural checks, standards-check validates document bodies:

- **Internal links** — every relative markdown link (and `#anchor`) must resolve to a real file/heading. External (`http(s)`/`mailto`) links are not checked.
- **Placeholders** — committed ADRs/RFCs must not retain template scaffolding (`<...>` tokens, literal `YYYY-MM-DD`, bare `NNNN`).
- **Skill format / parity / index** — every `.claude/skills/<n>/SKILL.md` needs frontmatter `name` (matching its directory) and `description`, a matching `.github/prompts/<n>.prompt.md` twin, and a row in the `AGENTS.md` `## Available skills` index. (Adopters: these default to warnings, escalatable via the `skill-format` key.)
- **Discovery** — every `status: promoted` item under `docs/discovery/` must have a `promoted_to:` path that exists.

**Severity.** In the kit itself these are **errors**. In an adopting repo (one with a `.standards-kit.json` marker) they default to **warnings**. To escalate a check to an error in your repo, add a `"check"` map to `.standards-kit.json`:

```json
{ "check": { "links": "error", "placeholder": "error", "skill-format": "error" } }
```
