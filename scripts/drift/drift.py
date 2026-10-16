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
  python scripts/drift/drift.py [repo]   report which docs are behind
  python scripts/drift/drift.py --hook   Stop hook; reads the hook's JSON on stdin

As a Stop hook it blocks once in `enforce` mode, printing top-level
{"decision": "block", "reason": ...}, and lets the next stop through
(`stop_hook_active`). On CI runners (the Copilot cloud agent) it blocks at most
once per session. In `advise` mode it only prints a reminder. It never fails
closed: if git can't be read, it says why on stderr and lets the turn end.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
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


def valid_rule(rule: object) -> bool:
    if not isinstance(rule, dict) or not isinstance(rule.get("update"), str):
        return False
    lists = [rule.get(key, []) for key in ("when", "when_commits")]
    return all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in lists)


def load_rules(marker: dict | None) -> list[dict]:
    """Defaults, with the marker's `drift` rules replacing same-doc defaults or adding new ones.

    Malformed marker rules are ignored, so a typo can't break or disable the defaults.
    """
    rules = {r["update"]: r for r in DEFAULT_RULES}
    extra = (marker or {}).get("drift")
    for rule in extra if isinstance(extra, list) else []:
        if valid_rule(rule):
            rules[rule["update"]] = rule
    return list(rules.values())


def git(root: Path, *args: str, stdin: str | None = None) -> str:
    try:
        result = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=root, input=stdin,
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


def doc_updates(root: Path, doc: str, base_point: str | None) -> list[str]:
    """Commits that updated `doc`, after the base when there is one. Merges don't count:
    combining branches isn't a deliberate doc update."""
    since = [f"^{base_point}"] if base_point else []
    return git(root, "rev-list", "--full-history", "--no-merges", "HEAD", *since,
               "--", doc).split()


def uncovered_commits(root: Path, doc: str, base_point: str | None) -> list[Commit]:
    """Commits no later update of `doc` covers, oldest first, with the paths each changed.

    That is HEAD's history minus everything reachable from the base or from any
    commit that updated the doc, so it holds up across merges in either direction.
    `--no-renames` keeps both sides of a move; `--cc` shows changes made in a merge
    commit itself without repeating what the merged branch already did.
    """
    updates = doc_updates(root, doc, base_point)
    if not updates and base_point is None:
        return []  # the doc has no history to measure from
    revs = ["HEAD", *(f"^{sha}" for sha in updates), *([f"^{base_point}"] if base_point else [])]
    out = git(root, "log", "--reverse", "--no-renames", "--cc", "--name-only",
              "--format=%x1e%H%x1f%s%x1f%b%x1f", "--stdin", stdin="\n".join(revs) + "\n")
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


def find_drift(root: Path, waivers: list[str] | tuple = (),
               base: str | None = None) -> dict[str, list[str]]:
    """Doc -> reasons it is behind, for every rule whose doc this repo keeps.

    A commit is behind when no later update of the doc descends from it. With
    `base` (a pull request's target, such as `origin/main`), only commits after
    the merge-base count, so drift already on the base branch isn't blamed on
    the PR, and base-branch doc updates don't cover the PR's changes.
    """
    root = Path(root)
    uncommitted = uncommitted_paths(root)
    if git(root, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise DriftError("shallow clone: drift needs the full history (in CI, use fetch-depth: 0)")
    history = has_commits(root)
    base_point = git(root, "merge-base", base, "HEAD").strip() if base else None
    out: dict[str, list[str]] = {}
    for rule in load_rules(read_marker(root)):
        doc = rule["update"]
        if not (root / doc).is_file():
            continue  # this repo doesn't keep that doc
        commits = uncovered_commits(root, doc, base_point) if history else []
        reasons = rule_drift(rule, commits, uncommitted, waivers)
        if reasons:
            out[doc] = reasons
    return out


def hook_mode(root: Path) -> str:
    """Only `standards init`/`adopt` write a marker, so no marker means the kit's own
    repo, which enforces. Adopters without `hook_mode` predate ADR-0023 and advise."""
    if not (root / MARKER).exists():
        return "enforce"
    mode = (read_marker(root) or {}).get("hook_mode", "advise")
    return mode if mode in ("advise", "enforce") else "advise"


def block_reason(found: dict[str, list[str]]) -> str:
    lines = ["Not done yet: these docs are behind the changes that should update them."]
    lines += [f"- {doc}: " + "; ".join(reasons) for doc, reasons in found.items()]
    lines.append("Update each doc now, or reply in one line why it is unaffected and add a "
                 "`Docs-Unaffected: doc-name (reason)` trailer when you commit.")
    return "\n".join(lines)


def ci_block_used(payload: dict) -> bool:
    """On CI runners the Copilot cloud agent reprompts the same session for the PR
    description, each reprompt a new turn, and a block there replaces the description
    and fails the job. So a session blocks once; the CI drift check covers the rest."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return False
    session = re.sub(r"[^A-Za-z0-9-]", "", str(payload.get("session_id", ""))) or "unknown"
    try:
        folder = os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()
        (Path(folder) / f"standards-drift-{session}").touch(exist_ok=False)
    except FileExistsError:
        return True
    except OSError as exc:  # blocking without a record would block on every later turn
        print(f"drift: can't record the block, so not blocking: {exc}", file=sys.stderr)
        return True
    return False


def run_hook(stdin_text: str, fallback: Path) -> int:
    try:
        payload = json.loads(stdin_text)
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        # Without readable input there's no stop_hook_active guard, so blocking could loop.
        print("drift: unreadable hook input, so not blocking", file=sys.stderr)
        return 0
    if payload.get("stop_hook_active"):
        return 0  # the agent already had its chance this turn
    cwd = payload.get("cwd")
    start = Path(cwd) if isinstance(cwd, str) and cwd else fallback
    try:
        root = Path(git(start, "rev-parse", "--show-toplevel").strip())
        found = find_drift(root)
        mode = hook_mode(root)
    except Exception as exc:  # a hook must never fail closed
        print(f"drift: can't check, so not blocking: {exc}", file=sys.stderr)
        return 0
    if not found:
        return 0
    if mode == "enforce":
        if ci_block_used(payload):
            return 0
        print(json.dumps({"decision": "block", "reason": block_reason(found)}))
    else:
        print(block_reason(found), file=sys.stderr)
    return 0


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):  # hosts and pipes read UTF-8
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if "--hook" in argv[1:]:
        return run_hook(sys.stdin.buffer.read().decode("utf-8", errors="replace"), Path.cwd())
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
