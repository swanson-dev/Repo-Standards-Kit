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
