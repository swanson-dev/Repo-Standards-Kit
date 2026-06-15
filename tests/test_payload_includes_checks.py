"""Regression: the standards-check checks/ package must ship in the payload."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from standards.manifest import iter_payload  # noqa: E402


class PayloadIncludesChecksTests(unittest.TestCase):
    def test_checks_package_modules_are_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        for expected in (
            "scripts/standards-check/checks/__init__.py",
            "scripts/standards-check/checks/structural.py",
            "scripts/standards-check/checks/links.py",
            "scripts/standards-check/checks/external_links.py",
            "scripts/standards-check/checks/content.py",
            "scripts/standards-check/checks/skills.py",
            "scripts/standards-check/checks/_text.py",
        ):
            self.assertIn(expected, rels, f"{expected} missing from payload")

    def test_pycache_not_in_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        self.assertFalse(any("__pycache__" in r or r.endswith(".pyc") for r in rels))

    def test_kit_only_workflow_not_in_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        self.assertNotIn(".github/workflows/kit-guards.yml", rels)
        # The shipped CI workflow IS in the payload (sanity check on the assertion).
        self.assertIn(".github/workflows/repo-standards.yml", rels)

    def test_skills_and_templates_are_payload(self):
        rels = {rel for _, rel in iter_payload(REPO_ROOT)}
        for expected in (
            ".claude/skills/standards-check/SKILL.md",
            ".github/prompts/standards-check.prompt.md",
            "docs/templates/skill-template.md",
            "docs/templates/skill-prompt-template.md",
        ):
            self.assertIn(expected, rels, f"{expected} missing from payload")


if __name__ == "__main__":
    unittest.main()
