import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


class InitTests(unittest.TestCase):
    def _run(self, target, **kw):
        from standards.init import run_init
        return run_init(target, **kw)

    def test_new_adoption_enforces_the_stop_hook(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            self.assertEqual(read_marker(target)["hook_mode"], "enforce")

    def test_default_adoption_gets_only_the_claude_hook_file(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            self.assertTrue((target / ".claude" / "settings.json").is_file())
            self.assertFalse((target / ".github" / "hooks").exists())
            self.assertEqual(read_marker(target)["agents"], ["claude", "copilot"])

    def test_copilot_only_adoption_gets_only_the_copilot_hook_file(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29", agents=["copilot"])
            marker = read_marker(target)
            self.assertTrue((target / ".github" / "hooks" / "standards.json").is_file())
            self.assertFalse((target / ".claude" / "settings.json").exists())
            self.assertFalse((target / "docs" / "templates" / "copilot-hooks.json").exists())
            self.assertEqual(marker["agents"], ["copilot"])
            self.assertIn(".github/hooks/standards.json", marker["tracked"])
            self.assertNotIn(".claude/settings.json", marker["tracked"])

    def test_copilot_only_init_ignores_an_existing_claude_settings_file(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / ".claude").mkdir()
            (target / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
            self._run(target, profile="library", adopted="2026-05-29", agents=["copilot"])
            self.assertEqual(
                (target / ".claude" / "settings.json").read_text(encoding="utf-8"), "{}\n")

    def test_force_reinit_refuses_to_switch_while_the_old_hook_file_remains(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29", agents=["claude"])
            with self.assertRaisesRegex(FileExistsError, r"\.claude/settings\.json"):
                self._run(target, profile="library", adopted="2026-05-29", force=True,
                          agents=["copilot"])
            self.assertFalse((target / ".github" / "hooks").exists())
            (target / ".claude" / "settings.json").unlink()
            self._run(target, profile="library", adopted="2026-05-29", force=True,
                      agents=["copilot"])
            self.assertEqual(read_marker(target)["agents"], ["copilot"])

    def test_copies_tracked_and_writes_marker(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            self.assertTrue((target / "README.md").is_file())
            self.assertTrue((target / "CHANGELOG.md").is_file())
            self.assertTrue((target / "docs" / "templates" / "adr-template.md").is_file())
            self.assertTrue((target / "docs" / "STANDARDS.md").is_file())
            marker = read_marker(target)
            self.assertEqual(marker["profile"], "library")
            self.assertIn("docs/STANDARDS.md", marker["tracked"])
            self.assertTrue((target / "ai" / "current-state.md").is_file())
            from standards.marker import sha256_file
            self.assertEqual(
                marker["tracked"]["docs/STANDARDS.md"],
                sha256_file(target / "docs" / "STANDARDS.md"),
            )

    def test_scaffold_once_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "ai").mkdir()
            (target / "ai" / "current-state.md").write_text("MINE\n", encoding="utf-8")
            (target / "README.md").write_text("# Mine\n", encoding="utf-8")
            (target / "CHANGELOG.md").write_text("# Mine changelog\n", encoding="utf-8")
            self._run(target, profile="application", adopted="2026-05-29")
            self.assertEqual(
                (target / "ai" / "current-state.md").read_text(encoding="utf-8"), "MINE\n"
            )
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "# Mine\n")
            self.assertEqual(
                (target / "CHANGELOG.md").read_text(encoding="utf-8"),
                "# Mine changelog\n",
            )

    def test_scaffolded_readme_and_changelog_are_filled(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="documentation", adopted="2026-05-29")
            readme = (target / "README.md").read_text(encoding="utf-8")
            changelog = (target / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertIn("# " + target.name, readme)
            self.assertIn("documentation", readme)
            self.assertIn("## [0.1.0] - 2026-05-29", changelog)
            self.assertIn("Initial adoption of the Repo-Standards-Kit", changelog)

    def test_scaffolds_normal_discovery_folder(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            disc = target / "docs" / "discovery"
            self.assertTrue((disc / "README.md").is_file())
            self.assertFalse((disc / ".gitignore").exists())
            self.assertFalse((disc / "captured").exists())
            for sub in ("meetings", "requirements", "use-cases", "notes", "artifacts"):
                self.assertFalse((disc / sub).exists(), f"{sub}/ should not be scaffolded")

    def test_optional_knowledge_lanes_not_scaffolded_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="application", adopted="2026-05-29")
            for rel in (
                "docs/design",
                "support/incidents",
                "support/troubleshooting",
                "support/guides",
            ):
                self.assertFalse((target / rel).exists(), f"{rel} should be optional")

    def test_profile_written_into_checklist(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="data", adopted="2026-05-29")
            checklist = (target / "docs" / "STANDARDS-CHECKLIST.md").read_text(encoding="utf-8")
            self.assertIn("**Profile:** data", checklist)
            self.assertNotIn("infra", checklist)

    def test_combined_profiles_reach_the_marker_and_checklist(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="application,data", adopted="2026-05-29")
            marker = read_marker(target)
            checklist = (target / "docs" / "STANDARDS-CHECKLIST.md").read_text(encoding="utf-8")
            self.assertEqual(marker["profile"], "application")
            self.assertEqual(marker["profiles"], ["application", "data"])
            self.assertIn("**Profile:** application + data\n", checklist)

    def test_creates_and_ticks_the_docs_the_profiles_need(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            docs = target / "docs"
            checklist = (docs / "STANDARDS-CHECKLIST.md").read_text(encoding="utf-8")
            for doc in ("04-api-and-integrations.md", "07-testing.md",  # Required
                        "02-architecture.md", "08-security-and-compliance.md"):  # Expected
                self.assertTrue((docs / doc).is_file(), doc)
                self.assertIn(f"- [x] `docs/{doc}`", checklist)
            for doc in ("01-prd.md", "03-data-model.md", "05-implementation-plan.md",
                        "06-runbook.md", "09-deployment.md"):  # Optional or N/A
                self.assertFalse((docs / doc).exists(), doc)
            self.assertIn("- `docs/versioning-policy.md`", checklist)  # listed, not created
            self.assertNotIn("<doc>", checklist)
            self.assertEqual((docs / "07-testing.md").read_text(encoding="utf-8"),
                             (REPO / "docs" / "templates" / "testing-template.md")
                             .read_text(encoding="utf-8"))

    def test_strongest_tier_decides_which_docs_are_created(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library,data", adopted="2026-05-29")
            self.assertTrue((target / "docs" / "06-runbook.md").is_file())  # N/A for library
            self.assertTrue((target / "docs" / "01-prd.md").is_file())  # Optional for library

    def test_existing_profile_docs_are_kept(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "07-testing.md").write_text("MINE\n", encoding="utf-8")
            self._run(target, profile="library", adopted="2026-05-29")
            self.assertEqual((target / "docs" / "07-testing.md").read_text(encoding="utf-8"),
                             "MINE\n")

    def test_rejects_documentation_combined_with_another_profile(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                self._run(Path(d), profile="documentation,library", adopted="2026-05-29")

    def test_refuses_reinit_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="data", adopted="2026-05-29")
            with self.assertRaises(FileExistsError):
                self._run(target, profile="data", adopted="2026-05-29")
            self._run(target, profile="data", adopted="2026-05-29", force=True)

    def test_partial_files_recorded_in_managed_with_block_hash(self):
        from standards.managed import block_hash
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            marker = read_marker(target)
            self.assertIn("AGENTS.md", marker["managed"])
            self.assertNotIn("AGENTS.md", marker["tracked"])
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertEqual(
                marker["managed"]["AGENTS.md"],
                block_hash((target / "AGENTS.md").read_text(encoding="utf-8")),
            )


    def test_init_refuses_differing_existing_kit_tracked(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("PREEXISTING DIFFERENT\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                self._run(target, profile="library", adopted="2026-05-29")
            self.assertFalse((target / ".standards-kit.json").exists())

    def test_init_allows_identical_existing_file(self):
        from standards.payload import payload_root
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            src = payload_root() / "docs" / "STANDARDS.md"
            (target / "docs" / "STANDARDS.md").write_bytes(src.read_bytes())
            self._run(target, profile="library", adopted="2026-05-29")  # no raise
            self.assertTrue((target / ".standards-kit.json").is_file())

    def test_init_force_overwrites_differing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("DIFFERENT\n", encoding="utf-8")
            self._run(target, profile="library", adopted="2026-05-29", force=True)
            self.assertTrue((target / ".standards-kit.json").is_file())

    def test_partial_existing_preserves_downstream_content(self):
        # A pre-existing partial file with the SAME managed block but extra
        # downstream content must NOT be clobbered by the payload copy.
        from standards.marker import read_marker
        from standards.payload import payload_root
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            src = (payload_root() / "AGENTS.md").read_text(encoding="utf-8")
            (target / "AGENTS.md").write_text(
                src + "\n## My downstream section\nkeep me\n", encoding="utf-8")
            self._run(target, profile="library", adopted="2026-05-29")  # guard passes (block matches)
            after = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## My downstream section", after)  # preserved, not overwritten
            self.assertIn("AGENTS.md", read_marker(target)["managed"])


if __name__ == "__main__":
    unittest.main()
