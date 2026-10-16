"""Tests for scripts/drift/drift.py (ADR-0023 drift detection)."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import drift  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "drift.py"
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

    def test_malformed_marker_rules_are_ignored(self):
        defaults = drift.load_rules(None)
        self.assertEqual(drift.load_rules({"drift": None}), defaults)
        bad = {"drift": [{"update": "CHANGELOG.md", "when": "src/**"},
                         {"update": "docs/x.md", "when_commits": "feat"}]}
        self.assertEqual(drift.load_rules(bad), defaults)


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


def branch_off(root: Path) -> str:
    """Start a `pr` branch and return the name of the branch it came from."""
    base = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root,
                          capture_output=True, text=True, check=True).stdout.strip()
    git(root, "checkout", "-q", "-b", "pr")
    return base


class PullRequestRangeTests(unittest.TestCase):
    def test_ignores_drift_already_on_the_base_branch(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            write_commit(root, "src/old.py", "feat: old change with no entry")
            base = branch_off(root)
            write_commit(root, "docs/x.md", "docs: tweak")
            self.assertEqual(drift.find_drift(root),
                             {"CHANGELOG.md": ["feat: old change with no entry"]})
            self.assertEqual(drift.find_drift(root, base=base), {})

    def test_counts_the_prs_own_commits(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            base = branch_off(root)
            write_commit(root, "src/new.py", "feat: new")
            self.assertEqual(drift.find_drift(root, base=base), {"CHANGELOG.md": ["feat: new"]})

    def test_doc_updated_later_in_the_pr_is_current(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            base = branch_off(root)
            write_commit(root, "src/new.py", "feat: new")
            write_commit(root, "CHANGELOG.md", "docs: note new")
            self.assertEqual(drift.find_drift(root, base=base), {})

    def test_pr_description_waiver_covers_the_whole_pr(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            base = branch_off(root)
            write_commit(root, "src/new.py", "feat: internal helper")
            found = drift.find_drift(root, waivers=["changelog (internal only)"], base=base)
            self.assertEqual(found, {})

    def test_doc_update_still_counts_after_the_base_moves_on(self):
        # GitHub checks out a synthetic merge of the PR into the latest base.
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            base = branch_off(root)
            write_commit(root, "src/new.py", "feat: new")
            write_commit(root, "CHANGELOG.md", "docs: note new")
            git(root, "checkout", "-q", base)
            write_commit(root, "docs/other.md", "docs: unrelated base change")
            git(root, "checkout", "-q", "--detach", base)
            git(root, "merge", "-q", "--no-ff", "pr", "-m", "Merge pr into base")
            self.assertEqual(drift.find_drift(root, base=base), {})

    def test_doc_update_still_counts_after_merging_the_base_in(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            base = branch_off(root)
            write_commit(root, "src/new.py", "feat: new")
            write_commit(root, "CHANGELOG.md", "docs: note new")
            git(root, "checkout", "-q", base)
            write_commit(root, "docs/other.md", "docs: unrelated base change")
            git(root, "checkout", "-q", "pr")
            git(root, "merge", "-q", "--no-ff", base, "-m", "Merge base into pr")
            self.assertEqual(drift.find_drift(root, base=base), {})

    def test_base_branch_doc_updates_dont_cover_the_prs_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            base = branch_off(root)
            write_commit(root, "src/new.py", "feat: new")
            git(root, "checkout", "-q", base)
            write_commit(root, "CHANGELOG.md", "docs: base changelog entry")
            git(root, "checkout", "-q", "--detach", base)
            git(root, "merge", "-q", "--no-ff", "pr", "-m", "Merge pr into base")
            self.assertEqual(drift.find_drift(root, base=base), {"CHANGELOG.md": ["feat: new"]})

    def test_unknown_base_is_an_error_not_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            with self.assertRaises(drift.DriftError):
                drift.find_drift(root, base="no-such-branch")


def run_hook(cwd: Path, stdin: str, env: dict | None = None) -> subprocess.CompletedProcess:
    # Hosts send UTF-8 JSON, unescaped, whatever the Windows code page is.
    # Drop GITHUB_ACTIONS so the suite behaves the same locally and in CI.
    base = {k: v for k, v in os.environ.items() if k != "GITHUB_ACTIONS"}
    return subprocess.run([sys.executable, str(SCRIPT), "--hook"], cwd=cwd, input=stdin,
                          capture_output=True, encoding="utf-8", errors="replace",
                          env={**base, **(env or {})})


def stop_input(root: Path, active: bool = False, session: str = "s1") -> str:
    return json.dumps({"hook_event_name": "Stop", "cwd": str(root), "stop_hook_active": active,
                       "session_id": session}, ensure_ascii=False)


def drifting_repo(d: str) -> Path:
    root = make_repo(d)
    write_commit(root, "src/a.py", "feat: add a")
    return root


def set_marker(root: Path, data: dict) -> None:
    (root / ".standards-kit.json").write_text(json.dumps(data), encoding="utf-8")


class HookTests(unittest.TestCase):
    def test_kit_repo_without_a_marker_blocks_once(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            result = run_hook(root, stop_input(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)
            # Top-level fields only: Codex rejects unknown keys and drops the block.
            self.assertEqual(set(out), {"decision", "reason"})
            self.assertEqual(out["decision"], "block")
            self.assertIn("CHANGELOG.md", out["reason"])
            self.assertIn("feat: add a", out["reason"])

    def test_second_stop_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            result = run_hook(root, stop_input(root, active=True))
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_existing_adopters_default_to_advise(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            set_marker(root, {"kit_version": "1.3.0", "profile": "library"})
            result = run_hook(root, stop_input(root))
            self.assertEqual((result.returncode, result.stdout), (0, ""))
            self.assertIn("CHANGELOG.md", result.stderr)

    def test_adopters_can_opt_into_enforce(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            set_marker(root, {"hook_mode": "enforce"})
            result = run_hook(root, stop_input(root))
            self.assertEqual(json.loads(result.stdout)["decision"], "block")

    def test_nothing_behind_lets_the_turn_end(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            result = run_hook(root, stop_input(root))
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_git_errors_fail_open(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_hook(Path(d), stop_input(Path(d)))
            self.assertEqual((result.returncode, result.stdout), (0, ""))
            self.assertIn("can't check", result.stderr)

    def test_reads_the_repo_from_hook_input(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root = drifting_repo(d)
            result = run_hook(Path(elsewhere), stop_input(root))
            self.assertEqual(json.loads(result.stdout)["decision"], "block")

    def test_unreadable_hook_input_never_blocks(self):
        # Without readable input there's no stop_hook_active guard, so blocking could loop.
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            for stdin in ("not json", "[1, 2]", ""):
                with self.subTest(stdin=stdin):
                    result = run_hook(root, stdin)
                    self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_bad_drift_config_never_breaks_the_hook(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            set_marker(root, {"hook_mode": "enforce", "drift": None})
            result = run_hook(root, stop_input(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["decision"], "block")  # defaults still apply

    def test_non_ascii_repo_path_in_hook_input(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "dépôt-漢字"
            folder.mkdir()
            root = drifting_repo(str(folder))
            result = run_hook(Path(d), stop_input(root))
            self.assertEqual(json.loads(result.stdout)["decision"], "block")

    def test_advisory_output_survives_non_ascii_subjects(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            write_commit(root, "src/a.py", "feat: 漢字の機能")
            set_marker(root, {"profile": "library"})
            result = run_hook(root, stop_input(root))
            self.assertEqual((result.returncode, result.stdout), (0, ""))
            self.assertIn("CHANGELOG.md", result.stderr)

    def test_local_hosts_block_again_on_a_new_turn(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            for _ in range(2):
                self.assertEqual(json.loads(run_hook(root, stop_input(root)).stdout)["decision"], "block")


class CiRunnerHookTests(unittest.TestCase):
    """On CI runners (the Copilot cloud agent) the engine reprompts the same session for
    the PR description, and a block there replaces it, so block once per session."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {"GITHUB_ACTIONS": "true", "RUNNER_TEMP": self.tmp.name}

    def tearDown(self):
        self.tmp.cleanup()

    def stop(self, root: Path, session: str = "s1") -> subprocess.CompletedProcess:
        return run_hook(root, stop_input(root, session=session), self.env)

    def test_blocks_only_once_per_session(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            self.assertEqual(json.loads(self.stop(root).stdout)["decision"], "block")
            later = self.stop(root)  # the engine's PR-description turn
            self.assertEqual((later.returncode, later.stdout), (0, ""))

    def test_each_session_gets_its_own_block(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            self.stop(root, session="s1")
            self.assertEqual(json.loads(self.stop(root, session="s2").stdout)["decision"], "block")

    def test_a_stop_with_nothing_behind_does_not_use_up_the_block(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(d)
            self.assertEqual(self.stop(root).stdout, "")
            write_commit(root, "src/a.py", "feat: add a")
            self.assertEqual(json.loads(self.stop(root).stdout)["decision"], "block")

    def test_hostile_session_id_stays_inside_runner_temp(self):
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            self.assertEqual(json.loads(self.stop(root, session="../../escape").stdout)["decision"], "block")
            self.assertEqual([p.parent for p in Path(self.tmp.name).iterdir()], [Path(self.tmp.name)])
            self.assertFalse((Path(self.tmp.name).parent.parent / "escape").exists())

    def test_cannot_record_the_block_so_does_not_block(self):
        # Blocking without a record would block again on every later turn.
        with tempfile.TemporaryDirectory() as d:
            root = drifting_repo(d)
            self.env["RUNNER_TEMP"] = str(Path(self.tmp.name) / "missing")
            result = self.stop(root)
            self.assertEqual((result.returncode, result.stdout), (0, ""))
            self.assertIn("not blocking", result.stderr)

    def test_no_usable_temp_folder_does_not_block_or_crash(self):
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}), \
                mock.patch("drift.tempfile.gettempdir", side_effect=FileNotFoundError("no temp")), \
                contextlib.redirect_stderr(io.StringIO()):
            os.environ.pop("RUNNER_TEMP", None)
            self.assertTrue(drift.ci_block_used({"session_id": "s1"}))


if __name__ == "__main__":
    unittest.main()
