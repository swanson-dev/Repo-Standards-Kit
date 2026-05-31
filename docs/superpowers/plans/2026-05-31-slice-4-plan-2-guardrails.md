# Slice 4 Plan 2 — Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three guardrails — a kit-only version-coherence tool with CI/release gates, tighter AI-freshness (handoff 7→5 days + louder Stop-hook nudge), and a shipped `promoted_to`-existence discovery check — and ship them as v0.8.0.

**Architecture:** Version-coherence is kit-only: a standalone `tools/check_version_coherence.py` run by a NON-shipped `kit-guards.yml` (PR-time) and `release.yml` (tag-time, asserting tag==version). It is NOT in the `checks/` package because `repo-standards.yml` ships to adopters who lack `__about__.py`. The discovery check IS adopter-relevant, so it joins the shipped `checks/` package using Plan 1's `run(root, ctx) -> list[Finding]` + `resolve_severity` model. Freshness is a one-constant change in `checks/structural.py` plus a hook-nudge enhancement.

**Tech Stack:** Python 3.9+ stdlib only (`re`, `argparse`, `datetime`, `pathlib`, `unittest`). Tests run via `python tools/run_tests.py`. Reference spec: `docs/superpowers/specs/2026-05-31-slice-4-plan-2-guardrails-design.md`.

**Conventions for every task below:**
- `from __future__ import annotations` is the **first code line** of every new module and test (CI matrix runs Python 3.9).
- Run a check-package suite: `python scripts/standards-check/test_<name>.py -v`. Run a top-level suite: `python tests/test_<name>.py -v`. Run everything: `python tools/run_tests.py`. Run the kit's own check: `python scripts/standards-check/check.py`. Run the coherence tool: `python tools/check_version_coherence.py`.

---

### Task 1: `tools/check_version_coherence.py` — the version-coherence tool

**Files:**
- Create: `tools/check_version_coherence.py`
- Create: `tests/test_version_coherence.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_version_coherence.py`:

```python
"""Tests for the kit-only version-coherence tool."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from check_version_coherence import find_incoherences  # noqa: E402


def _make_kit(root: Path, about="0.8.0", changelog="0.8.0", kitver="0.8.0", sentinel="0.8.0") -> None:
    (root / "src" / "standards").mkdir(parents=True, exist_ok=True)
    (root / "src" / "standards" / "__about__.py").write_text(
        f'__version__ = "{about}"\n', encoding="utf-8"
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [Unreleased]\n\n## [{changelog}] - 2026-05-31\n\n- x\n", encoding="utf-8"
    )
    (root / "AGENTS.md").write_text(
        f"<!-- BEGIN kit-managed: agents-core (v{sentinel}) -->\n"
        f"- Kit version: **{kitver}**\n"
        f"<!-- END kit-managed: agents-core -->\n",
        encoding="utf-8",
    )


class CoherenceTests(unittest.TestCase):
    def test_all_aligned_is_empty(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root)
            self.assertEqual(find_incoherences(root), [])

    def test_changelog_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root, changelog="0.7.0")
            msgs = find_incoherences(root)
            self.assertTrue(any("CHANGELOG" in m for m in msgs))

    def test_kitver_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root, kitver="0.7.0")
            msgs = find_incoherences(root)
            self.assertTrue(any("Kit-version" in m for m in msgs))

    def test_sentinel_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root, sentinel="0.7.0")
            msgs = find_incoherences(root)
            self.assertTrue(any("sentinel" in m for m in msgs))

    def test_unreleased_top_is_skipped(self):
        # The [Unreleased] heading must not be read as the version.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root)  # CHANGELOG has [Unreleased] above [0.8.0]
            self.assertEqual(find_incoherences(root), [])

    def test_tag_match_and_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root)
            self.assertEqual(find_incoherences(root, tag="v0.8.0"), [])
            self.assertTrue(any("tag" in m for m in find_incoherences(root, tag="v0.9.0")))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_version_coherence.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'check_version_coherence'`.

- [ ] **Step 3: Write `tools/check_version_coherence.py`**

