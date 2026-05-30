"""Internal markdown link + anchor resolution.

Scans every committed *.md (skipping .git/ and src/standards/_payload, which is a
force-include duplicate of the source tree). Relative link targets must resolve
to a real file; #anchor fragments must match a heading slug in the target file.
External links (http/https/mailto/tel) are out of scope.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "links"
DEFAULT_SEVERITY = "error"

# Inline [text](target) — (?<!!) skips images; optional "title" after the target.
_INLINE_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
# Reference definition: [id]: target
_REFDEF_RE = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(\S+)")
# ATX heading line.
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
_EXTERNAL_RE = re.compile(r"^(?:https?:|mailto:|tel:|//)", re.IGNORECASE)

_SKIP_DIR_PARTS = {".git"}
_SKIP_PATH_PREFIXES = ("src/standards/_payload",)


def slugify(heading: str) -> str:
    """GitHub-style heading slug for ASCII headings."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)   # drop punctuation; keep word chars, space, hyphen
    s = re.sub(r"\s+", "-", s)        # spaces -> hyphen
    return s


def _strip_code_and_comments(text: str) -> str:
    """Blank out fenced code blocks, inline code spans, and HTML comments.

    Replaces them with same-length-ish blanks so links inside them are not
    scanned. Newlines are preserved so line numbers stay correct.
    """
    # HTML comments (may span lines).
    text = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)
    # Fenced code blocks ``` ... ``` (preserve newlines).
    text = re.sub(r"```.*?```", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)
    # Inline code spans `...` (single line).
    text = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), text)
    return text


def extract_links(text: str):
    """Return [(line_number, target)] for inline + reference links, skipping
    images, external schemes, and links inside code/comments."""
    cleaned = _strip_code_and_comments(text)
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
    cleaned = _strip_code_and_comments(text)
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
            # Resolve the file part.
            if file_part == "":
                target_path = path  # same-file anchor
            else:
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
