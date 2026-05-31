# `docs/templates/`

Starter templates for every artifact the kit ships. Copy these into a downstream repo when adopting the kit; copy individual templates when authoring a new artifact in an already-adopted repo.

A future Skill (Slice 2) will automate the copy + parametrize step.

## What's here

### Decision artifacts
- [`adr-template.md`](./adr-template.md) — MADR 3.0 Architecture Decision Record.
- [`rfc-template.md`](./rfc-template.md) — Time-boxed technical investigation.

### Discovery soft-landing templates (optional)
- [`discovery-meeting-notes.md`](./discovery-meeting-notes.md)
- [`discovery-use-case.md`](./discovery-use-case.md)

### Numbered-doc skeletons (`docs/00–10`)
- [`overview-template.md`](./overview-template.md) → `docs/00-overview.md`
- [`prd-template.md`](./prd-template.md) → `docs/01-prd.md`
- [`architecture-template.md`](./architecture-template.md) → `docs/02-architecture.md`
- [`data-model-template.md`](./data-model-template.md) → `docs/03-data-model.md`
- [`api-and-integrations-template.md`](./api-and-integrations-template.md) → `docs/04-api-and-integrations.md`
- [`implementation-plan-template.md`](./implementation-plan-template.md) → `docs/05-implementation-plan.md`
- [`runbook-template.md`](./runbook-template.md) → `docs/06-runbook.md`
- [`testing-template.md`](./testing-template.md) → `docs/07-testing.md`
- [`security-template.md`](./security-template.md) → `docs/08-security-and-compliance.md`
- [`deployment-template.md`](./deployment-template.md) → `docs/09-deployment.md`
- [`glossary-template.md`](./glossary-template.md) → `docs/10-glossary.md`

### Profile-specific extras
- [`versioning-policy-template.md`](./versioning-policy-template.md) — library profile.
- [`environments-template.md`](./environments-template.md) — infra profile.
- [`data-contract-template.md`](./data-contract-template.md) — data profile (one per dataset).

### `ai/` starters
- [`ai-starters/current-state.md`](./ai-starters/current-state.md)
- [`ai-starters/next-actions.md`](./ai-starters/next-actions.md)
- [`ai-starters/open-questions.md`](./ai-starters/open-questions.md)
- [`ai-starters/handoff.md`](./ai-starters/handoff.md)

### Skill skeletons
- [`skill-template.md`](./skill-template.md) — Claude `SKILL.md` skeleton.
- [`skill-prompt-template.md`](./skill-prompt-template.md) — Copilot `.prompt.md` skeleton.

### Per-repo governance
- [`STANDARDS.md.template`](./STANDARDS.md.template) → `docs/STANDARDS.md`
- [`STANDARDS-CHECKLIST.md.template`](./STANDARDS-CHECKLIST.md.template) → `docs/STANDARDS-CHECKLIST.md`

## Convention

Every template uses **HTML comments** (`<!-- ... -->`) for authoring guidance. This way the rendered document starts clean — the guidance is visible only in source view (and to AI agents that read the raw markdown).

## What to do when adopting

See `docs/STANDARDS.md` § "Adopting the kit in a new repo".