```python
#!/usr/bin/env python3
"""Version-coherence guard (kit-only). Verifies the kit's version strings agree.

Source of truth: src/standards/__about__.py __version__ (pyproject reads it via
[tool.hatch.version]). Asserts the CHANGELOG top version section, the AGENTS.md
Kit-version line, and the AGENTS.md agents-core sentinel tag all match. With
--tag vX.Y.Z, also asserts the release tag matches. Exit 1 on any mismatch.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ABOUT_RE = re.compile(r"""__version__\s*=\s*["']([^"']+)["']""")
_CHANGELOG_RE = re.compile(r"(?m)^##\s+\[(\d+\.\d+\.\d+)\]")
_KITVER_RE = re.compile(r"(?m)^-\s*Kit version:\s*\*\*([^*]+)\*\*")
_SENTINEL_RE = re.compile(r"kit-managed:\s*agents-core\s*\(v([^)]+)\)")


def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "src" / "standards" / "__about__.py").exists():
            return parent
    raise SystemExit("Could not locate kit root (no src/standards/__about__.py above this script).")


def read_about_version(root: Path):
    text = (root / "src" / "standards" / "__about__.py").read_text(encoding="utf-8")
    m = _ABOUT_RE.search(text)
    return m.group(1) if m else None


def find_incoherences(root: Path, tag: str = None) -> list:
    """Return human-readable mismatch messages; empty list means coherent."""
    about = read_about_version(root)
    if about is None:
        return ["src/standards/__about__.py: no __version__ found"]
    msgs = []

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    m = _CHANGELOG_RE.search(changelog)  # first numeric version section ([Unreleased] is skipped)
    if not m:
        msgs.append("CHANGELOG.md: no version section (## [x.y.z]) found")
    elif m.group(1) != about:
        msgs.append(f"CHANGELOG.md top version {m.group(1)} != __about__ {about}")

    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    m = _KITVER_RE.search(agents)
    if not m:
        msgs.append("AGENTS.md: no `- Kit version: **x.y.z**` line found")
    elif m.group(1).strip() != about:
        msgs.append(f"AGENTS.md Kit-version {m.group(1).strip()} != __about__ {about}")

    m = _SENTINEL_RE.search(agents)
    if not m:
        msgs.append("AGENTS.md: no agents-core sentinel version tag found")
    elif m.group(1) != about:
        msgs.append(f"AGENTS.md sentinel (v{m.group(1)}) != __about__ {about}")

    if tag is not None:
        tag_ver = tag[1:] if tag.startswith("v") else tag
        if tag_ver != about:
            msgs.append(f"release tag {tag} != __about__ {about}")

    return msgs


def main(argv) -> int:
    parser = argparse.ArgumentParser(prog="check-version-coherence")
    parser.add_argument("--tag", default=None, help="release tag (e.g. v0.8.0) to verify against __about__")
    args = parser.parse_args(argv[1:])
    root = find_repo_root(Path(__file__).resolve().parent)
    msgs = find_incoherences(root, tag=args.tag)
    if msgs:
        print("Version coherence: FAIL")
        for m in msgs:
            print(f"  {m}")
        return 1
    print("Version coherence: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_version_coherence.py -v`
Expected: PASS (6 tests). Fix the tool until green.

- [ ] **Step 5: Run the tool against the real kit**

Run: `python tools/check_version_coherence.py`
Expected: `Version coherence: OK` (everything is currently at 0.7.0). If it reports a mismatch, the regexes need adjusting to the real file shapes — fix the tool, not the kit.

- [ ] **Step 6: Commit**

```bash
git add tools/check_version_coherence.py tests/test_version_coherence.py
git commit -m "feat(slice-4): add kit-only version-coherence tool"
```

---

### Task 2: Refactor `tests/test_version.py` off the hardcoded literal

**Files:**
- Modify: `tests/test_version.py`

- [ ] **Step 1: Replace the file contents**

The current file hardcodes `assertEqual(__version__, "0.7.0")` — the brittle literal. Replace the ENTIRE file with a version that keeps the semver-shape check and adds a coherence assertion (no literal to bump):

