# Distribution Build — Plan 2: `standards update` + Managed-Region Class Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the third ownership class (partial/managed-region) and a `standards update` command that reconciles a vendored kit against a newer version, plus close the deferred first-init data-loss gap.

**Architecture:** A new `managed.py` handles HTML-comment sentinel blocks (find/splice/hash). `manifest.py` gains a `partial` class for `AGENTS.md`/`CLAUDE.md`/`.github/copilot-instructions.md`, which are restructured so the kit-owned contract lives in one sentinel block and repo-specifics live outside. A new `update.py` reconciles each payload file by class against the target's marker (kit-tracked: hash-guarded overwrite + sidecar; partial: managed-block splice + sidecar; scaffold-once: untouched). `init` records managed-block hashes and gains a non-destructive first-init guard. All non-destructive: conflicts produce `<path>.kit-<version>` sidecars, never silent overwrites.

**Tech Stack:** Python ≥3.9 stdlib only (`re`, `hashlib`, `shutil`, `pathlib`, `argparse`, `json`); stdlib `unittest`. Builds on Plan 1 modules (`payload`, `manifest`, `marker`, `init`, `cli`).

**Ships as:** `0.6.0`.

**Spec:** `docs/superpowers/specs/2026-05-29-standards-update-and-managed-regions-design.md`.

**Note on the spec's "shared hash-compare helper" (B2):** init's guard and `update` use the same *primitives* (`marker.sha256_file`, `managed.block_hash`) but different *comparisons* — the guard compares destination-vs-payload (no marker yet), `update` compares destination-vs-recorded-marker (drift). This plan implements them as distinct functions over shared primitives, not one function. (Refinement of the spec wording; no design change.)

---

## File Structure

| Path | Phase | Responsibility |
|---|---|---|
| `src/standards/managed.py` (create) | A | Sentinel block find / splice / hash. |
| `src/standards/manifest.py` (modify) | A | `PARTIAL_FILES`; `classify` → `"partial"`. |
| `AGENTS.md` (modify) | A | Wrap contract in `agents-core` block; move repo-specifics to `## About this repository`. |
| `CLAUDE.md` (modify) | A | Wrap pointer in `claude-pointer` block. |
| `.github/copilot-instructions.md` (modify) | A | Wrap pointer in `copilot-pointer` block. |
| `src/standards/init.py` (modify) | A, B | Record `managed` hashes for partial files (A); first-init guard (B). |
| `src/standards/update.py` (create) | B | Reconciliation engine `run_update`. |
| `src/standards/cli.py` (modify) | B | `update` subcommand + `--dry-run`. |
| `docs/decisions/0010-*.md` (create) | B | ADR-0010 sentinel convention. |
| `tests/test_managed.py`, `tests/test_manifest.py`, `tests/test_init.py`, `tests/test_update.py`, `tests/test_cli.py` | A, B | Coverage. |
| `CHANGELOG.md` (modify) | B | `## [0.6.0]`. |

---

# PHASE A — Partial / managed-region ownership class

## Task A1: ADR-0010 (sentinel convention)

**Files:** Create `docs/decisions/0010-*.md` via the kit's `new-adr`.

- [ ] **Step 1: Generate**

Run: `python scripts/new-doc/new-adr.py "Managed-region sentinels for partially kit-owned files"`
Expected: `Created docs/decisions/0010-managed-region-sentinels-for-partially-kit-owned-files.md`

- [ ] **Step 2: Fill the body**

