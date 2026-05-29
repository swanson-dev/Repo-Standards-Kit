#!/usr/bin/env python3
"""promote-discovery — list raw discovery items, or flip one from raw to promoted.

Subcommands:
  list              List all `status: raw` items in docs/discovery/. Default subcommand.
  list --check      Hook mode: silent if 0 raw items; otherwise one stderr line. Always exit 0.
  promote <path> --to <target>
                    Flip `<path>` from status: raw to status: promoted and set
                    promoted_to: <target>. Both args required. Monotonic — no --force.

Exit codes:
  0  success
  2  precondition failure in non-check modes (single-line stderr message)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

# Reuse Slice 2's repo_root helper.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import RepoRootNotFound, repo_root  # noqa: E402

DISCOVERY_REL = Path("docs") / "discovery"
LEADING_HTML_COMMENT_RE = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)
FRONTMATTER_OPEN_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
STATUS_LINE_RE = re.compile(r"(?m)^(status:\s+)(\S+)(.*?)$")
PROMOTED_TO_LINE_RE = re.compile(r"(?m)^(promoted_to:)[ \t]*?[^\s#\n]*([ \t]*#.*)?$")


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def strip_leading_html_comment(text: str) -> str:
    return LEADING_HTML_COMMENT_RE.sub("", text, count=1)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return key→value dict from leading frontmatter, or None if absent.

    Skips a leading HTML comment block (like the ones in discovery templates) before
    looking for the `---` fences. Values are stripped of inline `# ...` annotations
    so callers see clean strings.
    """
    cleaned = strip_leading_html_comment(text)
    match = FRONTMATTER_OPEN_RE.match(cleaned)
    if not match:
        return None
    block = match.group(1)
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        comment_pos = rest.find("#")
        value = rest[:comment_pos] if comment_pos != -1 else rest
        out[key.strip()] = value.strip()
    return out


def iter_discovery_files(root: Path) -> list[Path]:
    """Walk docs/discovery/**/*.md, excluding README.md and any templates subtree."""
    base = root / DISCOVERY_REL
    if not base.exists():
        return []
    files = []
    for path in sorted(base.rglob("*.md")):
        if path.name == "README.md":
            continue
        if "templates" in path.parts:
            continue
        files.append(path)
    return files


def collect_raw_items(root: Path) -> list[tuple[Path, dict[str, str]]]:
    """Return (path, frontmatter_dict) for each discovery file with status: raw."""
    items = []
    for path in iter_discovery_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = parse_frontmatter(text)
        if fm is None:
            continue
        if fm.get("status") == "raw":
            items.append((path, fm))
    return items


def cmd_list(args: argparse.Namespace) -> None:
    if args.check:
        try:
            root = repo_root(Path.cwd())
        except RepoRootNotFound:
            return  # silent exit 0 in hook mode
        items = collect_raw_items(root)
        if not items:
            return
        msg = (
            f"promote-discovery: {len(items)} raw items in docs/discovery/ — "
            f"consider /promote-discovery"
        )
        print(msg, file=sys.stderr)
        return
    # Verbose mode
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")
    items = collect_raw_items(root)
    if not items:
        print("0 raw discovery items.")
        return
    print(f"{len(items)} raw discovery items:\n")
    print(f"  {'PATH':<60} {'TOPIC':<28} {'CAPTURED':<12}")
    for path, fm in items:
        rel = path.relative_to(root).as_posix()
        topic = fm.get("topic", "")[:28]
        captured = fm.get("date_captured", "")[:12]
        print(f"  {rel:<60} {topic:<28} {captured:<12}")


def flip_status_and_set_target(text: str, target: str) -> str:
    """Surgically rewrite frontmatter: status raw → promoted; promoted_to: <target>.

    Preserves inline `# ...` annotations on both lines and all other frontmatter / body.
    Caller is responsible for ensuring current status is `raw`.
    """
    cleaned_start = strip_leading_html_comment(text)
    offset = len(text) - len(cleaned_start)
    match = FRONTMATTER_OPEN_RE.match(cleaned_start)
    if not match:
        raise ValueError("no frontmatter block to modify")
    block_start = offset + match.start(1)
    block_end = offset + match.end(1)
    fm_block = text[block_start:block_end]

    new_block = STATUS_LINE_RE.sub(r"\1promoted\3", fm_block, count=1)

    def _replace_promoted_to(m: re.Match[str]) -> str:
        trailing = m.group(2) or ""
        return f"{m.group(1)} {target}{trailing}"

    new_block = PROMOTED_TO_LINE_RE.sub(_replace_promoted_to, new_block, count=1)
    return text[:block_start] + new_block + text[block_end:]


def cmd_promote(args: argparse.Namespace) -> None:
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")
    if not args.path:
        die("usage: promote-discovery promote <path> --to <target>")
    if not args.to:
        die("usage: promote-discovery promote <path> --to <target>")
    target = args.to
    if PurePosixPath(target).is_absolute() or PureWindowsPath(target).is_absolute():
        die(f"refuse to promote: target must be a relative path, not absolute: {target}")
    if ".." in Path(target).parts:
        die(f"refuse to promote: target contains '..' parent traversal: {target}")

    src = (Path.cwd() / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    try:
        src_rel = src.relative_to(root)
    except ValueError:
        die(f"refuse to promote: path is outside the repo: {args.path}")

    if not src.exists():
        die(f"refuse to promote: file not found: {args.path}")
    if DISCOVERY_REL not in src_rel.parents and src_rel.parent != DISCOVERY_REL:
        die(f"refuse to promote: not under docs/discovery/: {args.path}")

    text = src.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        die(f"refuse to promote: no frontmatter in {args.path}")
    current_status = fm.get("status")
    if current_status is None:
        die(f"refuse to promote: no status: field in {args.path}")
    if current_status != "raw":
        die(f"refuse to promote: status is already '{current_status}'; promotion is monotonic")

    new_text = flip_status_and_set_target(text, target)
    src.write_text(new_text, encoding="utf-8")
    print(f"Promoted {src_rel.as_posix()} -> {target}")


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="promote-discovery", description=__doc__)
    sub = parser.add_subparsers(dest="cmd")

    list_p = sub.add_parser("list", help="list raw discovery items")
    list_p.add_argument("--check", action="store_true", help="hook mode (silent unless raw items exist)")

    promote_p = sub.add_parser("promote", help="flip one item from raw to promoted")
    promote_p.add_argument("path", nargs="?", help="discovery file to promote")
    promote_p.add_argument("--to", dest="to", help="target path the content was promoted into")

    args = parser.parse_args(argv[1:])
    if args.cmd is None or args.cmd == "list":
        if not hasattr(args, "check"):
            args.check = False
        cmd_list(args)
    elif args.cmd == "promote":
        cmd_promote(args)


if __name__ == "__main__":
    main(sys.argv)
