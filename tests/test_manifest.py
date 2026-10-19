import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class ManifestTests(unittest.TestCase):
    def test_templates_are_kit_tracked(self):
        from standards.manifest import classify
        self.assertEqual(classify("docs/templates/adr-template.md"), "kit-tracked")
        self.assertEqual(classify("docs/STANDARDS.md"), "kit-tracked")
        self.assertEqual(classify("scripts/standards-check/check.py"), "kit-tracked")

    def test_known_scaffold_targets(self):
        from standards.manifest import SCAFFOLD_ONCE
        self.assertEqual(
            SCAFFOLD_ONCE["docs/templates/ai-starters/current-state.md"],
            "ai/current-state.md",
        )
        self.assertEqual(
            SCAFFOLD_ONCE["docs/templates/STANDARDS-CHECKLIST.md.template"],
            "docs/STANDARDS-CHECKLIST.md",
        )
        self.assertEqual(
            SCAFFOLD_ONCE["docs/templates/repo-readme-template.md"],
            "README.md",
        )
        self.assertEqual(
            SCAFFOLD_ONCE["docs/templates/changelog-template.md"],
            "CHANGELOG.md",
        )

    def test_ai_starters_dir_excluded_from_kit_tracked_copy(self):
        from standards.manifest import is_excluded_from_tracked
        self.assertTrue(is_excluded_from_tracked("docs/templates/ai-starters/current-state.md"))
        self.assertFalse(is_excluded_from_tracked("docs/templates/adr-template.md"))

    def test_iter_payload_yields_known_files_and_excludes_non_payload(self):
        from standards.manifest import iter_payload
        from standards.payload import payload_root
        rels = {rel for _full, rel in iter_payload(payload_root())}
        self.assertIn("docs/templates/adr-template.md", rels)
        self.assertIn("docs/templates/discovery-note-template.md", rels)
        self.assertIn("docs/templates/discovery-meeting-template.md", rels)
        self.assertIn("docs/templates/discovery-artifact-template.md", rels)
        self.assertIn("docs/templates/design-template.md", rels)
        self.assertIn("docs/templates/incident-template.md", rels)
        self.assertIn("docs/templates/troubleshooting-template.md", rels)
        self.assertIn("docs/templates/guide-template.md", rels)
        self.assertIn("scripts/_doc_lib/helpers.py", rels)
        self.assertIn("scripts/session-context/session_context.py", rels)
        self.assertIn("scripts/drift/drift.py", rels)
        self.assertIn("docs/STANDARDS.md", rels)
        self.assertIn("scripts/standards-check/check.py", rels)
        self.assertNotIn("docs/discovery/captured/README.md", rels)
        self.assertNotIn("scripts/capture-discovery/capture_discovery.py", rels)
        self.assertNotIn("scripts/promote-discovery/promote_discovery.py", rels)
        self.assertIn("AGENTS.md", rels)
        self.assertFalse(any(r.startswith(".git/") for r in rels))
        self.assertFalse(any(r.startswith("src/") for r in rels))
        self.assertFalse(any(r.startswith("tests/") for r in rels))
        self.assertFalse(any(r == "ai/handoff.md" for r in rels))
        self.assertFalse(any(r.endswith(".pyc") for r in rels))


    def test_copilot_hook_file_ships_from_a_template_source(self):
        from standards.manifest import is_excluded_from_tracked, iter_payload
        from standards.payload import payload_root
        sources = {rel: full for full, rel in iter_payload(payload_root())}
        self.assertEqual(sources[".github/hooks/standards.json"].name, "copilot-hooks.json")
        self.assertTrue(is_excluded_from_tracked("docs/templates/copilot-hooks.json"))

    def test_agents_choice_ships_one_hook_file(self):
        from standards.manifest import iter_payload
        from standards.payload import payload_root

        def rels(agents):
            return {rel for _full, rel in iter_payload(payload_root(), agents=agents)}

        for agents in (["claude"], ["claude", "copilot"]):
            self.assertIn(".claude/settings.json", rels(agents))
            self.assertNotIn(".github/hooks/standards.json", rels(agents))
        self.assertIn(".github/hooks/standards.json", rels(["copilot"]))
        self.assertNotIn(".claude/settings.json", rels(["copilot"]))
        self.assertIn(".claude/skills/standards-check/SKILL.md", rels(["copilot"]))

    def test_iter_payload_skips_machine_local_claude_files(self):
        import tempfile

        from standards.manifest import iter_payload
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                ".claude/settings.json",
                ".claude/skills/standards-check/SKILL.md",
                ".claude/settings.local.json",
                ".claude/worktrees/wt/AGENTS.md",
            ):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text("x\n", encoding="utf-8")
            rels = {rel for _full, rel in iter_payload(root)}
        self.assertIn(".claude/settings.json", rels)
        self.assertIn(".claude/skills/standards-check/SKILL.md", rels)
        self.assertNotIn(".claude/settings.local.json", rels)
        self.assertFalse(any(r.startswith(".claude/worktrees/") for r in rels))

    def test_partial_files_classified_partial(self):
        from standards.manifest import PARTIAL_FILES, classify
        self.assertIn("AGENTS.md", PARTIAL_FILES)
        self.assertIn("CLAUDE.md", PARTIAL_FILES)
        self.assertIn(".github/copilot-instructions.md", PARTIAL_FILES)
        self.assertEqual(classify("AGENTS.md"), "partial")
        self.assertEqual(classify("CLAUDE.md"), "partial")
        self.assertEqual(classify(".github/copilot-instructions.md"), "partial")
        self.assertEqual(classify("docs/templates/adr-template.md"), "kit-tracked")


if __name__ == "__main__":
    unittest.main()
