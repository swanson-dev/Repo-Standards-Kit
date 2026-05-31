# Slice 4 Plan 3 — Skills Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the kit's AI-skill surface consistent and drift-proof — add a `/standards-check` skill, polish the four existing wrappers, add SKILL.md⟺prompt.md parity + skills-index-drift guards, skill templates, and an end-of-session tie-in — shipped as v0.9.0.

**Architecture:** Build the consistent state FIRST (new skill with both halves → AGENTS.md index listing all five skills → polished wrappers → templates), THEN extend the already-wired `checks/skills.py` with the parity + index guards LAST, so when the error-severity guards go live the kit already satisfies them. The checker's own tests use temp fixtures (red→green independent of kit state).

**Tech Stack:** Python 3.9+ stdlib only (`re`, `pathlib`, `unittest`); Markdown for skills/templates/docs. Tests run via `python tools/run_tests.py`. Reference spec: `docs/superpowers/specs/2026-05-31-slice-4-plan-3-skills-surface-design.md`.

**Conventions:**
- `from __future__ import annotations` first code line of any modified Python module/test.
- Run the skills suite: `python scripts/standards-check/test_skills.py -v`. Run everything: `python tools/run_tests.py`. Run the kit check: `python scripts/standards-check/check.py`. Coherence: `python tools/check_version_coherence.py`.
- The four existing skills already have both halves: `.claude/skills/<n>/SKILL.md` + `.github/prompts/<n>.prompt.md` for `new-adr`, `new-rfc`, `update-handoff`, `promote-discovery`.

---

### Task 1: New `/standards-check` skill (both halves)

**Files:**
- Create: `.claude/skills/standards-check/SKILL.md`
- Create: `.github/prompts/standards-check.prompt.md`

- [ ] **Step 1: Create the Claude skill**

Create `.claude/skills/standards-check/SKILL.md`:

```markdown
---
name: standards-check
description: Run the repo's standards checks and fix any findings before pushing or ending a session.
---

# standards-check

## When to invoke

Run before you finish a session that touched docs, before you push, or when CI's
"Structural lint" job is red. This satisfies the `AGENTS.md` end-of-session contract
item "Run `/standards-check` … before ending a session that touched docs."

## How to invoke

Run from the repo root:

`python scripts/standards-check/check.py`

Exit `1` with `ERROR` lines means there is work to fix. `WARN` lines are advisory and
do not fail CI. The output lists each finding as `[<check_id>] <file>:<line> <message>`.

## After running — how to fix, by check_id

- **`links`** — the relative link or `#anchor` doesn't resolve. Correct the path
  (relative to the linking file) or fix the fragment to match the target heading slug.
- **`placeholder`** — a committed ADR/RFC still has template scaffolding. Fill the
  `<…>`, `YYYY-MM-DD`, or `NNNN`.
- **`changelog`** — `CHANGELOG.md` has no `## [x.y.z]` version section; add one.
- **`discovery`** — a `status: promoted` item's `promoted_to:` path is missing or wrong.
- **`skill-format`** — a skill is missing frontmatter, its `.github/prompts/<n>.prompt.md`
  twin, or an entry in the `AGENTS.md` `## Available skills` index. Add the missing piece.
- **`structural`** — a core file is missing, a profile/waiver is unset, or an ADR/RFC
  filename/status is invalid. Add the file or a `**Waived:**` reason in `docs/STANDARDS-CHECKLIST.md`.
- **`ai` freshness (WARN)** — `ai/handoff.md`/`current-state.md` is stale. Run `/update-handoff`.

Re-run until `0 error(s)`. (Kit maintainers: version coherence is a separate kit-only
guard, `tools/check_version_coherence.py`, not covered by this skill.)
```

- [ ] **Step 2: Create the Copilot twin**

Create `.github/prompts/standards-check.prompt.md`:

```markdown
---
mode: agent
description: Run the repo's standards checks and fix any findings before pushing or ending a session.
---

# standards-check

When finishing a session that touched docs, before pushing, or when CI's structural
lint is red, run this from the repo root:

`python scripts/standards-check/check.py`

Exit `1` with `ERROR` lines means there is work to fix; `WARN` lines are advisory.
Each finding is `[<check_id>] <file>:<line> <message>`.

