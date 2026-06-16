# `docs/discovery/`

**Lightweight discovery notes.** Stakeholder material, meeting notes, requirements sketches,
use cases, research, and reconnaissance can land here before they are synthesized into the
numbered docs, an RFC, or an ADR. This folder is deliberately loose; forcing early context into
engineering structure too soon kills the practice.

Write normal tracked markdown files directly under `docs/discovery/`, or use optional
subfolders when they keep a repo clearer:

- `notes/` for general research, stakeholder context, and reconnaissance.
- `meetings/` for meeting notes and customer conversations.
- `artifacts/` for markdown indexes that point to external source artifacts.

There is no capture command, promotion command, status lifecycle, or required
subfolder structure.

## What does NOT go here

- **Technical investigations with a question and recommendation** -> RFCs under [`docs/rfcs/`](../rfcs/).
- **Decisions** -> ADRs under [`docs/decisions/`](../decisions/).
- **Large binary source files** -> keep those outside the repo and link to them from a markdown note or artifact index when useful.
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

## Artifact policy

Discovery artifacts are pointer-first. Prefer a markdown index with source,
owner, external location, sensitivity, retention note, summary, and follow-ups.
Do not commit raw binary artifacts by default. If a repo needs binaries in git,
document that local policy explicitly and use a deliberate mechanism such as
Git LFS.

## Templates

- [`../templates/discovery-note-template.md`](../templates/discovery-note-template.md) - soft-landing template for general notes.
- [`../templates/discovery-meeting-template.md`](../templates/discovery-meeting-template.md) - soft-landing template for meeting notes.
- [`../templates/discovery-artifact-template.md`](../templates/discovery-artifact-template.md) - pointer-first artifact index template.
- [`../templates/discovery-meeting-notes.md`](../templates/discovery-meeting-notes.md) - legacy meeting-note starter.
- [`../templates/discovery-use-case.md`](../templates/discovery-use-case.md) - soft-landing template for use cases.

Neither template is required. Use them when they help, ignore them when stakeholder material has its own shape.
