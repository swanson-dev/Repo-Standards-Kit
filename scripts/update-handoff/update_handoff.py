#!/usr/bin/env python3
"""update-handoff — generate ai/handoff.md from git state, or emit a Stop-hook advisory.

Modes:
  (no flag)   Write a draft ai/handoff.md. Refuse to overwrite unless --force.
  --force     With write mode, overwrite an existing handoff.
  --check     Advisory mode (for Claude Code Stop hook). Silent unless commits or
              modified files have accumulated since the prior handoff. Always exits 0.

Exit codes (write mode):
  0  success
  2  precondition failure (single-line stderr message)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Reuse Slice 2's repo_root helper.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import RepoRootNotFound, repo_root  # noqa: E402

HANDOFF_REL = Path("ai") / "handoff.md"
WRITTEN_RE = re.compile(r"^written:\s*(.+?)\s*$", re.MULTILINE)


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def git(args: list[str], cwd: Path, check: bool = True) -> str:
    """Run a git command, return stdout.

    When check=True (default), die with exit 2 on non-zero git exit — for write mode.
    When check=False, silently return "" on non-zero — for advisory check mode where
    the hook must never break the session.
    """
    result = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True,
    )
    if result.returncode != 0:
        if check:
            die(f"git {' '.join(args)} failed: {result.stderr.strip() or 'no stderr'}")
        return ""
    return result.stdout


def read_prior_written_ts(handoff_path: Path) -> str | None:
    """Parse `written:` from existing handoff *frontmatter*, verbatim. None if absent.

    Scoped to the leading frontmatter block (between the first two `---` fences) so
    a stray `written:` line in the body doesn't get matched.
    """
    if not handoff_path.exists():
        return None
    text = handoff_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    # Find the end of the frontmatter block.
    end = text.find("\n---\n", 4)  # start at 4 to skip the opening fence
    if end == -1:
        return None
    frontmatter = text[4:end]
    match = WRITTEN_RE.search(frontmatter)
    return match.group(1) if match else None


def collect_recent(cwd: Path, since_ts: str | None) -> tuple[list[str], list[str]]:
    """Return (commit_subjects, changed_files) for the range since `since_ts`.

    If since_ts is None, fall back to last 10 commits.
    Also falls back to last 10 commits if `since_ts` is set but returned zero commits
    AND zero changed files — defensive against a prior handoff that was hand-written
    with a future timestamp.
    """
    def _run(since_args: list[str]) -> tuple[list[str], list[str]]:
        log_out = git(["log", *since_args, "--pretty=format:%s"], cwd=cwd)
        commits = [line for line in log_out.splitlines() if line.strip()]
        files_out = git(["log", *since_args, "--name-only", "--pretty=format:"], cwd=cwd)
        files_seen: dict[str, None] = {}  # preserve order, dedupe
        for raw in files_out.splitlines():
            path = raw.strip()
            if path:
                files_seen[path] = None
        return commits, list(files_seen.keys())

    if since_ts is None:
        return _run(["-n", "10"])
    commits, files = _run([f"--since={since_ts}"])
    if not commits and not files:
        # since_ts may be in the future (hand-written handoff timestamp) — fall back.
        return _run(["-n", "10"])
    return commits, files


def author_name(cwd: Path) -> str:
    name = git(["config", "user.name"], cwd=cwd, check=False).strip()
    return name or "unknown"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def render_draft(
    now_ts: str,
    author: str,
    commits: list[str],
    files: list[str],
) -> str:
    commit_lines = "\n".join(f"- {c}" for c in commits) if commits else "- (no committed changes since last handoff)"
    file_lines = "\n".join(f"  - `{f}`" for f in files) if files else "  - (no file changes detected)"
    return (
        f"---\n"
        f"written: {now_ts}\n"
        f"written_by: {author} (via claude-code-assistant)\n"
        f"for: next-session\n"
        f"---\n"
        f"\n"
        f"# Handoff\n"
        f"\n"
        f"## TL;DR\n"
        f"\n"
        f"<one or two sentences — what changed and where it stands>\n"
        f"\n"
        f"## Recently touched\n"
        f"\n"
        f"{commit_lines}\n"
        f"\n"
        f"Files changed:\n"
        f"{file_lines}\n"
        f"\n"
        f"## Open threads\n"
        f"\n"
        f"- <thing the next session should be aware of>\n"
        f"\n"
        f"## Don't do\n"
        f"\n"
        f"- <dead end or rule the next session should not violate>\n"
    )


def cmd_write(args: argparse.Namespace) -> None:
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")
    handoff_path = root / HANDOFF_REL
    existed = handoff_path.exists()
    if existed and not args.force:
        die("refuse to overwrite existing ai/handoff.md; pass --force to replace")
    prior_ts = read_prior_written_ts(handoff_path) if existed else None
    commits, files = collect_recent(root, prior_ts)
    draft = render_draft(now_iso(), author_name(root), commits, files)
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(draft, encoding="utf-8")
    verb = "Updated" if existed else "Created"
    print(f"{verb} ai/handoff.md")


def _porcelain_path(line: str) -> str:
    """Extract the path from a `git status --porcelain` line (handles renames)."""
    # Format: 'XY <path>' or 'XY <old> -> <new>' for renames.
    body = line[3:] if len(line) > 3 else ""
    if " -> " in body:
        body = body.split(" -> ", 1)[1]
    return body.strip().strip('"')


# Use POSIX form to match git's path output regardless of platform.
HANDOFF_POSIX = HANDOFF_REL.as_posix()


def cmd_check(args: argparse.Namespace) -> None:
    # Hook mode: silent + exit 0 on ANY trouble; never break the session.
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        return
    handoff_path = root / HANDOFF_REL
    prior_ts = read_prior_written_ts(handoff_path) if handoff_path.exists() else None
    if prior_ts:
        log_out = git(["log", f"--since={prior_ts}", "--oneline"], cwd=root, check=False)
        commit_count = len([line for line in log_out.splitlines() if line.strip()])
    else:
        commit_count = 0  # no prior handoff → flag modified files only; commits unbounded
    # `--untracked-files=all` so an untracked `ai/handoff.md` isn't collapsed to
    # `ai/`, which we'd otherwise fail to filter out below.
    status_out = git(["status", "--porcelain", "--untracked-files=all"], cwd=root, check=False)
    file_count = 0
    for line in status_out.splitlines():
        if not line.strip():
            continue
        if _porcelain_path(line) == HANDOFF_POSIX:
            # The handoff file's own modification isn't "pending work" —
            # that would be circular advice.
            continue
        file_count += 1
    if commit_count == 0 and file_count == 0:
        return
    msg = (
        f"update-handoff: {commit_count} commits + {file_count} modified files "
        f"since last handoff — consider /update-handoff before ending the session"
    )
    print(msg, file=sys.stderr)


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="update-handoff", description=__doc__)
    parser.add_argument("--force", action="store_true", help="(write mode) overwrite existing handoff")
    parser.add_argument("--check", action="store_true", help="advisory hook mode (no file writes)")
    args = parser.parse_args(argv[1:])
    if args.check:
        cmd_check(args)
    else:
        cmd_write(args)


if __name__ == "__main__":
    main(sys.argv)