Fix by check_id: `links` → correct the relative path / `#anchor`; `placeholder` → fill
`<…>`/`YYYY-MM-DD`/`NNNN` in the committed ADR/RFC; `changelog` → add a `## [x.y.z]`
section; `discovery` → fix the `promoted_to:` path; `skill-format` → add the missing
frontmatter / `.github/prompts/<n>.prompt.md` twin / `AGENTS.md` index entry;
`structural` → add the missing file or a `**Waived:**` reason; `ai` freshness → run
the update-handoff prompt. Re-run until `0 error(s)`.
```

- [ ] **Step 3: Verify the new SKILL.md passes the existing format check**

Run: `python scripts/standards-check/check.py`
Expected: still `0 error(s)` — the new SKILL.md has `name: standards-check` (matches its dir) and a description, so the existing skill-format check is satisfied. (The parity/index guards don't exist yet — they arrive in Task 5.)

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/standards-check/SKILL.md .github/prompts/standards-check.prompt.md
git commit -m "feat(slice-4): add /standards-check skill (Claude + Copilot)"
```

---

### Task 2: Skill templates

**Files:**
- Create: `docs/templates/skill-template.md`
- Create: `docs/templates/skill-prompt-template.md`
- Modify: `docs/templates/README.md`

- [ ] **Step 1: Create the SKILL.md template**

Create `docs/templates/skill-template.md`:

```markdown
<!--
Skill template (Claude). Copy to .claude/skills/<name>/SKILL.md.
`name` MUST equal the directory name (kebab-case). Pair it with a Copilot twin at
.github/prompts/<name>.prompt.md (see skill-prompt-template.md) and add a row to the
AGENTS.md `## Available skills` index.
-->
---
name: <skill-name>
description: <one line — what it does and when to reach for it>
---

# <skill-name>

## When to invoke

<The trigger. If it satisfies an AGENTS.md end-of-session contract item, name it.>

## How to invoke

Run from the repo root:

`python scripts/<path-to-script>.py <args>`

<What the script does / prints.>

## After

<What the agent does with the result — fill fields, paste an index row, re-run, etc.>
```

- [ ] **Step 2: Create the prompt.md template**

Create `docs/templates/skill-prompt-template.md`:

```markdown
<!--
Skill template (Copilot). Copy to .github/prompts/<name>.prompt.md. Keep it in sync
with the Claude twin at .claude/skills/<name>/SKILL.md — same guidance, different header.
-->
---
mode: agent
description: <one line — same as the SKILL.md twin>
---

# <skill-name>

<When to reach for it.> Run from the repo root:

`python scripts/<path-to-script>.py <args>`

<What the script does, and what to do with the result.>
```

- [ ] **Step 3: List the new templates in the templates README**

Read `docs/templates/README.md`, then add the two new templates to its list of templates, matching the existing entry style (e.g. a bullet or table row per template). Add entries for:
- `skill-template.md` — Claude `SKILL.md` skeleton.
- `skill-prompt-template.md` — Copilot `.prompt.md` skeleton.

- [ ] **Step 4: Verify no new check errors**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)`. (Templates live under `docs/templates/`, which the skill checks never scan; the `<…>` placeholders in them are not linted because the placeholder check only scans `docs/decisions/` ADRs and `docs/rfcs/` RFCs.)

- [ ] **Step 5: Commit**

```bash
git add docs/templates/skill-template.md docs/templates/skill-prompt-template.md docs/templates/README.md
git commit -m "feat(slice-4): add SKILL.md + prompt.md templates"
```

---

### Task 3: AGENTS.md — index, contract tie-in, authoring line, refresh note

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Add the `## Available skills` index in the adopter-owned region**

In `AGENTS.md`, immediately AFTER the `<!-- END kit-managed: agents-core -->` line and BEFORE `## About this repository`, insert this section (the lint parses the backtick names in the first column):

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

- [ ] **Step 2: Add the end-of-session checkbox (inside the managed block)**

In the `## End-of-session contract` list (inside the `kit-managed: agents-core` block), add this as the FINAL checkbox (after the `docs/discovery/` line):

```markdown
- [ ] Run `/standards-check` (or `python scripts/standards-check/check.py`) and fix any findings before ending a session that touched docs.
```

