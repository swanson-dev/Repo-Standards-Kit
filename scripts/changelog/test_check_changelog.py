"""Tests for the advisory changelog reminder hook."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "changelog" / "check_changelog.py"


def git(*args: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True,
        env=full_env, check=True,
    )


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd), capture_output=True, text=True,
    )


def make_git_repo(tmp: Path) -> Path:
    git("init", "-q", cwd=tmp)
    git("config", "user.email", "test@example.invalid", cwd=tmp)
    git("config", "user.name", "Test User", cwd=tmp)
    (tmp / "README.md").write_text("# test\n", encoding="utf-8")
    (tmp / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [0.1.0] - 2026-06-01\n\n### Added\n- Initial.\n",
        encoding="utf-8",
    )
    git("add", "README.md", "CHANGELOG.md", cwd=tmp)
    git("commit", "-q", "-m", "initial", cwd=tmp)
    return tmp


class CheckModeTests(unittest.TestCase):
    def test_missing_changelog_reminds_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            git("init", "-q", cwd=tmp)

            result = run("--check", cwd=tmp)

            self.assertEqual(result.returncode, 0)
            self.assertIn("CHANGELOG.md is missing", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_clean_repo_after_changelog_commit_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))

            result = run("--check", cwd=tmp)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")

    def test_dirty_work_reminds(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            (tmp / "feature.md").write_text("# feature\n", encoding="utf-8")

            result = run("--check", cwd=tmp)

            self.assertEqual(result.returncode, 0)
            self.assertIn("CHANGELOG.md may need an entry", result.stderr)
            self.assertIn("1 modified", result.stderr)

    def test_commits_after_latest_changelog_commit_remind(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            (tmp / "feature.md").write_text("# feature\n", encoding="utf-8")
            git("add", "feature.md", cwd=tmp)
            git("commit", "-q", "-m", "feat: add feature doc", cwd=tmp)

            result = run("--check", cwd=tmp)

            self.assertEqual(result.returncode, 0)
            self.assertIn("CHANGELOG.md may need an entry", result.stderr)
            self.assertIn("1 commit", result.stderr)

    def test_non_git_cwd_is_silent_success(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("--check", cwd=Path(d))

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
