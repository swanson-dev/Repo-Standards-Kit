# `docs/discovery/captured/`

**Synthesized discovery notes — tracked.** Markdown notes produced by `/capture-discovery`
from raw source material in the intake folders (`../meetings/`, `../requirements/`,
`../use-cases/`, `../notes/`). The raw originals stay local and gitignored; the synthesized
markdown here is the committed, auditable record. See [`../README.md`](../README.md) and
ADR-0014.

## What goes here

- One markdown note per captured source, with frontmatter (`source`, `date_captured`,
  `topic`, `status: raw`, `promoted_to:`). Filename `YYYY-MM-DD-source-topic.md`.
- These notes enter the normal promotion lifecycle: `/promote-discovery` flips a note to
  `status: promoted` and sets `promoted_to:` when its content is synthesized into a PRD/ADR.

## What does NOT go here

- Raw source files (PDFs, JSON, decks) — those live in the intake folders and are gitignored.
- Hand-authored intake markdown — drop that straight into the relevant intake subfolder.
