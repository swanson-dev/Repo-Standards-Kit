"""Tests for new-skill.py scaffold generation."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "new-doc" / "new-skill.py"


def write_base_repo(root: Path, *, agents: bool = True, templates: bool = True) -> None:
    (root / ".git").mkdir()
    if templates:
        templates_dir = root / "docs" / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "skill-template.md").write_text(
            "---\n"
            "name: <skill-name>\n"
            "description: <description>\n"
            "---\n"
            "\n"
            "# <skill-name>\n"
            "\n"
            "## When to invoke\n"
            "\n"
            "<description>\n",
            encoding="utf-8",
        )
        (templates_dir / "skill-prompt-template.md").write_text(
            "---\n"
            "mode: agent\n"
            "description: <description>\n"
            "---\n"
            "\n"
            "# <skill-name>\n"
            "\n"
            "<description>\n",
            encoding="utf-8",
        )
    if agents:
        (root / "AGENTS.md").write_text(
            "# AGENTS.md\n"
            "\n"
            "## Available skills\n"
            "\n"
            "| Skill | When to use |\n"
            "|---|---|\n"
            "| `new-adr` | Recording decisions |\n"
            "\n"
            "## About this repository\n",
            encoding="utf-8",
        )


def run_new_skill(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(root),
        capture_output=True,
        text=True,
    )


class NewSkillTests(unittest.TestCase):
    def test_creates_skill_prompt_and_index_row(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_base_repo(root)

            result = run_new_skill(root, "review-docs", "Review docs before shipping")

            self.assertEqual(result.returncode, 0, result.stderr)
            skill = root / ".claude" / "skills" / "review-docs" / "SKILL.md"
            prompt = root / ".github" / "prompts" / "review-docs.prompt.md"
            self.assertTrue(skill.is_file())
            self.assertTrue(prompt.is_file())
            self.assertIn("name: review-docs", skill.read_text(encoding="utf-8"))
            self.assertIn("description: Review docs before shipping", skill.read_text(encoding="utf-8"))
            self.assertIn("description: Review docs before shipping", prompt.read_text(encoding="utf-8"))
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("| `review-docs` | Review docs before shipping |", agents)

    def test_rejects_non_kebab_case_name(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_base_repo(root)

            result = run_new_skill(root, "ReviewDocs", "Review docs")

            self.assertEqual(result.returncode, 2)
            self.assertIn("kebab-case", result.stderr)

    def test_refuses_existing_skill_or_prompt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_base_repo(root)
            existing = root / ".claude" / "skills" / "review-docs" / "SKILL.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("# existing\n", encoding="utf-8")

            result = run_new_skill(root, "review-docs", "Review docs")

            self.assertEqual(result.returncode, 2)
            self.assertIn("refuse to overwrite", result.stderr.lower())

    def test_refuses_existing_index_row(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_base_repo(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            agents = agents.replace(
                "| `new-adr` | Recording decisions |\n",
                "| `new-adr` | Recording decisions |\n| `review-docs` | old |\n",
            )
            (root / "AGENTS.md").write_text(agents, encoding="utf-8")

            result = run_new_skill(root, "review-docs", "Review docs")

            self.assertEqual(result.returncode, 2)
            self.assertIn("already lists", result.stderr.lower())

    def test_fails_when_templates_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_base_repo(root, templates=False)

            result = run_new_skill(root, "review-docs", "Review docs")

            self.assertEqual(result.returncode, 2)
            self.assertIn("template not found", result.stderr.lower())

    def test_fails_when_agents_skills_section_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_base_repo(root, agents=False)
            (root / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")

            result = run_new_skill(root, "review-docs", "Review docs")

            self.assertEqual(result.returncode, 2)
            self.assertIn("available skills", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
