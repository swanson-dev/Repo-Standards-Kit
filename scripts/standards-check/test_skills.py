"""Tests for the SKILL.md format check."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.skills import run  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


def _skill(root: Path, name: str, body: str) -> None:
    p = root / ".claude" / "skills" / name / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


class SkillFormatTests(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\nname: new-adr\ndescription: Scaffold an ADR.\n---\n\n# New ADR\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_description_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\nname: new-adr\n---\n\n# New ADR\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")
            self.assertIn("description", findings[0].message)

    def test_name_mismatch_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\nname: make-adr\ndescription: x\n---\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertIn("!= dir", findings[0].message)

    def test_missing_name_in_adopter_is_warn(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "new-adr", "---\ndescription: x\n---\n")
            findings = run(root, _ctx(root, adopter=True))
            self.assertEqual(findings[0].severity, "warn")

    def test_no_skills_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(Path(d), _ctx(Path(d))), [])


if __name__ == "__main__":
    unittest.main()
