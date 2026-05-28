"""Unit tests for scripts/_doc_lib/helpers.py — stdlib unittest, runnable directly."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

# Make `_doc_lib` importable from this test file (sibling under scripts/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import next_nnnn, slugify, fill_template, repo_root, RepoRootNotFound


NNNN_PATTERN = re.compile(r"^(\d{4})-.*\.md$")


class NextNnnnTests(unittest.TestCase):
    def test_empty_dir_returns_0001(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(next_nnnn(Path(d), NNNN_PATTERN), "0001")

    def test_gaps_are_ignored_uses_max_plus_one(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "0001-foo.md").write_text("x")
            (p / "0003-bar.md").write_text("x")
            self.assertEqual(next_nnnn(p, NNNN_PATTERN), "0004")

    def test_non_matching_names_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "README.md").write_text("x")
            (p / "draft-notes.md").write_text("x")
            (p / "0002-real.md").write_text("x")
            self.assertEqual(next_nnnn(p, NNNN_PATTERN), "0003")

    def test_missing_dir_raises(self):
        with self.assertRaises(FileNotFoundError):
            next_nnnn(Path("/definitely/does/not/exist"), NNNN_PATTERN)


class SlugifyTests(unittest.TestCase):
    def test_lowercase_and_dashes(self):
        self.assertEqual(slugify("Adopt MADR 3.0!"), "adopt-madr-3-0")

    def test_collapses_runs(self):
        self.assertEqual(slugify("hello   ---   world"), "hello-world")

    def test_strips_leading_trailing_dashes(self):
        self.assertEqual(slugify("---foo---"), "foo")

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            slugify("")

    def test_all_punctuation_raises(self):
        with self.assertRaises(ValueError):
            slugify("!!!---???")


class FillTemplateTests(unittest.TestCase):
    def test_replaces_literal_placeholders(self):
        text = "date: YYYY-MM-DD\nstatus: Proposed"
        out = fill_template(text, {"YYYY-MM-DD": "2026-05-28"})
        self.assertEqual(out, "date: 2026-05-28\nstatus: Proposed")

    def test_leaves_unmatched_angle_placeholders_intact(self):
        text = "deciders: <name>, <name>\nfilled: YYYY-MM-DD"
        out = fill_template(text, {"YYYY-MM-DD": "2026-05-28"})
        self.assertIn("<name>", out)
        self.assertIn("2026-05-28", out)

    def test_multiple_substitutions(self):
        text = "# NNNN. <Title>\ndate: YYYY-MM-DD"
        out = fill_template(text, {"NNNN": "0007", "<Title>": "My ADR", "YYYY-MM-DD": "2026-05-28"})
        self.assertEqual(out, "# 0007. My ADR\ndate: 2026-05-28")


class RepoRootTests(unittest.TestCase):
    def test_finds_git_dir_walking_up(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".git").mkdir()
            nested = root / "a" / "b" / "c"
            nested.mkdir(parents=True)
            self.assertEqual(repo_root(nested).resolve(), root.resolve())

    def test_raises_when_no_git(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RepoRootNotFound):
                repo_root(Path(d))


if __name__ == "__main__":
    unittest.main()
