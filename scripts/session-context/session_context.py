#!/usr/bin/env python3
"""Print a read-only AI session context brief from repo-local ai/*.md files.

Hook mode is advisory: it never writes files and always exits 0.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import RepoRootNotFound, repo_root  # noqa: E402

AI_FILES = (
    Path("ai") / "handoff.md",
    Path("ai") / "current-state.md",
    Path("ai") / "next-actions.md",
    Path("ai") / "open-questions.md",
)
HANDOFF_STALE_DAYS = 5
ROLLING_STALE_DAYS = 14


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def frontmatter_value(text: str, field: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.+?)\s*$", text[4:end])
    return match.group(1).strip() if match else None


def is_stale(value: str | None, max_days: int) -> bool:
    if not value:
        return False
    try:
        parsed = date.fromisoformat(value.split("T")[0])
    except ValueError:
        return False
    return date.today() - parsed > timedelta(days=max_days)


def section(text: str, heading: str, max_lines: int = 4) -> list[str]:
    lines = text.splitlines()
    start = None
    target = f"## {heading}".lower()
    for i, line in enumerate(lines):
        if line.strip().lower() == target:
            start = i + 1
            break
    if start is None:
        return []
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if stripped:
            out.append(stripped)
        if len(out) >= max_lines:
            break
    return out


def numbered_or_bullets(text: str, max_lines: int = 5) -> list[str]:
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s+", stripped) or stripped.startswith("- "):
            out.append(stripped)
        if len(out) >= max_lines:
            break
    return out


def question_headings(text: str, max_lines: int = 5) -> list[str]:
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^##\s+Q-\d+:", stripped):
            out.append(stripped.removeprefix("## ").strip())
        if len(out) >= max_lines:
            break
    return out


def build_brief(root: Path) -> list[str]:
    lines = ["Session Context", f"Repo: {root}"]
    warnings: list[str] = []

    texts: dict[Path, str] = {}
    for rel in AI_FILES:
        text = read_text(root / rel)
        if text is None:
            warnings.append(f"WARN: {rel.as_posix()} missing")
        else:
            texts[rel] = text

    handoff = texts.get(Path("ai") / "handoff.md")
    if handoff:
        written = frontmatter_value(handoff, "written")
        if is_stale(written, HANDOFF_STALE_DAYS):
            warnings.append(f"WARN: handoff is stale (> {HANDOFF_STALE_DAYS} days)")
        lines.append("")
        lines.append("Handoff TL;DR:")
        lines.extend(f"- {item}" for item in (section(handoff, "TL;DR", 3) or ["(no TL;DR found)"]))

    current_state = texts.get(Path("ai") / "current-state.md")
    if current_state:
        updated = frontmatter_value(current_state, "last_updated")
        if is_stale(updated, ROLLING_STALE_DAYS):
            warnings.append(f"WARN: current-state is stale (> {ROLLING_STALE_DAYS} days)")
        lines.append("")
        lines.append("Current State:")
        lines.extend(f"- {item}" for item in (section(current_state, "What's in progress", 5) or ["(no in-progress section found)"]))
        blocked = section(current_state, "What's blocked", 3)
        if blocked:
            lines.append("Blocked:")
            lines.extend(f"- {item}" for item in blocked)

    next_actions = texts.get(Path("ai") / "next-actions.md")
    if next_actions:
        lines.append("")
        lines.append("Next Actions:")
        lines.extend(numbered_or_bullets(next_actions, 5) or ["- (no next actions found)"])

    open_questions = texts.get(Path("ai") / "open-questions.md")
    if open_questions:
        lines.append("")
        lines.append("Open Questions:")
        lines.extend(f"- {item}" for item in (question_headings(open_questions, 5) or ["(no open question headings found)"]))

    if warnings:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(warnings)
    return lines


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="session-context", description=__doc__)
    parser.add_argument("--hook", action="store_true", help="advisory hook mode; always exits 0")
    args = parser.parse_args(argv[1:])
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        root = Path.cwd()
        lines = build_brief(root)
        lines.append("WARN: not in a git repo")
        for line in lines:
            print(line)
        return 0
    for line in build_brief(root):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
