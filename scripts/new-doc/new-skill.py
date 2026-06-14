#!/usr/bin/env python3
"""new-skill - scaffold paired Claude/Copilot skill files and index AGENTS.md.

Usage:
  python scripts/new-doc/new-skill.py "<skill-name>" "<description>"

Exits 0 on success, 2 on any precondition failure (single-line stderr message).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import RepoRootNotFound, repo_root  # noqa: E402

NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
INDEX_HEADING_RE = re.compile(r"(?m)^##\s+Available skills\s*$")
INDEX_ROW_TEMPLATE = "| `{name}` | {description} |"


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def validate_name(name: str) -> None:
    if not NAME_RE.match(name) or "--" in name:
        die("skill name must be kebab-case using lowercase letters, numbers, and single hyphens")


def render_template(template: str, name: str, description: str) -> str:
    rendered = template.replace("<skill-name>", name)
    rendered = rendered.replace("<description>", description)
    rendered = re.sub(
        r"(?m)^description:\s*<[^>\n]+>\s*$",
        f"description: {description}",
        rendered,
    )
    return rendered


def add_index_row(agents_text: str, name: str, description: str) -> str:
    heading = INDEX_HEADING_RE.search(agents_text)
    if not heading:
        die("AGENTS.md has no `## Available skills` section")

    rest = agents_text[heading.end():]
    next_heading = re.search(r"(?m)^##\s+", rest)
    section_end = heading.end() + (next_heading.start() if next_heading else len(rest))
    section = agents_text[heading.end():section_end]

    if re.search(rf"(?m)^\|\s*`{re.escape(name)}`\s*\|", section):
        die(f"AGENTS.md already lists skill '{name}'")

    table_rows = list(re.finditer(r"(?m)^\|.*\|\s*$", section))
    if not table_rows:
        die("AGENTS.md `## Available skills` section has no markdown table")

    insert_at = heading.end() + table_rows[-1].end()
    row = "\n" + INDEX_ROW_TEMPLATE.format(name=name, description=description)
    return agents_text[:insert_at] + row + agents_text[insert_at:]


def main(argv: list[str]) -> None:
    if len(argv) < 3 or not argv[1].strip() or not argv[2].strip():
        die("usage: new-skill.py \"<skill-name>\" \"<description>\"")
    name = argv[1].strip()
    description = argv[2].strip()
    validate_name(name)

    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")

    skill_template_path = root / "docs" / "templates" / "skill-template.md"
    prompt_template_path = root / "docs" / "templates" / "skill-prompt-template.md"
    agents_path = root / "AGENTS.md"
    for template_path in (skill_template_path, prompt_template_path):
        if not template_path.exists():
            die(f"template not found: {template_path}")
    if not agents_path.exists():
        die(f"AGENTS.md not found: {agents_path}")

    skill_path = root / ".claude" / "skills" / name / "SKILL.md"
    prompt_path = root / ".github" / "prompts" / f"{name}.prompt.md"
    for out_path in (skill_path, prompt_path):
        if out_path.exists():
            die(f"refuse to overwrite existing file: {out_path}")

    skill_template = skill_template_path.read_text(encoding="utf-8")
    prompt_template = prompt_template_path.read_text(encoding="utf-8")
    agents_text = agents_path.read_text(encoding="utf-8")
    updated_agents = add_index_row(agents_text, name, description)

    skill_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(render_template(skill_template, name, description), encoding="utf-8")
    prompt_path.write_text(render_template(prompt_template, name, description), encoding="utf-8")
    agents_path.write_text(updated_agents, encoding="utf-8")

    print(f"Created {skill_path.relative_to(root).as_posix()}")
    print(f"Created {prompt_path.relative_to(root).as_posix()}")
    print("Updated AGENTS.md `## Available skills` index")


if __name__ == "__main__":
    main(sys.argv)
