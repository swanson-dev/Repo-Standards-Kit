# Team Repository Standards

**Kit version:** 1.3.0
**Status:** v1.3.0 adoption starter and changelog assist shipped; roadmap in `docs/05-implementation-plan.md`
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
| **documentation** | Documentation/specification repos whose implementation lives elsewhere. Care about source maps, freshness, links, and ownership boundaries. |

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
| `docs/discovery/` | Lightweight stakeholder, research, and reconnaissance notes (folder + README). |
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

| Doc | application | library | infra | data | documentation |
|---|---|---|---|---|---|
| `01-prd.md` | Required | Optional | Optional | Expected | Expected |
| `02-architecture.md` | Required | Expected | Required | Required | Expected (information architecture) |
| `03-data-model.md` | Expected (if state-bearing) | N/A | Optional | Required | Optional |
| `04-api-and-integrations.md` | Required | Required (public API contract) | Expected | Required (sources/sinks) | Required (linked source repos and reference contracts) |
| `05-implementation-plan.md` | Expected | Optional | Expected | Expected | Expected |
| `06-runbook.md` | Required | N/A | Required | Required | N/A (unless the docs site has operations) |
| `07-testing.md` | Required | Required | Expected (drift/preview) | Required (data quality) | Required (links, generated docs, freshness) |
| `08-security-and-compliance.md` | Required | Expected | Required | Required | Expected (sensitivity, redaction, access, licensing) |
| `09-deployment.md` | Required | N/A (publishing policy in CHANGELOG) | Required | Required (orchestration) | Optional (docs site publishing only) |

### Profile-specific extras

| Profile | Adds |
|---|---|
| `library` | `docs/versioning-policy.md` (SemVer commitments, deprecation cadence, support window) |
| `infra` | `docs/environments.md` (dev/stage/prod topology + change windows) |
| `data` | `docs/data-contracts/` (per-dataset contracts: schema, owner, freshness SLO, lineage) |
| `documentation` | `docs/source-map.md` (linked implementation repos, owners, reference policy, sync cadence) |

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

`docs/discovery/` is a lightweight folder for stakeholder, research, and reconnaissance notes that are useful before they become structured project documentation. Keep it loose: discovery notes preserve context and language that may later inform PRDs, architecture docs, ADRs, RFCs, or glossary entries.

Discovery notes are normal tracked markdown files directly under `docs/discovery/`. Do not use a separate capture/promote lifecycle; when a note informs a durable artifact, link the note from that artifact or mention it in the relevant ADR/RFC.

Optional subfolders may be used when they help a repo stay organized:

| Folder | Use when |
|---|---|
| `docs/discovery/notes/` | General research, stakeholder context, and reconnaissance notes. |
| `docs/discovery/meetings/` | Meeting notes, customer conversations, and working-session summaries. |
| `docs/discovery/artifacts/` | Markdown indexes for source artifacts such as screenshots, exports, recordings, diagrams, PDFs, or whiteboards. |

Artifact storage is **pointer-first**. Prefer a markdown index in `docs/discovery/artifacts/` that records source, owner, external location, sensitivity, retention, summary, and follow-ups. Do not commit raw binary artifacts by default. Small text-native artifacts may be tracked when sanitized and useful; binary storage requires an explicit local policy, ADR, Git LFS, release assets, object storage, Drive/SharePoint, issue attachments, or another deliberate mechanism.

### Filename convention

`YYYY-MM-DD-source-topic.md`

Examples:
- `2026-05-12-acme-corp-kickoff.md`
- `2026-04-30-procurement-requirements-draft.md`
- `2026-05-02-claims-adjuster-use-case.md`

### Optional frontmatter (encouraged for traceability)

```yaml
source: <person, meeting, doc URL>
date: 2026-05-12
topic: <free text>
```

### What does NOT belong in `docs/discovery/`

- Technical investigations with a question and recommendation -> those are **RFCs** under `docs/rfcs/`.
- Decisions -> those are **ADRs** under `docs/decisions/`.
- Large binary source files -> keep those outside the repo and link to them from a markdown note when needed.

## Optional knowledge lanes

These folders are optional and should not be created just because the kit mentions them:

| Folder | Use when |
|---|---|
| `docs/design/` | Product, UX, workflow, or system design notes that are not ADRs or RFCs. |
| `support/incidents/` | Operational incident notes and post-incident follow-ups. Most relevant for application, infra, and data repos. |
| `support/troubleshooting/` | Recurring symptoms, likely causes, checks, fixes, and escalation paths. |
| `support/guides/` | User, admin, contributor, or operator guides that do not belong in numbered docs. |

Use templates under `docs/templates/` when starting these documents. `standards doctor --recommend` may suggest optional lanes from repo state. AI agents may also suggest them from session context, such as when a conversation captures a meeting, incident, design note, support guide, or external artifact. These recommendations are advisory and non-blocking; no files are created unless the user asks.

