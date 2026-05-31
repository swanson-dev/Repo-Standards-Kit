# standards-check v2 (content-level checks) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `standards-check` from structural to content-level — internal link+anchor resolution, placeholder/CHANGELOG lint, and SKILL.md format lint — shipped to adopters with error-in-kit / warn-default-in-adopters severity.

**Architecture:** Split `scripts/standards-check/check.py` into a `checks/` package: a thin orchestrator (`check.py`) that resolves a kit-vs-adopter `Context` and runs each `checks/*.py` module's `run(root, ctx) -> list[Finding]`. The existing v1 logic moves verbatim into `checks/structural.py`; three new modules (`links`, `content`, `skills`) add body-level checks. Severity for the new checks resolves to `error` in the kit (no `.standards-kit.json`) and `warn` in adopters (escalatable via the marker's `"check"` map).

**Tech Stack:** Python 3.9+ stdlib only (`re`, `json`, `dataclasses`, `pathlib`, `unittest`). No third-party deps. Tests run via `python tools/run_tests.py`. Reference spec: `docs/superpowers/specs/2026-05-30-slice-4-plan-1-content-checks-design.md`.

**Conventions for every task below:**
- `from __future__ import annotations` is the **first code line** of every new module and test (the CI matrix runs Python 3.9; PEP 604/585 annotations fail at def-time without it).
- Run a single test file with: `python scripts/standards-check/test_<name>.py -v` (each suite ends in `unittest.main()` and inserts its own dir on `sys.path`).
- Run everything with: `python tools/run_tests.py`.
- Run the kit's own check with: `python scripts/standards-check/check.py`.

---

### Task 1: `checks/` package skeleton — shared types + severity resolution

**Files:**
- Create: `scripts/standards-check/checks/__init__.py`
- Create: `scripts/standards-check/test_severity.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_severity.py`:

```python
"""Unit tests for the checks package shared types + severity resolution."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context, Finding, resolve_severity  # noqa: E402


class ResolveSeverityTests(unittest.TestCase):
    def _ctx(self, adopter: bool, overrides=None) -> Context:
        return Context(root=Path("."), adopter_mode=adopter, overrides=overrides or {})

    def test_kit_mode_uses_default_error(self):
        sev = resolve_severity("links", "error", self._ctx(adopter=False))
        self.assertEqual(sev, "error")

    def test_adopter_mode_softens_to_warn(self):
        sev = resolve_severity("links", "error", self._ctx(adopter=True))
        self.assertEqual(sev, "warn")

    def test_adopter_override_escalates_to_error(self):
        sev = resolve_severity("links", "error", self._ctx(adopter=True, overrides={"links": "error"}))
        self.assertEqual(sev, "error")

    def test_finding_is_frozen(self):
        f = Finding(check_id="links", severity="error", message="x")
        with self.assertRaises(Exception):
            f.message = "y"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scripts/standards-check/test_severity.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'checks'`.

- [ ] **Step 3: Write the package `__init__.py`**

Create `scripts/standards-check/checks/__init__.py`:

```python
"""standards-check check modules: shared types + severity resolution.

Each check module exposes `run(root, ctx) -> list[Finding]`. The orchestrator
(check.py) builds one Context, runs every module, and exits 1 iff any error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

# "error" | "warn" — kept as plain str for 3.9 friendliness.
Severity = str


@dataclass(frozen=True)
class Finding:
    check_id: str
    severity: Severity
    message: str


@dataclass
class Context:
    """Resolved run context shared by all checks."""
    root: Path
    adopter_mode: bool                    # True iff .standards-kit.json present at root
    overrides: Dict[str, Severity] = field(default_factory=dict)


def resolve_severity(check_id: str, default: Severity, ctx: Context) -> Severity:
    """Severity for a NEW content-check finding.

    Kit mode (not adopter): the default (error). Adopter mode: warn, unless the
    adopter's marker escalates this check_id to error. v1 structural checks do
    NOT call this — they emit their fixed historical severities directly.
    """
    if not ctx.adopter_mode:
        return default
    return ctx.overrides.get(check_id, "warn")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scripts/standards-check/test_severity.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/standards-check/checks/__init__.py scripts/standards-check/test_severity.py
git commit -m "feat(slice-4): add checks package types + severity resolution"
```

---

### Task 2: Move v1 logic into `checks/structural.py`; reduce `check.py` to an orchestrator

This is a behavior-preserving refactor. The guard rails are: `test_check.py` stays green **unchanged**, and `python scripts/standards-check/check.py` still prints `0 error(s), 0 warning(s)` for the kit (no new checks wired yet).

**Files:**
- Create: `scripts/standards-check/checks/structural.py`
- Modify: `scripts/standards-check/check.py` (becomes the orchestrator)
- Unchanged: `scripts/standards-check/test_check.py` (must keep passing)

- [ ] **Step 1: Verify the baseline is green before refactoring**

Run: `python scripts/standards-check/check.py`
Expected: `Standards check: 0 error(s), 0 warning(s)`

Run: `python scripts/standards-check/test_check.py -v`
Expected: PASS (5 tests).

- [ ] **Step 2: Create `checks/structural.py` with the v1 logic moved verbatim**

