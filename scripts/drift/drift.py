#!/usr/bin/env python3
"""Drift detection (ADR-0023): which docs fell behind the changes that should move them.

Each rule names a doc (`update`) and what should move it: conventional-commit
types (`when_commits`, used for the changelog) and/or path globs (`when`).
In globs, `**/` matches zero or more folders, `**` matches anything, and `*`
and `?` stay within one folder. Drift counts the commits made since the doc was
last committed, plus uncommitted files. A `Docs-Unaffected: deployment (renamed
a job)` commit trailer waives that commit for the named doc.

If git history can't be read, or the clone is shallow, detection raises
DriftError instead of reporting that nothing is behind.

Usage:
  python scripts/drift/drift.py [repo]

This slice only reports. The block-once Stop hook and the CI mode build on it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

# A repo adds or overrides rules under a `drift` key in .standards-kit.json.
DEFAULT_RULES: list[dict] = [
    {"update": "CHANGELOG.md", "when_commits": ["feat", "fix", "perf", "revert", "!"],
     "when": ["src/**", "scripts/**"]},
    {"update": "docs/09-deployment.md", "when": [".github/workflows/**", "infra/**", "Dockerfile"]},
    {"update": "docs/04-api-and-integrations.md", "when": ["src/**/api/**"]},
]
MARKER = ".standards-kit.json"
CONVENTIONAL_RE = re.compile(r"^(?P<type>[a-z]+)(?:\([^)]*\))?(?P<bang>!)?: ")
BREAKING_RE = re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE)
WAIVER_RE = re.compile(r"^docs-unaffected:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


class DriftError(Exception):
    """Git history couldn't be read, so drift can't be judged."""


@dataclass
class Commit:
    sha: str
    subject: str
    body: str
    paths: list[str] = field(default_factory=list)


def commit_type(subject: str, body: str) -> tuple[str | None, bool]:
    """(type, breaking) for a conventional-commit subject; (None, False) otherwise."""
    m = CONVENTIONAL_RE.match(subject)
    if m is None:
        return None, False
    return m.group("type"), bool(m.group("bang")) or bool(BREAKING_RE.search(body))


@cache
def glob_regex(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z")


def matches(path: str, patterns: list[str]) -> bool:
    return any(glob_regex(p).match(path) for p in patterns)


def waived(doc: str, values: list[str]) -> bool:
    """True if a waiver names this doc by path, by file name, or by a word in it."""
    stem = Path(doc).stem.lower()
    words = set(re.split(r"[-_.\s]+", stem))
    for value in values:
        name = value.split("(", 1)[0].strip().lower()
        if name and (name in (doc.lower(), stem) or name in words):
            return True
    return False


def rule_drift(rule: dict, commits: list[Commit], uncommitted: list[str],
               waivers: list[str] | tuple = ()) -> list[str]:
    """Why this rule's doc is behind: commit subjects, plus uncommitted trigger paths."""
    doc = rule["update"]
    if doc in uncommitted or waived(doc, list(waivers)):
        return []  # being edited right now, or waived for the whole range
    types = rule.get("when_commits", [])
    paths = rule.get("when", [])
    reasons = []
    for c in commits:
        if waived(doc, WAIVER_RE.findall(c.body)):
            continue
        ctype, breaking = commit_type(c.subject, c.body)
        if types and ctype is not None:
            hit = ctype in types or (breaking and "!" in types)
        else:
            hit = any(matches(p, paths) for p in c.paths)
        if hit:
            reasons.append(c.subject)
    touched = [p for p in uncommitted if matches(p, paths)]
    if touched:
        reasons.append("uncommitted: " + ", ".join(touched[:5]))
    return reasons


def load_rules(marker: dict | None) -> list[dict]:
    """Defaults, with the marker's `drift` rules replacing same-doc defaults or adding new ones."""
    rules = {r["update"]: r for r in DEFAULT_RULES}
    for rule in (marker or {}).get("drift", []):
        if isinstance(rule, dict) and isinstance(rule.get("update"), str):
            rules[rule["update"]] = rule
    return list(rules.values())


def git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=root,
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as exc:
        raise DriftError(f"could not run git: {exc}") from exc
    if result.returncode != 0:
        raise DriftError(f"git {args[0]} failed: {result.stderr.strip() or result.returncode}")
    return result.stdout


def has_commits(root: Path) -> bool:
    try:
        git(root, "rev-parse", "--verify", "-q", "HEAD")
    except DriftError:
        return False
    return True


def last_touch(root: Path, doc: str) -> str | None:
    return git(root, "log", "-1", "--format=%H", "--", doc).strip() or None


def commits_since(root: Path, sha: str | None) -> list[Commit]:
    """Commits after `sha` up to HEAD, oldest first, with the paths each one changed.

    `--no-renames` keeps both sides of a move; `--cc` shows changes made in a
    merge commit itself without repeating what the merged branch already did.
    """
    if sha is None:
        return []
    out = git(root, "log", "--reverse", "--no-renames", "--cc", "--name-only",
              "--format=%x1e%H%x1f%s%x1f%b%x1f", f"{sha}..HEAD")
    commits = []
    for record in out.split("\x1e"):
        parts = record.split("\x1f")
        if len(parts) != 4:
            continue
        sha_, subject, body, files = parts
        commits.append(Commit(sha_.strip(), subject.strip(), body.strip(),
                              [f.strip() for f in files.splitlines() if f.strip()]))
    return commits


def uncommitted_paths(root: Path) -> list[str]:
    out = git(root, "status", "--porcelain", "-z", "-uall", "--no-renames")
    return [entry[3:] for entry in out.split("\0") if len(entry) > 3]


def read_marker(root: Path) -> dict | None:
    try:
        data = json.loads((root / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def find_drift(root: Path, waivers: list[str] | tuple = ()) -> dict[str, list[str]]:
    """Doc -> reasons it is behind, for every rule whose doc this repo keeps."""
    root = Path(root)
    uncommitted = uncommitted_paths(root)
    if git(root, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise DriftError("shallow clone: drift needs the full history (in CI, use fetch-depth: 0)")
    history = has_commits(root)
    out: dict[str, list[str]] = {}
    for rule in load_rules(read_marker(root)):
        doc = rule["update"]
        if not (root / doc).is_file():
            continue  # this repo doesn't keep that doc
        commits = commits_since(root, last_touch(root, doc)) if history else []
        reasons = rule_drift(rule, commits, uncommitted, waivers)
        if reasons:
            out[doc] = reasons
    return out


def main(argv: list[str]) -> int:
    start = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        top = git(start, "rev-parse", "--show-toplevel").strip()
        found = find_drift(Path(top))
    except DriftError as exc:
        print(f"drift: can't check: {exc}", file=sys.stderr)
        return 2
    for doc, reasons in found.items():
        print(f"drift: {doc} is behind:")
        for reason in reasons:
            print(f"  - {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
