# Slice 4 Plan 1 Design — `standards-check` v2: content-level checks

**Status:** Approved (brainstorming, 2026-05-30)
**Slice:** 4 (deeper CI enforcement). **Plan:** 1 of 3.
**Builds on:** Slice 3 (the kit is a vendored PyPI package; `standards init`/`update` ship `scripts/standards-check/` into adopters). `standards-check` v1 today is purely *structural*.

## Slice 4 context (the whole slice, for orientation)

Slice 4 ("deeper CI enforcement") decomposes into three sequential plans, each brainstormed + spec'd when its turn comes (the Slice 3 rhythm):

- **Plan 1 (this spec) — `standards-check` v2: content-level checks** (shipped to adopters): internal link checking, placeholder/content lint, skill-format lint.
- **Plan 2 — Guardrails:** version-coherence lint (kit-only CI + `release.yml` gate), AI-freshness teeth (tighter thresholds + stronger Stop-hook nudge), discovery hardening (verify `promoted_to:` targets exist; surface stale-`raw` items).
- **Plan 3 — Skills surface:** polish the four existing `.claude/skills/*` wrappers; add a `/standards-check` local-fix skill so an agent runs + fixes the new checks before pushing.

Only Plan 1 is designed here. Plans 2/3 are recorded so the decomposition is durable, not to scope them now.

## Goal

