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

    def test_ignores_inline_code_span(self):
        # Placeholders used as metasyntax inside backticks are legit prose, not unfilled tokens.
        hits = find_placeholders("the sidecar is `<path>.kit-<version>` on conflict\n")
        self.assertEqual(hits, [])

    def test_ignores_fenced_code_block(self):
        hits = find_placeholders("```\n--profile <library> NNNN YYYY-MM-DD\n```\n")
        self.assertEqual(hits, [])


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
