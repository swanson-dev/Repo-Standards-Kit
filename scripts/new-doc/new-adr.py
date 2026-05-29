#!/usr/bin/env python3
"""new-adr — scaffold a new MADR 3.0 ADR with auto-numbered NNNN, today, and title.

Usage:
  python scripts/new-doc/new-adr.py "<Title of the decision>"

Exits 0 on success, 2 on any precondition failure (single-line stderr message).
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

# Make `_doc_lib` importable: scripts/ is two levels up from this file.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import (  # noqa: E402
    RepoRootNotFound,
    fill_template,
    next_nnnn,
    repo_root,
    slugify,
)

NNNN_PATTERN = re.compile(r"^(\d{4})-.*\.md$")
TITLE_HEADING = "NNNN. <Title — the decision, not the question>"

LEADING_HTML_COMMENT_RE = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)


def strip_leading_html_comment(text: str) -> str:
    """Remove a single leading HTML comment block (and surrounding whitespace) from text.

    The ADR/RFC templates begin with `<!-- ... -->` guidance for human authors; that
    block must not survive into generated ADRs because it breaks frontmatter parsing
    by scripts/standards-check/check.py.
    """
    return LEADING_HTML_COMMENT_RE.sub("", text, count=1)


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def main(argv: list[str]) -> None:
    if len(argv) < 2 or not argv[1].strip():
        die("usage: new-adr.py \"<Title of the decision>\"")
    title = argv[1].strip()

    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")

    template_path = root / "docs" / "templates" / "adr-template.md"
    decisions_dir = root / "docs" / "decisions"
    if not template_path.exists():
        die(f"adr template not found: {template_path}")
    if not decisions_dir.exists():
        die(f"decisions dir not found: {decisions_dir}")

    try:
        slug = slugify(title)
    except ValueError as exc:
        die(f"invalid title: {exc}")

    slug_collision = re.compile(rf"^\d{{4}}-{re.escape(slug)}\.md$")
    existing = [p for p in decisions_dir.iterdir() if p.is_file() and slug_collision.match(p.name)]
    if existing:
        die(f"refuse to overwrite existing file: {sorted(existing)[0]}")

    nnnn = next_nnnn(decisions_dir, NNNN_PATTERN)
    out_path = decisions_dir / f"{nnnn}-{slug}.md"

    template = template_path.read_text(encoding="utf-8")
    template = strip_leading_html_comment(template)
    filled = fill_template(
        template,
        {
            "YYYY-MM-DD": date.today().isoformat(),
            TITLE_HEADING: f"{nnnn}. {title}",
        },
    )
    out_path.write_text(filled, encoding="utf-8")

    rel = out_path.relative_to(root).as_posix()
    print(f"Created {rel}")
    print("Add to docs/decisions/README.md index:")
    print(f"| [{nnnn}](./{nnnn}-{slug}.md) | {title} |")


if __name__ == "__main__":
    main(sys.argv)