Extend `standards-check` from *structural* (does the file exist; is the filename/status/frontmatter valid) to *content-level* (is the file's **body** correct), via three new checks — **internal link resolution**, **placeholder/content lint**, **skill-format lint**. All three ship to every adopter and are profile-agnostic. Severity resolves to **error in the kit, warn-by-default + escalatable in adopters.**

## Decisions (from brainstorming)

1. **Decomposition:** Slice 4 = 3 plans (above). Design Plan 1 now; defer 2/3.
2. **Severity model:** new content checks are **errors** when run in the kit itself, **warnings** in adopting repos by default, escalatable to errors per-check via the adopter's marker. v1 structural checks keep their current behavior unchanged.
3. **Kit-vs-adopter detection:** presence of `.standards-kit.json` at the repo root. The kit's own repo has no marker (only `standards init` writes one), so "no marker" = kit mode = strictest. No new config file or env var.
4. **Module split:** break `scripts/standards-check/check.py` into a `checks/` package (orchestrator + one module per check group). Accepted cost: the payload manifest + `init`/`update` file list must learn the new layout.
5. **Link depth:** resolve relative file targets **and** validate `#anchor` fragments (GitHub heading-slug algorithm). Anchor validation is the part most prone to false positives — it is the first thing softened to `warn` if it proves noisy in practice.
6. **Skill targets:** `.claude/skills/*/SKILL.md`. There are no Copilot `prompt.md` counterparts in the tree; SKILL.md is the sole target. Parity checks are out of scope.
7. **SHA-pin** (supply-chain): de-selected by the user. Not in Slice 4.

## Architecture

### Module layout

```
scripts/standards-check/
  check.py            # orchestrator: find repo root, resolve severity mode,
                      # run every check, aggregate, print, exit 1 iff any error
  checks/
    __init__.py       # exports the check registry / shared types
    structural.py     # the existing v1 checks, moved verbatim (no behavior change)
    links.py          # internal link + anchor resolution
    content.py        # placeholder lint + CHANGELOG shape
    skills.py         # .claude/skills/*/SKILL.md frontmatter + structure
  test_check.py       # existing; stays (orchestrator-level)
  test_links.py       # new
  test_content.py     # new
  test_skills.py      # new
```

`check.py` keeps `find_repo_root`, `build_context`, the `main()` entry, and orchestration, and **re-exports `parse_frontmatter`** (`from checks.structural import parse_frontmatter`) so the unchanged `test_check.py` stays green. Each `checks/*.py` module exposes a single `run(root, ctx) -> list[Finding]` so the orchestrator can call them uniformly. `structural.py` is the v1 logic relocated unchanged — pure move, asserted by the unchanged `test_check.py`.

### Shared types

```python
# checks/__init__.py
Severity = Literal["error", "warn"]

@dataclass(frozen=True)
class Finding:
    check_id: str          # e.g. "links", "placeholder", "skill-format"
    severity: Severity     # resolved severity for this finding
    message: str

@dataclass
class Context:
    root: Path
    adopter_mode: bool                 # True iff .standards-kit.json present
    overrides: dict[str, Severity]     # check_id -> escalated severity (adopters)
```

### Severity resolution

- The orchestrator builds `Context` once: `adopter_mode = (root / ".standards-kit.json").exists()`; `overrides` parsed from the marker's optional `"check"` object (absent/garbled → `{}`, never fatal).
- Each new check has a **default severity** (`error`). Resolution:
  - kit mode (`not adopter_mode`) → use the default (`error`).
  - adopter mode → `warn`, unless `overrides[check_id] == "error"`.
- v1 structural findings keep their **current** severities (most are `error`; the AI-freshness staleness findings are already `warn`). They do **not** pass through the new kit/adopter softening — only the three new content checks do.
- Exit code: `1` iff any `Finding.severity == "error"`, else `0`. Warnings print but never fail. (Unchanged contract: warnings are advisory.)

### Marker shape (adopter-side escalation)

```jsonc
// .standards-kit.json (adopter; optional new field)
{
  "kit_version": "…", "profile": "…", "adopted": "…",
  "tracked": { /* … */ }, "managed": { /* … */ },
  "check": { "links": "error", "placeholder": "error" }   // optional; default warn
}
```
Reading this is additive and tolerant — a missing `"check"` key (every adopter today) means all-warn. Writing/managing it is **not** in Plan 1 (adopters hand-edit, or a later plan adds a CLI). Plan 1 only *reads* it.

## The three checks

### A · `links` — internal link + anchor resolution (`checks/links.py`)

- **Discovery:** every committed `*.md` under the repo (reuse the repo-walk; honor the same exclusions the other checks use — skip `.git/`, and for the kit, `src/standards/_payload` duplicates are the same files via force-include, so walk the source tree once).
- **Parse:** inline links `[text](target)` and reference definitions `[id]: target`. Ignore links inside fenced/indented code blocks and inside `<!-- -->` comments.
- **Classify target:**
  - External scheme (`http:`, `https:`, `mailto:`, `tel:`, `//`) → skip (out of scope; external link liveness is not Plan 1).
  - Pure fragment (`#anchor`) → resolve against the *same* file's headings.
  - Relative path (optionally with `#anchor`) → resolve the path against the linking file's directory; the file must exist. If a fragment is present, resolve it against the *target* file's headings.
- **Anchor resolution:** compute GitHub heading slugs (lowercase; strip non-word/non-space/non-hyphen; spaces → `-`; collapse repeats; de-duplicate with `-1`, `-2` suffixes). A fragment matches if it equals a computed slug. Unmatched anchor → `links` finding (the candidate to soften to `warn` first if noisy).
- **Finding:** `links` — `"<file>:<line> broken link -> <target> (<reason: missing file | missing anchor>)"`.

### B · `content` — placeholder lint + CHANGELOG shape (`checks/content.py`)

- **Placeholder lint — targets:** committed ADRs (`docs/decisions/NNNN-*.md`, excluding `README.md`/`template.md`) and RFCs (`docs/rfcs/NNNN-*/rfc.md`). These are the docs that are *authored from templates* and must not retain template scaffolding.
- **Rule:** strip `<!-- … -->` comment blocks first (template guidance comments are allowed to remain or be deleted — they are not the signal). In the remaining body, flag:
  - angle-bracket placeholder tokens — `<…>` spans whose content is placeholder-like (letters/spaces/em-dash/commas, e.g. `<name>`, `<Driver 1>`, `<Option X>`, `<Title — …>`). Conservative pattern to avoid matching legitimate inline HTML or generics; tuned against the real templates.
  - literal `YYYY-MM-DD` (the template date placeholder) and bare standalone `NNNN`.
- **CHANGELOG shape:** `CHANGELOG.md` parses as Keep-a-Changelog — at least one version section heading (`## [x.y.z]` or `## [Unreleased]`). Light; a single finding if the file is present but has no recognizable version section.
- **Finding:** `placeholder` — `"<file>:<line> unfilled template placeholder: <token>"`; `changelog` — `"CHANGELOG.md: no Keep-a-Changelog version section found"`.

### C · `skill-format` — SKILL.md frontmatter + structure (`checks/skills.py`)

- **Targets:** `.claude/skills/*/SKILL.md`.
- **Rule:** each has YAML frontmatter with a non-empty `name` and a non-empty `description`; `name` equals the containing directory name (kebab-case). (Mirrors the skill-authoring contract this kit dogfoods.)
- **Finding:** `skill-format` — `"<path>: <missing name | missing description | name 'x' != dir 'y'>"`.

## Testing strategy

- **TDD, per check.** New `test_links.py`, `test_content.py`, `test_skills.py`, each with good/bad fixtures in a `tmp` tree and assertions on `Finding` content + severity-by-mode (kit → error, adopter-no-override → warn, adopter-with-override → error).
- **`test_check.py` stays green unchanged** — proving `structural.py` is a behavior-preserving move and the orchestrator still wires v1 checks identically.
- **Runner:** all suites run under `python tools/run_tests.py` (discovery already globs `scripts/**/test_*.py`). New basenames are unique → no collision.
- **Dogfooding consequence (in scope for Plan 1):** running the new checks at **error** severity against the kit will surface the kit's own pre-existing violations (most likely some stale relative links and possibly residual `YYYY-MM-DD`/`<…>` in older docs). **Fixing those is part of Plan 1** — the kit must pass its own new checks (`0 errors`) before the plan is done. This is the proof the checks work.

## Components & files

| Path | Action | Responsibility |
|---|---|---|
| `scripts/standards-check/check.py` | modify | Orchestrator: root, `Context`, run registry, aggregate, exit. |
| `scripts/standards-check/checks/__init__.py` | new | `Severity`/`Finding`/`Context` types + check registry. |
| `scripts/standards-check/checks/structural.py` | new (move) | v1 checks relocated verbatim. |
| `scripts/standards-check/checks/links.py` | new | Internal link + anchor resolution. |
| `scripts/standards-check/checks/content.py` | new | Placeholder + CHANGELOG-shape lint. |
| `scripts/standards-check/checks/skills.py` | new | SKILL.md frontmatter + structure. |
| `scripts/standards-check/test_{links,content,skills}.py` | new | Per-check TDD suites. |
| `src/standards/manifest.py` | **verify (no change)** | `PAYLOAD_DIRS` already includes `"scripts"` wholesale, so `iter_payload` ships `scripts/standards-check/checks/` to adopters automatically. A test asserts this rather than editing the manifest. |
| kit docs with broken links / residual placeholders | fix | Whatever the new checks surface at error severity. |
| `docs/STANDARDS.md` | modify | Document the v2 checks + the adopter severity-override marker field. |
| `CHANGELOG.md` | modify | New entry (version bump — see below). |
| `AGENTS.md` Kit-version managed block | modify | Bump to match. |

## Out of scope (later plans / dropped)

- Version-coherence lint, AI-freshness teeth, discovery hardening → **Plan 2**.
- Polishing the 4 skill wrappers, the `/standards-check` local-fix skill → **Plan 3**.
- External (HTTP) link liveness — Plan 1 does internal links only.
- A CLI to *write* the adopter `"check"` override map — Plan 1 only reads it.
- SHA-pinning `pypa/gh-action-pypi-publish` — de-selected.

## Version

Minor bump (new shipped behavior, backward-compatible for adopters since new checks default to `warn` there): **v0.7.0**. `__about__.py` + CHANGELOG top entry + `AGENTS.md` Kit-version block move together (the very invariant Plan 2's version-coherence lint will later enforce).