Create `scripts/standards-check/checks/structural.py`. Move every constant, regex, the `Report` dataclass, `parse_frontmatter`, and the six `check_*` functions from `check.py` **unchanged**, then add a `run()` adapter that converts the `Report` into `Finding`s:

```python
"""Structural checks (standards-check v1) — relocated verbatim from check.py.

These predate the content checks and keep their historical severities: most are
errors; the ai/ staleness findings are warnings. They bypass the kit/adopter
severity softening (resolve_severity is only for the new content checks).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from . import Context, Finding

ALLOWED_PROFILES = {"application", "library", "infra", "data"}
ADR_STATUSES = {"Proposed", "Accepted", "Deprecated"}
RFC_STATUSES = {"Open", "Concluded", "Abandoned"}

ADR_FILENAME_RE = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
RFC_SLUG_RE = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SUPERSEDED_RE = re.compile(r"^Superseded by \d{4}$")

UNIVERSAL_CORE = [
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/STANDARDS.md",
    "docs/STANDARDS-CHECKLIST.md",
    "docs/00-overview.md",
    "docs/10-glossary.md",
    "docs/decisions/README.md",
    "docs/discovery/README.md",
    "docs/rfcs/README.md",
    "docs/templates/README.md",
    "ai/current-state.md",
    "ai/next-actions.md",
    "ai/open-questions.md",
    "ai/handoff.md",
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
    ".github/workflows/repo-standards.yml",
]

CURRENT_STATE_STALE_DAYS = 14
HANDOFF_STALE_DAYS = 7


@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            val = re.sub(r"\s+#.*$", "", val)
            fm[key.strip()] = val.strip()
    return fm


def check_universal_core(root: Path, report: Report) -> None:
    for rel in UNIVERSAL_CORE:
        if not (root / rel).exists():
            report.err(f"[core] Universal core file missing: {rel}")


def check_profile(root: Path, report: Report):
    checklist = root / "docs/STANDARDS-CHECKLIST.md"
    if not checklist.exists():
        return None
    text = checklist.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Profile:\*\*\s+([^\n<]+)", text)
    if not m:
        report.err("[profile] docs/STANDARDS-CHECKLIST.md does not declare a Profile field.")
        return None
    profile = m.group(1).strip().split()[0]
    if profile not in ALLOWED_PROFILES:
        report.err(
            f"[profile] Declared profile '{profile}' is not in allowed set {sorted(ALLOWED_PROFILES)}."
        )
        return None
    return profile


def check_waivers(root: Path, report: Report) -> None:
    checklist = root / "docs/STANDARDS-CHECKLIST.md"
    if not checklist.exists():
        return
    in_optional_section = False
    in_na_section = False
    for i, raw in enumerate(checklist.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if raw.startswith("#"):
            h = raw.lower()
            in_optional_section = "optional" in h
            in_na_section = ("n/a" in h) or ("not applicable" in h)
            continue
        if in_optional_section or in_na_section:
            continue
        m = re.match(r"^\s*-\s*\[\s*\]\s*(.+)$", raw)
        if not m:
            continue
        body = m.group(1).strip()
        if body.startswith("<") and body.endswith(">"):
            continue
        if "**Waived:**" not in body:
            report.err(
                f"[waiver] docs/STANDARDS-CHECKLIST.md:{i} unchecked box has no `**Waived:**` reason: {body}"
            )


def _check_date_field(path, field_name, raw, stale_days, today, report, file_label) -> None:
    if not raw:
        report.err(f"[ai] {file_label} missing `{field_name}:` frontmatter.")
        return
    date_part = raw.split("T")[0]
    try:
        parsed = date.fromisoformat(date_part)
    except ValueError:
        report.err(f"[ai] {file_label} `{field_name}:` is not a valid ISO 8601 date: {raw}")
        return
    if today - parsed > timedelta(days=stale_days):
        report.warn(f"[ai] {file_label} `{field_name}: {date_part}` is older than {stale_days} days.")


def check_ai_freshness(root: Path, report: Report) -> None:
    today = date.today()
    cs = root / "ai/current-state.md"
    if cs.exists():
        fm = parse_frontmatter(cs.read_text(encoding="utf-8", errors="replace"))
        _check_date_field(cs, "last_updated", fm.get("last_updated"), CURRENT_STATE_STALE_DAYS, today, report, "ai/current-state.md")
    ho = root / "ai/handoff.md"
    if ho.exists():
        fm = parse_frontmatter(ho.read_text(encoding="utf-8", errors="replace"))
        _check_date_field(ho, "written", fm.get("written"), HANDOFF_STALE_DAYS, today, report, "ai/handoff.md")


def check_adrs(root: Path, report: Report) -> None:
    decisions = root / "docs/decisions"
    if not decisions.exists():
        return
    for adr in sorted(decisions.glob("*.md")):
        if adr.name in {"README.md", "template.md"}:
            continue
        if not ADR_FILENAME_RE.match(adr.name):
            report.err(f"[adr] Filename does not match NNNN-kebab-case.md: docs/decisions/{adr.name}")
            continue
        fm = parse_frontmatter(adr.read_text(encoding="utf-8", errors="replace"))
        status = fm.get("status", "").strip()
        if status in ADR_STATUSES or SUPERSEDED_RE.match(status):
            continue
        report.err(f"[adr] docs/decisions/{adr.name} has invalid status: {status!r}")


def check_rfcs(root: Path, report: Report) -> None:
    rfcs = root / "docs/rfcs"
    if not rfcs.exists():
        return
    for entry in sorted(rfcs.iterdir()):
        if entry.is_file():
            continue
        if not RFC_SLUG_RE.match(entry.name):
            report.err(f"[rfc] RFC folder name does not match NNNN-kebab-case: docs/rfcs/{entry.name}")
            continue
        rfc_md = entry / "rfc.md"
        if not rfc_md.exists():
            report.err(f"[rfc] docs/rfcs/{entry.name}/ missing rfc.md")
            continue
        fm = parse_frontmatter(rfc_md.read_text(encoding="utf-8", errors="replace"))
        status = fm.get("status", "").strip()
        if status not in RFC_STATUSES:
            report.err(f"[rfc] docs/rfcs/{entry.name}/rfc.md has invalid status: {status!r}")


def run(root: Path, ctx: Context) -> list:
    """Run all v1 structural checks; return Findings at their historical severities."""
    report = Report()
    check_universal_core(root, report)
    check_profile(root, report)
    check_waivers(root, report)
    check_ai_freshness(root, report)
    check_adrs(root, report)
    check_rfcs(root, report)
    findings = [Finding("structural", "error", m) for m in report.errors]
    findings += [Finding("structural", "warn", m) for m in report.warnings]
    return findings
```

