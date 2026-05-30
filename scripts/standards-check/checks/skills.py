"""SKILL.md format lint: every .claude/skills/*/SKILL.md needs frontmatter with a
non-empty `name` (matching its directory) and a non-empty `description`.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "skill-format"
DEFAULT_SEVERITY = "error"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    skills_dir = root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    findings = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        rel = skill_md.relative_to(root).as_posix()
        dir_name = skill_md.parent.name
        fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: missing frontmatter `name`"))
        elif name != dir_name:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: name '{name}' != dir '{dir_name}'"))
        if not desc:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: missing frontmatter `description`"))
    return findings