```python
"""Version sanity: semver shape + cross-file coherence (no hardcoded literal)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from standards.__about__ import __version__  # noqa: E402
from check_version_coherence import find_incoherences  # noqa: E402


class VersionTests(unittest.TestCase):
    def test_version_is_semver_string(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")

    def test_kit_version_is_coherent(self):
        # __about__ must agree with CHANGELOG top, AGENTS.md Kit-version + sentinel.
        self.assertEqual(find_incoherences(REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python tests/test_version.py -v`
Expected: PASS (2 tests) — the kit is coherent at 0.7.0.

- [ ] **Step 3: Commit**

```bash
git add tests/test_version.py
git commit -m "test(slice-4): assert version coherence instead of a hardcoded literal"
```

---

### Task 3: `kit-guards.yml` — non-shipped PR-time coherence workflow

**Files:**
- Create: `.github/workflows/kit-guards.yml`

- [ ] **Step 1: Create the workflow**

```yaml
name: Kit guards

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  coherence:
    name: Version coherence
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Check version coherence
        run: python tools/check_version_coherence.py
```

- [ ] **Step 2: Verify it parses as YAML and is NOT in the payload**

Run:
```bash
python -c "import sys; sys.path.insert(0,'src'); from standards.manifest import iter_payload; rels={r for _,r in iter_payload('.')}; assert '.github/workflows/kit-guards.yml' not in rels, 'kit-guards.yml must NOT ship to adopters'; print('OK: not shipped')"
```
Expected: `OK: not shipped`. (It lives directly under `.github/workflows/`, which is not a wholesale `PAYLOAD_DIR`, and is not in `PAYLOAD_FILES`. A regression test for this is added in Task 8.)

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/kit-guards.yml
git commit -m "ci(slice-4): add non-shipped kit-guards workflow (version coherence)"
```

---

### Task 4: `release.yml` — coherence + tag==version gate

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Read the current file**

Run: `cat .github/workflows/release.yml`
Locate the `release` job's steps: checkout → setup-python → run-tests → build → publish.

- [ ] **Step 2: Insert the coherence gate step**

Add this step IMMEDIATELY AFTER the `setup-python` step and BEFORE the test/build steps (so a mis-tagged or incoherent release fails fast). `github.ref_name` for a tag push is the tag (e.g. `v0.8.0`):

```yaml
      - name: Verify version coherence + tag
        run: python tools/check_version_coherence.py --tag "${{ github.ref_name }}"
```

Match the existing indentation of the other steps in that job exactly.

- [ ] **Step 3: Verify YAML well-formedness**

Run: `python -c "import yaml" 2>/dev/null && python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/release.yml')); print('valid yaml')" || python -c "print('pyyaml not available; visually confirm indentation matches sibling steps')"`
Expected: `valid yaml` (or the fallback note — then eyeball the indentation against the other steps).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci(slice-4): gate release on version coherence + tag match"
```

---

### Task 5: Tighten the handoff freshness threshold (7 → 5 days)

**Files:**
- Modify: `scripts/standards-check/checks/structural.py` (the `HANDOFF_STALE_DAYS` constant)
- Create: `scripts/standards-check/test_freshness.py`

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_freshness.py`:

```python
"""Behavioral test for the ai/ freshness thresholds in structural checks."""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks.structural import Report, check_ai_freshness  # noqa: E402


def _write_ai(root: Path, handoff_days_old: int, state_days_old: int) -> None:
    ai = root / "ai"
    ai.mkdir(parents=True, exist_ok=True)
    h = (date.today() - timedelta(days=handoff_days_old)).isoformat()
    s = (date.today() - timedelta(days=state_days_old)).isoformat()
    (ai / "handoff.md").write_text(f"---\nwritten: {h}\n---\n", encoding="utf-8")
    (ai / "current-state.md").write_text(f"---\nlast_updated: {s}\n---\n", encoding="utf-8")


class FreshnessThresholdTests(unittest.TestCase):
    def test_handoff_warns_at_6_days(self):
        # 6 days exceeds the new 5-day handoff threshold; 6 is under the 14-day
        # current-state threshold, so only the handoff warns.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ai(root, handoff_days_old=6, state_days_old=6)
            report = Report()
            check_ai_freshness(root, report)
            handoff_warns = [w for w in report.warnings if "handoff" in w]
            state_warns = [w for w in report.warnings if "current-state" in w]
            self.assertEqual(len(handoff_warns), 1, report.warnings)
            self.assertEqual(len(state_warns), 0, report.warnings)

    def test_fresh_handoff_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ai(root, handoff_days_old=1, state_days_old=1)
            report = Report()
            check_ai_freshness(root, report)
            self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scripts/standards-check/test_freshness.py -v`
