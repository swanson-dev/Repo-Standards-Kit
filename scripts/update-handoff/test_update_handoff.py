"""End-to-end tests for update_handoff.py — invokes via subprocess against tmp git repos."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "update-handoff" / "update_handoff.py"


def git(*args: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True,
        env=full_env, check=True,
    )


def make_git_repo(tmp: Path, initial_when: str = "2020-01-01T00:00:00+00:00") -> Path:
    """Init a git repo with one initial commit and stable user config.

    `initial_when` pins the initial commit timestamp so tests can place handoffs
    after it deterministically.
    """
    git("init", "-q", cwd=tmp)
    git("config", "user.email", "test@example.invalid", cwd=tmp)
    git("config", "user.name", "Test User", cwd=tmp)
    (tmp / "README.md").write_text("# test\n", encoding="utf-8")
    git("add", "README.md", cwd=tmp)
    git(
        "commit", "-q", "-m", "initial", cwd=tmp,
        env={"GIT_COMMITTER_DATE": initial_when, "GIT_AUTHOR_DATE": initial_when},
    )
    return tmp


def add_commit(
    tmp: Path,
    filename: str,
    message: str | None = None,
    when: str | None = None,
) -> None:
    (tmp / filename).write_text(filename, encoding="utf-8")
    git("add", filename, cwd=tmp)
    env = None
    if when is not None:
        env = {"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
    git("commit", "-q", "-m", message or f"add {filename}", cwd=tmp, env=env)


def write_handoff(tmp: Path, written_ts: str, body: str = "(prior)") -> Path:
    handoff = tmp / "ai" / "handoff.md"
    handoff.parent.mkdir(parents=True, exist_ok=True)
    handoff.write_text(
        f"---\nwritten: {written_ts}\nwritten_by: prior-session\nfor: next-session\n---\n\n# Handoff\n\n{body}\n",
        encoding="utf-8",
    )
    return handoff


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd), capture_output=True, text=True,
    )


class WriteModeTests(unittest.TestCase):
    def test_creates_handoff_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            add_commit(tmp, "feature.py", "feat: add feature one")
            result = run(cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            handoff = tmp / "ai" / "handoff.md"
            self.assertTrue(handoff.exists())
            body = handoff.read_text(encoding="utf-8")
            # Frontmatter
            self.assertRegex(body, r"written: \d{4}-\d{2}-\d{2}T")
            self.assertIn("written_by: Test User", body)
            self.assertIn("for: next-session", body)
            # Sections
            self.assertIn("## TL;DR", body)
            self.assertIn("## Recently touched", body)
            self.assertIn("## Open threads", body)
            self.assertIn("## Don't do", body)
            # Recently touched pre-fill (commits + files)
            self.assertIn("feat: add feature one", body)
            self.assertIn("feature.py", body)
            self.assertIn("Created ai/handoff.md", result.stdout)

    def test_refuses_to_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_handoff(tmp, "2026-05-01T00:00:00+00:00")
            result = run(cwd=tmp)
            self.assertEqual(result.returncode, 2)
            self.assertIn("refuse to overwrite", result.stderr.lower())

    def test_force_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_handoff(tmp, "2026-05-01T00:00:00+00:00", body="OLD CONTENT")
            add_commit(tmp, "new.py", "feat: add new thing")
            result = run("--force", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            body = (tmp / "ai" / "handoff.md").read_text(encoding="utf-8")
            self.assertNotIn("OLD CONTENT", body)
            self.assertIn("feat: add new thing", body)
            self.assertIn("Updated ai/handoff.md", result.stdout)

    def test_falls_back_to_last_10_commits_when_no_prior_handoff(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))  # 1 initial commit
            # Make 11 more commits (12 total). Spread dates so they're orderly.
            for i in range(11):
                add_commit(
                    tmp, f"f{i:02d}.py",
                    message=f"feat: commit {i:02d}",
                    when=f"2025-0{(i // 5) + 1}-{(i % 5) + 1:02d}T00:00:00+00:00",
                )
            # No handoff exists. Run write mode.
            result = run(cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            body = (tmp / "ai" / "handoff.md").read_text(encoding="utf-8")
            # Recently touched should contain exactly the 10 most-recent commit subjects.
            commit_lines = [
                line for line in body.splitlines() if line.startswith("- feat: commit ")
            ]
            self.assertEqual(len(commit_lines), 10, f"expected 10 commit lines, got {len(commit_lines)}")
            # The most recent (commit 10) should be present; the oldest (commit 00) should not.
            self.assertIn("feat: commit 10", body)
            self.assertNotIn("feat: commit 00", body)

    def test_recently_touched_falls_back_when_prior_ts_is_in_the_future(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))  # initial commit at 2020-01-01
            add_commit(tmp, "a.py", message="feat: add a", when="2021-01-01T00:00:00+00:00")
            add_commit(tmp, "b.py", message="feat: add b", when="2021-01-02T00:00:00+00:00")
            # Prior handoff with a future timestamp.
            write_handoff(tmp, "2099-01-01T00:00:00+00:00")
            result = run("--force", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            body = (tmp / "ai" / "handoff.md").read_text(encoding="utf-8")
            # Should fall back to last-10 instead of returning empty.
            self.assertIn("feat: add a", body)
            self.assertIn("feat: add b", body)
            self.assertNotIn("(no committed changes since last handoff)", body)

    def test_non_git_cwd_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            result = run(cwd=Path(d))
            self.assertEqual(result.returncode, 2)
            self.assertIn("not in a git repo", result.stderr.lower())


class CheckModeTests(unittest.TestCase):
    def test_silent_when_no_work_happened(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            # Handoff timestamp far in the future → no commits "since" it; no modified files.
            write_handoff(tmp, "2099-01-01T00:00:00+00:00")
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")

    def test_advisory_when_commits_pending(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))  # initial commit at 2020-01-01
            # Handoff written after initial commit but before the two new commits.
            write_handoff(tmp, "2024-01-01T00:00:00+00:00")
            # New commits dated after the handoff timestamp.
            add_commit(tmp, "a.py", when="2025-01-01T00:00:00+00:00")
            add_commit(tmp, "b.py", when="2025-01-02T00:00:00+00:00")
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("update-handoff:", result.stderr.lower())
            self.assertIn("ai/handoff.md", result.stderr)
            self.assertIn("2 commits", result.stderr)
            self.assertIn("/update-handoff", result.stderr)

    def test_advisory_when_modified_files_present(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            write_handoff(tmp, "2099-01-01T00:00:00+00:00")
            (tmp / "README.md").write_text("# modified\n", encoding="utf-8")
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("update-handoff:", result.stderr.lower())
            self.assertIn("ai/handoff.md", result.stderr)
            self.assertIn("1 modified", result.stderr)
            self.assertIn("0 commits", result.stderr)

    def test_advisory_when_handoff_is_stale_even_without_new_work(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))  # initial commit dated 2020-01-01
            # Handoff written 10 days ago (older than the 5-day threshold); no commits since.
            stale = (date.today() - timedelta(days=10)).isoformat() + "T00:00:00+00:00"
            write_handoff(tmp, stale)
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("update-handoff:", result.stderr.lower())
            self.assertIn("ai/handoff.md", result.stderr)
            self.assertIn("days old", result.stderr.lower())

    def test_fresh_handoff_with_no_work_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = make_git_repo(Path(d))
            fresh = (date.today() - timedelta(days=1)).isoformat() + "T00:00:00+00:00"
            write_handoff(tmp, fresh)
            result = run("--check", cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")
            self.assertEqual(result.stdout, "")

    def test_check_silent_exit_0_in_non_git_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            result = run("--check", cwd=Path(d))
            # Hook mode must never break the session.
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