Set `status: Accepted`, `date: 2026-05-29`, `deciders: swanson-dev`; remove any inline `<!-- -->` body hints. Record the decision: files that are partially kit-owned (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`) carry exactly **one** HTML-comment-delimited managed block (`<!-- BEGIN kit-managed: <id> (v<ver>) -->` … `<!-- END kit-managed: <id> -->`); `update` rewrites only the inner content; drift is detected by a sha256 of the block recorded in `.standards-kit.json`'s `managed` table; on downstream edits inside the block or missing markers, `update`/`init` write a `<path>.kit-<version>` sidecar instead of overwriting. One block per file for v1 (multi-block deferred). Companion to ADR-0009. Link the spec.

- [ ] **Step 3: Verify**

Run: `python scripts/standards-check/check.py`
Expected: `Standards check: 0 error(s), 0 warning(s)`

- [ ] **Step 4: Commit**

```bash
git add docs/decisions/0010-*.md
git commit -m "docs(slice-3): ADR-0010 managed-region sentinel convention"
```
End the body with: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Task A2: `managed.py` — sentinel block primitives

**Files:** Create `src/standards/managed.py`, `tests/test_managed.py`.

- [ ] **Step 1: Write the failing test**

`tests/test_managed.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

WRAPPED = (
    "# Title\n\n"
    "<!-- BEGIN kit-managed: agents-core (v0.6.0) -->\n"
    "contract body\n"
    "<!-- END kit-managed: agents-core -->\n\n"
    "## About this repository\n"
    "downstream stuff\n"
)


class ManagedTests(unittest.TestCase):
    def test_find_block_returns_inner(self):
        from standards.managed import find_block
        block = find_block(WRAPPED)
        self.assertIsNotNone(block)
        self.assertEqual(block.inner, "contract body")
        self.assertEqual(block.block_id, "agents-core")

    def test_find_block_none_when_absent(self):
        from standards.managed import find_block
        self.assertIsNone(find_block("# Title\n\nno markers here\n"))

    def test_find_block_none_when_unterminated(self):
        from standards.managed import find_block
        self.assertIsNone(find_block("<!-- BEGIN kit-managed: x (v1) -->\nbody\n"))

    def test_splice_replaces_only_inner(self):
        from standards.managed import splice_block
        out = splice_block(WRAPPED, "NEW BODY")
        self.assertIn("NEW BODY", out)
        self.assertNotIn("contract body", out)
        # everything outside the block is preserved byte-for-byte
        self.assertTrue(out.startswith("# Title\n\n"))
        self.assertIn("## About this repository\ndownstream stuff\n", out)

    def test_block_hash_stable_and_changes_with_content(self):
        from standards.managed import block_hash, splice_block
        h1 = block_hash(WRAPPED)
        self.assertEqual(h1, block_hash(WRAPPED))
        self.assertNotEqual(h1, block_hash(splice_block(WRAPPED, "different")))

    def test_block_hash_none_when_absent(self):
        from standards.managed import block_hash
        self.assertIsNone(block_hash("no markers"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, verify FAIL**

Run: `python tests/test_managed.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards.managed'`.

- [ ] **Step 3: Implement**

`src/standards/managed.py`:
```python
"""Single managed-region block per file, delimited by HTML-comment sentinels.

    <!-- BEGIN kit-managed: <id> (v<ver>) -->
    ...kit-owned content...
    <!-- END kit-managed: <id> -->

`update` rewrites only the inner content; drift is detected by hashing the inner
text (recorded in the marker's `managed` table). One block per file (v1).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_BEGIN = re.compile(
    r"<!--\s*BEGIN kit-managed:\s*(?P<id>[\w-]+)\s*\(v[^)]*\)\s*-->", re.MULTILINE
)


@dataclass(frozen=True)
class Block:
    block_id: str
    inner: str          # text between the markers, stripped of the bracketing newlines
    start: int          # index where inner begins (in the source text)
    end: int            # index where inner ends


def _end_pattern(block_id: str) -> re.Pattern:
    return re.compile(rf"<!--\s*END kit-managed:\s*{re.escape(block_id)}\s*-->")


def find_block(text: str) -> Block | None:
    """Locate the single managed block; None if absent, duplicated, or unterminated."""
    begins = list(_BEGIN.finditer(text))
    if len(begins) != 1:
        return None
    b = begins[0]
    end_match = _end_pattern(b.group("id")).search(text, b.end())
    if end_match is None:
        return None
    inner = text[b.end():end_match.start()].strip("\n")
    return Block(block_id=b.group("id"), inner=inner,
                 start=b.end(), end=end_match.start())


def splice_block(text: str, new_inner: str) -> str:
    """Return `text` with the managed block's inner content replaced. Raises if none."""
    block = find_block(text)
    if block is None:
        raise ValueError("no single managed block found")
    return text[:block.start] + "\n" + new_inner + "\n" + text[block.end:]


def block_hash(text: str) -> str | None:
    """sha256 of the managed block's inner content; None if no block."""
    block = find_block(text)
    if block is None:
        return None
    return hashlib.sha256(block.inner.encode("utf-8")).hexdigest()
```

- [ ] **Step 4: Run, verify PASS**

Run: `python tests/test_managed.py`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add src/standards/managed.py tests/test_managed.py
git commit -m "feat(dist): add managed-region sentinel primitives (find/splice/hash)"
```
Trailer: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Task A3: `manifest.py` — add the `partial` class

**Files:** Modify `src/standards/manifest.py`; modify `tests/test_manifest.py`.

- [ ] **Step 1: Add failing test cases**

Append to `tests/test_manifest.py` inside `ManifestTests`:
```python
    def test_partial_files_classified_partial(self):
        from standards.manifest import classify, PARTIAL_FILES
        self.assertIn("AGENTS.md", PARTIAL_FILES)
        self.assertIn("CLAUDE.md", PARTIAL_FILES)
        self.assertIn(".github/copilot-instructions.md", PARTIAL_FILES)
        self.assertEqual(classify("AGENTS.md"), "partial")
        self.assertEqual(classify("CLAUDE.md"), "partial")
        self.assertEqual(classify(".github/copilot-instructions.md"), "partial")
        # a normal template stays kit-tracked
        self.assertEqual(classify("docs/templates/adr-template.md"), "kit-tracked")
```

- [ ] **Step 2: Run, verify FAIL**

Run: `python tests/test_manifest.py`
Expected: FAIL — `ImportError: cannot import name 'PARTIAL_FILES'`.

- [ ] **Step 3: Implement**

In `src/standards/manifest.py`, add after `PAYLOAD_FILES`:
```python
# Files the kit partially owns: a single managed block is kit-owned, the rest is
# downstream-owned. Handled by update via managed-region splice (ADR-0010).
PARTIAL_FILES: frozenset[str] = frozenset({
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
})
```
And change `classify` to:
```python
def classify(rel: str) -> str:
    """Classify a payload-relative path: scaffold-once-source / partial / kit-tracked."""
    if rel in _TRACKED_EXCLUSIONS:
        return "scaffold-once-source"
    if rel in PARTIAL_FILES:
        return "partial"
    return "kit-tracked"
```

- [ ] **Step 4: Run, verify PASS**

Run: `python tests/test_manifest.py`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add src/standards/manifest.py tests/test_manifest.py
git commit -m "feat(dist): add partial ownership class to manifest"
```
Trailer as above.

---

## Task A4: Restructure `AGENTS.md` with the managed block

**Files:** Modify `AGENTS.md` (overwrite with the structure below).

This is a content task; verification is `standards-check` + a managed-block assertion.

- [ ] **Step 1: Overwrite `AGENTS.md` with exactly:**

```markdown
# AGENTS.md

<!-- BEGIN kit-managed: agents-core (v0.6.0) -->
Single source of truth for AI agents working in this repository. Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`) are thin pointers to this document.

- Kit version: **0.6.0**

## Canonical reading order

When you start a session in a repo that follows this kit, read in this order before taking action:

1. **`docs/00-overview.md`** — what this repo is, in 1 page.
2. **`ai/handoff.md`** — what the last session left for you. If `written` is older than 7 days, treat as "no handoff available".
3. **`ai/current-state.md`** — the current truth about what works, what's in progress, what's blocked.
4. **`docs/STANDARDS.md`** — which profile this repo follows and any local deviations.
5. **`ai/next-actions.md`** — the next 1–7 things on deck.
6. **`ai/open-questions.md`** — unresolved questions you may need to factor in.

Only after that, dive into the code or the user's specific request.

## End-of-session contract

Before you finish a session that produced meaningful change:

- [ ] Update `ai/current-state.md` if any of the four sections changed (What works · What's in progress · What's blocked · Active environments).
- [ ] Write `ai/handoff.md` for the next session — TL;DR, recently touched, open threads, and **Don't do** (dead-ends to spare the next session).
- [ ] If you opened a new question while working, add it to `ai/open-questions.md` with a unique anchor (`#q-N`).
- [ ] If you closed an `ai/open-questions.md` entry, flip status to `answered` and link the ADR (if one was produced) or the resolution.
- [ ] If you made a material technical decision, write an ADR in `docs/decisions/` (MADR 3.0 format — see `docs/templates/adr-template.md`).
- [ ] If you ran a time-boxed investigation, write or conclude an RFC in `docs/rfcs/<NNNN-slug>/rfc.md`.
- [ ] If you used content from `docs/discovery/`, flip its `status: raw` → `promoted` and set `promoted_to:`.

## How to author each artifact type

- **ADRs:** `docs/templates/adr-template.md`. Immutable once `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- **RFCs:** `docs/templates/rfc-template.md`. One folder per RFC under `docs/rfcs/NNNN-slug/`. Every RFC must either spawn an ADR, be `Abandoned` with reason, or its question must be tracked in `ai/open-questions.md`.
- **Discovery items:** `docs/templates/discovery-meeting-notes.md` or `discovery-use-case.md`. Filename: `YYYY-MM-DD-source-topic.md`. Place in the right subfolder. Optional but encouraged frontmatter (`source`, `date_captured`, `topic`, `status`, `promoted_to`).
- **Numbered docs:** see `docs/STANDARDS.md` for which docs are Required/Expected/Optional/N/A for this profile.

## Standard conventions

- Date format everywhere: ISO 8601 (`YYYY-MM-DD`).
- Filename conventions: lowercase kebab-case for slugs.
- Don't edit files in `docs/decisions/` whose status is `Accepted` — write a superseding ADR instead.
- Don't create numbered docs marked **N/A** for this profile. If a doc is **Optional** and you skip it, no waiver is needed. If it's **Required** or **Expected** and you skip it, add a `**Waived:** <reason>` line in `docs/STANDARDS-CHECKLIST.md`.
<!-- END kit-managed: agents-core -->

## About this repository

This is the **Team Repository Standards Kit** — a versioned set of documentation standards, templates, AI Skills + a `standards` CLI, and CI checks that other repositories adopt.

- Profile: **library** (this kit ships templates; it has no runtime, no deployment, no runbook)

### Local conventions

- This kit follows itself. Every Slice 1 decision (profile model, ADR format, RFC format, `ai/` contract, AGENTS.md pattern) is captured as an ADR in `docs/decisions/`.

### What's out of scope right now (queued slices)

- **Slice 4:** Deeper CI enforcement (content linting, doc freshness, link checking).

If you're tempted to add a deeper CI check before Slice 4 — don't. Open an RFC or an `ai/open-questions.md` entry instead.
```

- [ ] **Step 2: Verify managed block parses + standards-check passes**

Run:
```powershell
$env:PYTHONPATH="src"; python -c "from standards.managed import find_block; from pathlib import Path; b=find_block(Path('AGENTS.md').read_text(encoding='utf-8')); print('block id:', b.block_id); assert b.block_id=='agents-core'; assert 'Canonical reading order' in b.inner; assert 'About this repository' not in b.inner; print('OK')"
python scripts/standards-check/check.py
```
Expected: `block id: agents-core` … `OK`, then `Standards check: 0 error(s), 0 warning(s)`.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "refactor(slice-3): wrap AGENTS.md contract in kit-managed block"
```
Trailer as above.

---

## Task A5: Restructure `CLAUDE.md` and `.github/copilot-instructions.md`

**Files:** Modify `CLAUDE.md`, `.github/copilot-instructions.md`.

- [ ] **Step 1: Overwrite `CLAUDE.md` with exactly:**

```markdown
# CLAUDE.md

<!-- BEGIN kit-managed: claude-pointer (v0.6.0) -->
See [`AGENTS.md`](./AGENTS.md) — the canonical agent contract for this repo. Read it first.
<!-- END kit-managed: claude-pointer -->

## Claude-specific notes

- Follow the **end-of-session contract** in `AGENTS.md` before exiting. The `ai/handoff.md` file is the single most valuable artifact you leave behind.
```

- [ ] **Step 2: Overwrite `.github/copilot-instructions.md` with exactly:**

```markdown
# Copilot Instructions

<!-- BEGIN kit-managed: copilot-pointer (v0.6.0) -->
See [`AGENTS.md`](../AGENTS.md) — the canonical agent contract for this repo. Read it first.
<!-- END kit-managed: copilot-pointer -->

## Copilot-specific notes

- Copilot does not yet read `ai/handoff.md` automatically. When suggesting code or docs, treat `AGENTS.md` § "Canonical reading order" as the source of context.
```

- [ ] **Step 3: Verify both blocks parse**

Run:
```powershell
$env:PYTHONPATH="src"; python -c "from standards.managed import find_block; from pathlib import Path; [print(p, find_block(Path(p).read_text(encoding='utf-8')).block_id) for p in ['CLAUDE.md','.github/copilot-instructions.md']]"
python scripts/standards-check/check.py
```
Expected: prints `CLAUDE.md claude-pointer` and `.github/copilot-instructions.md copilot-pointer`; standards-check `0 error(s), 0 warning(s)`.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md .github/copilot-instructions.md
git commit -m "refactor(slice-3): wrap CLAUDE.md and copilot-instructions pointers in kit-managed blocks"
```
Trailer as above.

---

## Task A6: `init` records managed-block hashes for partial files

**Files:** Modify `src/standards/init.py`; modify `tests/test_init.py`.

- [ ] **Step 1: Add failing test**

Append to `tests/test_init.py` inside `InitTests`:
```python
    def test_partial_files_recorded_in_managed_with_block_hash(self):
        from standards.marker import read_marker
        from standards.managed import block_hash
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            marker = read_marker(target)
            # partial files are copied and recorded under managed, not tracked
            self.assertIn("AGENTS.md", marker["managed"])
            self.assertNotIn("AGENTS.md", marker["tracked"])
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertEqual(
                marker["managed"]["AGENTS.md"],
                block_hash((target / "AGENTS.md").read_text(encoding="utf-8")),
            )
```

- [ ] **Step 2: Run, verify FAIL**

Run: `python tests/test_init.py`
Expected: FAIL — `AGENTS.md` is currently in `tracked`, not `managed` (`KeyError`/assertion failure).

- [ ] **Step 3: Implement**

In `src/standards/init.py`:
- Add imports: `from standards.manifest import PARTIAL_FILES, SCAFFOLD_ONCE, classify, is_excluded_from_tracked, iter_payload` and `from standards.managed import block_hash`.
- Replace the kit-tracked copy loop body so partial files are copied and hashed into a `managed` dict instead of `tracked`:

```python
    src_root = payload_root()
    tracked: dict[str, str] = {}
    managed: dict[str, str] = {}

    for full, rel in iter_payload(src_root):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue  # handled in the scaffold-once loop below
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(full, dest)
        if cls == "partial":
            managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
        else:  # kit-tracked
            tracked[rel] = sha256_file(dest)
```

And update the marker write to pass `managed`:
```python
    write_marker(target, kit_version=__version__, profile=profile,
                 adopted=adopted, tracked=tracked, managed=managed)
    return read_marker(target)
```

(Keep the existing scaffold-once loop and the FileExistsError marker guard unchanged. Note `classify`/`is_excluded_from_tracked` both recognize scaffold-once sources; using `classify(...) == "scaffold-once-source"` is equivalent to the old `is_excluded_from_tracked` check — keep one consistently.)

- [ ] **Step 4: Run, verify PASS (whole init + manifest suite)**

Run: `python tests/test_init.py` then `python tests/test_manifest.py`
Expected: PASS. (`test_copies_tracked_and_writes_marker` still passes — `docs/STANDARDS.md` remains kit-tracked; only AGENTS/CLAUDE/copilot moved to `managed`.)

- [ ] **Step 5: Commit**

```bash
git add src/standards/init.py tests/test_init.py
git commit -m "feat(dist): init records managed-block hashes for partial files"
```
Trailer as above.

---

# PHASE B — `standards update` + first-init guard

## Task B1: `update.py` — reconciliation engine

**Files:** Create `src/standards/update.py`, `tests/test_update.py`.

- [ ] **Step 1: Write the failing test**

`tests/test_update.py`:
```python
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _adopt(target):
    """init the kit then roll the marker's kit_version back to simulate an older adoption."""
    from standards.init import run_init
    from standards.marker import MARKER_NAME
    run_init(target, profile="library", adopted="2026-05-29")
    marker_path = target / MARKER_NAME
    data = json.loads(marker_path.read_text(encoding="utf-8"))
    data["kit_version"] = "0.5.0"
    marker_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class UpdateTests(unittest.TestCase):
    def test_unchanged_kit_tracked_is_not_a_conflict(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            report = run_update(target)
            # STANDARDS.md was untouched by the user => no conflict for it
            self.assertNotIn("docs/STANDARDS.md", report["conflicts"])

    def test_edited_kit_tracked_produces_sidecar_not_overwrite(self):
        from standards.update import run_update
        from standards.__about__ import __version__
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            edited = target / "docs" / "STANDARDS.md"
            edited.write_text("MY LOCAL EDITS\n", encoding="utf-8")
            report = run_update(target)
            self.assertIn("docs/STANDARDS.md", report["conflicts"])
            # original is preserved; the kit version is offered alongside
            self.assertEqual(edited.read_text(encoding="utf-8"), "MY LOCAL EDITS\n")
            self.assertTrue((target / f"docs/STANDARDS.md.kit-{__version__}").is_file())

    def test_partial_unedited_block_is_spliced(self):
        from standards.update import run_update
        from standards.managed import find_block
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            # simulate a downstream edit OUTSIDE the managed block
            agents = target / "AGENTS.md"
            text = agents.read_text(encoding="utf-8")
            agents.write_text(text + "\n## My team notes\nlocal\n", encoding="utf-8")
            report = run_update(target)
            self.assertIn("AGENTS.md", report["spliced"])
            after = agents.read_text(encoding="utf-8")
            self.assertIn("## My team notes", after)          # downstream content kept
            self.assertIsNotNone(find_block(after))            # block still present

    def test_partial_edited_block_produces_sidecar(self):
        from standards.update import run_update
        from standards.managed import splice_block
        from standards.__about__ import __version__
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            agents = target / "AGENTS.md"
            agents.write_text(splice_block(agents.read_text(encoding="utf-8"),
                                           "I HACKED THE CONTRACT"), encoding="utf-8")
            report = run_update(target)
            self.assertIn("AGENTS.md", report["conflicts"])
            self.assertTrue((target / f"AGENTS.md.kit-{__version__}").is_file())

    def test_scaffold_once_never_touched(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            cs = target / "ai" / "current-state.md"
            cs.write_text("MY STATE\n", encoding="utf-8")
            run_update(target)
            self.assertEqual(cs.read_text(encoding="utf-8"), "MY STATE\n")

    def test_dry_run_writes_nothing(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            edited = target / "docs" / "STANDARDS.md"
            edited.write_text("LOCAL\n", encoding="utf-8")
            before = sorted(p.name for p in target.rglob("*"))
            run_update(target, dry_run=True)
            after = sorted(p.name for p in target.rglob("*"))
            self.assertEqual(before, after)          # no sidecar created
            self.assertEqual(edited.read_text(encoding="utf-8"), "LOCAL\n")

    def test_no_marker_raises(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                run_update(Path(d))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run, verify FAIL**

Run: `python tests/test_update.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'standards.update'`.

- [ ] **Step 3: Implement**

`src/standards/update.py`:
```python
"""`standards update` — reconcile a vendored kit against the running version.

Non-destructive: downstream edits never get clobbered. Conflicts are written as
`<rel>.kit-<version>` sidecars and reported. See ADR-0009 / ADR-0010.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.managed import block_hash, find_block, splice_block
from standards.manifest import classify, iter_payload
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root

REPORT_KEYS = ("updated", "unchanged", "spliced", "conflicts", "added", "removed")


def _empty_report() -> dict[str, list[str]]:
    return {k: [] for k in REPORT_KEYS}


def _sidecar(target: Path, rel: str, src_full: Path, dry_run: bool) -> None:
    if dry_run:
        return
    dest = target / f"{rel}.kit-{__version__}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_full, dest)


def run_update(target: Path, *, dry_run: bool = False) -> dict[str, list[str]]:
    """Reconcile `target` against the payload. Returns a report keyed by REPORT_KEYS.

    Raises FileNotFoundError if `target` has no adoption marker.
    """
    target = Path(target)
    marker = read_marker(target)
    if marker is None:
        raise FileNotFoundError(
            f"{target / MARKER_NAME} not found; run `standards init` first"
        )

    src_root = payload_root()
    report = _empty_report()
    tracked = dict(marker.get("tracked", {}))
    managed = dict(marker.get("managed", {}))
    seen: set[str] = set()

    for full, rel in iter_payload(src_root):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue
        seen.add(rel)
        dest = target / rel

        if cls == "kit-tracked":
            if not dest.exists():
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(full, dest)
                    tracked[rel] = sha256_file(dest)
                report["added"].append(rel)
                continue
            dest_hash = sha256_file(dest)
            src_hash = sha256_file(full)
            if dest_hash == src_hash:
                tracked[rel] = dest_hash
                report["unchanged"].append(rel)
            elif dest_hash == tracked.get(rel):   # untouched since last sync
                if not dry_run:
                    shutil.copyfile(full, dest)
                    tracked[rel] = sha256_file(dest)
                report["updated"].append(rel)
            else:                                  # downstream edited it
                _sidecar(target, rel, full, dry_run)
                report["conflicts"].append(rel)

        elif cls == "partial":
            if not dest.exists():
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(full, dest)
                    managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
                report["added"].append(rel)
                continue
            cur_text = dest.read_text(encoding="utf-8")
            cur_block = block_hash(cur_text)
            src_block = block_hash(full.read_text(encoding="utf-8"))
            if cur_block == src_block:
                managed[rel] = cur_block
                report["unchanged"].append(rel)
            elif cur_block is not None and cur_block == managed.get(rel):
                if not dry_run:
                    new_inner = find_block(full.read_text(encoding="utf-8")).inner
                    dest.write_text(splice_block(cur_text, new_inner), encoding="utf-8")
                    managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
                report["spliced"].append(rel)
            else:                                  # block edited, or markers gone
                _sidecar(target, rel, full, dry_run)
                report["conflicts"].append(rel)

    # Files the marker tracked/managed that no longer exist in the payload.
    for rel in list(tracked) + list(managed):
        if rel not in seen:
            report["removed"].append(rel)

    if not dry_run:
        write_marker(target, kit_version=__version__, profile=marker["profile"],
                     adopted=marker["adopted"], tracked=tracked, managed=managed)
    return report
```

- [ ] **Step 4: Run, verify PASS**

Run: `python tests/test_update.py`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add src/standards/update.py tests/test_update.py
git commit -m "feat(dist): add standards update reconciliation engine"
```
Trailer as above.

---

## Task B2: First-init guard

**Files:** Modify `src/standards/init.py`; modify `tests/test_init.py`.

- [ ] **Step 1: Add failing tests**

Append to `tests/test_init.py` inside `InitTests`:
```python
    def test_init_refuses_differing_existing_kit_tracked(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("PREEXISTING DIFFERENT\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self._run(target, profile="library", adopted="2026-05-29")
            # nothing was copied (guard fires before writes)
            self.assertFalse((target / ".standards-kit.json").exists())

    def test_init_allows_identical_existing_file(self):
        from standards.payload import payload_root
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            # pre-place an IDENTICAL copy of the payload file
            src = payload_root() / "docs" / "STANDARDS.md"
            (target / "docs" / "STANDARDS.md").write_bytes(src.read_bytes())
            self._run(target, profile="library", adopted="2026-05-29")  # no raise
            self.assertTrue((target / ".standards-kit.json").is_file())

    def test_init_force_overwrites_differing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("DIFFERENT\n", encoding="utf-8")
            self._run(target, profile="library", adopted="2026-05-29", force=True)
            self.assertTrue((target / ".standards-kit.json").is_file())
```

- [ ] **Step 2: Run, verify FAIL**

Run: `python tests/test_init.py`
Expected: FAIL — `test_init_refuses_differing_existing_kit_tracked` does not raise (init currently overwrites).

- [ ] **Step 3: Implement the guard**

In `src/standards/init.py`, add a pre-flight collision scan right after the existing marker `FileExistsError` check and before the copy loop:
```python
    if not force:
        collisions: list[str] = []
        for full, rel in iter_payload(payload_root()):
            cls = classify(rel)
            if cls == "scaffold-once-source":
                continue
            dest = target / rel
            if not dest.exists():
                continue
            if cls == "partial":
                differs = block_hash(dest.read_text(encoding="utf-8")) != \
                    block_hash(full.read_text(encoding="utf-8"))
            else:
                differs = sha256_file(dest) != sha256_file(full)
            if differs:
                collisions.append(rel)
        if collisions:
            shown = ", ".join(sorted(collisions)[:5])
            more = "" if len(collisions) <= 5 else f" (+{len(collisions) - 5} more)"
            raise FileExistsError(
                f"{len(collisions)} kit file(s) already exist with different content: "
                f"{shown}{more}. Re-run with force=True to overwrite, or adopt into an empty repo."
            )
```
(`payload_root` is already imported; `classify`, `block_hash`, `sha256_file` were added in Task A6 — confirm the imports are present.)

- [ ] **Step 4: Run, verify PASS (init + full dist suite)**

Run: `python tests/test_init.py`
Expected: PASS. Then `python tests/test_update.py` and `python tests/test_cli.py` to confirm no regressions (the greenfield/temp-dir cases still adopt cleanly).

- [ ] **Step 5: Commit**

```bash
git add src/standards/init.py tests/test_init.py
git commit -m "fix(dist): make first-time init non-destructive (guard differing kit files)"
```
Trailer as above.

---

## Task B3: `cli.py` — `update` subcommand + `--dry-run`

**Files:** Modify `src/standards/cli.py`; modify `tests/test_cli.py`.

- [ ] **Step 1: Add failing tests**

Append to `tests/test_cli.py` inside `CliTests`:
```python
    def test_update_after_init(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            res = self._run("update", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("unchanged", res.stdout.lower() + res.stderr.lower())

    def test_update_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run("init", "--profile", "library", str(target), cwd=REPO)
            (target / "docs" / "STANDARDS.md").write_text("LOCAL\n", encoding="utf-8")
            before = sorted(p.name for p in target.rglob("*"))
            res = self._run("update", "--dry-run", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(before, sorted(p.name for p in target.rglob("*")))

    def test_update_without_marker_errors(self):
        with tempfile.TemporaryDirectory() as d:
            res = self._run("update", d, cwd=REPO)
            self.assertNotEqual(res.returncode, 0)
```

- [ ] **Step 2: Run, verify FAIL**

Run: `python tests/test_cli.py`
Expected: FAIL — `update` is an invalid choice / non-zero for the success cases.

- [ ] **Step 3: Implement**

In `src/standards/cli.py`:
- Add import: `from standards.update import run_update`.
- Register the subcommand after the `init` parser:
```python
    p_update = sub.add_parser("update", help="Reconcile an adopted repo with this kit version.")
    p_update.add_argument("target", nargs="?", default=".", help="Target repo (default: .)")
    p_update.add_argument("--dry-run", action="store_true",
                          help="Preview changes without writing anything.")
```
- Add the dispatch branch before the final `return 1`:
```python
    if args.command == "update":
        try:
            report = run_update(Path(args.target), dry_run=args.dry_run)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        prefix = "[dry-run] " if args.dry_run else ""
        summary = ", ".join(f"{k}={len(report[k])}" for k in
                            ("updated", "spliced", "added", "conflicts", "unchanged", "removed"))
        print(f"{prefix}standards update: {summary}")
        if report["conflicts"]:
            print("conflicts (your file kept; kit version written as <path>.kit-"
                  f"{__version__}): " + ", ".join(report["conflicts"]), file=sys.stderr)
        print("Run `python scripts/standards-check/check.py` to re-verify.")
        return 0
```

- [ ] **Step 4: Run, verify PASS**

Run: `python tests/test_cli.py`
Expected: PASS (5 tests). Also run `$env:PYTHONPATH="src"; python -m standards.cli update --help` → shows `target` and `--dry-run`.

- [ ] **Step 5: Commit**

```bash
git add src/standards/cli.py tests/test_cli.py
git commit -m "feat(dist): wire standards update subcommand with --dry-run"
```
Trailer as above.

---

## Task B4: Full suite + CHANGELOG 0.6.0

**Files:** Modify `CHANGELOG.md`.

- [ ] **Step 1: Run every suite**

Run each; all must end `OK`:
```
python scripts/new-doc/test_helpers.py
python scripts/new-doc/test_cli.py
python scripts/update-handoff/test_update_handoff.py
python scripts/promote-discovery/test_promote_discovery.py
python scripts/standards-check/test_check.py
python tests/test_version.py
python tests/test_payload.py
python tests/test_manifest.py
python tests/test_marker.py
python tests/test_managed.py
python tests/test_init.py
python tests/test_update.py
python tests/test_cli.py
```
Report the total count. If any fails, STOP (BLOCKED).

- [ ] **Step 2: standards-check + version self-consistency**

Run: `python scripts/standards-check/check.py` → expect `0 error(s), 0 warning(s)`.
Confirm `AGENTS.md`'s managed block shows `Kit version: **0.6.0**` and `src/standards/__about__.py` is bumped (next step).

- [ ] **Step 3: Bump version + add CHANGELOG entry**

In `src/standards/__about__.py`, set `__version__ = "0.6.0"`.

Prepend under the CHANGELOG header (before `## [0.5.0]`):
```markdown
## [0.6.0] - 2026-05-29

### Added
- `standards update [target] [--dry-run]` — reconciles an adopted repo with the running kit version: hash-guarded overwrite of unmodified kit-tracked files, managed-block splice for partial files, `<path>.kit-<version>` sidecars on conflict, never destructive. Reports updated/spliced/added/conflicts/unchanged/removed.
- `src/standards/managed.py` — single managed-region block primitives (find/splice/hash) per ADR-0010.
- Partial/managed-region ownership class: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` carry a kit-owned `<!-- BEGIN/END kit-managed -->` block; the rest of each file is downstream-owned.
- `docs/decisions/0010-…md` — ADR-0010 (managed-region sentinel convention).

### Changed
- `AGENTS.md` restructured: the agent contract lives in the `agents-core` managed block; repo-specifics moved to a downstream-owned `## About this repository` section.
- `init` now records partial files under the marker's `managed` table (block hash) and **refuses to overwrite pre-existing kit files with differing content** without `force` (first-init guard; closes the PR #2 data-loss gap).

### Notes
- One managed block per file (multi-block deferred). `standards set-profile` and the PyPI release workflow remain future work (Plan 3).
```

Add the reference link with the others at the bottom of `CHANGELOG.md` (above `[0.5.0]:`):
```
[0.6.0]: https://example.invalid/releases/tag/v0.6.0
```

- [ ] **Step 4: Re-verify**

Run: `python tests/test_version.py` (now asserts 0.6.0 — UPDATE the assertion in `tests/test_version.py` from `"0.5.0"` to `"0.6.0"` first), then `python scripts/standards-check/check.py` → 0/0.

> The version bump means `tests/test_version.py`'s `assertEqual(__version__, "0.5.0")` must change to `"0.6.0"`. Make that one-line edit in this task and include it in the commit.

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md src/standards/__about__.py tests/test_version.py
git commit -m "docs(slice-3): record v0.6.0 (update + managed-region class)"
```
Trailer as above.

---

## Self-Review (completed by plan author)

- **Spec coverage:** A1→Task A1 (ADR-0010); managed.py→A2; partial class→A3; restructure→A4/A5; init managed hashes→A6; update engine→B1; first-init guard→B2; CLI update+dry-run→B3; version/CHANGELOG→B4. Breaking-change surfacing is implemented as a CHANGELOG-reminder line in B3's output rather than a section parser — a deliberate YAGNI simplification noted here (full section extraction deferred).
- **Placeholder scan:** none — every code/content step is complete; restructured file contents are given verbatim.
- **Type consistency:** `classify` returns `"kit-tracked" | "partial" | "scaffold-once-source"` everywhere (manifest, init, update); `find_block` returns a `Block` dataclass with `.inner`/`.block_id`/`.start`/`.end` used consistently; `block_hash`/`sha256_file` return `str | None` / `str`; marker schema `kit_version/profile/adopted/tracked/managed` matches Plan 1's `write_marker`. `run_update` report keys (`REPORT_KEYS`) match what `cli.py` and the tests read.

---

## Follow-on (Plan 3)

PyPI Trusted-Publishing (OIDC) workflow on tag-push, wire all test suites into CI, cut/tag `v0.6.0` (and backfill `v0.5.0`). Optional later: `standards set-profile`, multi-block managed regions, Slice 4 marker/sentinel CI lint.