Expected: `test_handoff_warns_at_6_days` FAILS — at the current threshold of 7, a 6-day-old handoff does not warn (`len(handoff_warns)` is 0, not 1).

- [ ] **Step 3: Lower the threshold**

In `scripts/standards-check/checks/structural.py`, change:
```python
HANDOFF_STALE_DAYS = 7
```
to:
```python
HANDOFF_STALE_DAYS = 5
```
Leave `CURRENT_STATE_STALE_DAYS = 14` unchanged.

- [ ] **Step 4: Run test to verify it passes**

Run: `python scripts/standards-check/test_freshness.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Confirm the kit itself stays green**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)` (the kit's own `ai/handoff.md` is recent, so no new error; a freshness *warning* is acceptable and does not fail the build).

- [ ] **Step 6: Commit**

```bash
git add scripts/standards-check/checks/structural.py scripts/standards-check/test_freshness.py
git commit -m "feat(slice-4): tighten handoff freshness threshold to 5 days"
```

---

### Task 6: Louder Stop-hook nudge + staleness trigger

**Files:**
- Modify: `scripts/update-handoff/update_handoff.py`
- Modify: `scripts/update-handoff/test_update_handoff.py`

- [ ] **Step 1: Write the failing test**

Add these two tests to `scripts/update-handoff/test_update_handoff.py` inside `class CheckModeTests` (the existing helpers `make_git_repo`, `write_handoff`, `run` are already in that file; do not redefine them). Add `from datetime import date, timedelta` to the file's imports if not present:

```python
    def test_advisory_when_handoff_is_stale_even_without_new_work(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))  # initial commit dated 2020-01-01
            # Handoff written 10 days ago (older than the 5-day threshold); no commits since.
            stale = (date.today() - timedelta(days=10)).isoformat() + "T00:00:00+00:00"
            write_handoff(tmp, stale)
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("update-handoff:", result.stderr.lower())
            self.assertIn("days old", result.stderr.lower())

    def test_fresh_handoff_with_no_work_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            fresh = (date.today() - timedelta(days=1)).isoformat() + "T00:00:00+00:00"
            write_handoff(tmp, fresh)
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")
```

- [ ] **Step 2: Run to verify the new test fails**

Run: `python scripts/update-handoff/test_update_handoff.py -v`
Expected: `test_advisory_when_handoff_is_stale_even_without_new_work` FAILS — the current `cmd_check` only nudges on commits/modified files, so a stale-but-idle handoff produces no output.

- [ ] **Step 3: Add the staleness trigger + louder wording**

In `scripts/update-handoff/update_handoff.py`:

(a) Change the datetime import line:
```python
from datetime import datetime
```
to:
```python
from datetime import date, datetime, timedelta
```

(b) Add this constant just below `WRITTEN_RE` (near the top, after the existing module constants):
```python
# Mirrors standards-check HANDOFF_STALE_DAYS — keep in sync.
HANDOFF_STALE_DAYS = 5
```

(c) Add this helper above `cmd_check`:
```python
def _is_stale(written_ts: str, max_days: int) -> bool:
    """True if the handoff `written:` date is older than max_days. Tolerant of bad input."""
    date_part = written_ts.split("T")[0]
    try:
        parsed = date.fromisoformat(date_part)
    except ValueError:
        return False
    return date.today() - parsed > timedelta(days=max_days)
```

(d) Replace the BODY of `cmd_check` from the `if commit_count == 0 and file_count == 0:` line to the end of the function with:
```python
    stale = bool(prior_ts) and _is_stale(prior_ts, HANDOFF_STALE_DAYS)
    if commit_count == 0 and file_count == 0 and not stale:
        return
    clauses = []
    if commit_count or file_count:
        clauses.append(f"{commit_count} commits + {file_count} modified files since last handoff")
    if stale:
        clauses.append(f"handoff is >{HANDOFF_STALE_DAYS} days old")
    detail = "; ".join(clauses)
    msg = f"update-handoff: {detail} — run /update-handoff before ending the session"
    print(msg, file=sys.stderr)
```

This preserves the existing substrings the other tests assert (`update-handoff:`, `N commits`, `N modified`, `/update-handoff`) while making the wording imperative ("run") and adding the staleness clause.

- [ ] **Step 4: Run the full hook suite to verify all pass**

Run: `python scripts/update-handoff/test_update_handoff.py -v`
Expected: PASS — the two new tests plus all pre-existing ones (`test_advisory_when_commits_pending`, `test_advisory_when_modified_files_present`, `test_silent_when_no_work_happened`, etc.). If a pre-existing test broke, your message wording dropped a required substring — restore it.

- [ ] **Step 5: Commit**

```bash
git add scripts/update-handoff/update_handoff.py scripts/update-handoff/test_update_handoff.py
git commit -m "feat(slice-4): louder handoff nudge + staleness trigger in hook"
```

---

### Task 7: `checks/discovery.py` — shipped `promoted_to`-existence check

**Files:**
- Create: `scripts/standards-check/checks/discovery.py`
- Create: `scripts/standards-check/test_discovery.py`
- Modify: `scripts/standards-check/check.py` (add `discovery.run` to `CHECKS`)

- [ ] **Step 1: Write the failing test**

Create `scripts/standards-check/test_discovery.py`:

```python
"""Tests for the discovery promoted_to-existence check."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.discovery import run  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


def _disc(root: Path, name: str, status: str, promoted_to: str = None) -> None:
    p = root / "docs" / "discovery" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"status: {status}"]
    if promoted_to is not None:
        lines.append(f"promoted_to: {promoted_to}")
    lines += ["---", "", "# note", ""]
    p.write_text("\n".join(lines), encoding="utf-8")


class DiscoveryCheckTests(unittest.TestCase):
    def test_promoted_with_existing_target_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs" / "01-prd.md").parent.mkdir(parents=True, exist_ok=True)
            (root / "docs" / "01-prd.md").write_text("# prd\n", encoding="utf-8")
            _disc(root, "2026-05-01-acme.md", "promoted", "docs/01-prd.md")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_promoted_with_missing_target_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _disc(root, "2026-05-01-acme.md", "promoted", "docs/does-not-exist.md")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")
            self.assertIn("does not exist", findings[0].message)

    def test_promoted_with_missing_target_is_warn_in_adopter(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _disc(root, "2026-05-01-acme.md", "promoted", "docs/nope.md")
            findings = run(root, _ctx(root, adopter=True))
            self.assertEqual(findings[0].severity, "warn")

    def test_promoted_with_empty_target_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _disc(root, "2026-05-01-acme.md", "promoted", "")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertIn("empty", findings[0].message)

    def test_raw_item_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _disc(root, "2026-05-01-acme.md", "raw")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_readme_and_missing_dir_are_silent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(run(root, _ctx(root)), [])  # no docs/discovery
            (root / "docs" / "discovery").mkdir(parents=True)
            (root / "docs" / "discovery" / "README.md").write_text(
                "---\nstatus: promoted\npromoted_to: nowhere.md\n---\n", encoding="utf-8"
            )
            self.assertEqual(run(root, _ctx(root)), [])  # README excluded


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python scripts/standards-check/test_discovery.py -v`
Expected: FAIL — `ImportError: cannot import name 'run' from 'checks.discovery'`.

- [ ] **Step 3: Write `checks/discovery.py`**

```python
"""Discovery promoted_to-existence check: every `status: promoted` item under
docs/discovery/ must have a `promoted_to:` path that exists. Forward-looking —
catches a promotion pointing at a deleted or renamed doc.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "discovery"
DEFAULT_SEVERITY = "error"

# Allow a leading HTML comment (discovery templates ship one) before the frontmatter.
_FRONTMATTER_RE = re.compile(r"\A(?:\s*<!--.*?-->\s*)?---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        hash_pos = val.find("#")
        if hash_pos != -1:
            val = val[:hash_pos]
        fm[key.strip()] = val.strip()
    return fm


def _iter_discovery(root: Path):
    base = root / "docs" / "discovery"
    if not base.is_dir():
        return
    for path in sorted(base.rglob("*.md")):
        if path.name == "README.md":
            continue
        if "templates" in path.parts:
            continue
        yield path


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    findings = []
    for path in _iter_discovery(root):
        rel = path.relative_to(root).as_posix()
        fm = _parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if fm.get("status") != "promoted":
            continue
        target = fm.get("promoted_to", "")
        if not target:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: status: promoted but promoted_to: is empty"))
            continue
        if not (root / target).exists():
            findings.append(Finding(CHECK_ID, severity, f"{rel}: promoted_to: {target} does not exist"))
    return findings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python scripts/standards-check/test_discovery.py -v`
Expected: PASS (6 tests). Fix `discovery.py` until green.

- [ ] **Step 5: Wire `discovery.run` into the orchestrator**

In `scripts/standards-check/check.py`:
- change `from checks import structural, links, content, skills` to `from checks import structural, links, content, skills, discovery`
- change `CHECKS = [structural.run, links.run, content.run, skills.run]` to `CHECKS = [structural.run, links.run, content.run, skills.run, discovery.run]`

- [ ] **Step 6: Confirm the kit stays green**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)` — the kit's `docs/discovery/` has only `README.md` (excluded), so the discovery check finds nothing.

- [ ] **Step 7: Commit**

```bash
git add scripts/standards-check/checks/discovery.py scripts/standards-check/test_discovery.py scripts/standards-check/check.py
git commit -m "feat(slice-4): add discovery promoted_to-existence check"
```

---

### Task 8: Payload regression tests (discovery ships, kit-guards does NOT)

**Files:**
- Modify: `tests/test_payload_includes_checks.py`

- [ ] **Step 1: Extend the payload test**

In `tests/test_payload_includes_checks.py`, add `scripts/standards-check/checks/discovery.py` to the `expected` tuple in `test_checks_package_modules_are_payload`, and add a new test asserting the kit-only workflow does NOT ship. The file already imports `iter_payload` and defines `REPO_ROOT`. Add the discovery line:

```python
            "scripts/standards-check/checks/discovery.py",
