"""Content lint: residual template placeholders in committed ADRs/RFCs, and a
light Keep-a-Changelog shape check for CHANGELOG.md.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

PLACEHOLDER_ID = "placeholder"
CHANGELOG_ID = "changelog"
DEFAULT_SEVERITY = "error"

# Angle-bracket placeholder: <words, spaces, commas, em-dash, ellipsis>. Excludes
# tags with '/' or '!' (HTML/comments) and '#' (won't appear in placeholders).
_ANGLE_RE = re.compile(r"<[A-Za-z][^<>\n/!]*?>")
_DATE_PLACEHOLDER_RE = re.compile(r"\bYYYY-MM-DD\b")
_BARE_NNNN_RE = re.compile(r"\bNNNN\b")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_VERSION_SECTION_RE = re.compile(r"(?m)^##\s+\[[^\]]+\]")

_ADR_FILE_RE = re.compile(r"^\d{4}-[a-z0-9-]+\.md$")


def _blank_comments(text: str) -> str:
    return _COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def find_placeholders(text: str):
    """Return [(line_number, token)] for residual template placeholders, ignoring
    anything inside <!-- --> comment blocks."""
    cleaned = _blank_comments(text)
    out = []
    for i, line in enumerate(cleaned.splitlines(), 1):
        for m in _ANGLE_RE.finditer(line):
            out.append((i, m.group(0)))
        for m in _DATE_PLACEHOLDER_RE.finditer(line):
            out.append((i, m.group(0)))
        for m in _BARE_NNNN_RE.finditer(line):
            out.append((i, m.group(0)))
    return out


def _authored_docs(root: Path):
    decisions = root / "docs/decisions"
    if decisions.is_dir():
        for p in sorted(decisions.glob("*.md")):
            if _ADR_FILE_RE.match(p.name):
                yield p
    rfcs = root / "docs/rfcs"
    if rfcs.is_dir():
        for entry in sorted(rfcs.iterdir()):
            rfc_md = entry / "rfc.md"
            if entry.is_dir() and rfc_md.exists():
                yield rfc_md


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(PLACEHOLDER_ID, DEFAULT_SEVERITY, ctx)
    findings = []
    for path in _authored_docs(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, token in find_placeholders(text):
            findings.append(Finding(
                PLACEHOLDER_ID, severity,
                f"{rel}:{line_no} unfilled template placeholder: {token}",
            ))
    changelog = root / "CHANGELOG.md"
    if changelog.exists():
        text = changelog.read_text(encoding="utf-8", errors="replace")
        if not _VERSION_SECTION_RE.search(text):
            findings.append(Finding(
                CHANGELOG_ID, resolve_severity(CHANGELOG_ID, DEFAULT_SEVERITY, ctx),
                "CHANGELOG.md: no Keep-a-Changelog version section (## [x.y.z]) found",
            ))
    return findings
