---
name: capture-discovery
description: Turn raw source material (PDFs, JSON, drafts) dropped in the discovery intake folders into synthesized markdown notes under docs/discovery/captured/, ready for promotion.
---

# capture-discovery

## When to invoke

Use when:
- The SessionStart hook surfaced an "N uncaptured sources" reminder.
- The user dropped source material (PDFs, JSON exports, decks, hand-written drafts) into
  `docs/discovery/{meetings,requirements,use-cases,notes}/` and wants it turned into tracked
  markdown discovery notes.

Capture is the stage *before* promote (ADR-0014). Raw intake is gitignored and local; the
synthesized markdown notes you produce in `docs/discovery/captured/` are what gets committed.
`/promote-discovery` then promotes those notes when they feed a PRD/ADR.

## How to invoke

**1. See what's uncaptured** (default verbose mode) from the repo root:

`python scripts/capture-discovery/capture_discovery.py list`

**2. For each source file**, read it (you can open PDFs, JSON, etc. directly), then scaffold
a note. The script writes the frontmatter skeleton; you write the synthesized body:

`python scripts/capture-discovery/capture_discovery.py new --kind <meetings|requirements|use-cases|notes> --topic "<short topic>" --source <path-to-source>`

`--kind` and `--topic` are required; `--source` is the relative path to the raw file and is
recorded in the note's `source:` frontmatter for provenance. The note lands at
`docs/discovery/captured/YYYY-MM-DD-<slug>.md` with `status: raw`.

**3. Fill the body.** Open the created note and replace the placeholder comment with a faithful
synthesis of the source: key points, decisions, requirements, open questions — in the team's
engineering language. The script does NOT parse the source; that synthesis is your job.

## Reading binary sources (PDF fallback)

Claude reads PDFs and most documents directly via its file tools — no extra tooling needed. The
kit ships **no** PDF dependency by design (ADR-0007, stdlib-only); extraction tooling is the
caller's choice, used only when direct reading isn't possible (a scanned/image-only PDF, an
unsupported format, or a non-Claude agent like Copilot). To dump text first, then synthesize:

```sh
python -m pip install pypdf
python -c "from pypdf import PdfReader; print(chr(10).join(p.extract_text() for p in PdfReader(r'<path-to.pdf>').pages))"
```

Scanned/image PDFs return empty text from `extract_text()` — those need OCR (or just let Claude read the file).

## After scaffolding

- The raw source stays where it is (gitignored). Do not commit it.
- Commit the new `captured/*.md` note(s).
- When a note's content is later synthesized into a structured doc, run `/promote-discovery`
  to flip `status: raw → promoted` and set `promoted_to:`.