## AGENTS.md pattern

The kit uses a single root **`AGENTS.md`** as the canonical agent contract. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`) are short pointers (≤10 lines) that link back to `AGENTS.md` and add only tool-specific notes.

**Why:** maintaining three near-identical agent files invites drift. One source of truth + thin pointers = consistent behavior across Claude, Copilot, Cursor, Aider, etc.

`AGENTS.md` must include:

1. Kit version + profile.
2. Canonical reading order (`docs/00-overview` → `ai/handoff` → `ai/current-state` → `docs/STANDARDS` → `ai/next-actions` → `ai/open-questions`).
3. End-of-session contract (what to update before exiting a session).
4. Pointers to the templates for each artifact type.
5. Local conventions (date format, naming, etc.).

### Agent-readiness checklist

A repo is ready for AI-assisted work when:

- `AGENTS.md` exists and names the canonical reading order.
- `ai/current-state.md` is present and current enough to trust.
- `ai/handoff.md` is present and not older than the handoff stale threshold.
- Every local skill is paired across Claude and Copilot surfaces and listed in `AGENTS.md`.
- `standards check` passes, or any adopter warnings are explicitly accepted by the team.

### Optional AI continuity hooks

Tools may add advisory hooks around the canonical AI context files. A session-start
hook may read `ai/handoff.md`, `ai/current-state.md`, `ai/next-actions.md`, and
`ai/open-questions.md` to print a context brief, but it must not block session
start and must not mutate files. Compact snapshots and handoff refreshes are
explicit command/manual actions that write `ai/handoff.md`; they are not automatic
SessionStart behavior.

Stop hooks may also run advisory checks such as changelog reminders. These
checks should exit successfully and print guidance instead of mutating files or
blocking the session; explicit skill or slash-command surfaces handle the write.

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
7. Create the profile-required numbered docs from their templates. Leave Expected docs as stubs to be filled in (or waive them). For `documentation` repos, create `docs/source-map.md` from `docs/templates/source-map-template.md`.
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
4. **`ai/` freshness** — `ai/current-state.md`, `ai/next-actions.md`, and `ai/handoff.md` have required frontmatter; warn if `last_updated` / `written` is older than the stale threshold.
5. **ADR filename + status** — filenames match `NNNN-kebab-case.md`; status is `Proposed` | `Accepted` | `Deprecated` | `Superseded by NNNN`.
6. **RFC structure + status** — `docs/rfcs/NNNN-slug/rfc.md` exists; status is `Open` | `Concluded` | `Abandoned`.

Link checking, placeholder/content linting, skill-format linting, opt-in external-link liveness, and opt-in freshness reporting now ship as the v2 content checks (see below).

The kit's own release is guarded by `tools/check_version_coherence.py` and `tools/check_v1_readiness.py` (run in `kit-guards.yml` and `release.yml`): version strings and release tags must agree, and generated downstream fixture repos for every supported profile must pass `init`, `check`, `update`, and `check` again. These guards are kit-internal and are not shipped to adopters.

## Content checks (v2)

Beyond the structural checks, standards-check validates document bodies:

- **Internal links** — every relative markdown link (and `#anchor`) must resolve to a real file/heading. External schemes are ignored by the default offline check.
- **Placeholders** — committed ADRs/RFCs must not retain template scaffolding (`<...>` tokens, literal `YYYY-MM-DD`, bare `NNNN`).
- **Skill format / parity / index** — every `.claude/skills/<n>/SKILL.md` needs frontmatter `name` (matching its directory) and `description`, a matching `.github/prompts/<n>.prompt.md` twin, and a row in the `AGENTS.md` `## Available skills` index. (Adopters: these default to warnings, escalatable via the `skill-format` key.)

- **Agent surface pointers** - Copilot instructions must point back to `AGENTS.md`, and local Claude hook commands must reference scripts that exist.
- **External-link liveness** — opt-in networked check for `http(s)` markdown links. It is off by default so normal CI stays deterministic; run `python scripts/standards-check/check.py --external-links` or `standards check --external-links` when you want to verify release, docs, or vendor links.
- **Freshness report** — opt-in status output for `ai/current-state.md`, `ai/next-actions.md`, and `ai/handoff.md`; run `python scripts/standards-check/check.py --freshness-report` or `standards check --freshness-report`.

**Severity.** In the kit itself these are **errors**. In an adopting repo (one with a `.standards-kit.json` marker) they default to **warnings**. To escalate a check to an error in your repo, add a `"check"` map to `.standards-kit.json`:

```json
{ "check": { "links": "error", "placeholder": "error", "skill-format": "error", "external-links": "error" } }
```
