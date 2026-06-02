"""E2E tests for promote_discovery.py — invokes via subprocess against tmp git repos."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "promote-discovery" / "promote_discovery.py"

DISCOVERY_FILE_RAW = """\
<!--
Discovery: meeting notes (soft-landing template, NOT required structure)
-->
---
source: stakeholder X
date_captured: 2026-05-12
topic: kickoff
status: raw               # raw | reviewed | promoted
promoted_to:              # e.g. docs/01-prd.md
---

# Kickoff notes

Body content goes here.
"""

DISCOVERY_FILE_PROMOTED = """\
---
source: stakeholder Y
date_captured: 2026-05-13
topic: review
status: promoted
promoted_to: docs/01-prd.md
---

# Review notes
"""

DISCOVERY_FILE_NO_FRONTMATTER = """\
# Just a markdown file

No frontmatter at all.
"""


def make_git_repo(tmp: Path) -> Path:
    """Minimal git repo + docs/discovery/ subtree for tests."""
    subprocess.run(["git", "init", "-q"], cwd=str(tmp), check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=str(tmp), check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp), check=True)
    (tmp / "docs" / "discovery" / "meetings").mkdir(parents=True)
    (tmp / "docs" / "discovery" / "use-cases").mkdir(parents=True)
    (tmp / "docs" / "discovery" / "captured").mkdir(parents=True)
    (tmp / "docs" / "discovery" / "README.md").write_text("# discovery\n", encoding="utf-8")
    return tmp


def write_discovery(tmp: Path, rel: str, content: str) -> Path:
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
    def test_empty_discovery_dir(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("0 raw discovery items.", result.stdout)

    def test_lists_only_raw_items(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/captured/2026-05-12-kickoff.md", DISCOVERY_FILE_RAW)
            write_discovery(tmp, "docs/discovery/captured/2026-05-13-review.md", DISCOVERY_FILE_PROMOTED)
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 raw discovery items", result.stdout)
            self.assertIn("2026-05-12-kickoff.md", result.stdout)
            self.assertNotIn("2026-05-13-review.md", result.stdout)
            self.assertIn("kickoff", result.stdout)  # topic column
            self.assertIn("2026-05-12", result.stdout)  # captured column

    def test_skips_readme_and_files_without_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            # README.md created by make_git_repo
            write_discovery(tmp, "docs/discovery/captured/random.md", DISCOVERY_FILE_NO_FRONTMATTER)
            write_discovery(tmp, "docs/discovery/captured/real-raw.md", DISCOVERY_FILE_RAW)
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 raw discovery items", result.stdout)
            self.assertNotIn("README.md", result.stdout)
            self.assertNotIn("random.md", result.stdout)

    def test_skips_templates_subtree(self):
        # Even if someone drops a status: raw file under docs/discovery/templates/,
        # the script should skip it — that subtree is for templates, not real discovery items.
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/templates/example-raw.md", DISCOVERY_FILE_RAW)
            write_discovery(tmp, "docs/discovery/captured/real-raw.md", DISCOVERY_FILE_RAW)
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            # Only the real raw item should be listed; the templates subtree file is skipped.
            self.assertIn("1 raw discovery items", result.stdout)
            self.assertIn("real-raw.md", result.stdout)
            self.assertNotIn("example-raw.md", result.stdout)
            self.assertNotIn("templates", result.stdout)

    def test_skips_intake_subfolders(self):
        # ADR-0014: raw intake folders are gitignored source. list operates on tracked
        # notes (captured/), not on un-captured intake drafts.
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/meetings/draft.md", DISCOVERY_FILE_RAW)
            write_discovery(tmp, "docs/discovery/captured/real.md", DISCOVERY_FILE_RAW)
            result = run("list", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 raw discovery items", result.stdout)
            self.assertIn("real.md", result.stdout)
            self.assertNotIn("draft.md", result.stdout)

    def test_non_git_cwd_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("list", cwd=Path(d))
            self.assertEqual(result.returncode, 2)
            self.assertIn("not in a git repo", result.stderr.lower())


class CheckTests(unittest.TestCase):
    def test_silent_when_no_raw_items(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("list", "--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")

    def test_advisory_when_raw_items_present(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/captured/a.md", DISCOVERY_FILE_RAW)
            write_discovery(tmp, "docs/discovery/captured/b.md", DISCOVERY_FILE_RAW)
            result = run("list", "--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("promote-discovery:", result.stderr.lower())
            self.assertIn("2 raw items", result.stderr)
            self.assertIn("/promote-discovery", result.stderr)

    def test_check_silent_exit_0_in_non_git_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("list", "--check", cwd=Path(d))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")


class PromoteTests(unittest.TestCase):
    def test_flips_status_and_sets_target(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            disc = write_discovery(tmp, "docs/discovery/meetings/a.md", DISCOVERY_FILE_RAW)
            result = run(
                "promote", "docs/discovery/meetings/a.md", "--to", "docs/01-prd.md",
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            body = disc.read_text(encoding="utf-8")
            self.assertIn("status: promoted", body)
            self.assertNotIn("status: raw", body)
            self.assertIn("promoted_to: docs/01-prd.md", body)
            # Inline comment alignment preserved (catches PROMOTED_TO_LINE_RE eating whitespace bug)
            self.assertRegex(body, r"promoted_to: docs/01-prd\.md\s+# e\.g\.")
            # Other fields preserved
            self.assertIn("source: stakeholder X", body)
            self.assertIn("topic: kickoff", body)
            # Body preserved
            self.assertIn("# Kickoff notes", body)
            self.assertIn("Body content goes here.", body)
            # Stdout confirms
            self.assertIn("Promoted", result.stdout)
            self.assertIn("docs/01-prd.md", result.stdout)

    def test_refuses_when_already_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/meetings/a.md", DISCOVERY_FILE_PROMOTED)
            result = run(
                "promote", "docs/discovery/meetings/a.md", "--to", "docs/02-x.md",
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("status is already", result.stderr.lower())

    def test_refuses_when_path_not_under_discovery(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            (tmp / "docs" / "elsewhere").mkdir(parents=True)
            write_discovery(tmp, "docs/elsewhere/a.md", DISCOVERY_FILE_RAW)
            result = run("promote", "docs/elsewhere/a.md", "--to", "docs/01-prd.md", cwd=tmp)
            self.assertEqual(result.returncode, 2)
            self.assertIn("not under docs/discovery", result.stderr.lower())

    def test_refuses_when_path_missing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            result = run("promote", "docs/discovery/meetings/nope.md", "--to", "docs/01-prd.md", cwd=tmp)
            self.assertEqual(result.returncode, 2)
            self.assertIn("not found", result.stderr.lower())

    def test_refuses_when_target_absolute(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/meetings/a.md", DISCOVERY_FILE_RAW)
            result = run(
                "promote", "docs/discovery/meetings/a.md", "--to", "/abs/path.md",
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("absolute", result.stderr.lower())

    def test_refuses_when_target_has_parent_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/meetings/a.md", DISCOVERY_FILE_RAW)
            result = run(
                "promote", "docs/discovery/meetings/a.md", "--to", "../escape.md",
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("..", result.stderr)

    def test_refuses_when_to_flag_missing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/meetings/a.md", DISCOVERY_FILE_RAW)
            result = run("promote", "docs/discovery/meetings/a.md", cwd=tmp)
            self.assertEqual(result.returncode, 2)

    def test_refuses_when_target_is_unc_path(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_discovery(tmp, "docs/discovery/meetings/a.md", DISCOVERY_FILE_RAW)
            result = run(
                "promote", "docs/discovery/meetings/a.md", "--to", r"\\server\share\foo.md",
                cwd=tmp,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("absolute", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
