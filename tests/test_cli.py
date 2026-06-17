import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def _run(self, *args, cwd):
        full_env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
        return subprocess.run(
            [sys.executable, "-m", "standards.cli", *args],
            cwd=str(cwd), capture_output=True, text=True, env=full_env,
        )

    def _seed_downstream_core(self, target: Path):
        (target / "README.md").write_text("# Test Repo\n", encoding="utf-8")
        (target / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [0.1.0] - 2026-06-16\n\n### Added\n- Initial adoption.\n",
            encoding="utf-8",
        )

    def test_top_level_help_lists_workflow_commands(self):
        res = self._run("--help", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        text = res.stdout.lower()
        for expected in ("init", "adopt", "update", "check", "doctor", "new-skill", "commands"):
            self.assertIn(expected, text)
        for heading in ("adopt", "maintain", "diagnose", "author"):
            self.assertIn(heading, text)

    def test_help_alias_prints_top_level_help(self):
        flag_help = self._run("--help", cwd=REPO)
        alias_help = self._run("help", cwd=REPO)
        self.assertEqual(alias_help.returncode, 0, alias_help.stderr)
        self.assertEqual(alias_help.stdout, flag_help.stdout)

    def test_help_alias_for_subcommand_prints_examples(self):
        res = self._run("help", "init", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("init --profile library", res.stdout)

    def test_check_help_lists_external_links_flag(self):
        res = self._run("help", "check", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("--external-links", res.stdout)

    def test_check_help_lists_freshness_report_flag(self):
        res = self._run("help", "check", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("--freshness-report", res.stdout)

    def test_help_alias_for_doctor_prints_examples(self):
        res = self._run("help", "doctor", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("doctor --recommend", res.stdout)

    def test_help_alias_for_new_skill_prints_examples(self):
        res = self._run("help", "new-skill", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("new-skill review-docs", res.stdout)

    def test_commands_lists_public_commands(self):
        res = self._run("commands", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        text = res.stdout.lower()
        for expected in ("init", "adopt", "update", "check", "doctor", "new-skill"):
            self.assertIn(expected, text)

    def test_help_alias_unknown_topic_lists_valid_topics(self):
        res = self._run("help", "bogus", cwd=REPO)
        self.assertNotEqual(res.returncode, 0)
        text = (res.stdout + res.stderr).lower()
        self.assertIn("valid help topics", text)
        for expected in ("init", "adopt", "update", "check", "doctor", "new-skill"):
            self.assertIn(expected, text)

    def test_init_subcommand_creates_repo(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".standards-kit.json").is_file())
            self.assertTrue((target / "docs" / "STANDARDS.md").is_file())

    def test_init_accepts_documentation_profile(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("init", "--profile", "documentation", str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            marker = (target / ".standards-kit.json").read_text(encoding="utf-8")
            self.assertIn('"profile": "documentation"', marker)

    def test_rejects_unknown_profile(self):
        with tempfile.TemporaryDirectory() as d:
            result = self._run("init", "--profile", "bogus", d, cwd=REPO)
            self.assertNotEqual(result.returncode, 0)

    def test_update_after_init(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            res = self._run("update", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("unchanged", (res.stdout + res.stderr).lower())

    def test_update_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run("init", "--profile", "library", str(target), cwd=REPO)
            (target / "docs" / "STANDARDS.md").write_text("LOCAL\n", encoding="utf-8")
            before = sorted(p.name for p in target.rglob("*"))
            res = self._run("update", "--dry-run", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(before, sorted(p.name for p in target.rglob("*")))

    def test_update_without_marker_errors(self):
        with tempfile.TemporaryDirectory() as d:
            res = self._run("update", d, cwd=REPO)
            self.assertNotEqual(res.returncode, 0)
            text = (res.stdout + res.stderr).lower()
            self.assertIn("standards init", text)
            self.assertIn("standards adopt", text)

    def test_adopt_subcommand_is_nondestructive(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("MINE\n", encoding="utf-8")
            res = self._run("adopt", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual((target / "docs" / "STANDARDS.md").read_text(encoding="utf-8"), "MINE\n")
            self.assertTrue((target / ".standards-kit.json").is_file())
            self.assertIn("conflicts", (res.stdout + res.stderr).lower())

    def test_check_clean_repo_exits_zero(self):
        # The kit repo itself is self-clean (0 errors); `standards check` on it passes.
        res = self._run("check", str(REPO), cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("standards check", (res.stdout + res.stderr).lower())

    def test_check_reports_violations_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            # Remove a universal-core file -> structural check must error -> exit 1.
            (target / "AGENTS.md").unlink()
            res = self._run("check", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 1, res.stdout + res.stderr)

    def test_doctor_clean_adopted_repo_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            res = self._run("doctor", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("Doctor: healthy", res.stdout)
            self.assertIn("profile=library", res.stdout)

    def test_doctor_missing_marker_recommends_init_or_adopt(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            res = self._run("doctor", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 1)
            text = (res.stdout + res.stderr).lower()
            self.assertIn("not adopted", text)
            self.assertIn("standards init", text)
            self.assertIn("standards adopt", text)

    def test_doctor_reports_standards_check_errors(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            (target / "AGENTS.md").unlink()
            res = self._run("doctor", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 1)
            self.assertIn("standards check: failing", res.stdout.lower())
            self.assertIn("ERROR", res.stdout)

    def test_doctor_reports_stale_ai_files(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            (target / "ai" / "handoff.md").write_text(
                "---\nwritten: 2020-01-01T00:00:00-05:00\nwritten_by: test\nfor: next-session\n---\n",
                encoding="utf-8",
            )
            res = self._run("doctor", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("[ai]", res.stdout)

    def test_doctor_reports_sidecar_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            (target / "docs" / "STANDARDS.md.kit-1.0.0").write_text("kit copy\n", encoding="utf-8")
            res = self._run("doctor", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 1)
            self.assertIn("sidecar conflicts", res.stdout.lower())
            self.assertIn("docs/STANDARDS.md.kit-1.0.0", res.stdout)

    def test_doctor_reports_managed_region_drift(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            agents = target / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8").replace("Canonical reading order", "Changed reading order"), encoding="utf-8")
            res = self._run("doctor", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 1)
            self.assertIn("managed region drift", res.stdout.lower())
            self.assertIn("AGENTS.md", res.stdout)

    def test_doctor_recommend_suggests_optional_lanes(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "application", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            (target / "docs" / "06-runbook.md").write_text("# Runbook\n", encoding="utf-8")
            res = self._run("doctor", "--recommend", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("docs/discovery/meetings", res.stdout)
            self.assertIn("support/incidents", res.stdout)
            self.assertIn("docs/design", res.stdout)

    def test_doctor_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._seed_downstream_core(target)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            before = sorted(p.relative_to(target).as_posix() for p in target.rglob("*"))
            res = self._run("doctor", "--recommend", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            after = sorted(p.relative_to(target).as_posix() for p in target.rglob("*"))
            self.assertEqual(before, after)

    def test_new_skill_subcommand_creates_skill_prompt_and_index_row(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            (target / ".git").mkdir()
            res = self._run(
                "new-skill",
                "review-docs",
                "Review docs before shipping",
                str(target),
                cwd=REPO,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((target / ".claude" / "skills" / "review-docs" / "SKILL.md").is_file())
            self.assertTrue((target / ".github" / "prompts" / "review-docs.prompt.md").is_file())
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("| `review-docs` | Review docs before shipping |", agents)

    def test_new_skill_subcommand_rejects_invalid_name(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            (target / ".git").mkdir()
            res = self._run("new-skill", "ReviewDocs", "Review docs", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 2)
            self.assertIn("kebab-case", res.stderr)


if __name__ == "__main__":
    unittest.main()