- [ ] **Step 3: Add the Skills authoring line (inside the managed block)**

In the `## How to author each artifact type` list, add this bullet after the `Discovery items:` bullet:

```markdown
- **Skills:** `docs/templates/skill-template.md` (Claude) + `docs/templates/skill-prompt-template.md` (Copilot). Name must equal the skill's directory; add a row to the `## Available skills` index.
```

- [ ] **Step 4: Refresh the stale queued-slices note (adopter-owned region)**

The `### What's out of scope right now (queued slices)` block still lists Slice 4 as out of scope, but Slice 4 is now shipping. Replace its body with:

```markdown
- **Slice 4 (delivered):** Deeper CI enforcement — content/link/placeholder linting, SKILL.md format + parity + index guards, version-coherence, discovery checks.

Genuinely-future work (open an RFC or `ai/open-questions.md` entry before starting): external-link liveness, richer doc-freshness reporting, a `new-skill` scaffolder.
```

- [ ] **Step 5: Verify checks still pass**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)`. (The new section adds no broken links; the index/parity guards aren't live yet.)

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md
git commit -m "feat(slice-4): AGENTS.md skills index + /standards-check contract tie-in"
```

---

### Task 4: Polish the four existing wrappers to one shape

**Files:**
- Modify: `.claude/skills/new-adr/SKILL.md`, `.claude/skills/new-rfc/SKILL.md`, `.claude/skills/update-handoff/SKILL.md`, `.claude/skills/promote-discovery/SKILL.md`
- Modify: `.github/prompts/new-adr.prompt.md`, `.github/prompts/new-rfc.prompt.md`, `.github/prompts/update-handoff.prompt.md`, `.github/prompts/promote-discovery.prompt.md`

- [ ] **Step 1: Read all eight files**

Read each of the eight files above to see its current content and the exact command each wraps. Do NOT change any command, path, or behavioral guidance — this is a consistency pass only.

- [ ] **Step 2: Conform each SKILL.md to the canonical shape**

Each `.claude/skills/<n>/SKILL.md` must have, in this order: the `---\nname: <n>\ndescription: …\n---` frontmatter, then `# <n>`, then three sections with these exact headings: `## When to invoke`, `## How to invoke`, `## After`. Use `new-adr/SKILL.md` as the reference shape (it already follows it). For each file:
- Keep the existing `name`/`description` and the actual command/guidance verbatim.
- Reorganize the prose under the three canonical headings if it isn't already.
- In `## When to invoke`, name the specific `AGENTS.md` end-of-session contract checkbox the skill satisfies (e.g. update-handoff → "Write `ai/handoff.md` for the next session"; promote-discovery → "If you used content from `docs/discovery/`, flip its `status`…"; new-adr → "If you made a material technical decision, write an ADR"; new-rfc → "If you ran a time-boxed investigation, write or conclude an RFC").

- [ ] **Step 3: Sync each prompt.md twin**

Each `.github/prompts/<n>.prompt.md` keeps its `---\nmode: agent\ndescription: …\n---` frontmatter (the `description` must match its SKILL.md twin exactly), then `# <n>`, then the same guidance as the SKILL.md in prose form (the prompt.md may be more compact but must not contradict the SKILL.md). Ensure the `description` strings match between each pair.

