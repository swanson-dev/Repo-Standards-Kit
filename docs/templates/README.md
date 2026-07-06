# `docs/templates/`

Starter templates for every artifact the kit ships. Copy these into a downstream repo when adopting the kit; copy individual templates when authoring a new artifact in an already-adopted repo.

`standards adopt` (existing repos) and `standards init` (empty repos) automate the copy + parametrize step.

## What's here

### Decision artifacts
- [`adr-template.md`](./adr-template.md) — MADR 3.0 Architecture Decision Record.
- [`rfc-template.md`](./rfc-template.md) — Time-boxed technical investigation.

### Discovery soft-landing templates (optional)
- [`discovery-note-template.md`](./discovery-note-template.md)
- [`discovery-meeting-template.md`](./discovery-meeting-template.md)
- [`discovery-artifact-template.md`](./discovery-artifact-template.md) — pointer-first index for external artifacts; do not commit raw binaries by default.
- [`discovery-use-case.md`](./discovery-use-case.md)

Hand-authored discovery notes from these templates are normal tracked markdown files under `docs/discovery/`. Link them from any structured doc, RFC, or ADR they later inform.

### Optional knowledge lanes
- [`design-template.md`](./design-template.md) — for optional `docs/design/` notes.
- [`incident-template.md`](./incident-template.md) — for optional `support/incidents/` notes.
- [`troubleshooting-template.md`](./troubleshooting-template.md) — for optional `support/troubleshooting/` notes.
- [`guide-template.md`](./guide-template.md) — for optional `support/guides/` docs.

These folders are not scaffolded by default. Create them when they fit the repo,
or let `standards doctor --recommend` point out likely candidates.

### Numbered-doc skeletons (`docs/00–10`)
- `overview-template.md` → `docs/00-overview.md` (seeded automatically at adoption).
- [`prd-template.md`](./prd-template.md) → `docs/01-prd.md`
- [`architecture-template.md`](./architecture-template.md) → `docs/02-architecture.md`
- [`data-model-template.md`](./data-model-template.md) → `docs/03-data-model.md`
- [`api-and-integrations-template.md`](./api-and-integrations-template.md) → `docs/04-api-and-integrations.md`
- [`implementation-plan-template.md`](./implementation-plan-template.md) → `docs/05-implementation-plan.md`
- [`runbook-template.md`](./runbook-template.md) → `docs/06-runbook.md`
- [`testing-template.md`](./testing-template.md) → `docs/07-testing.md`
- [`security-template.md`](./security-template.md) → `docs/08-security-and-compliance.md`
- [`deployment-template.md`](./deployment-template.md) → `docs/09-deployment.md`
- `glossary-template.md` → `docs/10-glossary.md` (seeded automatically at adoption).

### Profile-specific extras
- [`versioning-policy-template.md`](./versioning-policy-template.md) — library profile.
- [`environments-template.md`](./environments-template.md) — infra profile.
- [`data-contract-template.md`](./data-contract-template.md) — data profile (one per dataset).
- [`source-map-template.md`](./source-map-template.md) — documentation profile.

### `ai/` starters (seeded automatically at adoption)
- `ai-starters/current-state.md` → `ai/current-state.md`
- `ai-starters/next-actions.md` → `ai/next-actions.md`
- `ai-starters/open-questions.md` → `ai/open-questions.md`
- `ai-starters/handoff.md` → `ai/handoff.md`

### Skill skeletons
- [`skill-template.md`](./skill-template.md) — Claude `SKILL.md` skeleton.
- [`skill-prompt-template.md`](./skill-prompt-template.md) — Copilot `.prompt.md` skeleton.

Create skill surfaces as pairs: `.claude/skills/<name>/SKILL.md` and
`.github/prompts/<name>.prompt.md` should share the same kebab-case name,
same one-line description, and the same core invocation guidance. Add the name
to `AGENTS.md` `## Available skills` so agents can discover it. Example index
row: ``| `review-docs` | Review docs before shipping |``.

### Per-repo governance
- `repo-readme-template.md` → `README.md` (seeded automatically at adoption).
- `changelog-template.md` → `CHANGELOG.md` (seeded automatically at adoption).
- [`STANDARDS.md.template`](./STANDARDS.md.template) → `docs/STANDARDS.md`
- `STANDARDS-CHECKLIST.md.template` → `docs/STANDARDS-CHECKLIST.md` (seeded automatically at adoption).

## Convention

Every template uses **HTML comments** (`<!-- ... -->`) for authoring guidance. This way the rendered document starts clean — the guidance is visible only in source view (and to AI agents that read the raw markdown).

## What to do when adopting

See `docs/STANDARDS.md` § "Adopting the kit in a new repo".
