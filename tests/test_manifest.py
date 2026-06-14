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

    def test_ai_starters_dir_excluded_from_kit_tracked_copy(self):
        from standards.manifest import is_excluded_from_tracked
        self.assertTrue(is_excluded_from_tracked("docs/templates/ai-starters/current-state.md"))
        self.assertFalse(is_excluded_from_tracked("docs/templates/adr-template.md"))

    def test_iter_payload_yields_known_files_and_excludes_non_payload(self):
        from standards.manifest import iter_payload
        from standards.payload import payload_root
        rels = {rel for _full, rel in iter_payload(payload_root())}
        self.assertIn("docs/templates/adr-template.md", rels)
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


    def test_partial_files_classified_partial(self):
        from standards.manifest import classify, PARTIAL_FILES
        self.assertIn("AGENTS.md", PARTIAL_FILES)
        self.assertIn("CLAUDE.md", PARTIAL_FILES)
        self.assertIn(".github/copilot-instructions.md", PARTIAL_FILES)
        self.assertEqual(classify("AGENTS.md"), "partial")
        self.assertEqual(classify("CLAUDE.md"), "partial")
        self.assertEqual(classify(".github/copilot-instructions.md"), "partial")
        self.assertEqual(classify("docs/templates/adr-template.md"), "kit-tracked")


if __name__ == "__main__":
    unittest.main()
