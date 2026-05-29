"""Internal helpers for scripts under scripts/new-doc/. Stdlib only."""
from __future__ import annotations

import re
from pathlib import Path


class RepoRootNotFound(Exception):
    """Raised when no .git directory is found walking up from a start path."""


def repo_root(start: Path) -> Path:
    """Walk up from `start` looking for a `.git` directory. Return the containing dir.

    Raises RepoRootNotFound if no .git is found before filesystem root.
    """
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RepoRootNotFound(f"no .git directory found walking up from {start}")


def next_nnnn(directory: Path, pattern: re.Pattern[str]) -> str:
    """Return the next zero-padded 4-digit number for filenames in `directory`.

    `pattern` must capture the 4-digit prefix as group 1. Files that don't match
    are ignored. Returns "0001" if no matching files exist.
    """
    if not directory.exists():
        raise FileNotFoundError(directory)
    highest = 0
    for entry in directory.iterdir():
        if not entry.is_file():
            continue
        match = pattern.match(entry.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{highest + 1:04d}"


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    """Lowercase, kebab-case, alnum-only. Raises ValueError on empty result."""
    lowered = title.lower()
    slug = _SLUG_RE.sub("-", lowered).strip("-")
    if not slug:
        raise ValueError(f"slugify produced empty string from {title!r}")
    return slug


def fill_template(text: str, subs: dict[str, str]) -> str:
    """Literal-string replace each (key, value) in `subs` into `text`.

    Unmatched `<...>` placeholders are intentionally left intact for the author.
    """
    out = text
    for key, value in subs.items():
        out = out.replace(key, value)
    return out
