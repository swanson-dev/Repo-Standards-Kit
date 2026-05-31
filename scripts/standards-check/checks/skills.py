"""Skill-hygiene checks: SKILL.md frontmatter format, SKILL.md<->prompt.md parity,
and skills-index drift (the AGENTS.md `## Available skills` table).

All findings share check_id "skill-format" so adopters have one override knob.
Error in the kit, warn in adopters (resolve_severity).
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "skill-format"
DEFAULT_SEVERITY = "error"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_INDEX_HEADING_RE = re.compile(r"(?m)^##\s+Available skills\s*$")
_INDEX_ROW_RE = re.compile(r"(?m)^\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|")
_PROMPT_SUFFIX = ".prompt.md"


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


def _skill_dirs(root: Path) -> list:
    base = root / ".claude" / "skills"
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if (p / "SKILL.md").is_file())


def _index_names(root: Path):
    """Skill names in the AGENTS.md `## Available skills` table, or None if the
    file or section is absent."""
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return None
    text = agents.read_text(encoding="utf-8", errors="replace")
    m = _INDEX_HEADING_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    section = rest[: nxt.start()] if nxt else rest
    return {row.group(1) for row in _INDEX_ROW_RE.finditer(section)}


def _check_format(root: Path, severity: str) -> list:
    findings = []
    for skill_md in sorted((root / ".claude" / "skills").glob("*/SKILL.md")):
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


def _check_parity(root: Path, skill_dirs: list, severity: str) -> list:
    findings = []
    prompts_dir = root / ".github" / "prompts"
    for name in skill_dirs:
        if not (prompts_dir / f"{name}{_PROMPT_SUFFIX}").is_file():
            findings.append(Finding(
                CHECK_ID, severity,
                f".claude/skills/{name}/SKILL.md has no matching .github/prompts/{name}{_PROMPT_SUFFIX}",
            ))
    if prompts_dir.is_dir():
        skill_set = set(skill_dirs)
        for prompt in sorted(prompts_dir.glob("*" + _PROMPT_SUFFIX)):
            name = prompt.name[: -len(_PROMPT_SUFFIX)]
            if name not in skill_set:
                findings.append(Finding(
                    CHECK_ID, severity,
                    f".github/prompts/{name}{_PROMPT_SUFFIX} has no matching .claude/skills/{name}/SKILL.md",
                ))
    return findings


def _check_index(root: Path, skill_dirs: list, severity: str) -> list:
    index = _index_names(root)
    if index is None:
        return [Finding(
            CHECK_ID, severity,
            "AGENTS.md: no `## Available skills` section (skills must be discoverable)",
        )]
    findings = []
    for name in skill_dirs:
        if name not in index:
            findings.append(Finding(
                CHECK_ID, severity,
                f"skill '{name}' is not listed in the AGENTS.md `## Available skills` index",
            ))
    for name in sorted(index - set(skill_dirs)):
        findings.append(Finding(
            CHECK_ID, severity,
            f"AGENTS.md `## Available skills` lists '{name}' but no such skill exists",
        ))
    return findings


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    skill_dirs = _skill_dirs(root)
    if not skill_dirs:
        return []  # no skills → nothing to lint
    findings = []
    findings += _check_format(root, severity)
    findings += _check_parity(root, skill_dirs, severity)
    findings += _check_index(root, skill_dirs, severity)
    return findings