- [ ] **Step 4: Verify format + (still-passing) checks**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)`. Run: `python tools/run_tests.py` → all suites still pass (no test changes yet).

- [ ] **Step 5: Commit**

```bash
git add .claude/skills .github/prompts
git commit -m "docs(slice-4): polish the four skill wrappers to one shape"
```

---

### Task 5: Extend `checks/skills.py` with parity + index-drift guards (TDD)

**Files:**
- Modify: `scripts/standards-check/checks/skills.py`
- Modify (replace): `scripts/standards-check/test_skills.py`

NOTE: `skills.run` is already in `check.py`'s `CHECKS`; no orchestrator change is needed. The four existing skills + the new `standards-check` skill all have both halves (Tasks 1–4) and are all in the AGENTS.md index (Task 3), so the kit will satisfy the new guards.

- [ ] **Step 1: Replace `test_skills.py` with the extended suite (the failing test)**

Replace the ENTIRE contents of `scripts/standards-check/test_skills.py` with:

```python
"""Tests for the skill-hygiene checks: format, parity, and index-drift."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.skills import run  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


def _write_skill(root: Path, name: str, frontmatter: str = None, prompt: bool = True) -> None:
    fm = frontmatter if frontmatter is not None else f"name: {name}\ndescription: does {name}"
    sk = root / ".claude" / "skills" / name / "SKILL.md"
    sk.parent.mkdir(parents=True, exist_ok=True)
    sk.write_text(f"---\n{fm}\n---\n\n# {name}\n", encoding="utf-8")
    if prompt:
        pr = root / ".github" / "prompts" / f"{name}.prompt.md"
        pr.parent.mkdir(parents=True, exist_ok=True)
        pr.write_text(f"---\nmode: agent\ndescription: does {name}\n---\n\n# {name}\n", encoding="utf-8")


def _write_orphan_prompt(root: Path, name: str) -> None:
    pr = root / ".github" / "prompts" / f"{name}.prompt.md"
    pr.parent.mkdir(parents=True, exist_ok=True)
    pr.write_text(f"---\nmode: agent\ndescription: x\n---\n\n# {name}\n", encoding="utf-8")


def _write_index(root: Path, names) -> None:
    rows = "\n".join(f"| `{n}` | use {n} |" for n in names)
    (root / "AGENTS.md").write_text(
        f"# AGENTS.md\n\n## Available skills\n\n| Skill | When to use |\n|---|---|\n{rows}\n",
        encoding="utf-8",
    )


class FormatTests(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr"])
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_description_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", frontmatter="name: new-adr")
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root)) if "description" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")

    def test_name_mismatch_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", frontmatter="name: make-adr\ndescription: x")
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root)) if "!= dir" in f.message]
            self.assertEqual(len(findings), 1)

    def test_missing_name_in_adopter_is_warn(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", frontmatter="description: x")
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root, adopter=True)) if "`name`" in f.message]
            self.assertEqual(findings[0].severity, "warn")

    def test_no_skills_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(Path(d), _ctx(Path(d))), [])


class ParityTests(unittest.TestCase):
    def test_skill_without_prompt_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", prompt=False)
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root)) if "no matching .github/prompts" in f.message]
            self.assertEqual(len(findings), 1)

    def test_prompt_without_skill_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")            # valid pair + indexed
            _write_index(root, ["new-adr"])
            _write_orphan_prompt(root, "ghost")      # prompt with no skill dir
            findings = [f for f in run(root, _ctx(root)) if "no matching .claude/skills" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertIn("ghost", findings[0].message)


class IndexTests(unittest.TestCase):
    def test_skill_missing_from_index_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, [])  # section present but empty
            findings = [f for f in run(root, _ctx(root)) if "not listed" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertIn("new-adr", findings[0].message)

    def test_orphan_index_entry_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr", "ghost"])
            findings = [f for f in run(root, _ctx(root)) if "no such skill exists" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertIn("ghost", findings[0].message)

    def test_no_available_skills_section_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")  # no AGENTS.md written at all
            findings = [f for f in run(root, _ctx(root)) if "no `## Available skills`" in f.message]
            self.assertEqual(len(findings), 1)

    def test_index_severity_warn_in_adopter(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, [])
            findings = [f for f in run(root, _ctx(root, adopter=True)) if "not listed" in f.message]
            self.assertEqual(findings[0].severity, "warn")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python scripts/standards-check/test_skills.py -v`
Expected: the parity + index tests FAIL with `AssertionError` (the current `skills.py` only checks format — parity/index findings don't exist yet). The format tests still pass.

- [ ] **Step 3: Replace `checks/skills.py` with the extended checker**

Replace the ENTIRE contents of `scripts/standards-check/checks/skills.py` with:

```python
"""Skill-hygiene checks: SKILL.md frontmatter format, SKILL.md<->prompt.md parity,
and skills-index drift (the AGENTS.md `## Available skills` table).

All findings share check_id "skill-format" so adopters have one override knob.
Error in the kit, warn in adopters (resolve_severity).
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "skill-format"
DEFAULT_SEVERITY = "error"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_INDEX_HEADING_RE = re.compile(r"(?m)^##\s+Available skills\s*$")
_INDEX_ROW_RE = re.compile(r"(?m)^\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|")
_PROMPT_SUFFIX = ".prompt.md"


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm


