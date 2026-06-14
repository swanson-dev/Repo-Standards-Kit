"""Tests for the skill-hygiene checks: format, parity, and index-drift."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.skills import run  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


def _write_skill(root: Path, name: str, frontmatter: str = None, prompt: bool = True) -> None:
    fm = frontmatter if frontmatter is not None else f"name: {name}\ndescription: does {name}"
    sk = root / ".claude" / "skills" / name / "SKILL.md"
    sk.parent.mkdir(parents=True, exist_ok=True)
    sk.write_text(f"---\n{fm}\n---\n\n# {name}\n", encoding="utf-8")
    if prompt:
        pr = root / ".github" / "prompts" / f"{name}.prompt.md"
        pr.parent.mkdir(parents=True, exist_ok=True)
        pr.write_text(f"---\nmode: agent\ndescription: does {name}\n---\n\n# {name}\n", encoding="utf-8")


def _write_orphan_prompt(root: Path, name: str) -> None:
    pr = root / ".github" / "prompts" / f"{name}.prompt.md"
    pr.parent.mkdir(parents=True, exist_ok=True)
    pr.write_text(f"---\nmode: agent\ndescription: x\n---\n\n# {name}\n", encoding="utf-8")


def _write_index(root: Path, names) -> None:
    rows = "\n".join(f"| `{n}` | use {n} |" for n in names)
    (root / "AGENTS.md").write_text(
        f"# AGENTS.md\n\n## Available skills\n\n| Skill | When to use |\n|---|---|\n{rows}\n",
        encoding="utf-8",
    )


class FormatTests(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr"])
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_description_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", frontmatter="name: new-adr")
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root)) if "description" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")

    def test_name_mismatch_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", frontmatter="name: make-adr\ndescription: x")
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root)) if "!= dir" in f.message]
            self.assertEqual(len(findings), 1)

    def test_missing_name_in_adopter_is_warn(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", frontmatter="description: x")
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root, adopter=True)) if "`name`" in f.message]
            self.assertEqual(findings[0].severity, "warn")

    def test_no_skills_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run(Path(d), _ctx(Path(d))), [])


class ParityTests(unittest.TestCase):
    def test_skill_without_prompt_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr", prompt=False)
            _write_index(root, ["new-adr"])
            findings = [f for f in run(root, _ctx(root)) if "no matching .github/prompts" in f.message]
            self.assertEqual(len(findings), 1)

    def test_prompt_without_skill_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr"])
            _write_orphan_prompt(root, "ghost")
            findings = [f for f in run(root, _ctx(root)) if "no matching .claude/skills" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertIn("ghost", findings[0].message)


class IndexTests(unittest.TestCase):
    def test_skill_missing_from_index_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, [])
            findings = [f for f in run(root, _ctx(root)) if "not listed" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertIn("new-adr", findings[0].message)

    def test_orphan_index_entry_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr", "ghost"])
            findings = [f for f in run(root, _ctx(root)) if "no such skill exists" in f.message]
            self.assertEqual(len(findings), 1)
            self.assertIn("ghost", findings[0].message)

    def test_no_available_skills_section_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            findings = [f for f in run(root, _ctx(root)) if "no `## Available skills`" in f.message]
            self.assertEqual(len(findings), 1)

    def test_index_severity_warn_in_adopter(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, [])
            findings = [f for f in run(root, _ctx(root, adopter=True)) if "not listed" in f.message]
            self.assertEqual(findings[0].severity, "warn")


class AgentSurfaceTests(unittest.TestCase):
    def test_copilot_instructions_must_point_to_agents(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr"])
            copilot = root / ".github" / "copilot-instructions.md"
            copilot.parent.mkdir(parents=True, exist_ok=True)
            copilot.write_text("# Copilot\n\nUse local conventions.\n", encoding="utf-8")

            findings = [f for f in run(root, _ctx(root)) if "copilot-instructions.md" in f.message]

            self.assertEqual(len(findings), 1)
            self.assertIn("AGENTS.md", findings[0].message)

    def test_local_hook_script_paths_must_exist(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_skill(root, "new-adr")
            _write_index(root, ["new-adr"])
            settings = root / ".claude" / "settings.json"
            settings.parent.mkdir(parents=True, exist_ok=True)
            settings.write_text(
                json.dumps({
                    "hooks": {
                        "Stop": [{
                            "matcher": "",
                            "hooks": [{
                                "type": "command",
                                "command": "python scripts/missing-tool/run.py --check",
                            }],
                        }],
                    },
                }),
                encoding="utf-8",
            )

            findings = [f for f in run(root, _ctx(root)) if "missing-tool" in f.message]

            self.assertEqual(len(findings), 1)
            self.assertIn(".claude/settings.json", findings[0].message)


if __name__ == "__main__":
    unittest.main()
