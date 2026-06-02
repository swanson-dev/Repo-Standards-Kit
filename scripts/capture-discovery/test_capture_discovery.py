"""E2E tests for capture_discovery.py — invokes via subprocess against tmp git repos."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "capture-discovery" / "capture_discovery.py"

INTAKE_KINDS = ("meetings", "requirements", "use-cases", "notes")


def make_git_repo(tmp: Path) -> Path:
    """Minimal git repo + the ADR-0014 discovery scaffold (intake folders + captured/)."""
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=str(tmp), check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp), check=True)
    disc = tmp / "docs" / "discovery"
    for kind in INTAKE_KINDS:
        (disc / kind).mkdir(parents=True)
        (disc / kind / ".gitkeep").write_text("", encoding="utf-8")
    (disc / "captured").mkdir(parents=True)
    (disc / "captured" / "README.md").write_text("# captured\n", encoding="utf-8")
    (disc / "README.md").write_text("# discovery\n", encoding="utf-8")
    return tmp


def drop_source(tmp: Path, rel: str, content: str = "binary-ish") -> Path:
    path = tmp / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd), capture_output=True, text=True,
    )


class ListTests(unittest.TestCase):
    def test_empty_intake_reports_zero(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 uncaptured sources.", result.stdout)

    def test_lists_uncaptured_sources_ignoring_gitkeep(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            drop_source(tmp, "docs/discovery/meetings/acme-kickoff.pdf")
            drop_source(tmp, "docs/discovery/requirements/export.json")
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("2 uncaptured sources", result.stdout)
            self.assertIn("acme-kickoff.pdf", result.stdout)
            self.assertIn("export.json", result.stdout)
            self.assertNotIn(".gitkeep", result.stdout)

    def test_captured_output_not_counted_as_source(self):
        # Notes already synthesized into captured/ are not "uncaptured sources".
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            drop_source(tmp, "docs/discovery/captured/2026-06-01-x.md", "# x\n")
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 uncaptured sources.", result.stdout)

    def test_non_git_cwd_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("list", cwd=Path(d))
            self.assertEqual(result.returncode, 2)
            self.assertIn("not in a git repo", result.stderr.lower())


class CheckTests(unittest.TestCase):
    def test_silent_when_no_sources(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("list", "--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")

    def test_advisory_when_sources_present(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            drop_source(tmp, "docs/discovery/meetings/a.pdf")
            drop_source(tmp, "docs/discovery/notes/b.json")
            result = run("list", "--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("capture-discovery:", result.stderr.lower())
            self.assertIn("2 uncaptured", result.stderr)
            self.assertIn("/capture-discovery", result.stderr)

    def test_check_silent_exit_0_in_non_git_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("list", "--check", cwd=Path(d))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")


class NewTests(unittest.TestCase):
    def _captured(self, tmp: Path) -> list[Path]:
        base = tmp / "docs" / "discovery" / "captured"
        return [p for p in base.glob("*.md") if p.name != "README.md"]

    def test_creates_note_in_captured_with_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("new", "--kind", "meetings", "--topic", "Acme Kickoff", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            notes = self._captured(tmp)
            self.assertEqual(len(notes), 1)
            note = notes[0]
            self.assertTrue(note.name.endswith("-acme-kickoff.md"), note.name)
            body = note.read_text(encoding="utf-8")
            self.assertIn("status: raw", body)
            self.assertIn("topic: Acme Kickoff", body)
            self.assertIn("promoted_to:", body)
            self.assertIn("date_captured:", body)
            self.assertIn("Created", result.stdout)

    def test_records_source_when_given(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            drop_source(tmp, "docs/discovery/meetings/acme.pdf")
            result = run(
                "new", "--kind", "meetings", "--topic", "Acme Kickoff",
                "--source", "docs/discovery/meetings/acme.pdf", cwd=tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            body = self._captured(tmp)[0].read_text(encoding="utf-8")
            self.assertIn("docs/discovery/meetings/acme.pdf", body)

    def test_refuses_unknown_kind(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("new", "--kind", "bogus", "--topic", "X", cwd=tmp)
            self.assertEqual(result.returncode, 2)

    def test_refuses_empty_topic(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("new", "--kind", "notes", "--topic", "   ", cwd=tmp)
            self.assertEqual(result.returncode, 2)

    def test_refuses_overwriting_existing_note(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            run("new", "--kind", "notes", "--topic", "Same Topic", cwd=tmp)
            result = run("new", "--kind", "notes", "--topic", "Same Topic", cwd=tmp)
            self.assertEqual(result.returncode, 2)
            self.assertIn("refuse", result.stderr.lower())

    def test_new_non_git_cwd_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("new", "--kind", "notes", "--topic", "X", cwd=Path(d))
            self.assertEqual(result.returncode, 2)
            self.assertIn("not in a git repo", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
