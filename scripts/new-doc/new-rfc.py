#!/usr/bin/env python3
"""new-rfc — scaffold a new RFC folder with auto-numbered NNNN and today as `opened`.

Usage:
  python scripts/new-doc/new-rfc.py "<Question being investigated>"

Creates docs/rfcs/<NNNN>-<slug>/rfc.md. Exits 0 on success, 2 on precondition failure.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _doc_lib.helpers import (  # noqa: E402
    RepoRootNotFound,
    fill_template,
    repo_root,
    slugify,
)

NNNN_FOLDER_PATTERN = re.compile(r"^(\d{4})-.*$")
TITLE_HEADING = "NNNN. <Question being investigated>"

LEADING_HTML_COMMENT_RE = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)


def strip_leading_html_comment(text: str) -> str:
    """Remove a single leading HTML comment block (and surrounding whitespace) from text.

    The ADR/RFC templates begin with `<!-- ... -->` guidance for human authors; that
    block must not survive into generated RFCs because it breaks frontmatter parsing
    by scripts/standards-check/check.py.
    """
    return LEADING_HTML_COMMENT_RE.sub("", text, count=1)


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def next_folder_nnnn(directory: Path) -> str:
    """Folder-aware counterpart to next_nnnn — scans subdirectories instead of files.

    Kept private here until a third script needs folder numbering; lift to _doc_lib then.
    """
    if not directory.exists():
        raise FileNotFoundError(directory)
    highest = 0
    for entry in directory.iterdir():
        if not entry.is_dir():
            continue
        match = NNNN_FOLDER_PATTERN.match(entry.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{highest + 1:04d}"


def main(argv: list[str]) -> None:
    if len(argv) < 2 or not argv[1].strip():
        die("usage: new-rfc.py \"<Question being investigated>\"")
    title = argv[1].strip()

    try:
        root = repo_root(Path.cwd())
    except RepoRootNotFound:
        die("not in a git repo (no .git found walking up from cwd)")

    template_path = root / "docs" / "templates" / "rfc-template.md"
    rfcs_dir = root / "docs" / "rfcs"
    if not template_path.exists():
        die(f"rfc template not found: {template_path}")
    if not rfcs_dir.exists():
        die(f"rfcs dir not found: {rfcs_dir}")

    try:
        slug = slugify(title)
    except ValueError as exc:
        die(f"invalid title: {exc}")

    slug_collision = re.compile(rf"^\d{{4}}-{re.escape(slug)}$")
    existing = [p for p in rfcs_dir.iterdir() if p.is_dir() and slug_collision.match(p.name)]
    if existing:
        die(f"refuse to overwrite existing folder: {sorted(existing)[0]}")

    nnnn = next_folder_nnnn(rfcs_dir)
    out_dir = rfcs_dir / f"{nnnn}-{slug}"

    template = template_path.read_text(encoding="utf-8")
    template = strip_leading_html_comment(template)
    filled = fill_template(
        template,
        {
            "opened: YYYY-MM-DD": f"opened: {date.today().isoformat()}",
            TITLE_HEADING: f"{nnnn}. {title}",
        },
    )
    out_dir.mkdir()
    out_path = out_dir / "rfc.md"
    out_path.write_text(filled, encoding="utf-8")

    rel = out_path.relative_to(root).as_posix()
    print(f"Created {rel}")


if __name__ == "__main__":
    main(sys.argv)