- [ ] **Step 3: Rewrite `check.py` as the orchestrator**

Replace the entire contents of `scripts/standards-check/check.py` with:

```python
#!/usr/bin/env python3
"""Standards check — runs structural (v1) + content (v2) checks.

Run from anywhere; walks up from this script to find the repo root (nearest
directory containing docs/STANDARDS.md). Exits 1 iff any error finding; warnings
are advisory and never fail the build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context, Finding  # noqa: E402
from checks import structural  # noqa: E402
# Re-exported so the unchanged test_check.py keeps importing it from `check`.
from checks.structural import parse_frontmatter  # noqa: E402,F401

CHECKS = [structural.run]


def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "docs" / "STANDARDS.md").exists():
            return parent
    raise SystemExit("Could not locate repo root (no docs/STANDARDS.md above this script).")


def build_context(root: Path) -> Context:
    """Detect adopter mode + parse the optional severity-override map.

    Kit repos have no .standards-kit.json (only `standards init` writes one), so
    'no marker' => kit mode => new checks run at error severity.
    """
    marker = root / ".standards-kit.json"
    if not marker.exists():
        return Context(root=root, adopter_mode=False, overrides={})
    overrides = {}
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        raw = data.get("check", {})
        if isinstance(raw, dict):
            overrides = {k: v for k, v in raw.items() if v in ("error", "warn")}
    except (OSError, ValueError):
        overrides = {}
    return Context(root=root, adopter_mode=True, overrides=overrides)


def main() -> int:
    root = find_repo_root(Path(__file__).resolve().parent)
    ctx = build_context(root)
    findings: list = []
    for run in CHECKS:
        findings.extend(run(root, ctx))
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warn"]
    print(f"Standards check: {len(errors)} error(s), {len(warnings)} warning(s)")
    for f in errors:
        print(f"  ERROR  [{f.check_id}] {f.message}")
    for f in warnings:
        print(f"  WARN   [{f.check_id}] {f.message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Verify the unchanged test still passes and output is identical**

Run: `python scripts/standards-check/test_check.py -v`
Expected: PASS (5 tests) — proves `parse_frontmatter` is still importable from `check`.

Run: `python scripts/standards-check/check.py`
Expected: `Standards check: 0 error(s), 0 warning(s)` (note: messages now carry a `[structural]` check_id prefix in addition to the existing `[core]`/`[adr]` tags — there are none to print while green).

Run: `python scripts/standards-check/test_severity.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/standards-check/check.py scripts/standards-check/checks/structural.py
git commit -m "refactor(slice-4): split check.py into checks/ package (structural moved verbatim)"
```

---

### Task 3: `build_context` tests — marker detection + override parsing

**Files:**
- Create: `scripts/standards-check/test_context.py`
- Unchanged: `scripts/standards-check/check.py` (`build_context` already implemented in Task 2)

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_context.py`:

```python
"""Tests for check.build_context: kit vs adopter detection + override parsing."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check import build_context  # noqa: E402


class BuildContextTests(unittest.TestCase):
    def test_no_marker_is_kit_mode(self):
        with tempfile.TemporaryDirectory() as d:
            ctx = build_context(Path(d))
            self.assertFalse(ctx.adopter_mode)
            self.assertEqual(ctx.overrides, {})

    def test_marker_present_is_adopter_mode(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".standards-kit.json").write_text("{}", encoding="utf-8")
            ctx = build_context(Path(d))
            self.assertTrue(ctx.adopter_mode)

    def test_override_map_parsed(self):
        with tempfile.TemporaryDirectory() as d:
            marker = {"check": {"links": "error", "placeholder": "warn", "bogus": "loud"}}
            (Path(d) / ".standards-kit.json").write_text(json.dumps(marker), encoding="utf-8")
            ctx = build_context(Path(d))
            self.assertEqual(ctx.overrides, {"links": "error", "placeholder": "warn"})

    def test_garbled_marker_is_tolerated(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".standards-kit.json").write_text("{not json", encoding="utf-8")
            ctx = build_context(Path(d))
            self.assertTrue(ctx.adopter_mode)
            self.assertEqual(ctx.overrides, {})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it passes (implementation already exists)**

Run: `python scripts/standards-check/test_context.py -v`
Expected: PASS (4 tests). If any fail, fix `build_context` in `check.py` to match the test, then re-run.

- [ ] **Step 3: Commit**

```bash
git add scripts/standards-check/test_context.py
git commit -m "test(slice-4): cover build_context kit/adopter detection + overrides"
```

---

### Task 4: `checks/links.py` — internal link + anchor resolution

**Files:**
- Create: `scripts/standards-check/checks/links.py`
- Create: `scripts/standards-check/test_links.py`
- Modify: `scripts/standards-check/check.py` (add `links.run` to `CHECKS`)

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_links.py`:

