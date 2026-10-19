"""The profile matrix as data (ADR-0025): parsing, combining, and the sync with docs/STANDARDS.md."""
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _table(heading: str) -> list[list[str]]:
    """Rows of the first markdown table after `heading` in docs/STANDARDS.md, header included."""
    text = (REPO / "docs" / "STANDARDS.md").read_text(encoding="utf-8")
    section = text[text.index(heading):]
    rows = []
    for line in section.splitlines()[1:]:
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not set("".join(cells)) <= set("-: "):
                rows.append(cells)
        elif rows:
            break
    return rows


class ProfileMatrixSyncTests(unittest.TestCase):
    def test_matrix_matches_standards_md(self):
        from standards.profiles import MATRIX, PROFILES
        header, *rows = _table("## Profile matrix (numbered docs)")
        self.assertEqual(header[1:], list(PROFILES))
        parsed = {row[0].strip("`"): tuple(cell.split()[0] for cell in row[1:]) for row in rows}
        self.assertEqual(len(parsed), len(rows), "a doc appears twice in the matrix table")
        self.assertEqual(parsed, {doc: tiers for doc, (_template, tiers) in MATRIX.items()})

    def test_extras_match_standards_md(self):
        from standards.profiles import EXTRAS
        _header, *rows = _table("### Profile-specific extras")
        parsed = {row[0].strip("`"): re.search(r"`([^`]+)`", row[1]).group(1) for row in rows}
        self.assertEqual(len(parsed), len(rows), "a profile appears twice in the extras table")
        self.assertEqual(parsed, EXTRAS)

    def test_every_matrix_doc_has_a_template(self):
        from standards.profiles import MATRIX
        for doc, (template, _tiers) in MATRIX.items():
            self.assertTrue((REPO / "docs" / "templates" / template).is_file(), doc)


class ParseProfilesTests(unittest.TestCase):
    def test_comma_lists_keep_order_and_drop_repeats(self):
        from standards.profiles import parse_profiles
        self.assertEqual(parse_profiles("application,data"), ["application", "data"])
        self.assertEqual(parse_profiles("data, application, data"), ["data", "application"])
        self.assertEqual(parse_profiles(["library"]), ["library"])

    def test_infra_reads_as_application(self):
        from standards.profiles import parse_profiles
        self.assertEqual(parse_profiles("infra"), ["application"])
        self.assertEqual(parse_profiles("application,infra"), ["application"])

    def test_bad_lists_are_rejected(self):
        from standards.profiles import parse_profiles
        for bad in ("", " , ", "bogus", "library,bogus", "documentation,library", ["library", 3]):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                parse_profiles(bad)


class CombineTests(unittest.TestCase):
    def test_the_strongest_tier_wins(self):
        from standards.profiles import combine
        tiers = combine(["library", "data"])
        self.assertEqual(tiers["01-prd.md"], "Expected")  # Optional for library, Expected for data
        self.assertEqual(tiers["06-runbook.md"], "Required")  # N/A for library
        self.assertEqual(combine(["library"])["06-runbook.md"], "N/A")

    def test_needed_docs_are_the_required_and_expected_ones(self):
        from standards.profiles import needed_docs
        required, expected = needed_docs(["library"])
        self.assertEqual(required, ["04-api-and-integrations.md", "07-testing.md"])
        self.assertEqual(expected, ["02-architecture.md", "08-security-and-compliance.md"])


if __name__ == "__main__":
    unittest.main()
