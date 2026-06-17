#!/usr/bin/env python3
"""Advisory changelog reminder for AI stop hooks.

The hook never blocks work. It only reminds when repository changes exist after
the last CHANGELOG.md update, or when the required changelog is missing.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def _is_git_repo(cwd: Path) -> bool:
    result = _run_git(cwd, "rev-parse", "--is-inside-work-tree")
    return result.returncode == 0 and result.stdout.strip() == "true"


def _last_changelog_commit(cwd: Path) -> str | None:
    result = _run_git(cwd, "log", "-n", "1", "--format=%H", "--", "CHANGELOG.md")
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None


def _commit_count_since(cwd: Path, sha: str | None) -> int:
    if sha is None:
        return 0
    result = _run_git(cwd, "rev-list", "--count", f"{sha}..HEAD")
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def _status_paths(cwd: Path) -> list[str]:
    result = _run_git(cwd, "status", "--porcelain", "--untracked-files=all")
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for raw in result.stdout.splitlines():
        if not raw:
            continue
        path = raw[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.replace("\\", "/")
        if path == "CHANGELOG.md":
            continue
        paths.append(path)
    return paths


def _plural(count: int, singular: str) -> str:
    suffix = "" if count == 1 else "s"
    return f"{count} {singular}{suffix}"


def check(cwd: Path) -> int:
    if not _is_git_repo(cwd):
        return 0

    changelog = cwd / "CHANGELOG.md"
    if not changelog.exists():
        print(
            "changelog: CHANGELOG.md is missing; add one before standards check or release.",
            file=sys.stderr,
        )
        return 0

    commits = _commit_count_since(cwd, _last_changelog_commit(cwd))
    modified = len(_status_paths(cwd))
    if commits == 0 and modified == 0:
        return 0

    parts = []
    if commits:
        parts.append(_plural(commits, "commit"))
    if modified:
        parts.append(_plural(modified, "modified file"))
    summary = " and ".join(parts)
    print(
        "changelog: CHANGELOG.md may need an entry; "
        f"{summary} since the last changelog update. "
        "Run /standard-update-changelog before ending the session.",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run advisory hook mode. This is always non-blocking.",
    )
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("only --check mode is supported")
    return check(Path.cwd())


if __name__ == "__main__":
    raise SystemExit(main())

