# Distribution Build — Plan 1: Packaging + `standards init` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Repo-Standards-Kit installable from PyPI and add a `standards init` command that vendors the kit into a target repo and records a version+hash marker.

**Architecture:** *Additive* packaging — add a new `src/standards/` package containing only the distribution CLI; bundle the existing kit content (templates, `docs/STANDARDS.md`, `scripts/`, workflows, AI wrappers) into the wheel as **package data** via hatchling `force-include`, mirroring the downstream target layout under `standards/_payload/`. The existing 57 tests and `scripts/` are **not moved** — they keep working in-repo and double as the bundled payload. The payload is an **explicitly enumerated set of paths** (`PAYLOAD_DIRS` + `PAYLOAD_FILES` in `manifest.py`, mirrored by the `force-include` map) — never "everything under a root", so `.git/`, `src/`, `tests/`, and the kit's own `ai/`/`docs/rfcs/` are never copied into adopters. `payload_root()` returns the bundled `_payload` when present (installed wheel) and falls back to the **repo root** when running from source (so dev/tests use the real files — zero duplication). `init` enumerates the payload via `manifest.iter_payload(payload_root())`, classifies each file (kit-tracked vs scaffold-once), copies accordingly, and writes a JSON marker.

**Tech Stack:** Python ≥3.9 stdlib only (runtime zero-dependency); hatchling build backend; `importlib.resources`, `hashlib`, `json`, `argparse`, `shutil`, `pathlib`. Tests: stdlib `unittest` (matches the kit's existing convention).

**Scope of this plan:** ADR-0009 + packaging + `standards init`. **Out of scope (later plans):** Plan 2 = `standards update` sync engine + the partial/managed-region class (markers in `AGENTS.md`/`CLAUDE.md`/`copilot-instructions.md`); Plan 3 = PyPI Trusted-Publishing release workflow + `v0.5.0` cut. Because `update` and the partial class are deferred, **this plan treats `AGENTS.md`/`CLAUDE.md`/`copilot-instructions.md` as kit-tracked** (copied verbatim); Plan 2 reclassifies them to partial and introduces the sentinels.

**Decisions locked (record in ADR-0009):**
- PyPI distribution name: `repo-standards-kit`; import package: `standards`; console script: `standards`.
- New version: `0.5.0` (feature minor).
- Marker file: `.standards-kit.json` at target repo root (JSON, not TOML — stdlib has no TOML writer; keeps zero-dependency).
- Marker schema: `{ "kit_version": str, "profile": str, "adopted": "YYYY-MM-DD", "tracked": {relpath: sha256}, "managed": {} }` (`managed` reserved for Plan 2).

---

## File Structure

| Path | Responsibility |
|---|---|
| `pyproject.toml` (create, repo root) | Build config: hatchling, metadata, `[project.scripts]` entry point, `force-include` payload map. |
| `src/standards/__init__.py` (create) | Package marker. |
| `src/standards/__about__.py` (create) | Single source of `__version__`. |
| `src/standards/payload.py` (create) | Locate the kit content: bundled `_payload` (wheel) or repo root (dev) via `importlib.resources` + sentinel walk. |
| `src/standards/manifest.py` (create) | Enumerate the payload (`PAYLOAD_DIRS`/`PAYLOAD_FILES` + `iter_payload`); classify a payload-relative path → `"kit-tracked"` / `"scaffold-once-source"`; map scaffold-once sources → target paths. |
| `src/standards/marker.py` (create) | `sha256_file`, `read_marker`, `write_marker` for `.standards-kit.json`. |
| `src/standards/init.py` (create) | `run_init(target, profile, force)` — the copy + marker logic. |
| `src/standards/cli.py` (create) | `argparse` dispatch; `main()`; the `init` subcommand. |
| `tests/test_payload.py` (create) | Payload accessor finds bundled files. |
| `tests/test_manifest.py` (create) | Classification + scaffold mapping. |
| `tests/test_marker.py` (create) | Hash + marker round-trip. |
| `tests/test_init.py` (create) | `run_init` behavior into temp repos. |
| `tests/test_cli.py` (create) | `standards init` end-to-end via subprocess. |
| `docs/decisions/0009-*.md` (create via `new-adr`) | Durable decision record. |
| `CHANGELOG.md` (modify) | `## [0.5.0]` entry. |

> Tests live under a new top-level `tests/` (the distribution package's own suite), distinct from the existing per-script `scripts/**/test_*.py`. Keep both; the CI step in Plan 3 will run both trees.

---

## Task 1: Record the decision (ADR-0009)

**Files:**
- Create: `docs/decisions/0009-<slug>.md` (via the kit's own `new-adr` script)

- [ ] **Step 1: Generate the ADR by dogfooding `new-adr`**

Run:
```bash
python scripts/new-doc/new-adr.py "Distribute the kit as a PyPI standards CLI with vendored-copy sync"
```
Expected: `Created docs/decisions/0009-distribute-the-kit-as-a-pypi-standards-cli-with-vendored-copy-sync.md`

- [ ] **Step 2: Fill the ADR body**

Set `status: Accepted`, `date: 2026-05-29`, `deciders: swanson-dev`. In **Context** reference [RFC-0001](../rfcs/0001-what-is-the-kit-s-distribution-and-upgrade-mechanism/rfc.md). In **Decision** record: PyPI package `repo-standards-kit`, console `standards`, `init`/`update` subcommands, three-class vendored sync (kit-tracked / scaffold-once / partial managed-region), `.standards-kit.json` version+hash marker, non-destructive sidecar conflicts, `pipx run`/`uvx` execution. In **Consequences** note the JSON-not-TOML correction and that `update` + the partial class land in Plan 2.

- [ ] **Step 3: Verify frontmatter parses and standards-check passes**

Run: `python scripts/standards-check/check.py`
Expected: `Standards check: 0 error(s), 0 warning(s)`
(If the inline-comment fix from commit `e68e5d0` is present, the generated `status: Accepted   # ...` line parses correctly.)

- [ ] **Step 4: Commit**

```bash
git add docs/decisions/0009-*.md
git commit -m "docs(slice-3): ADR-0009 record PyPI standards-CLI distribution decision"
```

---

## Task 2: Package skeleton + version

**Files:**
- Create: `src/standards/__init__.py`
- Create: `src/standards/__about__.py`
- Create: `tests/test_version.py`

- [ ] **Step 1: Write the failing test**

`tests/test_version.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class VersionTests(unittest.TestCase):
    def test_version_is_semver_string(self):
        from standards.__about__ import __version__
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
        self.assertEqual(__version__, "0.5.0")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_version.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards'`

- [ ] **Step 3: Create the package**

`src/standards/__about__.py`:
```python
__version__ = "0.5.0"
```

`src/standards/__init__.py`:
```python
"""repo-standards-kit distribution CLI."""
from standards.__about__ import __version__

__all__ = ["__version__"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_version.py`
Expected: PASS (`Ran 1 test ... OK`)

- [ ] **Step 5: Commit**

```bash
git add src/standards/__init__.py src/standards/__about__.py tests/test_version.py
git commit -m "feat(dist): add standards package skeleton with __version__ 0.5.0"
```

---

## Task 3: `pyproject.toml` with hatchling + payload bundling

**Files:**
- Create: `pyproject.toml`

This task is configuration; it is verified by building and inspecting the wheel rather than by a unit test.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "repo-standards-kit"
dynamic = ["version"]
description = "Team Repository Standards Kit — adopt and stay current with the standards via a single CLI."
readme = "README.md"
license = "MIT"
requires-python = ">=3.9"
authors = [{ name = "swanson-dev" }]
keywords = ["standards", "scaffold", "adr", "rfc", "governance"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = []   # runtime is stdlib-only by design

[project.scripts]
standards = "standards.cli:main"

[project.urls]
Repository = "https://github.com/swanson-dev/Repo-Standards-Kit"

[tool.hatch.version]
path = "src/standards/__about__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/standards"]

# Bundle the kit content into the wheel, mirroring the downstream target layout
# under standards/_payload/ so init can copy by relative path.
[tool.hatch.build.targets.wheel.force-include]
"docs/templates" = "standards/_payload/docs/templates"
"docs/STANDARDS.md" = "standards/_payload/docs/STANDARDS.md"
"scripts" = "standards/_payload/scripts"
".github/workflows/repo-standards.yml" = "standards/_payload/.github/workflows/repo-standards.yml"
".github/prompts" = "standards/_payload/.github/prompts"
".github/copilot-instructions.md" = "standards/_payload/.github/copilot-instructions.md"
".github/pull_request_template.md" = "standards/_payload/.github/pull_request_template.md"
".claude" = "standards/_payload/.claude"
"AGENTS.md" = "standards/_payload/AGENTS.md"
"CLAUDE.md" = "standards/_payload/CLAUDE.md"

[tool.hatch.build.targets.sdist]
exclude = ["/.git", "/dist", "/docs/superpowers"]
```

> **Note:** `force-include` copies the on-disk tree, so build from a **clean checkout** to avoid bundling `__pycache__` (already gitignored). Plan 3's CI builds from a fresh clone, satisfying this.

- [ ] **Step 2: Build the wheel and inspect contents**

Run:
```bash
python -m pip install --quiet build
python -m build --wheel
python -c "import zipfile,glob; z=zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1]); print('\n'.join(n for n in z.namelist() if '_payload' in n)[:2000])"
```
Expected: lines including `standards/_payload/docs/templates/adr-template.md`, `standards/_payload/docs/STANDARDS.md`, `standards/_payload/scripts/standards-check/check.py`, and `standards/_payload/AGENTS.md`. Also confirm the wheel's `entry_points.txt` lists `standards = standards.cli:main` (the build will warn if `cli.py` is missing — that is expected until Task 7; the wheel still builds).

> **No editable install needed.** Later tasks import `standards` from `src/` (each test inserts `src` on `sys.path`), and `payload_root()` falls back to the repo root in source mode — so the suite runs without installing. The real install path (`pipx run`/`uvx`) is exercised in Plan 3. Keep the built wheel from Step 2 only as a force-include sanity check; you may delete `dist/` afterward.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat(dist): add pyproject.toml — hatchling build, entry point, payload bundle"
```

---

## Task 4: Payload accessor

**Files:**
- Create: `src/standards/payload.py`
- Create: `tests/test_payload.py`

- [ ] **Step 1: Write the failing test**

`tests/test_payload.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class PayloadTests(unittest.TestCase):
    def test_payload_root_contains_known_files(self):
        from standards.payload import payload_root
        root = payload_root()
        self.assertTrue((root / "docs" / "templates" / "adr-template.md").is_file())
        self.assertTrue((root / "docs" / "STANDARDS.md").is_file())
        self.assertTrue((root / "scripts" / "standards-check" / "check.py").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_payload.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards.payload'`

> No install needed: in source mode `_payload` does not exist, so `payload_root()` falls back to the repo root (found by walking up to the `docs/STANDARDS.md` sentinel), whose real files satisfy the assertions.

- [ ] **Step 3: Write the implementation**

`src/standards/payload.py`:
```python
"""Locate the kit content: bundled `_payload` in a wheel, or the repo root in dev."""
from __future__ import annotations

from importlib import resources
from pathlib import Path

_SENTINEL = "docs/STANDARDS.md"


def _repo_root_from_source() -> Path:
    """Walk up from this file to the dir containing the sentinel (the repo root)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / _SENTINEL).is_file():
            return parent
    return here.parents[2]  # src/standards/payload.py -> repo root by layout


def payload_root() -> Path:
    """Directory holding the kit payload.

    An installed wheel bundles the content under `standards/_payload` (ADR-0009).
    Running from source there is no `_payload`, so fall back to the repo root,
    whose real files ARE the payload (kept DRY — no duplicated content).
    """
    bundled = Path(str(resources.files("standards") / "_payload"))
    if (bundled / _SENTINEL).is_file():
        return bundled
    return _repo_root_from_source()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_payload.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/standards/payload.py tests/test_payload.py
git commit -m "feat(dist): add payload accessor for bundled kit content"
```

---

## Task 5: Ownership manifest

**Files:**
- Create: `src/standards/manifest.py`
- Create: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing test**

`tests/test_manifest.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class ManifestTests(unittest.TestCase):
    def test_templates_are_kit_tracked(self):
        from standards.manifest import classify
        self.assertEqual(classify("docs/templates/adr-template.md"), "kit-tracked")
        self.assertEqual(classify("docs/STANDARDS.md"), "kit-tracked")
        self.assertEqual(classify("scripts/standards-check/check.py"), "kit-tracked")

    def test_known_scaffold_targets(self):
        from standards.manifest import SCAFFOLD_ONCE
        # source-template -> target path
        self.assertEqual(
            SCAFFOLD_ONCE["docs/templates/ai-starters/current-state.md"],
            "ai/current-state.md",
        )
        self.assertEqual(
            SCAFFOLD_ONCE["docs/templates/STANDARDS-CHECKLIST.md.template"],
            "docs/STANDARDS-CHECKLIST.md",
        )

    def test_ai_starters_dir_excluded_from_kit_tracked_copy(self):
        # ai-starters are sources for scaffold-once, not copied verbatim as templates
        from standards.manifest import is_excluded_from_tracked
        self.assertTrue(is_excluded_from_tracked("docs/templates/ai-starters/current-state.md"))
        self.assertFalse(is_excluded_from_tracked("docs/templates/adr-template.md"))

    def test_iter_payload_yields_known_files_and_excludes_non_payload(self):
        from standards.manifest import iter_payload
        from standards.payload import payload_root
        rels = {rel for _full, rel in iter_payload(payload_root())}
        # enumerated payload is present
        self.assertIn("docs/templates/adr-template.md", rels)
        self.assertIn("docs/STANDARDS.md", rels)
        self.assertIn("scripts/standards-check/check.py", rels)
        self.assertIn("AGENTS.md", rels)
        # non-payload paths are never yielded
        self.assertFalse(any(r.startswith(".git/") for r in rels))
        self.assertFalse(any(r.startswith("src/") for r in rels))
        self.assertFalse(any(r.startswith("tests/") for r in rels))
        self.assertFalse(any(r == "ai/handoff.md" for r in rels))
        self.assertFalse(any(r.endswith(".pyc") for r in rels))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_manifest.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards.manifest'`

- [ ] **Step 3: Write the implementation**

`src/standards/manifest.py`:
```python
"""Payload enumeration + ownership classification for kit files.

Plan 1 recognizes two classes:
  - kit-tracked  : kit owns it; update may overwrite (Plan 2).
  - scaffold-once: kit seeds it once; downstream owns it thereafter.

The partial / managed-region class arrives in Plan 2; until then AGENTS.md,
CLAUDE.md, and .github/copilot-instructions.md are treated as kit-tracked.

The payload is an explicitly enumerated set (mirrored by the force-include map in
pyproject.toml), NOT "everything under a root" — so .git/, src/, tests/, and the
kit's own ai/ and docs/rfcs/ are never copied into adopters.
"""
from __future__ import annotations

import os
from pathlib import Path

# Directories whose entire contents are payload (relative to payload root).
PAYLOAD_DIRS: tuple[str, ...] = (
    "docs/templates",
    "scripts",
    ".github/prompts",
    ".claude",
)

# Individual payload files (relative to payload root).
PAYLOAD_FILES: tuple[str, ...] = (
    "docs/STANDARDS.md",
    ".github/workflows/repo-standards.yml",
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
    "AGENTS.md",
    "CLAUDE.md",
)

# Source template (relative to payload root) -> target path (relative to repo root).
SCAFFOLD_ONCE: dict[str, str] = {
    "docs/templates/ai-starters/current-state.md": "ai/current-state.md",
    "docs/templates/ai-starters/handoff.md": "ai/handoff.md",
    "docs/templates/ai-starters/next-actions.md": "ai/next-actions.md",
    "docs/templates/ai-starters/open-questions.md": "ai/open-questions.md",
    "docs/templates/STANDARDS-CHECKLIST.md.template": "docs/STANDARDS-CHECKLIST.md",
}

# Payload files that are scaffold-once *sources* and must not be copied verbatim
# into the target as kit-tracked files.
_TRACKED_EXCLUSIONS = set(SCAFFOLD_ONCE.keys())


def is_excluded_from_tracked(rel: str) -> bool:
    """True if a payload file is a scaffold-once source (not a verbatim tracked copy)."""
    return rel in _TRACKED_EXCLUSIONS


def classify(rel: str) -> str:
    """Classify a payload-relative path. Plan 1: everything not excluded is kit-tracked."""
    if rel in _TRACKED_EXCLUSIONS:
        return "scaffold-once-source"
    return "kit-tracked"


def iter_payload(root: Path):
    """Yield (absolute_path, payload_relative_posix) for every enumerated payload file.

    Only PAYLOAD_DIRS + PAYLOAD_FILES are read; __pycache__ dirs and *.pyc files
    are skipped so build artifacts never leak into adopters.
    """
    root = Path(root)
    for d in PAYLOAD_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for name in files:
                if name.endswith(".pyc"):
                    continue
                full = Path(dirpath) / name
                yield full, full.relative_to(root).as_posix()
    for f in PAYLOAD_FILES:
        full = root / f
        if full.is_file():
            yield full, Path(f).as_posix()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_manifest.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/standards/manifest.py tests/test_manifest.py
git commit -m "feat(dist): add ownership manifest (kit-tracked + scaffold-once)"
```

---

## Task 6: Marker module

**Files:**
- Create: `src/standards/marker.py`
- Create: `tests/test_marker.py`

- [ ] **Step 1: Write the failing test**

`tests/test_marker.py`:
```python
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class MarkerTests(unittest.TestCase):
    def test_sha256_file_is_stable(self):
        from standards.marker import sha256_file
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.txt"
            p.write_bytes(b"hello\n")  # binary write: LF-only, platform-neutral on Windows
            self.assertEqual(
                sha256_file(p),
                "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03",
            )

    def test_write_then_read_round_trip(self):
        from standards.marker import read_marker, write_marker
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_marker(root, kit_version="0.5.0", profile="library",
                         adopted="2026-05-29",
                         tracked={"docs/STANDARDS.md": "abc"})
            data = read_marker(root)
            self.assertEqual(data["kit_version"], "0.5.0")
            self.assertEqual(data["profile"], "library")
            self.assertEqual(data["tracked"], {"docs/STANDARDS.md": "abc"})
            self.assertEqual(data["managed"], {})

    def test_read_missing_returns_none(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(read_marker(Path(d)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_marker.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards.marker'`

- [ ] **Step 3: Write the implementation**

`src/standards/marker.py`:
```python
"""Read/write the `.standards-kit.json` adoption marker."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MARKER_NAME = ".standards-kit.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def read_marker(root: Path) -> dict | None:
    p = root / MARKER_NAME
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def write_marker(root: Path, *, kit_version: str, profile: str, adopted: str,
                 tracked: dict[str, str], managed: dict[str, str] | None = None) -> None:
    data = {
        "kit_version": kit_version,
        "profile": profile,
        "adopted": adopted,
        "tracked": dict(sorted(tracked.items())),
        "managed": dict(sorted((managed or {}).items())),
    }
    (root / MARKER_NAME).write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_marker.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/standards/marker.py tests/test_marker.py
git commit -m "feat(dist): add .standards-kit.json marker read/write + sha256"
```

---

## Task 7: `run_init` core logic

**Files:**
- Create: `src/standards/init.py`
- Create: `tests/test_init.py`

- [ ] **Step 1: Write the failing test**

`tests/test_init.py`:
```python
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class InitTests(unittest.TestCase):
    def _run(self, target, **kw):
        from standards.init import run_init
        return run_init(target, **kw)

    def test_copies_tracked_and_writes_marker(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            self.assertTrue((target / "docs" / "templates" / "adr-template.md").is_file())
            self.assertTrue((target / "docs" / "STANDARDS.md").is_file())
            marker = read_marker(target)
            self.assertEqual(marker["profile"], "library")
            self.assertIn("docs/STANDARDS.md", marker["tracked"])
            # ai-starter sources are NOT copied verbatim into docs/templates/ai-starters
            # as tracked files; they are scaffolded to ai/.
            self.assertTrue((target / "ai" / "current-state.md").is_file())

    def test_scaffold_once_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "ai").mkdir()
            (target / "ai" / "current-state.md").write_text("MINE\n", encoding="utf-8")
            self._run(target, profile="application", adopted="2026-05-29")
            self.assertEqual(
                (target / "ai" / "current-state.md").read_text(encoding="utf-8"), "MINE\n"
            )

    def test_profile_written_into_checklist(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="infra", adopted="2026-05-29")
            checklist = (target / "docs" / "STANDARDS-CHECKLIST.md").read_text(encoding="utf-8")
            self.assertIn("infra", checklist)

    def test_refuses_reinit_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="data", adopted="2026-05-29")
            with self.assertRaises(FileExistsError):
                self._run(target, profile="data", adopted="2026-05-29")
            # with force it succeeds
            self._run(target, profile="data", adopted="2026-05-29", force=True)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_init.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards.init'`

- [ ] **Step 3: Write the implementation**

`src/standards/init.py`:
```python
"""`standards init` — vendor the kit into a target repo and write the marker."""
from __future__ import annotations

import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.manifest import SCAFFOLD_ONCE, is_excluded_from_tracked, iter_payload
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root

PROFILE_PLACEHOLDER = "<application | library | infra | data>"


def run_init(target: Path, *, profile: str, adopted: str, force: bool = False) -> dict:
    """Copy kit-tracked files + scaffold-once seeds into `target`; write the marker.

    Returns the marker dict. Raises FileExistsError if already adopted and not force.
    """
    target = Path(target)
    if read_marker(target) is not None and not force:
        raise FileExistsError(
            f"{target / MARKER_NAME} exists; pass force=True to re-init"
        )

    src_root = payload_root()
    tracked: dict[str, str] = {}

    for full, rel in iter_payload(src_root):
        if is_excluded_from_tracked(rel):
            continue  # scaffold-once sources handled below
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(full, dest)
        tracked[rel] = sha256_file(dest)

    # Scaffold-once: copy source template -> target path only if absent.
    for src_rel, dest_rel in SCAFFOLD_ONCE.items():
        dest = target / dest_rel
        if dest.exists():
            continue
        content = (src_root / src_rel).read_text(encoding="utf-8")
        if dest_rel == "docs/STANDARDS-CHECKLIST.md":
            content = content.replace(PROFILE_PLACEHOLDER, profile)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    write_marker(target, kit_version=__version__, profile=profile,
                 adopted=adopted, tracked=tracked)
    return read_marker(target)
```

> **Profile substitution:** `PROFILE_PLACEHOLDER` must match the literal placeholder string in `docs/templates/STANDARDS-CHECKLIST.md.template`. **Verify it during Step 4** — open the template, confirm the exact token, and adjust `PROFILE_PLACEHOLDER` if it differs (e.g. `**Profile:** <…>`). The `test_profile_written_into_checklist` test guards the outcome.

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_init.py`
Expected: PASS. If `test_profile_written_into_checklist` fails, fix `PROFILE_PLACEHOLDER` to the template's real token and re-run.

- [ ] **Step 5: Commit**

```bash
git add src/standards/init.py tests/test_init.py
git commit -m "feat(dist): implement run_init (copy tracked + scaffold-once + marker)"
```

---

## Task 8: CLI wiring

**Files:**
- Create: `src/standards/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

`tests/test_cli.py`:
```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def _run(self, *args, cwd):
        env = {"PYTHONPATH": str(REPO / "src")}
        import os
        full_env = {**os.environ, **env}
        return subprocess.run(
            [sys.executable, "-m", "standards.cli", *args],
            cwd=str(cwd), capture_output=True, text=True, env=full_env,
        )

    def test_init_subcommand_creates_repo(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".standards-kit.json").is_file())
            self.assertTrue((target / "docs" / "STANDARDS.md").is_file())

    def test_rejects_unknown_profile(self):
        with tempfile.TemporaryDirectory() as d:
            result = self._run("init", "--profile", "bogus", d, cwd=REPO)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_cli.py`
Expected: FAIL — `No module named standards.cli`

- [ ] **Step 3: Write the implementation**

`src/standards/cli.py`:
```python
"""Console entry point for the `standards` CLI."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from standards.__about__ import __version__
from standards.init import run_init

PROFILES = ["application", "library", "infra", "data"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="standards",
                                     description="Adopt and maintain the Repo-Standards-Kit.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Adopt the kit into a target repo.")
    p_init.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_init.add_argument("--profile", required=True, choices=PROFILES)
    p_init.add_argument("--force", action="store_true", help="Re-init even if already adopted.")

    args = parser.parse_args(argv)

    if args.command == "init":
        try:
            run_init(Path(args.target), profile=args.profile,
                     adopted=date.today().isoformat(), force=args.force)
        except FileExistsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"Adopted Repo-Standards-Kit {__version__} ({args.profile}) into {args.target}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_cli.py`
Expected: PASS

- [ ] **Step 5: Confirm the CLI entry point works from source**

Run (PowerShell, from repo root):
```powershell
$env:PYTHONPATH="src"; python -m standards.cli --version
```
Expected: `standards 0.5.0`
(The installed console-script form `standards --version` is verified in Plan 3 once the package is pip-installed; here we exercise the same `main()` via `-m`.)

- [ ] **Step 6: Commit**

```bash
git add src/standards/cli.py tests/test_cli.py
git commit -m "feat(dist): wire standards CLI with init subcommand"
```

---

## Task 9: Full suite + CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run every test suite (existing + new)**

Run:
```bash
for t in scripts/new-doc/test_helpers.py scripts/new-doc/test_cli.py \
         scripts/update-handoff/test_update_handoff.py \
         scripts/promote-discovery/test_promote_discovery.py \
         scripts/standards-check/test_check.py \
         tests/test_version.py tests/test_payload.py tests/test_manifest.py \
         tests/test_marker.py tests/test_init.py tests/test_cli.py; do
  echo "== $t =="; python "$t" 2>&1 | tail -1
done
```
Expected: every line `OK`. (Existing 57 + new ≈ 16 = ~73 tests.)

- [ ] **Step 2: Run standards-check on the kit itself**

Run: `python scripts/standards-check/check.py`
Expected: `Standards check: 0 error(s), 0 warning(s)`

- [ ] **Step 3: Add the CHANGELOG entry**

Prepend under the header in `CHANGELOG.md`:
```markdown
## [0.5.0] - 2026-05-29

### Added
- `pyproject.toml` — the kit is now a `pip`/`pipx`/`uvx`-installable package (`repo-standards-kit`), runtime zero-dependency, hatchling build backend, console entry point `standards`.
- `src/standards/` — distribution CLI: `payload`, `manifest`, `marker`, `init`, `cli` modules.
- `standards init [--profile …] [target]` — adopts the kit into a repo: vendors kit-tracked files, scaffolds `ai/` starters + `docs/STANDARDS-CHECKLIST.md` (profile-filled, copy-if-absent), writes the `.standards-kit.json` version+hash marker.
- `tests/` — distribution-package unit + CLI suite.
- `docs/decisions/0009-…md` — ADR-0009 recording the PyPI standards-CLI distribution decision (RFC-0001).

### Notes
- Marker format is JSON, not the `.standards-kit.toml` named in RFC-0001 (stdlib has no TOML writer; JSON keeps the zero-dependency stance). Recorded in ADR-0009.
- `standards update` and the partial / managed-region ownership class are deferred to Plan 2.
```

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(slice-3): record v0.5.0 (packaging + standards init) in CHANGELOG"
```

---

## Self-Review (completed by plan author)

- **Spec coverage:** RFC §Recommendation → PyPI package (Tasks 2–3), `init` (Tasks 7–8), three-class model (manifest Task 5 — *kit-tracked + scaffold-once only; partial deferred to Plan 2, stated explicitly*), version+hash marker (Task 6). `update`, sidecar conflicts, managed-region splice, and the release workflow are **intentionally out of this plan** (Plans 2–3) — noted up front, not gaps.
- **Placeholder scan:** none — every code/config step shows full content; the one runtime-verified value (`PROFILE_PLACEHOLDER`) has an explicit verification step + a guarding test.
- **Type consistency:** `run_init(target, *, profile, adopted, force)` signature is identical in `init.py`, `cli.py`, and all tests; marker schema keys (`kit_version`/`profile`/`adopted`/`tracked`/`managed`) match across `marker.py` and `init.py`; `payload_root()` returns `Path` everywhere.

---

## Follow-on plans (not in this document)

- **Plan 2 — `standards update` + partial class:** add managed-region sentinels to `AGENTS.md`/`CLAUDE.md`/`.github/copilot-instructions.md`; reclassify them as partial in `manifest.py`; implement `update` (hash-guard kit-tracked overwrite, managed-block splice, non-destructive `<path>.kit-<version>` sidecars, CHANGELOG-on-breaking print, leap-safe content compare). **Also: make first-time `init` non-destructive** — currently `run_init` overwrites pre-existing kit-tracked files (e.g. `AGENTS.md`, `scripts/*`) when no marker exists, a data-loss risk for adopting into a non-empty repo (Copilot, PR #2). Fix with the same hash-guard/sidecar mechanism `update` introduces, so first-init and update share one conflict path rather than a Plan-1 half-measure.
- **Plan 3 — Release + publish:** PyPI Trusted-Publishing (OIDC) GitHub Action on tag-push (`pypa/gh-action-pypi-publish`), CI step running both test trees + a clean-checkout wheel build, then cut `v0.5.0`.