```python
"""Tests for the internal-link check."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.links import run, slugify, extract_links  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


class SlugifyTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_strips_punctuation(self):
        self.assertEqual(slugify("What's the Plan?"), "whats-the-plan")

    def test_keeps_existing_hyphen(self):
        self.assertEqual(slugify("kit-tracked files"), "kit-tracked-files")


class ExtractLinksTests(unittest.TestCase):
    def test_inline_link(self):
        links = extract_links("see [the doc](./a.md) here")
        self.assertIn("./a.md", [t for _, t in links])

    def test_skips_images(self):
        links = extract_links("![alt](./img.png)")
        self.assertEqual(links, [])

    def test_skips_external(self):
        links = extract_links("[x](https://example.com) [y](mailto:a@b.c)")
        self.assertEqual(links, [])

    def test_ignores_fenced_code(self):
        fence = "`" * 3
        text = fence + "\n[x](./nope.md)\n" + fence + "\nreal [y](./yes.md)\n"
        targets = [t for _, t in extract_links(text)]
        self.assertEqual(targets, ["./yes.md"])

    def test_reference_definition(self):
        targets = [t for _, t in extract_links("[id]: ./ref.md\n")]
        self.assertIn("./ref.md", targets)


class RunTests(unittest.TestCase):
    def _write(self, root: Path, rel: str, body: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_valid_relative_link_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[b](./b.md)\n")
            self._write(root, "b.md", "# B\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_file_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](./gone.md)\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")
            self.assertIn("missing file", findings[0].message)

    def test_missing_file_is_warn_in_adopter(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](./gone.md)\n")
            findings = run(root, _ctx(root, adopter=True))
            self.assertEqual(findings[0].severity, "warn")

    def test_adopter_override_escalates(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](./gone.md)\n")
            findings = run(root, _ctx(root, adopter=True, overrides={"links": "error"}))
            self.assertEqual(findings[0].severity, "error")

    def test_valid_anchor_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[sec](./b.md#the-section)\n")
            self._write(root, "b.md", "# B\n\n## The Section\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_anchor_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[sec](./b.md#nope)\n")
            self._write(root, "b.md", "# B\n\n## The Section\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertIn("missing anchor", findings[0].message)

    def test_same_file_anchor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "# A\n\n## Top\n\nback to [top](#top)\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_git_dir_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, ".git/x.md", "[gone](./nope.md)\n")
            self._write(root, "a.md", "# A\n")
            self.assertEqual(run(root, _ctx(root)), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scripts/standards-check/test_links.py -v`
Expected: FAIL — `ImportError: cannot import name 'run' from 'checks.links'`.

- [ ] **Step 3: Write `checks/links.py`**

Create `scripts/standards-check/checks/links.py`:

```python
"""Internal markdown link + anchor resolution.

Scans every committed *.md (skipping .git/ and src/standards/_payload, which is a
force-include duplicate of the source tree). Relative link targets must resolve
to a real file; #anchor fragments must match a heading slug in the target file.
External links (http/https/mailto/tel) are out of scope.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "links"
DEFAULT_SEVERITY = "error"

# Inline [text](target) — (?<!!) skips images; optional "title" after the target.
_INLINE_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
# Reference definition: [id]: target
_REFDEF_RE = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(\S+)")
# ATX heading line.
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
_EXTERNAL_RE = re.compile(r"^(?:https?:|mailto:|tel:|//)", re.IGNORECASE)

_SKIP_DIR_PARTS = {".git"}
_SKIP_PATH_PREFIXES = ("src/standards/_payload",)


def slugify(heading: str) -> str:
    """GitHub-style heading slug for ASCII headings."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)   # drop punctuation; keep word chars, space, hyphen
    s = re.sub(r"\s+", "-", s)        # spaces -> hyphen
    return s


def _strip_code_and_comments(text: str) -> str:
    """Blank out fenced code blocks, inline code spans, and HTML comments.

    Replaces them with same-length-ish blanks so links inside them are not
    scanned. Newlines are preserved so line numbers stay correct.
    """
    # HTML comments (may span lines).
    text = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)
    # Fenced code blocks ``` ... ``` (preserve newlines).
    text = re.sub(r"```.*?```", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)
    # Inline code spans `...` (single line).
    text = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), text)
    return text


def extract_links(text: str):
    """Return [(line_number, target)] for inline + reference links, skipping
    images, external schemes, and links inside code/comments."""
    cleaned = _strip_code_and_comments(text)
    out = []
    for i, line in enumerate(cleaned.splitlines(), 1):
        for m in _INLINE_RE.finditer(line):
            target = m.group(1)
            if not _EXTERNAL_RE.match(target):
                out.append((i, target))
        for m in _REFDEF_RE.finditer(line):
            target = m.group(1)
            if not _EXTERNAL_RE.match(target):
                out.append((i, target))
    return out


def _heading_slugs(text: str):
    cleaned = _strip_code_and_comments(text)
    slugs = {}
    for line in cleaned.splitlines():
        m = _HEADING_RE.match(line)
        if not m:
            continue
        base = slugify(m.group(1))
        if base not in slugs:
            slugs[base] = 0
            yield base
        else:
            slugs[base] += 1
            yield f"{base}-{slugs[base]}"


def _iter_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if any(part in _SKIP_DIR_PARTS for part in path.relative_to(root).parts):
            continue
        if any(rel.startswith(prefix) for prefix in _SKIP_PATH_PREFIXES):
            continue
        yield path, rel


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    findings = []
    for path, rel in _iter_markdown(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, target in extract_links(text):
            frag = ""
            file_part = target
            if "#" in target:
                file_part, _, frag = target.partition("#")
            # Resolve the file part.
            if file_part == "":
                target_path = path  # same-file anchor
            else:
                target_path = (path.parent / file_part).resolve()
                if not target_path.exists():
                    findings.append(Finding(
                        CHECK_ID, severity,
                        f"{rel}:{line_no} broken link -> {target} (missing file)",
                    ))
                    continue
            # Resolve the anchor, if any.
            if frag:
                try:
                    target_text = target_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if frag not in set(_heading_slugs(target_text)):
                    findings.append(Finding(
                        CHECK_ID, severity,
                        f"{rel}:{line_no} broken link -> {target} (missing anchor)",
                    ))
    return findings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scripts/standards-check/test_links.py -v`
Expected: PASS (all tests). Fix `links.py` until green.

- [ ] **Step 5: Wire `links.run` into the orchestrator**

In `scripts/standards-check/check.py`, change the imports and `CHECKS`:

```python
from checks import structural, links  # noqa: E402
```
```python
CHECKS = [structural.run, links.run]
```

- [ ] **Step 6: Commit (do NOT yet run the kit check — that is the Task 8 dogfood)**

```bash
git add scripts/standards-check/checks/links.py scripts/standards-check/test_links.py scripts/standards-check/check.py
git commit -m "feat(slice-4): add internal link + anchor check (links.py)"
```

---

### Task 5: `checks/content.py` — placeholder lint + CHANGELOG shape

**Files:**
- Create: `scripts/standards-check/checks/content.py`
- Create: `scripts/standards-check/test_content.py`
- Modify: `scripts/standards-check/check.py` (add `content.run` to `CHECKS`)

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_content.py`:

```python
"""Tests for the placeholder + CHANGELOG content checks."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.content import run, find_placeholders  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


class FindPlaceholdersTests(unittest.TestCase):
    def test_angle_bracket_token(self):
        hits = find_placeholders("deciders: <name>, <name>\n")
        self.assertTrue(any("<name>" in h for _, h in hits))

    def test_literal_date_placeholder(self):
        hits = find_placeholders("date: YYYY-MM-DD\n")
        self.assertTrue(any("YYYY-MM-DD" in h for _, h in hits))

    def test_bare_nnnn(self):
        hits = find_placeholders("# NNNN. Title\n")
        self.assertTrue(any("NNNN" in h for _, h in hits))

    def test_ignores_comment_block(self):
        hits = find_placeholders("<!-- <name> YYYY-MM-DD NNNN -->\nreal body\n")
        self.assertEqual(hits, [])

    def test_real_date_is_not_a_placeholder(self):
        self.assertEqual(find_placeholders("date: 2026-05-30\n"), [])


class RunTests(unittest.TestCase):
    def _write(self, root: Path, rel: str, body: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_clean_adr_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "docs/decisions/0001-x.md",
                        "---\nstatus: Accepted\ndate: 2026-05-30\n---\n\n# 0001. Real Title\n\nBody.\n")
            self.assertEqual([f for f in run(root, _ctx(root)) if f.check_id == "placeholder"], [])

    def test_unfilled_adr_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "docs/decisions/0001-x.md",
                        "---\nstatus: Proposed\ndate: YYYY-MM-DD\n---\n\n# NNNN. <Title>\n")
            findings = [f for f in run(root, _ctx(root)) if f.check_id == "placeholder"]
            self.assertTrue(findings)
            self.assertTrue(all(f.severity == "error" for f in findings))

    def test_unfilled_adr_is_warn_in_adopter(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "docs/decisions/0001-x.md", "date: YYYY-MM-DD\n")
            findings = [f for f in run(root, _ctx(root, adopter=True)) if f.check_id == "placeholder"]
            self.assertTrue(findings)
            self.assertTrue(all(f.severity == "warn" for f in findings))

    def test_template_and_readme_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "docs/decisions/template.md", "date: YYYY-MM-DD\n<name>\n")
            self._write(root, "docs/decisions/README.md", "date: YYYY-MM-DD\n")
            self.assertEqual([f for f in run(root, _ctx(root)) if f.check_id == "placeholder"], [])

    def test_changelog_without_version_section_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "CHANGELOG.md", "# Changelog\n\nnothing structured here\n")
            findings = [f for f in run(root, _ctx(root)) if f.check_id == "changelog"]
            self.assertEqual(len(findings), 1)

    def test_changelog_with_version_section_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "CHANGELOG.md", "# Changelog\n\n## [0.7.0] - 2026-05-30\n\n- thing\n")
            self.assertEqual([f for f in run(root, _ctx(root)) if f.check_id == "changelog"], [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scripts/standards-check/test_content.py -v`
Expected: FAIL — `ImportError: cannot import name 'run' from 'checks.content'`.

- [ ] **Step 3: Write `checks/content.py`**

Create `scripts/standards-check/checks/content.py`:

```python
"""Content lint: residual template placeholders in committed ADRs/RFCs, and a
light Keep-a-Changelog shape check for CHANGELOG.md.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

PLACEHOLDER_ID = "placeholder"
CHANGELOG_ID = "changelog"
DEFAULT_SEVERITY = "error"

# Angle-bracket placeholder: <words, spaces, commas, em-dash, ellipsis>. Excludes
# tags with '/' or '!' (HTML/comments) and '#' (won't appear in placeholders).
_ANGLE_RE = re.compile(r"<[A-Za-z][^<>\n/!]*?>")
_DATE_PLACEHOLDER_RE = re.compile(r"\bYYYY-MM-DD\b")
_BARE_NNNN_RE = re.compile(r"\bNNNN\b")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_VERSION_SECTION_RE = re.compile(r"(?m)^##\s+\[[^\]]+\]")

_ADR_FILE_RE = re.compile(r"^\d{4}-[a-z0-9-]+\.md$")


def _blank_comments(text: str) -> str:
    return _COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def find_placeholders(text: str):
    """Return [(line_number, token)] for residual template placeholders, ignoring
    anything inside <!-- --> comment blocks."""
    cleaned = _blank_comments(text)
    out = []
    for i, line in enumerate(cleaned.splitlines(), 1):
        for m in _ANGLE_RE.finditer(line):
            out.append((i, m.group(0)))
        for m in _DATE_PLACEHOLDER_RE.finditer(line):
            out.append((i, m.group(0)))
        for m in _BARE_NNNN_RE.finditer(line):
            out.append((i, m.group(0)))
    return out


def _authored_docs(root: Path):
    decisions = root / "docs/decisions"
    if decisions.is_dir():
        for p in sorted(decisions.glob("*.md")):
            if _ADR_FILE_RE.match(p.name):
                yield p
    rfcs = root / "docs/rfcs"
    if rfcs.is_dir():
        for entry in sorted(rfcs.iterdir()):
            rfc_md = entry / "rfc.md"
            if entry.is_dir() and rfc_md.exists():
                yield rfc_md


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(PLACEHOLDER_ID, DEFAULT_SEVERITY, ctx)
    findings = []
    for path in _authored_docs(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, token in find_placeholders(text):
            findings.append(Finding(
                PLACEHOLDER_ID, severity,
                f"{rel}:{line_no} unfilled template placeholder: {token}",
            ))
    changelog = root / "CHANGELOG.md"
    if changelog.exists():
        text = changelog.read_text(encoding="utf-8", errors="replace")
        if not _VERSION_SECTION_RE.search(text):
            findings.append(Finding(
                CHANGELOG_ID, resolve_severity(CHANGELOG_ID, DEFAULT_SEVERITY, ctx),
                "CHANGELOG.md: no Keep-a-Changelog version section (## [x.y.z]) found",
            ))
    return findings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scripts/standards-check/test_content.py -v`
Expected: PASS (all tests). Fix `content.py` until green.

- [ ] **Step 5: Wire `content.run` into the orchestrator**

In `scripts/standards-check/check.py`:
```python
from checks import structural, links, content  # noqa: E402
```
```python
CHECKS = [structural.run, links.run, content.run]
```

- [ ] **Step 6: Commit**

```bash
git add scripts/standards-check/checks/content.py scripts/standards-check/test_content.py scripts/standards-check/check.py
git commit -m "feat(slice-4): add placeholder + CHANGELOG content check (content.py)"
```

---

### Task 6: `checks/skills.py` — SKILL.md frontmatter + structure

**Files:**
- Create: `scripts/standards-check/checks/skills.py`
- Create: `scripts/standards-check/test_skills.py`
- Modify: `scripts/standards-check/check.py` (add `skills.run` to `CHECKS`)

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_skills.py`:

```python
"""Tests for the SKILL.md format check."""
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


def _skill(root: Path, name: str, body: str) -> None:
    p = root / ".claude" / "skills" / name / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


class SkillFormatTests(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\nname: new-adr\ndescription: Scaffold an ADR.\n---\n\n# New ADR\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_description_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\nname: new-adr\n---\n\n# New ADR\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")
            self.assertIn("description", findings[0].message)

    def test_name_mismatch_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\nname: make-adr\ndescription: x\n---\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertIn("!= dir", findings[0].message)

    def test_missing_name_in_adopter_is_warn(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\ndescription: x\n---\n")
            findings = run(root, _ctx(root, adopter=True))
            self.assertEqual(findings[0].severity, "warn")

    def test_no_skills_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(Path(d), _ctx(Path(d))), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scripts/standards-check/test_skills.py -v`
Expected: FAIL — `ImportError: cannot import name 'run' from 'checks.skills'`.

- [ ] **Step 3: Write `checks/skills.py`**

Create `scripts/standards-check/checks/skills.py`:

```python
"""SKILL.md format lint: every .claude/skills/*/SKILL.md needs frontmatter with a
non-empty `name` (matching its directory) and a non-empty `description`.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "skill-format"
DEFAULT_SEVERITY = "error"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


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


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    findings = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scripts/standards-check/test_skills.py -v`
Expected: PASS (5 tests). Fix `skills.py` until green.

- [ ] **Step 5: Wire `skills.run` into the orchestrator**

In `scripts/standards-check/check.py`:
```python
from checks import structural, links, content, skills  # noqa: E402
```
```python
CHECKS = [structural.run, links.run, content.run, skills.run]
```

- [ ] **Step 6: Commit**

```bash
git add scripts/standards-check/checks/skills.py scripts/standards-check/test_skills.py scripts/standards-check/check.py
git commit -m "feat(slice-4): add SKILL.md format check (skills.py)"
```

---

### Task 7: Payload-inclusion test (no manifest change)

Proves the new `checks/` package is vendored into adopters by the existing `scripts/` payload walk — so `standards init` ships it without any `manifest.py` edit.

**Files:**
- Create: `tests/test_payload_includes_checks.py`

- [ ] **Step 1: Write the test**

Create `tests/test_payload_includes_checks.py`:

```python
"""Regression: the standards-check checks/ package must ship in the payload."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from standards.manifest import iter_payload  # noqa: E402


class PayloadIncludesChecksTests(unittest.TestCase):
    def test_checks_package_modules_are_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        for expected in (
            "scripts/standards-check/checks/__init__.py",
            "scripts/standards-check/checks/structural.py",
            "scripts/standards-check/checks/links.py",
            "scripts/standards-check/checks/content.py",
            "scripts/standards-check/checks/skills.py",
        ):
            self.assertIn(expected, rels, f"{expected} missing from payload")

    def test_pycache_not_in_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        self.assertFalse(any("__pycache__" in r or r.endswith(".pyc") for r in rels))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python tests/test_payload_includes_checks.py -v`
Expected: PASS (2 tests). The `checks/` modules exist (Tasks 1–6) and `scripts/` is a wholesale `PAYLOAD_DIR`, so they are yielded with no manifest change.

- [ ] **Step 3: Commit**

```bash
git add tests/test_payload_includes_checks.py
git commit -m "test(slice-4): assert checks/ package ships in the payload"
```

---

### Task 8: Dogfood — run the new checks against the kit and fix every error

The new checks now run at **error** severity for the kit (no `.standards-kit.json`). This task drives the kit's own check back to `0 errors`.

**Files:**
- Modify: whatever files the checks flag (broken relative links, residual placeholders, SKILL.md frontmatter gaps).

- [ ] **Step 1: Run the full check and capture findings**

Run: `python scripts/standards-check/check.py`
Expected: a list of `ERROR [links|placeholder|changelog|skill-format] …` lines (count unknown until run). Warnings (e.g. `[structural]` ai-staleness) are fine — only errors must reach zero.

- [ ] **Step 2: Fix each finding at its source**

For each error, edit the named `file:line`:
- `[links] … (missing file)` — correct the relative path, or remove/repoint the dead link. Verify the target exists with: `ls <resolved-path>`.
- `[links] … (missing anchor)` — fix the `#fragment` to match the target heading's slug (lowercase, spaces→`-`, punctuation stripped), or fix the heading. If a specific link is a legitimate false positive from the slug algorithm (e.g. an em-dash heading), note it for Step 4.
- `[placeholder] … <token>` — fill in the real value in the committed ADR/RFC (`<name>` → a real name, `YYYY-MM-DD` → the real date, bare `NNNN` → the real number). These should be rare; the kit's ADRs are authored, not templates.
- `[changelog] …` — ensure `CHANGELOG.md` has at least one `## [x.y.z]` section (it already should; investigate if flagged).
- `[skill-format] …` — add the missing `name`/`description` frontmatter to the named `.claude/skills/*/SKILL.md`, or align `name` with its directory.

- [ ] **Step 3: Re-run until clean**

Run: `python scripts/standards-check/check.py`
Expected: `Standards check: 0 error(s), N warning(s)` — zero errors. Repeat Step 2 until satisfied.

- [ ] **Step 4: If the anchor check produced unavoidable false positives, soften it**

Only if Step 2 found genuine slug-algorithm false positives that cannot be fixed at the source: change `checks/links.py` so a **missing anchor** is a warning even in kit mode, while **missing file** stays at full severity. Replace the anchor-finding append in `run()` with a fixed `"warn"`:

```python
                if frag not in set(_heading_slugs(target_text)):
                    findings.append(Finding(
                        CHECK_ID, "warn",   # anchors soften to warn (slug-algo false positives)
                        f"{rel}:{line_no} broken link -> {target} (missing anchor)",
                    ))
```
Then update `test_links.py::test_missing_anchor_is_flagged` to assert `severity == "warn"` and re-run `python scripts/standards-check/test_links.py -v`. Skip this step entirely if Step 3 already reached zero errors.

- [ ] **Step 5: Run the whole suite**

Run: `python tools/run_tests.py`
Expected: all suites pass (now includes test_severity, test_context, test_links, test_content, test_skills, test_payload_includes_checks).

- [ ] **Step 6: Commit the fixes**

```bash
git add -A
git commit -m "fix(slice-4): resolve content-check findings in the kit's own docs"
```

---

### Task 9: Docs + version bump to v0.7.0

**Files:**
- Modify: `docs/STANDARDS.md` (document the v2 checks + the adopter `"check"` override field)
- Modify: `src/standards/__about__.py` (`0.6.0` → `0.7.0`)
- Modify: `CHANGELOG.md` (new `## [0.7.0]` entry + reference link)
- Modify: `AGENTS.md` (Kit-version in the `kit-managed: agents-core` block)

- [ ] **Step 1: Document the new checks in `docs/STANDARDS.md`**

Find the section describing the standards-check workflow (search for `Standards check workflow`). Add a subsection documenting the three content checks and the adopter severity model. Insert this after the existing v1 checks list:

```markdown
### Content checks (v2)

Beyond the structural checks, standards-check validates document bodies:

- **Internal links** — every relative markdown link (and `#anchor`) must resolve to a real file/heading. External (`http(s)`/`mailto`) links are not checked.
- **Placeholders** — committed ADRs/RFCs must not retain template scaffolding (`<...>` tokens, literal `YYYY-MM-DD`, bare `NNNN`).
- **Skill format** — every `.claude/skills/*/SKILL.md` needs frontmatter `name` (matching its directory) and `description`.

**Severity.** In the kit itself these are **errors**. In an adopting repo (one with a `.standards-kit.json` marker) they default to **warnings**. To escalate a check to an error in your repo, add a `"check"` map to `.standards-kit.json`:

​```json
{ "check": { "links": "error", "placeholder": "error", "skill-format": "error" } }
​```
```

(Remove the zero-width characters around the inner fence — they only escape the nesting here.)

- [ ] **Step 2: Bump the package version**

Edit `src/standards/__about__.py`: change `__version__ = "0.6.0"` to `__version__ = "0.7.0"`.

- [ ] **Step 3: Add the CHANGELOG entry**

In `CHANGELOG.md`, add a new section above the current top entry:

```markdown
## [0.7.0] - 2026-05-30

### Added
- `standards-check` v2 content checks: internal link + anchor resolution, residual-placeholder lint for ADRs/RFCs, and SKILL.md format lint. New checks are errors in the kit and warnings (escalatable via `.standards-kit.json` `"check"`) in adopters.
- `scripts/standards-check/` split into a `checks/` package (structural/links/content/skills).
```

Add the matching reference link at the bottom of the file, following the existing pattern (placeholder URL is fine pre-tag, per `docs/RELEASING.md`):

```markdown
[0.7.0]: https://example.invalid/compare/v0.6.0...v0.7.0
```

- [ ] **Step 4: Bump the AGENTS.md Kit-version**

Run: `grep -n "0.6.0" AGENTS.md`
Edit each match inside the `<!-- BEGIN kit-managed: agents-core … -->` block (the `Kit version: **0.6.0**` line and the sentinel `(v0.6.0)` tags) to `0.7.0`.

- [ ] **Step 5: Verify everything is green**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)` (warnings allowed).

Run: `python tools/run_tests.py`
Expected: all suites pass.

- [ ] **Step 6: Commit**

```bash
git add docs/STANDARDS.md src/standards/__about__.py CHANGELOG.md AGENTS.md
git commit -m "docs(slice-4): document v2 content checks + bump to v0.7.0"
```

---

## Self-Review

**Spec coverage:**
- §4A internal links (files + anchors) → Task 4 ✓
- §4B placeholder + CHANGELOG → Task 5 ✓
- §4C SKILL.md format → Task 6 ✓
- §3 severity model (kit error / adopter warn / override) → Task 1 (`resolve_severity`) + Task 3 (`build_context`) + asserted in Tasks 4/5/6 ✓
- §2 module split + `parse_frontmatter` re-export → Task 2 ✓
- Payload ships to adopters (manifest verify, no change) → Task 7 ✓
- Dogfood to 0 errors → Task 8 ✓
- Docs + v0.7.0 bump (STANDARDS.md, __about__, CHANGELOG, AGENTS.md) → Task 9 ✓

**Placeholder scan:** No "TBD"/"implement later"; every code step shows complete code. Task 8 is intentionally data-driven (the exact findings are unknown until run) but gives concrete fix recipes per check_id — this is the dogfooding step, not a placeholder.

**Type consistency:** `Finding(check_id, severity, message)`, `Context(root, adopter_mode, overrides)`, `resolve_severity(check_id, default, ctx)`, and each module's `run(root, ctx) -> list` are used identically across Tasks 1–9. Check IDs are stable: `"structural"`, `"links"`, `"placeholder"`, `"changelog"`, `"skill-format"`. `extract_links`/`slugify`/`find_placeholders` signatures match their tests.

**Out of scope (later plans):** version-coherence lint, AI-freshness teeth, discovery hardening (Plan 2); skill polish + `/standards-check` skill (Plan 3).
