---
mode: agent
description: Turn raw source material (PDFs, JSON, drafts) in the discovery intake folders into synthesized markdown notes under docs/discovery/captured/, ready for promotion.
---

# capture-discovery

When the user has dropped source material (PDFs, JSON, decks, drafts) into
`docs/discovery/{meetings,requirements,use-cases,notes}/` and wants it turned into tracked
markdown discovery notes, run these from the repo root:

**1. See what's uncaptured:** `python scripts/capture-discovery/capture_discovery.py list`

**2. For each source, read it and scaffold a note** (the script writes frontmatter; you write
the body):

`python scripts/capture-discovery/capture_discovery.py new --kind <meetings|requirements|use-cases|notes> --topic "<short topic>" --source <path-to-source>`

`--kind` and `--topic` are required; `--source` is recorded in the note's `source:` frontmatter.
The note lands at `docs/discovery/captured/YYYY-MM-DD-<slug>.md` with `status: raw`.

**3. Fill the body** of the created note with a faithful synthesis of the source. The script
does not parse the source — that synthesis is your job.

Capture is the stage before promote (ADR-0014). The raw source stays gitignored and local;
commit only the synthesized `captured/*.md` notes. Later, run `/promote-discovery` to flip a
note `status: raw → promoted` once its content feeds a structured doc.

**Note for Copilot users:** Claude Code's SessionStart hook auto-pings when uncaptured sources
exist at session open; Copilot Chat has no equivalent. Run `list` periodically to check.
