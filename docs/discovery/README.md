# `docs/discovery/`

**Raw intake.** Stakeholder material the team *receives*: meeting notes, business requirements drafts, use case docs, anything pre-structured. This folder is deliberately loose — forcing engineering structure on stakeholder material kills the practice.

## What goes here

- Meeting notes (kickoffs, stakeholder syncs, customer calls).
- Business requirements drafts.
- Use case documents from product, sales, or the customer themselves.
- Raw notes from interviews, demos, or workshops.

## What does NOT go here

- **Technical investigations with a question and recommendation** → those are RFCs under [`docs/rfcs/`](../rfcs/).
- **Decisions** → those are ADRs under [`docs/decisions/`](../decisions/).
- **Synthesized product specs** → those are in `docs/01-prd.md` and friends.

## Subfolders

| Folder | Use for |
|---|---|
| `meetings/` | Meeting notes |
| `requirements/` | Business requirements drafts received from stakeholders |
| `use-cases/` | Use case docs (often stakeholder-authored) |
| `notes/` | Anything else pre-structured |

## Filename convention

`YYYY-MM-DD-source-topic.md`

Examples:
- `meetings/2026-05-12-acme-corp-kickoff.md`
- `requirements/2026-04-30-procurement-requirements-draft.md`
- `use-cases/2026-05-02-claims-adjuster-use-case.md`

## Optional frontmatter (encouraged for traceability)

```yaml
source: <person, meeting, doc URL>
date_captured: 2026-05-12
topic: <free text>
status: raw | reviewed | promoted
promoted_to: docs/01-prd.md
```

## Traceability flow

When content from a discovery file gets synthesized into a structured doc (a PRD section, an ADR, an architecture decision), flip `status: promoted` and set `promoted_to:` to the synthesized doc's path. This turns the folder from a write-only graveyard into a feeder system you can audit: a future Skill (Slice 2) will list everything still `raw` to surface unprocessed input.

## Templates

- [`../templates/discovery-meeting-notes.md`](../templates/discovery-meeting-notes.md) — soft-landing template for meeting notes.
- [`../templates/discovery-use-case.md`](../templates/discovery-use-case.md) — soft-landing template for use cases.

Neither template is required — use them when they help, ignore them when stakeholder material has its own shape.