def _skill_dirs(root: Path) -> list:
    base = root / ".claude" / "skills"
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if (p / "SKILL.md").is_file())


def _index_names(root: Path):
    """Skill names in the AGENTS.md `## Available skills` table, or None if the
    file or section is absent."""
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return None
    text = agents.read_text(encoding="utf-8", errors="replace")
    m = _INDEX_HEADING_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    section = rest[: nxt.start()] if nxt else rest
    return {row.group(1) for row in _INDEX_ROW_RE.finditer(section)}


def _check_format(root: Path, severity: str) -> list:
    findings = []
    for skill_md in sorted((root / ".claude" / "skills").glob("*/SKILL.md")):
        rel = skill_md.relative_to(root).as_posix()
        dir_name = skill_md.parent.name
        fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: missing frontmatter `name`"))
        elif name != dir_name:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: name '{name}' != dir '{dir_name}'"))
        if not desc:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: missing frontmatter `description`"))
    return findings


def _check_parity(root: Path, skill_dirs: list, severity: str) -> list:
    findings = []
    prompts_dir = root / ".github" / "prompts"
    for name in skill_dirs:
        if not (prompts_dir / f"{name}{_PROMPT_SUFFIX}").is_file():
            findings.append(Finding(
                CHECK_ID, severity,
                f".claude/skills/{name}/SKILL.md has no matching .github/prompts/{name}{_PROMPT_SUFFIX}",
            ))
    if prompts_dir.is_dir():
        skill_set = set(skill_dirs)
        for prompt in sorted(prompts_dir.glob("*" + _PROMPT_SUFFIX)):
            name = prompt.name[: -len(_PROMPT_SUFFIX)]
            if name not in skill_set:
                findings.append(Finding(
                    CHECK_ID, severity,
                    f".github/prompts/{name}{_PROMPT_SUFFIX} has no matching .claude/skills/{name}/SKILL.md",
                ))
    return findings


def _check_index(root: Path, skill_dirs: list, severity: str) -> list:
    index = _index_names(root)
    if index is None:
        return [Finding(
            CHECK_ID, severity,
            "AGENTS.md: no `## Available skills` section (skills must be discoverable)",
        )]
    findings = []
    for name in skill_dirs:
        if name not in index:
            findings.append(Finding(
                CHECK_ID, severity,
                f"skill '{name}' is not listed in the AGENTS.md `## Available skills` index",
            ))
    for name in sorted(index - set(skill_dirs)):
        findings.append(Finding(
            CHECK_ID, severity,
            f"AGENTS.md `## Available skills` lists '{name}' but no such skill exists",
        ))
    return findings


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    skill_dirs = _skill_dirs(root)
    if not skill_dirs:
        return []  # no skills → nothing to lint
    findings = []
    findings += _check_format(root, severity)
    findings += _check_parity(root, skill_dirs, severity)
    findings += _check_index(root, skill_dirs, severity)
    return findings
```

- [ ] **Step 4: Run to verify the suite passes**

Run: `python scripts/standards-check/test_skills.py -v`
Expected: PASS (all format + parity + index tests). Fix `skills.py` until green (do NOT change the tests).

- [ ] **Step 5: Run the kit check — the guards are now live against the kit**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)`. The kit has five skills, each with a SKILL.md + prompt.md (Tasks 1, 4) and all five in the AGENTS.md index (Task 3), so parity and index hold. If anything is flagged, fix it at the source (add the missing prompt.md, or add/correct the index row) — do NOT weaken the check.

- [ ] **Step 6: Run the full suite**

Run: `python tools/run_tests.py`
Expected: all suites pass.

- [ ] **Step 7: Commit**

```bash
git add scripts/standards-check/checks/skills.py scripts/standards-check/test_skills.py
git commit -m "feat(slice-4): add SKILL.md<->prompt.md parity + skills-index guards"
```

---

### Task 6: Docs + version bump to v0.9.0 (coherence-verified)

**Files:**
- Modify: `docs/STANDARDS.md`, `src/standards/__about__.py`, `CHANGELOG.md`, `AGENTS.md`

