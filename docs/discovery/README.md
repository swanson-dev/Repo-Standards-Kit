# `docs/discovery/`

**Lightweight discovery notes.** Stakeholder material, meeting notes, requirements sketches,
use cases, research, and reconnaissance can land here before they are synthesized into the
numbered docs, an RFC, or an ADR. This folder is deliberately loose; forcing early context into
engineering structure too soon kills the practice.

Write normal tracked markdown files directly under `docs/discovery/`. There is no capture command,
promotion command, status lifecycle, or required subfolder structure.

## What does NOT go here

- **Technical investigations with a question and recommendation** -> RFCs under [`docs/rfcs/`](../rfcs/).
- **Decisions** -> ADRs under [`docs/decisions/`](../decisions/).
- **Large binary source files** -> keep those outside the repo and link to them from a markdown note when useful.
- **Synthesized product specs** -> `docs/01-prd.md` and friends.

## Filename convention

`YYYY-MM-DD-source-topic.md` - e.g. `2026-05-12-acme-corp-kickoff.md`.

## Frontmatter

Optional, but useful for traceability:

```yaml
source: <person, meeting, doc path/URL>
date: 2026-05-12
topic: <free text>
```

## Traceability flow

When a discovery note informs a structured doc, link the note from that doc, RFC, or ADR.

## Templates

- [`../templates/discovery-meeting-notes.md`](../templates/discovery-meeting-notes.md) - soft-landing template for meeting notes.
- [`../templates/discovery-use-case.md`](../templates/discovery-use-case.md) - soft-landing template for use cases.

Neither template is required. Use them when they help, ignore them when stakeholder material has its own shape.
