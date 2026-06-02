<!--
Discovery: meeting notes (soft-landing template, NOT required structure)
Filename: docs/discovery/captured/YYYY-MM-DD-source-topic.md
A hand-authored note is already-synthesized markdown, so it lives in captured/ (tracked).
Raw drops (PDFs, recordings) go in the gitignored docs/discovery/meetings/ intake folder
and are turned into a captured/ note by /capture-discovery. See ADR-0014.
When this file's content is synthesized into a structured doc, flip status to "promoted"
and set promoted_to to the path of the synthesized doc.
-->
---
source: <attendee names, meeting title, or URL>
date_captured: YYYY-MM-DD
topic: <free text>
status: raw               # raw | reviewed | promoted
promoted_to:              # e.g. docs/01-prd.md  (filled when status flips to promoted)
---

# <Meeting title> — YYYY-MM-DD

## Attendees

- <name, role>
- <name, role>

## Agenda

- <item>
- <item>

## Notes

<!-- Free-form. Stakeholder material doesn't bend to engineering structure. -->

## Decisions made (if any)

- <decision — link to ADR if one was authored>

## Actions

- [ ] <owner> — <action> — <due date>

## Open questions raised

- <question — add to ai/open-questions.md as #q-N if it blocks something>
