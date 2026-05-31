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
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root)
            self.assertEqual(find_incoherences(root), [])

    def test_tag_match_and_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_kit(root)
            self.assertEqual(find_incoherences(root, tag="v0.8.0"), [])
            self.assertTrue(any("tag" in m for m in find_incoherences(root, tag="v0.9.0")))


if __name__ == "__main__":
    unittest.main()
