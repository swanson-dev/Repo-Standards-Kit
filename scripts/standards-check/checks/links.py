"""Internal markdown link + anchor resolution.

Scans repo-authored *.md files, skipping common VCS, dependency, build, and cache
directories plus src/standards/_payload, which is a force-include duplicate of
the source tree. Relative link targets must resolve to a real file; #anchor
fragments must match a heading slug in the target file. External links
(http/https/mailto/tel) are out of scope.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity
from ._text import strip_code_and_comments

CHECK_ID = "links"
DEFAULT_SEVERITY = "error"

# Inline [text](target) — (?<!!) skips images; optional "title" after the target.
_INLINE_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
# Reference definition: [id]: target
_REFDEF_RE = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(\S+)")
# ATX heading line.
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
_EXTERNAL_RE = re.compile(r"^(?:https?:|mailto:|tel:|//)", re.IGNORECASE)

_SKIP_DIR_PARTS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}
_SKIP_PATH_PREFIXES = ("src/standards/_payload",)


def slugify(heading: str) -> str:
    """GitHub-style heading slug for ASCII headings."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)   # drop punctuation; keep word chars, space, hyphen
    s = re.sub(r"\s+", "-", s)        # spaces -> hyphen
    return s


def extract_links(text: str) -> list:
    """Return [(line_number, target)] for inline + reference links, skipping
    images, external schemes, and links inside code/comments."""
    cleaned = strip_code_and_comments(text)
    out = []
    for i, line in enumerate(cleaned.splitlines(), 1):
        for m in _INLINE_RE.finditer(line):
            target = m.group(1)
            if not _EXTERNAL_RE.match(target):
                out.append((i, target))
        for m in _REFDEF_RE.finditer(line):
            target = m.group(1)
            if not _EXTERNAL_RE.match(target):
                out.append((i, target))
    return out


def _heading_slugs(text: str):
    """Yield each ATX heading's GitHub slug, de-duplicating with -1/-2 suffixes."""
    cleaned = strip_code_and_comments(text)
    slugs = {}
    for line in cleaned.splitlines():
        m = _HEADING_RE.match(line)
        if not m:
            continue
        base = slugify(m.group(1))
        if base not in slugs:
            slugs[base] = 0
            yield base
        else:
            slugs[base] += 1
            yield f"{base}-{slugs[base]}"


def _iter_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if any(part in _SKIP_DIR_PARTS for part in path.relative_to(root).parts):
            continue
        if any(rel.startswith(prefix) for prefix in _SKIP_PATH_PREFIXES):
            continue
        yield path, rel


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    findings = []
    for path, rel in _iter_markdown(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, target in extract_links(text):
            frag = ""
            file_part = target
            if "#" in target:
                file_part, _, frag = target.partition("#")
            file_part = file_part.strip("<>")
            # Resolve the file part.
            if file_part == "":
                target_path = path  # same-file anchor
            else:
                # NOTE: .exists() is case-insensitive on Windows but case-sensitive on
                # Linux CI — a wrong-case link can pass locally yet fail in CI.
                target_path = (path.parent / file_part).resolve()
                if not target_path.exists():
                    findings.append(Finding(
                        CHECK_ID, severity,
                        f"{rel}:{line_no} broken link -> {target} (missing file)",
                    ))
                    continue
            # Resolve the anchor, if any.
            if frag:
                try:
                    target_text = target_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if frag not in set(_heading_slugs(target_text)):
                    findings.append(Finding(
                        CHECK_ID, severity,
                        f"{rel}:{line_no} broken link -> {target} (missing anchor)",
                    ))
    return findings
