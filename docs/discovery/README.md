# `docs/discovery/`

**Raw intake → synthesized notes.** Stakeholder material the team *receives* — meeting notes,
business requirements drafts, use case docs, PDFs, JSON exports, anything pre-structured. This
folder is deliberately loose; forcing engineering structure on stakeholder material kills the
practice. See ADR-0014 for the capture lifecycle and ADR-0005 for the discovery/RFC split.

## How it works (ADR-0014)

```
docs/discovery/
├── meetings/        ┐
├── requirements/    │  raw intake — LOCAL ONLY, gitignored (drop PDFs/JSON/drafts here)
├── use-cases/       │
├── notes/           ┘
└── captured/        synthesized markdown notes — TRACKED (committed)
```

1. **Drop source material** into the matching intake subfolder. The contents of these folders
   are **gitignored** (`.gitignore` keeps the folders via `.gitkeep` but ignores their files), so
   binaries and drafts never enter version control — the "markdown only" constraint holds.
2. **Run `/capture-discovery`.** The AI reads each source and writes a synthesized markdown note
   into `captured/` with frontmatter (`status: raw`). The raw original stays local.
3. **Run `/promote-discovery`** when a captured note's content is synthesized into a structured
   doc — it flips `status: raw → promoted` and sets `promoted_to:`.

## What goes where

| Folder | Use for | Tracked? |
|---|---|---|
| `meetings/` | Meeting notes, call recordings, decks | No (gitignored) |
| `requirements/` | Business requirements drafts received from stakeholders | No (gitignored) |
| `use-cases/` | Use case docs (often stakeholder-authored) | No (gitignored) |
| `notes/` | Anything else pre-structured (PDFs, JSON, interviews) | No (gitignored) |
| `captured/` | Synthesized markdown notes produced by `/capture-discovery` | **Yes** |

## What does NOT go here

- **Technical investigations with a question and recommendation** → RFCs under [`docs/rfcs/`](../rfcs/).
- **Decisions** → ADRs under [`docs/decisions/`](../decisions/).
- **Synthesized product specs** → `docs/01-prd.md` and friends.

## Filename convention (for `captured/` notes)

`YYYY-MM-DD-source-topic.md` — e.g. `captured/2026-05-12-acme-corp-kickoff.md`.

## Frontmatter

```yaml
source: <person, meeting, doc path/URL>
date_captured: 2026-05-12
topic: <free text>
status: raw | reviewed | promoted
promoted_to: docs/01-prd.md
```

## Traceability flow

`docs/discovery/{intake}` (local) → `/capture-discovery` → `docs/discovery/captured/` →
`/promote-discovery` → `docs/decisions/` / numbered docs. Flipping `status: promoted` with a
`promoted_to:` turns the folder from a write-only graveyard into an auditable feeder system.

## Templates

- [`../templates/discovery-meeting-notes.md`](../templates/discovery-meeting-notes.md) — soft-landing template for meeting notes.
- [`../templates/discovery-use-case.md`](../templates/discovery-use-case.md) — soft-landing template for use cases.

Neither template is required — use them when they help, ignore them when stakeholder material has its own shape.
