# Slice 4 Plan 3 Design — Skills surface (polish, /standards-check, parity + index guards)

**Status:** Approved (brainstorming, 2026-05-31)
**Slice:** 4 (deeper CI enforcement). **Plan:** 3 of 3 (final).
**Builds on:** Plan 1 (the `checks/` package + skill-format check) and Plan 2 (version-coherence guard, managed-region maturity). Plan 3 makes the kit's *skill surface* consistent, discoverable, and drift-proof.

## Goal

Bring the kit's AI-skill surface up to the same standard as the rest of the kit: a new `/standards-check` skill that closes the "run the checks + fix before pushing" loop, the four existing wrappers polished to one shape, and two new shipped guards (SKILL.md ⟺ prompt.md parity, and skills-index drift) so the surface can't silently rot. Ships as **v0.9.0**.

## Decisions (from brainstorming)

1. **Deliverables:** new `/standards-check` skill; polish the 4 wrappers; parity check; skills index; index-drift lint; skill templates; end-of-session contract tie-in. The `new-skill` scaffolder script is **deferred** (its own future slice).
2. **`/standards-check` covers the shipped `check.py` only** — not the kit-only `tools/check_version_coherence.py` (adopters don't have it).
3. **Index lives in an `## Available skills` section in `AGENTS.md`**, placed in the **adopter-owned region** (outside the `kit-managed: agents-core` block) so adopters can list their own skills without `update` clobbering them. The kit seeds it; the lint keeps it honest.
4. **Parity + index checks extend the Plan 1 `checks/skills.py`** module, shipped, error-in-kit / warn-in-adopter via `resolve_severity`.

## § A — New `/standards-check` skill (shipped)

`.claude/skills/standards-check/SKILL.md` (`name: standards-check`, matching its dir so the existing skill-format check passes) + `.github/prompts/standards-check.prompt.md` (`mode: agent`). Content:
- **When:** before ending a session that touched docs; before pushing; when CI's "Structural lint" job is red.
- **How:** `python scripts/standards-check/check.py` (exit 1 = errors to fix; warnings are advisory).
- **How to fix, per `check_id`:** `links` → correct the relative path or `#anchor`; `placeholder` → fill the `<…>`/`YYYY-MM-DD`/`NNNN` in the committed ADR/RFC; `discovery` → fix the `promoted_to:` path; `skill-format` → add frontmatter / matching prompt.md / index entry; `structural` (core/profile/waiver/adr/rfc) → add the missing file or a `**Waived:**` reason; `ai` freshness → run `/update-handoff`.
- Explicitly notes it does **not** cover the kit-internal coherence tool.

## § B — Polish the 4 existing wrappers

`new-adr`, `new-rfc`, `update-handoff`, `promote-discovery`. Bring all four (both halves) to one shape:
- Same headings: **When to invoke** / **How to invoke** / **After**.
- Triggers cross-linked to the specific `AGENTS.md` end-of-session contract checkbox they satisfy.
- Each `SKILL.md` kept in lockstep with its `.github/prompts/<n>.prompt.md` twin (same guidance, adjusted only for the `mode: agent` frontmatter).
- Surgical edits only — **no change** to the underlying `scripts/` behavior.

## § C — Parity + index-drift guards (shipped, in `checks/skills.py`)

Extend the Plan 1 module. All findings keep `check_id = "skill-format"` (one override key for the whole skill-hygiene surface) and resolve severity the same way (error in kit, warn in adopters).

### C1. Parity
- For every `.claude/skills/<n>/SKILL.md`, require `.github/prompts/<n>.prompt.md` to exist.
- For every `.github/prompts/<n>.prompt.md`, require `.claude/skills/<n>/SKILL.md` to exist.
- Finding messages name the missing twin.

### C2. Index-drift
- Parse the `## Available skills` section of `AGENTS.md`. The index is a table; each skill is a row whose first cell is the skill name in backticks: `| \`<name>\` | <when to use> |`. The lint extracts names via a regex scoped to that section.
- Every `.claude/skills/<n>/` dir name (excluding none — all are skills) must appear in the index; every index entry must map to a real skill dir.
- If `AGENTS.md` has no `## Available skills` section at all, that is itself one finding (so the contract is discoverable).
- Missing-from-index and orphan-index-entry are separate finding messages.

### C3. Tests
Extend `scripts/standards-check/test_skills.py` (TDD): parity both directions; index missing-entry; index orphan-entry; index-section-absent; a fully-consistent fixture passes; severity-by-mode for the new findings.

## § D — Skills index + templates + contract tie-in

### D1. `AGENTS.md` `## Available skills` (adopter-owned region)
A new section placed **after** the `<!-- END kit-managed: agents-core -->` line (so it's adopter-owned), listing all five skills as the lintable table:
```markdown
## Available skills

| Skill | When to use |
|---|---|
| `new-adr` | Recording a material architecture decision |
| `new-rfc` | Starting a time-boxed investigation |
| `promote-discovery` | Marking a discovery item promoted |
| `update-handoff` | Writing the end-of-session handoff |
| `standards-check` | Running the standards checks + fixing findings before pushing |
```

### D2. Templates
`docs/templates/skill-template.md` (the canonical `SKILL.md` shape: frontmatter `name`/`description` + When/How/After) and `docs/templates/skill-prompt-template.md` (the `mode: agent` prompt.md shape). Add both to `docs/templates/README.md`. These are the one artifact type the kit didn't yet template. (They live under `docs/templates/`, so the skill-format/parity checks — which scan `.claude/skills/` and `.github/prompts/` — never lint the templates.)

### D3. End-of-session contract tie-in (managed block)
Add one checkbox to the `AGENTS.md` end-of-session contract (inside the `agents-core` managed block, so it ships to adopters):
```markdown
- [ ] Run `/standards-check` (or `python scripts/standards-check/check.py`) and fix any findings before ending a session that touched docs.
```
Also add a **Skills** line to the managed-block "How to author each artifact type" section pointing at `docs/templates/skill-template.md`.

### D4. Refresh the stale "queued slices" note
The adopter-owned "What's out of scope right now (queued slices)" note in the kit's own `AGENTS.md` still lists Slice 4 as out of scope; Slice 4 is now shipping. Update it to reflect reality (Slice 4 delivered; note any genuinely-future work).

## Components & files

| Path | Action | Responsibility |
|---|---|---|
| `.claude/skills/standards-check/SKILL.md` | new | Claude `/standards-check` skill. |
| `.github/prompts/standards-check.prompt.md` | new | Copilot twin. |
| `.claude/skills/{new-adr,new-rfc,update-handoff,promote-discovery}/SKILL.md` | modify | Polish to one shape. |
| `.github/prompts/{new-adr,new-rfc,update-handoff,promote-discovery}.prompt.md` | modify | Keep in sync with SKILL.md twins. |
| `scripts/standards-check/checks/skills.py` | modify | Add parity + index-drift checks. |
| `scripts/standards-check/test_skills.py` | modify | TDD for parity + index. |
| `AGENTS.md` | modify | `## Available skills` (adopter region); `/standards-check` checkbox + Skills authoring line (managed block); refresh queued-slices note; Kit-version → 0.9.0. |
| `docs/templates/skill-template.md` | new | Canonical SKILL.md shape. |
| `docs/templates/skill-prompt-template.md` | new | Canonical prompt.md shape. |
| `docs/templates/README.md` | modify | List the new templates. |
| `docs/STANDARDS.md` | modify | Document the parity + index checks. |
| `CHANGELOG.md` / `src/standards/__about__.py` | modify | Bump to v0.9.0 (coherence-verified by the Plan 2 guard). |

## Testing strategy

- TDD on `checks/skills.py` (parity both directions, index drift both directions, index-absent, severity-by-mode) in `test_skills.py`.
- Dogfood: the new parity + index checks run at **error** severity against the kit, so the kit must — as part of Plan 3 — have all five skills paired (SKILL.md + prompt.md) and all five listed in the `AGENTS.md` index, or `python scripts/standards-check/check.py` fails. Getting the kit to `0 errors` is the proof.
- `python tools/check_version_coherence.py` → OK at 0.9.0 (the Plan 2 guard self-verifies this bump).
- `python tools/run_tests.py` → all suites green on the CI matrix.

## Out of scope (later / dropped)

- The `new-skill` scaffolder script (`scripts/new-doc/new-skill.py`) — deferred to a future slice.
- Any change to the check *scripts'* runtime behavior (`new-adr.py` etc. are untouched).
- The kit-only coherence tool in the shipped `/standards-check` skill.
- Per-sub-check override keys (`skill-parity`/`skill-index`) — all skill-hygiene findings share the `skill-format` key for simplicity.

## Version

Minor bump → **v0.9.0** (new shipped skill + new shipped checks + new templates; backward-compatible for adopters since the new checks default to `warn` there).
