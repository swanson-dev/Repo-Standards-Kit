"""Tests for the CI drift check (checks/doc_drift.py, ADR-0023)."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check import build_context  # noqa: E402
from checks import Context  # noqa: E402
from checks.doc_drift import run  # noqa: E402


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                          text=True).stdout


def make_pr_repo(d: str) -> tuple[Path, str]:
    """A repo whose `pr` branch adds a feat commit with no changelog entry; returns (root, base)."""
    root = Path(d)
    git(root, "init", "-q")
    for key, value in (("user.email", "t@example.com"), ("user.name", "t"),
                       ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
        git(root, "config", key, value)
    (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "docs: start changelog")
    base = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    git(root, "checkout", "-q", "-b", "pr")
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("x\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "feat: add a")
    return root, base


def ctx(root: Path, base: str | None = None, adopter: bool = False,
        overrides: dict | None = None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {}, drift_base=base)


class DocDriftCheckTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"STANDARDS_PR_BODY": ""})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_off_without_a_base(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_pr_repo(d)
            self.assertEqual(run(root, ctx(root)), [])

    def test_kit_repo_fails_the_pr(self):
        with tempfile.TemporaryDirectory() as d:
            root, base = make_pr_repo(d)
            findings = run(root, ctx(root, base))
            self.assertEqual([(f.check_id, f.severity) for f in findings], [("drift", "error")])
            self.assertIn("CHANGELOG.md", findings[0].message)
            self.assertIn("feat: add a", findings[0].message)

    def test_adopters_get_a_warning_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            root, base = make_pr_repo(d)
            findings = run(root, ctx(root, base, adopter=True))
            self.assertEqual([f.severity for f in findings], ["warn"])

    def test_adopters_can_escalate_to_error(self):
        with tempfile.TemporaryDirectory() as d:
            root, base = make_pr_repo(d)
            findings = run(root, ctx(root, base, adopter=True, overrides={"drift": "error"}))
            self.assertEqual([f.severity for f in findings], ["error"])

    def test_pr_description_waives_a_doc(self):
        body = "Adds an internal helper.\n\nDocs-Unaffected: changelog (internal helper)\n"
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.dict(os.environ, {"STANDARDS_PR_BODY": body}):
            root, base = make_pr_repo(d)
            self.assertEqual(run(root, ctx(root, base)), [])

    def test_unreadable_history_is_reported_not_passed(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_pr_repo(d)
            findings = run(root, ctx(root, "no-such-branch"))
            self.assertEqual([f.severity for f in findings], ["error"])
            self.assertIn("can't check drift", findings[0].message)

    def test_unreadable_history_is_an_error_even_for_adopters(self):
        # An opted-in check that can't run must not pass quietly as a warning.
        with tempfile.TemporaryDirectory() as d:
            root, _ = make_pr_repo(d)
            findings = run(root, ctx(root, "no-such-branch", adopter=True))
            self.assertEqual([f.severity for f in findings], ["error"])

    def test_build_context_carries_the_base(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(build_context(Path(d), drift_base="origin/main").drift_base,
                             "origin/main")


if __name__ == "__main__":
    unittest.main()
