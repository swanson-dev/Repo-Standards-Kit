"""Tests for scripts/drift/drift.py (ADR-0023 drift detection)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import drift  # noqa: E402

CHANGELOG_RULE = {"update": "CHANGELOG.md", "when_commits": ["feat", "fix", "perf", "revert", "!"],
                  "when": ["src/**", "scripts/**"]}
DEPLOY_RULE = {"update": "docs/09-deployment.md", "when": [".github/workflows/**", "Dockerfile"]}


def commit(subject: str, paths: list[str], body: str = "") -> drift.Commit:
    return drift.Commit(sha="0" * 40, subject=subject, body=body, paths=paths)


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def make_repo(d: str) -> Path:
    root = Path(d)
    git(root, "init", "-q")
    for key, value in (("user.email", "t@example.com"), ("user.name", "t"),
                       ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
        git(root, "config", key, value)
    (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "docs: start changelog")
    return root


def write_commit(root: Path, path: str, message: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(message + "\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", message)


class CommitTypeTests(unittest.TestCase):
    def test_reads_type_scope_and_breaking_marks(self):
        self.assertEqual(drift.commit_type("feat(cli): add menu", ""), ("feat", False))
        self.assertEqual(drift.commit_type("fix: typo", ""), ("fix", False))
        self.assertEqual(drift.commit_type("refactor!: drop flag", ""), ("refactor", True))
        self.assertEqual(drift.commit_type("chore: x", "BREAKING CHANGE: gone"), ("chore", True))

    def test_non_conventional_subject_has_no_type(self):
        self.assertEqual(drift.commit_type("Update readme", ""), (None, False))

    def test_hyphenated_breaking_change_footer(self):
        self.assertEqual(drift.commit_type("refactor: remove option", "BREAKING-CHANGE: gone"),
                         ("refactor", True))


class MatchTests(unittest.TestCase):
    def test_double_star_matches_zero_or_more_folders(self):
        self.assertTrue(drift.matches("src/api/routes.py", ["src/**/api/**"]))
        self.assertTrue(drift.matches("src/v1/api/routes.py", ["src/**/api/**"]))
        self.assertTrue(drift.matches("src/a/b.py", ["src/**"]))

    def test_single_star_stays_within_one_folder(self):
        self.assertTrue(drift.matches("Dockerfile", ["Docker*"]))
        self.assertFalse(drift.matches("docs/a.md", ["*.md"]))
        self.assertTrue(drift.matches("docs/a.md", ["**/*.md"]))


class RuleDriftTests(unittest.TestCase):
    def test_feat_commit_needs_a_changelog_entry(self):
        reasons = drift.rule_drift(CHANGELOG_RULE, [commit("feat: add menu", ["README.md"])], [])
        self.assertEqual(reasons, ["feat: add menu"])

    def test_commit_type_overrides_paths(self):
        # A chore touching src/ declares itself not user-facing.
        self.assertEqual(drift.rule_drift(CHANGELOG_RULE, [commit("chore: tidy", ["src/a.py"])], []), [])

    def test_breaking_change_needs_an_entry(self):
        reasons = drift.rule_drift(CHANGELOG_RULE, [commit("refactor!: drop flag", ["src/a.py"])], [])
        self.assertEqual(reasons, ["refactor!: drop flag"])

    def test_non_conventional_commit_falls_back_to_paths(self):
        self.assertEqual(drift.rule_drift(CHANGELOG_RULE, [commit("Tweak parser", ["src/a.py"])], []),
                         ["Tweak parser"])
        self.assertEqual(drift.rule_drift(CHANGELOG_RULE, [commit("Fix typo", ["docs/x.md"])], []), [])

    def test_path_rule_ignores_commit_type(self):
        commits = [commit("chore: rename job", [".github/workflows/ci.yml"])]
        self.assertEqual(drift.rule_drift(DEPLOY_RULE, commits, []), ["chore: rename job"])

    def test_docs_unaffected_trailer_waives_that_commit(self):
        c = commit("ci: rename job", [".github/workflows/ci.yml"],
                   body="Docs-Unaffected: deployment (renamed a job)")
        self.assertEqual(drift.rule_drift(DEPLOY_RULE, [c], []), [])

    def test_extra_waiver_covers_every_commit(self):
        commits = [commit("ci: a", ["Dockerfile"]), commit("ci: b", ["Dockerfile"])]
        self.assertEqual(drift.rule_drift(DEPLOY_RULE, commits, [], waivers=["deployment (squash)"]), [])

    def test_uncommitted_trigger_paths_count(self):
        reasons = drift.rule_drift(CHANGELOG_RULE, [], ["src/a.py", "ai/handoff.md"])
        self.assertEqual(reasons, ["uncommitted: src/a.py"])

    def test_doc_being_edited_is_not_behind(self):
        reasons = drift.rule_drift(CHANGELOG_RULE, [commit("feat: x", [])], ["CHANGELOG.md", "src/a.py"])
        self.assertEqual(reasons, [])


class LoadRulesTests(unittest.TestCase):
    def test_defaults_without_a_marker(self):
        self.assertIn("CHANGELOG.md", [r["update"] for r in drift.load_rules(None)])

    def test_marker_rule_replaces_default_for_same_doc(self):
        marker = {"drift": [{"update": "CHANGELOG.md", "when": ["lib/**"]}]}
        rules = {r["update"]: r for r in drift.load_rules(marker)}
        self.assertEqual(rules["CHANGELOG.md"], {"update": "CHANGELOG.md", "when": ["lib/**"]})

    def test_marker_rule_for_new_doc_is_added(self):
        marker = {"drift": [{"update": "docs/runbook.md", "when": ["ops/**"]}]}
        self.assertIn("docs/runbook.md", [r["update"] for r in drift.load_rules(marker)])


class FindDriftTests(unittest.TestCase):
    def test_feat_after_changelog_is_drift_until_changelog_updated(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            write_commit(root, "src/a.py", "feat: add a")
            self.assertEqual(drift.find_drift(root), {"CHANGELOG.md": ["feat: add a"]})
            write_commit(root, "CHANGELOG.md", "docs: note a")
            self.assertEqual(drift.find_drift(root), {})

    def test_rules_for_missing_docs_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            write_commit(root, "Dockerfile", "chore: add dockerfile")
            self.assertNotIn("docs/09-deployment.md", drift.find_drift(root))

    def test_marker_rules_are_read_from_standards_kit_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            write_commit(root, "docs/runbook.md", "docs: add runbook")
            marker = {"drift": [{"update": "docs/runbook.md", "when": ["ops/**"]}]}
            (root / ".standards-kit.json").write_text(json.dumps(marker), encoding="utf-8")
            write_commit(root, "ops/deploy.sh", "chore: deploy script")
            self.assertEqual(drift.find_drift(root), {"docs/runbook.md": ["chore: deploy script"]})

    def test_outside_a_git_repo_is_an_error_not_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "CHANGELOG.md").write_text("x\n", encoding="utf-8")
            with self.assertRaises(drift.DriftError):
                drift.find_drift(Path(d))

    def test_repo_without_commits_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            git(root, "init", "-q")
            (root / "CHANGELOG.md").write_text("x\n", encoding="utf-8")
            self.assertEqual(drift.find_drift(root), {})

    def test_shallow_clone_is_an_error_not_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            origin = Path(d) / "origin"
            origin.mkdir()
            make_repo(str(origin))
            write_commit(origin, "src/a.py", "feat: add a")
            clone = Path(d) / "clone"
            git(Path(d), "clone", "-q", "--depth", "1", origin.as_uri(), str(clone))
            with self.assertRaises(drift.DriftError):
                drift.find_drift(clone)

    def test_change_made_only_in_a_merge_commit_counts(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            git(root, "checkout", "-q", "-b", "side")
            write_commit(root, "docs/b.md", "docs: side note")
            git(root, "checkout", "-q", "-")
            write_commit(root, "docs/m.md", "docs: main note")
            git(root, "merge", "-q", "--no-ff", "--no-commit", "side")
            (root / "src").mkdir()
            (root / "src" / "evil.py").write_text("x\n", encoding="utf-8")
            git(root, "add", ".")
            git(root, "commit", "-q", "-m", "Merge branch side")
            self.assertEqual(drift.find_drift(root), {"CHANGELOG.md": ["Merge branch side"]})

    def test_moving_a_file_out_of_a_trigger_folder_counts(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            write_commit(root, "src/old.py", "Add old module")
            write_commit(root, "CHANGELOG.md", "docs: note old module")
            (root / "lib").mkdir()
            git(root, "mv", "src/old.py", "lib/old.py")
            self.assertEqual(drift.find_drift(root), {"CHANGELOG.md": ["uncommitted: src/old.py"]})
            git(root, "commit", "-q", "-m", "Move module")
            self.assertEqual(drift.find_drift(root), {"CHANGELOG.md": ["Move module"]})


if __name__ == "__main__":
    unittest.main()
