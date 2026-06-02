#!/usr/bin/env python3
"""capture-discovery — surface raw source material in discovery intake, or scaffold a
synthesized markdown note for it under docs/discovery/captured/.

Capture is the stage *before* promote (ADR-0014): raw stakeholder material (PDFs, JSON,
drafts) lands in the gitignored intake folders; this command lists it and scaffolds the
tracked markdown note the agent fills in. `/promote-discovery` then promotes that note.

Subcommands:
  list              List source files in the intake folders. Default subcommand.
  list --check      Hook mode: silent if 0 sources; otherwise one stderr line. Always exit 0.
  new --kind <kind> --topic <text> [--source <path>]
                    Scaffold docs/discovery/captured/YYYY-MM-DD-<slug>.md with frontmatter
                    (status: raw). The agent writes the synthesized body. <kind> is one of
                    meetings | requirements | use-cases | notes.

Exit codes:
  0  success
  2  precondition failure in non-check modes (single-line stderr message)
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

# Reuse the shared doc helpers (repo_root, slugify).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import RepoRootNotFound, repo_root, slugify  # noqa: E402

DISCOVERY_REL = Path("docs") / "discovery"
CAPTURED_REL = DISCOVERY_REL / "captured"
INTAKE_KINDS = ("meetings", "requirements", "use-cases", "notes")


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def iter_intake_sources(root: Path) -> list[Path]:
    """Return source files dropped in the intake folders (excluding .gitkeep).

    Walks docs/discovery/{meetings,requirements,use-cases,notes}/** — anything that
    isn't a .gitkeep placeholder is treated as un-captured source material.
    """
    sources: list[Path] = []
    for kind in INTAKE_KINDS:
        base = root / DISCOVERY_REL / kind
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.name == ".gitkeep":
                continue
            sources.append(path)
    return sources


def cmd_list(args: argparse.Namespace) -> None:
    if args.check:
        try:
            root = repo_root(Path.cwd())
        except RepoRootNotFound:
            return  # silent exit 0 in hook mode
        sources = iter_intake_sources(root)
        if not sources:
            return
        print(
            f"capture-discovery: {len(sources)} uncaptured sources in docs/discovery/ — "
            f"consider /capture-discovery",
            file=sys.stderr,
        )
        return
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")
    sources = iter_intake_sources(root)
    if not sources:
        print("0 uncaptured sources.")
        return
    print(f"{len(sources)} uncaptured sources:\n")
    print(f"  {'PATH':<60} {'KIND':<14}")
    for path in sources:
        rel = path.relative_to(root).as_posix()
        kind = path.relative_to(root / DISCOVERY_REL).parts[0]
        print(f"  {rel:<60} {kind:<14}")


NOTE_TEMPLATE = """\
---
source: {source}
date_captured: {date}
topic: {topic}
status: raw               # raw | reviewed | promoted
promoted_to:              # e.g. docs/01-prd.md  (filled when status flips to promoted)
---

# {topic}

<!-- Synthesized from: {source}. Replace this comment with the captured content. -->
"""


def cmd_new(args: argparse.Namespace) -> None:
    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")
    if args.kind not in INTAKE_KINDS:
        die(f"invalid --kind {args.kind!r}; expected one of: {', '.join(INTAKE_KINDS)}")
    if not args.topic or not args.topic.strip():
        die("usage: capture-discovery new --kind <kind> --topic <text> [--source <path>]")
    try:
        slug = slugify(args.topic)
    except ValueError as exc:
        die(f"invalid topic: {exc}")

    captured_dir = root / CAPTURED_REL
    captured_dir.mkdir(parents=True, exist_ok=True)
    out_path = captured_dir / f"{date.today().isoformat()}-{slug}.md"
    if out_path.exists():
        die(f"refuse to overwrite existing note: {out_path.relative_to(root).as_posix()}")

    out_path.write_text(
        NOTE_TEMPLATE.format(
            source=(args.source or "<person, meeting, doc path/URL>"),
            date=date.today().isoformat(),
            topic=args.topic.strip(),
        ),
        encoding="utf-8",
    )
    rel = out_path.relative_to(root).as_posix()
    print(f"Created {rel}")
    print(f"Fill the body, then promote when synthesized: /promote-discovery {rel} --to <target>")


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="capture-discovery", description=__doc__)
    sub = parser.add_subparsers(dest="cmd")

    list_p = sub.add_parser("list", help="list uncaptured intake sources")
    list_p.add_argument("--check", action="store_true", help="hook mode (silent unless sources exist)")

    new_p = sub.add_parser("new", help="scaffold a captured/ note for an intake source")
    new_p.add_argument("--kind", help=f"one of: {', '.join(INTAKE_KINDS)}")
    new_p.add_argument("--topic", help="free-text topic for the note title/slug")
    new_p.add_argument("--source", help="path to the raw source file this note synthesizes")

    args = parser.parse_args(argv[1:])
    if args.cmd is None or args.cmd == "list":
        if not hasattr(args, "check"):
            args.check = False
        cmd_list(args)
    elif args.cmd == "new":
        cmd_new(args)


if __name__ == "__main__":
    main(sys.argv)
