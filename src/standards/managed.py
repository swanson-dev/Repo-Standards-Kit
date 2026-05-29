"""Single managed-region block per file, delimited by HTML-comment sentinels.

    <!-- BEGIN kit-managed: <id> (v<ver>) -->
    ...kit-owned content...
    <!-- END kit-managed: <id> -->

`update` rewrites only the inner content; drift is detected by hashing the inner
text (recorded in the marker's `managed` table). One block per file (v1).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_BEGIN = re.compile(
    r"<!--\s*BEGIN kit-managed:\s*(?P<id>[\w-]+)\s*\(v[^)]*\)\s*-->", re.MULTILINE
)


@dataclass(frozen=True)
class Block:
    block_id: str
    inner: str          # text between the markers, stripped of bracketing newlines
    start: int          # index where inner begins (in the source text)
    end: int            # index where inner ends


def _end_pattern(block_id: str) -> re.Pattern:
    return re.compile(rf"<!--\s*END kit-managed:\s*{re.escape(block_id)}\s*-->")


def find_block(text: str) -> Block | None:
    """Locate the single managed block; None if absent, duplicated, or unterminated."""
    begins = list(_BEGIN.finditer(text))
    if len(begins) != 1:
        return None
    b = begins[0]
    end_match = _end_pattern(b.group("id")).search(text, b.end())
    if end_match is None:
        return None
    inner = text[b.end():end_match.start()].strip("\n")
    return Block(block_id=b.group("id"), inner=inner,
                 start=b.end(), end=end_match.start())


def splice_block(text: str, new_inner: str) -> str:
    """Return `text` with the managed block's inner content replaced. Raises if none."""
    block = find_block(text)
    if block is None:
        raise ValueError("no single managed block found")
    return text[:block.start] + "\n" + new_inner + "\n" + text[block.end:]


def block_hash(text: str) -> str | None:
    """sha256 of the managed block's inner content; None if no block."""
    block = find_block(text)
    if block is None:
        return None
    return hashlib.sha256(block.inner.encode("utf-8")).hexdigest()