- [ ] **Step 1: Document the new guards in `docs/STANDARDS.md`**

In the "Content checks (v2)" section, update the existing **Skill format** bullet to describe all three skill-hygiene checks. Replace the current skill bullet with:

```markdown
- **Skill format / parity / index** — every `.claude/skills/<n>/SKILL.md` needs frontmatter `name` (matching its directory) and `description`, a matching `.github/prompts/<n>.prompt.md` twin, and a row in the `AGENTS.md` `## Available skills` index. (Adopters: these default to warnings, escalatable via the `skill-format` key.)
```

- [ ] **Step 2: Bump the source of truth**

Edit `src/standards/__about__.py`: `__version__ = "0.8.0"` → `__version__ = "0.9.0"`.

- [ ] **Step 3: Add the CHANGELOG entry + reference link**

In `CHANGELOG.md`, add above `## [0.8.0] - 2026-05-31`:

```markdown
## [0.9.0] - 2026-05-31

### Added
- `/standards-check` skill (Claude + Copilot) — run the checks and fix findings before pushing.
- SKILL.md ⟷ prompt.md parity and skills-index-drift guards in `standards-check`.
- Canonical `docs/templates/skill-template.md` + `skill-prompt-template.md`.
- An `## Available skills` index in `AGENTS.md` and an end-of-session `/standards-check` step.

### Changed
- The four existing skill wrappers polished to one consistent shape.
```

Add the reference link at the bottom, directly above the `[0.8.0]:` line, mirroring the existing format:

```markdown
[0.9.0]: https://example.invalid/releases/tag/v0.9.0
```

- [ ] **Step 4: Bump the AGENTS.md Kit-version markers**

Run: `grep -n "0.8.0" AGENTS.md`
Change both markers inside the `kit-managed: agents-core` block: the sentinel `(v0.8.0)` → `(v0.9.0)` and the `- Kit version: **0.8.0**` line → `**0.9.0**`.

- [ ] **Step 5: Verify coherence + everything green**

Run: `python tools/check_version_coherence.py`
Expected: `Version coherence: OK` (all sites now 0.9.0 — the Plan 2 guard verifies this bump).

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)`.

Run: `python tools/run_tests.py`
Expected: all suites pass.

- [ ] **Step 6: Commit**

```bash
git add docs/STANDARDS.md src/standards/__about__.py CHANGELOG.md AGENTS.md
git commit -m "docs(slice-4): document skill guards + bump to v0.9.0"
```

---

## Self-Review

**Spec coverage:**
- §A new `/standards-check` skill (both halves, check.py-only) → Task 1 ✓
- §B polish 4 wrappers → Task 4 ✓
- §C1 parity → Task 5 ✓
- §C2 index-drift → Task 5 ✓
- §C3 tests → Task 5 ✓
- §D1 AGENTS.md index (adopter region) → Task 3 ✓
- §D2 templates + README → Task 2 ✓
- §D3 contract tie-in + authoring line → Task 3 ✓
- §D4 refresh queued-slices note → Task 3 ✓
- docs + v0.9.0 (coherence-verified) → Task 6 ✓

**Placeholder scan:** No "TBD"/"implement later". Task 4 is a judgment pass (read 8 files, conform to a shape) with the canonical shape + per-skill trigger guidance spelled out — acceptable for a docs-consistency task. All code steps show complete code.

**Type consistency:** `run(root, ctx) -> list`, `Finding(check_id, severity, message)`, `Context`, `resolve_severity` match the established framework. `check_id` is `"skill-format"` for all three skill concerns (per the spec's single-knob decision). Helper names (`_skill_dirs`, `_index_names`, `_check_format/_check_parity/_check_index`) and test helpers (`_write_skill`, `_write_orphan_prompt`, `_write_index`) are consistent between the module and its tests. The index table format (`| \`name\` | … |`) is identical in Task 3 (kit), Task 5 (test fixtures), and the parser regex.

**Build-order safety:** the error-severity guards (Task 5) land only after the kit is made consistent (Tasks 1–4), so the kit check stays green at every commit.

**Out of scope:** `new-skill` scaffolder (deferred); check-script behavior unchanged; coherence tool excluded from the shipped skill.