```
(append it inside the existing `for expected in ( ... )` tuple, after the `_text.py` entry)

and add this test method to the `PayloadIncludesChecksTests` class:

```python
    def test_kit_only_workflow_not_in_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        self.assertNotIn(".github/workflows/kit-guards.yml", rels)
        # The shipped CI workflow IS in the payload (sanity check on the assertion).
        self.assertIn(".github/workflows/repo-standards.yml", rels)
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python tests/test_payload_includes_checks.py -v`
Expected: PASS (3 tests) — discovery.py ships (it's under the wholesale `scripts/` walk), kit-guards.yml does not.

- [ ] **Step 3: Commit**

```bash
git add tests/test_payload_includes_checks.py
git commit -m "test(slice-4): assert discovery ships + kit-guards stays kit-only"
```

---

### Task 9: Docs + version bump to v0.8.0 (coherence-verified)

**Files:**
- Modify: `docs/STANDARDS.md`, `src/standards/__about__.py`, `CHANGELOG.md`, `AGENTS.md`

- [ ] **Step 1: Document the new behaviors in `docs/STANDARDS.md`**

Open `docs/STANDARDS.md`. In the "Content checks (v2)" section added in Plan 1, add a bullet for the discovery check (keep the existing three bullets):

```markdown
- **Discovery** — every `status: promoted` item under `docs/discovery/` must have a `promoted_to:` path that exists.
```

Then, where the freshness/`ai/` behavior is described (search for `handoff` and `stale`/`days`), update any mention of the **7-day handoff** threshold to **5 days**. If no such number is documented, add a one-line note near the standards-check description:

```markdown
The `ai/` freshness check warns when `current-state.md` is older than 14 days or `handoff.md` older than 5 days (advisory only — never fails CI).
```

Also add a short note documenting the kit-only coherence guard (near the CI description):

```markdown
The kit's own release is guarded by `tools/check_version_coherence.py` (run in `kit-guards.yml` and `release.yml`): `src/standards/__about__.py`, the CHANGELOG top entry, and the `AGENTS.md` Kit-version must agree, and a release tag must match the version. This guard is kit-internal and is not shipped to adopters.
```

- [ ] **Step 2: Bump the version source of truth**

Edit `src/standards/__about__.py`: `__version__ = "0.7.0"` → `__version__ = "0.8.0"`.

- [ ] **Step 3: Add the CHANGELOG entry + reference link**

In `CHANGELOG.md`, add a new section above `## [0.7.0] - 2026-05-30`:

