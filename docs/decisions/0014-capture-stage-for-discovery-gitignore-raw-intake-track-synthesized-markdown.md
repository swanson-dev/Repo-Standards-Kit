---
status: Superseded by 0017
date: 2026-06-01
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0014. Capture stage for discovery: gitignore raw intake, track synthesized markdown

## Context and Problem Statement

ADR-0005 split discovery (raw intake the team *receives*) from RFCs (investigations the team *produces*), and `docs/02-architecture.md` constrains the repo to "Markdown only — no proprietary doc formats." In practice, stakeholder material arrives as PDFs, JSON exports, spreadsheets, and decks — not markdown. Today there is no path for that material: `promote-discovery` only flips existing markdown notes from `status: raw` to `promoted`, and `init`/`adopt` never scaffold the discovery subfolders, so adopters who drop a PDF into `docs/discovery/` and run `/promote-discovery` are correctly told there are zero raw markdown items. The missing piece is a **capture** stage — the act of turning received source material into a markdown discovery note — and a place to put the raw originals without violating the markdown-only constraint or bloating version control with binaries.

## Decision Drivers

- **Markdown-only-in-VCS must hold.** Binaries (PDFs, JSON, decks) should never enter git history; the constraint is about what is *committed*, not what sits on a contributor's disk.
- **Capture and promote are distinct lifecycle stages.** Capture: received source → tracked markdown note. Promote: `status: raw` note → synthesized PRD/ADR. Conflating them (e.g. "drop a PDF and it auto-promotes") muddies an auditable trail.
- **Scaffolding must actually create the folders.** Git does not track empty directories; the kit uses no `.gitkeep` today, so the documented `meetings/ requirements/ use-cases/ notes/` subfolders never materialize on adoption.
- **One source of truth per behavior (ADR-0007/0008).** The capture command is a stdlib-only Python script (deterministic scaffolding) plus an AI surface (the agent reads the source and synthesizes prose), with a `--check` hook mode that nudges but never writes.
- **No naming collisions in a kit others adopt.** The synthesized-output folder must not reuse the word `promoted`, which already names a frontmatter `status:` value.

## Considered Options

- **Option A — Capture stage with gitignored intake + tracked `captured/` (chosen).** Scaffold `meetings/ requirements/ use-cases/ notes/` (gitignored contents, tracked folders via `.gitkeep`) plus a tracked `captured/` folder. A new `/capture-discovery` command synthesizes intake into markdown notes in `captured/`; the existing `/promote-discovery` then promotes those.
- **Option B — Allow binary attachments in git** alongside an index note (the RFC `artifacts/` pattern). Faithful provenance, but commits binaries and breaks the markdown-only constraint.
- **Option C — Improve the error message only** — tell the user to hand-author markdown first. Zero new capability; leaves the actual gap (received non-markdown material) unsolved.

## Decision Outcome

Chosen option: **Option A**, because it preserves markdown-only-in-VCS, keeps capture and promote as separate auditable stages, and fixes the scaffolding gap — while the gitignore idiom keeps raw originals local. The synthesized-output folder is named `captured/` (not `promoted/`) to avoid colliding with the `status: promoted` frontmatter value.

### Consequences

- **Good:** Adopters can drop any source material into an intake subfolder and run one command (`/capture-discovery`) to land synthesized, tracked markdown notes that flow through the existing promote lifecycle.
- **Good:** The "markdown only" constraint becomes precise — *markdown only in version control* — and is enforced by a scaffolded `docs/discovery/.gitignore` rather than convention alone.
- **Good:** Intake subfolders finally exist after adoption (tracked via `.gitkeep`, contents ignored), so the README's documented structure is real.
- **Bad:** Raw source originals are not version-controlled, so provenance beyond the note's `source:` field is a local-only artifact; contributors must share originals out of band if needed.
- **Neutral:** Two discovery axes now coexist — folder location (`captured/` vs intake) and frontmatter `status:` (raw → promoted). The README and STANDARDS docs must keep both legible.

## More Information

- Extends: [0005](./0005-split-discovery-and-rfcs.md) — the discovery/RFC split this builds the capture stage onto.
- Related ADRs: [0007](./0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md) (scripts are dumb/deterministic + stdlib-only; the agent does the synthesis), [0008](./0008-hooks-invoke-script-in-check-mode-behavior-writes-via-slash-command.md) (`--check` hook mode + slash-command writes — the shape `capture-discovery` follows).
- Discovery conventions: `docs/discovery/README.md`, `docs/STANDARDS.md` § "Discovery".
- Information flow: `docs/discovery/{intake}` (local) → `docs/discovery/captured/` → `docs/decisions/` / numbered docs.
