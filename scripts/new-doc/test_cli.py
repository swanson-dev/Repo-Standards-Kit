"""End-to-end tests for new-adr.py and new-rfc.py — invoke via subprocess."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NEW_ADR = REPO_ROOT / "scripts" / "new-doc" / "new-adr.py"
NEW_RFC = REPO_ROOT / "scripts" / "new-doc" / "new-rfc.py"
ADR_TEMPLATE = REPO_ROOT / "docs" / "templates" / "adr-template.md"
RFC_TEMPLATE = REPO_ROOT / "docs" / "templates" / "rfc-template.md"


def make_fixture_repo(tmp: Path) -> Path:
    """Build a minimal repo-shaped tmp dir: .git/, docs/templates/, docs/decisions/, docs/rfcs/."""
    (tmp / ".git").mkdir()
    (tmp / "docs" / "templates").mkdir(parents=True)
    (tmp / "docs" / "decisions").mkdir()
    (tmp / "docs" / "rfcs").mkdir()
    shutil.copy(ADR_TEMPLATE, tmp / "docs" / "templates" / "adr-template.md")
    shutil.copy(RFC_TEMPLATE, tmp / "docs" / "templates" / "rfc-template.md")
    return tmp


def run(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


class NewAdrTests(unittest.TestCase):
    def test_creates_file_with_today_and_title(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_fixture_repo(Path(d))
            result = run(NEW_ADR, "My first decision", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            created = tmp / "docs" / "decisions" / "0001-my-first-decision.md"
            self.assertTrue(created.exists(), f"expected {created}")
            body = created.read_text()
            # date is today, ISO 8601
            self.assertRegex(body, r"date: \d{4}-\d{2}-\d{2}\n")
            # heading filled
            self.assertIn("# 0001. My first decision", body)
            # untouched placeholder still there
            self.assertIn("<name>", body)
            # stdout has paste-ready index row
            self.assertIn("| [0001](./0001-my-first-decision.md) | My first decision |", result.stdout)

    def test_picks_next_nnnn(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_fixture_repo(Path(d))
            (tmp / "docs" / "decisions" / "0001-existing.md").write_text("x")
            (tmp / "docs" / "decisions" / "0003-also-existing.md").write_text("x")
            result = run(NEW_ADR, "Third decision", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((tmp / "docs" / "decisions" / "0004-third-decision.md").exists())

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_fixture_repo(Path(d))
            run(NEW_ADR, "Same title", cwd=tmp)
            second = run(NEW_ADR, "Same title", cwd=tmp)
            self.assertEqual(second.returncode, 2)
            self.assertIn("refuse to overwrite", second.stderr.lower())

    def test_non_git_repo_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            # no .git, no docs/
            result = run(NEW_ADR, "Anything", cwd=Path(d))
            self.assertEqual(result.returncode, 2)
            self.assertIn("not in a git repo", result.stderr.lower())

    def test_missing_title_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_fixture_repo(Path(d))
            result = run(NEW_ADR, cwd=tmp)
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage:", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