```markdown
## [0.8.0] - 2026-05-31

### Added
- Version-coherence guard (`tools/check_version_coherence.py`) wired into a kit-only `kit-guards.yml` workflow and the release workflow (which also verifies the tag matches the version).
- `standards-check` discovery check: every `status: promoted` item must have a `promoted_to:` path that exists.

### Changed
- Handoff freshness warning tightened from 7 to 5 days; the Stop-hook nudge is louder and also fires on a stale handoff.
```

Add the matching reference link at the bottom, mirroring the existing format (`[0.7.0]: https://example.invalid/releases/tag/v0.7.0`):

```markdown
[0.8.0]: https://example.invalid/releases/tag/v0.8.0
```
Place it directly above the `[0.7.0]:` line.

- [ ] **Step 4: Bump the AGENTS.md Kit-version markers**

Run: `grep -n "0.7.0" AGENTS.md`
Edit both markers inside the `kit-managed: agents-core` block: the sentinel `(v0.7.0)` → `(v0.8.0)` and the `- Kit version: **0.7.0**` line → `**0.8.0**`. (There were exactly these two in Plan 1; confirm with the grep and change only managed-block version markers.)

- [ ] **Step 5: Verify coherence + everything green**

Run: `python tools/check_version_coherence.py`
Expected: `Version coherence: OK` (all four sites now at 0.8.0 — the tool verifies the bump it is shipping).

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s)`.

Run: `python tools/run_tests.py`
Expected: all suites pass (including the refactored `test_version.py`, which now passes because coherence holds at 0.8.0).

- [ ] **Step 6: Commit**

```bash
git add docs/STANDARDS.md src/standards/__about__.py CHANGELOG.md AGENTS.md
git commit -m "docs(slice-4): document guardrails + bump to v0.8.0"
```

---

## Self-Review

**Spec coverage:**
- §A1 coherence tool (`find_incoherences` + CLI + `--tag`) → Task 1 ✓
- §A2 non-shipped `kit-guards.yml` → Task 3 (+ Task 8 asserts non-shipping) ✓
- §A3 `release.yml` tag gate → Task 4 ✓
- §A4 `test_version.py` refactor off the literal → Task 2 ✓
- §B1 `HANDOFF_STALE_DAYS` 7→5 → Task 5 ✓
- §B2 louder nudge + staleness trigger → Task 6 ✓
- §C1 shipped `checks/discovery.py` + wiring → Task 7 ✓
- §C2 discovery tests → Task 7 ✓
- payload assertion (discovery ships) → Task 8 ✓
- docs + v0.8.0 (coherence-verified) → Task 9 ✓

**Placeholder scan:** No "TBD"/"implement later"; every code step has complete code. Task 9 Step 1 is data-driven on the doc's current wording but gives exact insertion text — acceptable for a docs edit.

**Type consistency:** `find_incoherences(root, tag=None) -> list[str]` used identically in Tasks 1, 2. `Finding(check_id, severity, message)`, `Context(root, adopter_mode, overrides)`, `resolve_severity(check_id, default, ctx)`, and `run(root, ctx) -> list` match the Plan 1 framework (Task 7). `HANDOFF_STALE_DAYS = 5` appears in both `checks/structural.py` (Task 5) and `update_handoff.py` (Task 6) with an explicit "keep in sync" comment. Check IDs stable: existing `structural`/`links`/`placeholder`/`changelog`/`skill-format` plus new `discovery`.

**Out of scope (later):** external-link liveness, doc-freshness reports, louder stale-raw in CI, freshness-as-error (rejected), Plan 3 (skills polish + `/standards-check` command).
