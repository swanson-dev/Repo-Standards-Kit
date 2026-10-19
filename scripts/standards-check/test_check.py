"""Unit tests for scripts/standards-check/check.py helpers."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check import parse_frontmatter  # noqa: E402
from checks.structural import Report, check_profile  # noqa: E402


class ProfileAliasTests(unittest.TestCase):
    def test_checklists_that_still_say_infra_pass(self):
        # ADR-0025 merged infra into application; old checklists stay valid.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs").mkdir()
            (root / "docs" / "STANDARDS-CHECKLIST.md").write_text("**Profile:** infra\n", encoding="utf-8")
            report = Report()
            check_profile(root, report)
            self.assertEqual(report.errors, [])


class ParseFrontmatterTests(unittest.TestCase):
    def test_strips_inline_comment_after_value(self):
        """A YAML `#` comment after whitespace is not part of the value.

        Regression: new-adr/new-rfc emit the template's inline guidance comment
        (e.g. `status: Concluded   # Open | Concluded | Abandoned`); the validator
        must read the value as `Concluded`, matching YAML semantics.
        """
        fm = parse_frontmatter(
            "---\nstatus: Concluded   # Open | Concluded | Abandoned\n---\n"
        )
        self.assertEqual(fm["status"], "Concluded")

    def test_value_without_comment_unchanged(self):
        fm = parse_frontmatter("---\nstatus: Accepted\n---\n")
        self.assertEqual(fm["status"], "Accepted")

    def test_hash_without_leading_whitespace_is_not_a_comment(self):
        """`#` not preceded by whitespace is a literal character, not a comment."""
        fm = parse_frontmatter("---\nlang: C#\n---\n")
        self.assertEqual(fm["lang"], "C#")

    def test_full_comment_line_skipped(self):
        fm = parse_frontmatter("---\n# a comment line\nstatus: Open\n---\n")
        self.assertEqual(fm, {"status": "Open"})

    def test_no_frontmatter_returns_empty(self):
        self.assertEqual(parse_frontmatter("# Just a heading\n"), {})


if __name__ == "__main__":
    unittest.main()
