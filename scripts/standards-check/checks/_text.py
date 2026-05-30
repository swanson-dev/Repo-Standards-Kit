"""Shared text utilities for content-scanning checks."""
from __future__ import annotations

import re

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def _blank(match) -> str:
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_code_and_comments(text: str) -> str:
    """Blank out HTML comments, fenced code blocks, and inline code spans.

    Replaced with spaces (newlines preserved) so links/placeholders inside them
    are not scanned and line numbers stay correct. Order matters: comments first
    (a comment may contain backticks), then fenced, then inline spans.
    """
    text = _COMMENT_RE.sub(_blank, text)
    text = _FENCED_RE.sub(_blank, text)
    text = _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)
    return text
