import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))  # in-process imports use this checkout, not an installed kit


class CliTests(unittest.TestCase):
    def _run(self, *args, cwd, env=None):
        full_env = {**os.environ, "PYTHONPATH": str(REPO / "src"), **(env or {})}
        return subprocess.run(
            [sys.executable, "-m", "standards.cli", *args],
            cwd=str(cwd), capture_output=True, text=True, env=full_env,
            stdin=subprocess.DEVNULL,  # never a terminal, so bare `standards` can't open the menu
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

    def test_check_help_lists_drift_base_flag(self):
        res = self._run("help", "check", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("--drift-base", res.stdout)

    def test_profile_help_lists_the_four_profiles(self):
        for command in ("init", "adopt"):
            res = self._run(command, "--help", cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            text = " ".join(res.stdout.split())  # argparse wraps help text
            self.assertIn("application, library, data, documentation", text)
            self.assertIn("comma-separated", text)

    def test_infra_profile_is_an_alias_for_application(self):
        # ADR-0025 merged infra into application; old scripts keep working.
        from standards.cli import build_parser
        parser, _ = build_parser()
        for command in ("init", "adopt"):
            args = parser.parse_args([command, "--profile", "infra", "."])
            self.assertEqual(args.profile, ["application"])

    def test_doctor_reads_a_legacy_infra_marker_as_application(self):
        from standards.doctor import doctor_lines
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".standards-kit.json").write_text(json.dumps(
                {"kit_version": "1.3.0", "profile": "infra", "tracked": {}, "managed": {}}), encoding="utf-8")
            _, lines = doctor_lines(root, recommend=True,
                                    check_runner=lambda _: subprocess.CompletedProcess([], 0, "", ""))
            text = "\n".join(lines)
            self.assertIn("profile=application", text)
            self.assertIn("support/incidents", text)  # application's support recommendations

    def test_init_takes_a_comma_list_of_profiles(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("init", "--profile", "application,data", "--agents", "claude",
                               str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            marker = json.loads((target / ".standards-kit.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["profiles"], ["application", "data"])
            self.assertIn("(application + data)", result.stdout)

    def test_rejects_documentation_combined_with_another_profile(self):
        with tempfile.TemporaryDirectory() as d:
            result = self._run("adopt", "--profile", "documentation,library", d, cwd=REPO)
            self.assertEqual(result.returncode, 2)
            self.assertIn("documentation", result.stderr)
            self.assertFalse((Path(d) / ".standards-kit.json").exists())

    def test_doctor_checks_every_profile_for_recommendations(self):
        from standards.doctor import doctor_lines
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".standards-kit.json").write_text(json.dumps(
                {"kit_version": "1.5.0", "profile": "library", "profiles": ["library", "data"],
                 "tracked": {}, "managed": {}}), encoding="utf-8")
            _, lines = doctor_lines(root, recommend=True,
                                    check_runner=lambda _: subprocess.CompletedProcess([], 0, "", ""))
            text = "\n".join(lines)
            self.assertIn("profile=library + data", text)
            self.assertIn("support/incidents", text)  # from data, not library

    def test_check_parses_drift_base(self):
        from standards.cli import build_parser
        parser, _ = build_parser()
        args = parser.parse_args(["check", "--drift-base", "origin/main", "."])
        self.assertEqual(args.drift_base, "origin/main")

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

    def test_bare_standards_without_a_terminal_prints_help(self):
        res = self._run(cwd=REPO)
        self.assertEqual(res.returncode, 2)
        self.assertIn("usage: standards", res.stdout)
        self.assertIn("no interactive terminal", res.stderr)

    def test_interactive_needs_more_than_isatty(self):
        # Windows reports the NUL device as a tty, so `standards < NUL > NUL` would
        # open the menu on isatty() alone. Requiring os.get_terminal_size() (which
        # raises OSError on NUL) closes that gap, cross-platform via mocks.
        from unittest import mock

        from standards import cli

        class _Tty:
            def isatty(self):
                return True

        with mock.patch.object(cli.sys, "stdin", _Tty()), \
                mock.patch.object(cli.sys, "stdout", _Tty()):
            with mock.patch.object(cli.os, "get_terminal_size", side_effect=OSError):
                self.assertFalse(cli._interactive())  # NUL: tty but no terminal size
            with mock.patch.object(cli.os, "get_terminal_size",
                                   return_value=os.terminal_size((80, 24))):
                self.assertTrue(cli._interactive())

    def test_change_command_updates_what_the_repo_contains(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", "--agents", "claude", str(target),
                             cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            res = self._run("change", "--profile", "library,data", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            marker = json.loads((target / ".standards-kit.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["profiles"], ["library", "data"])
            self.assertIn("docs/06-runbook.md", res.stdout)

    def test_change_without_a_marker_points_at_setup(self):
        with tempfile.TemporaryDirectory() as d:
            res = self._run("change", "--profile", "library", d, cwd=REPO)
            self.assertEqual(res.returncode, 2)
            self.assertIn("standards adopt", res.stderr)

    def test_commands_lists_public_commands(self):
        res = self._run("commands", cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        text = res.stdout.lower()
        for expected in ("init", "adopt", "change", "update", "check", "doctor", "new-skill"):
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

    def test_init_agents_flag_records_the_choice(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("init", "--profile", "library", "--agents", "copilot",
                               str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            marker = json.loads((target / ".standards-kit.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["agents"], ["copilot"])
            self.assertIn(".github/hooks/standards.json", result.stdout)

    def test_adopt_agents_flag_records_the_choice(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("adopt", "--profile", "library", "--agents", "copilot,claude",
                               str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            marker = json.loads((target / ".standards-kit.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["agents"], ["claude", "copilot"])
            self.assertIn(".claude/settings.json", result.stdout)

    def test_rejects_unknown_agent(self):
        with tempfile.TemporaryDirectory() as d:
            result = self._run("init", "--profile", "library", "--agents", "cursor", d,
                               cwd=REPO)
            self.assertEqual(result.returncode, 2)
            self.assertIn("claude", result.stderr)

    def test_init_without_agents_detects_the_machine(self):
        with tempfile.TemporaryDirectory() as d:
            home, target = Path(d) / "home", Path(d) / "repo"
            (home / ".copilot").mkdir(parents=True)
            target.mkdir()
            env = {"HOME": str(home), "USERPROFILE": str(home), "PATH": str(home)}
            result = self._run("init", "--profile", "library", str(target), cwd=REPO,
                               env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            marker = json.loads((target / ".standards-kit.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["agents"], ["copilot"])
            self.assertIn("detected", result.stdout)

    def test_force_reinit_without_agents_keeps_the_recorded_choice(self):
        with tempfile.TemporaryDirectory() as d:
            home, target = Path(d) / "home", Path(d) / "repo"
            (home / ".claude").mkdir(parents=True)  # this machine would detect claude
            target.mkdir()
            env = {"HOME": str(home), "USERPROFILE": str(home), "PATH": str(home)}
            first = self._run("init", "--profile", "library", "--agents", "copilot",
                              str(target), cwd=REPO, env=env)
            self.assertEqual(first.returncode, 0, first.stderr)
            again = self._run("init", "--profile", "library", "--force", str(target),
                              cwd=REPO, env=env)
            self.assertEqual(again.returncode, 0, again.stderr)
            marker = json.loads((target / ".standards-kit.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["agents"], ["copilot"])
            self.assertIn("recorded", again.stdout)
            self.assertFalse((target / ".claude" / "settings.json").exists())

    def test_detect_agents(self):
        from unittest import mock

        from standards.wizard import detect_agents
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            on_path: set[str] = set()
            with mock.patch("standards.wizard.Path.home", return_value=home), \
                    mock.patch("standards.wizard.shutil.which",
                               side_effect=lambda name: name if name in on_path else None):
                self.assertEqual(detect_agents(), ["claude", "copilot"])  # found neither
                on_path.add("copilot")
                self.assertEqual(detect_agents(), ["copilot"])
                (home / ".claude").mkdir()
                self.assertEqual(detect_agents(), ["claude", "copilot"])
                on_path.clear()
                self.assertEqual(detect_agents(), ["claude"])
                (home / ".vscode" / "extensions" / "github.copilot-chat-1.0").mkdir(parents=True)
                self.assertEqual(detect_agents(), ["claude", "copilot"])

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

    def test_corrupt_marker_errors_cleanly(self):
        # A corrupt .standards-kit.json must give a clean error + exit 2, not a traceback.
        for command in ("update", "change --profile library", "doctor"):
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / ".standards-kit.json").write_text("{ not json", encoding="utf-8")
                res = self._run(*command.split(), str(d), cwd=REPO)
                self.assertEqual(res.returncode, 2 if command != "doctor" else 1,
                                 f"{command}: {res.stderr}")
                self.assertNotIn("Traceback", res.stderr, f"{command} leaked a traceback")

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
