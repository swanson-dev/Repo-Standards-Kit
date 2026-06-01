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
    """Locate the single managed block; None unless exactly one BEGIN and one
    matching END marker exist (absent, duplicated, or unterminated → None)."""
    begins = list(_BEGIN.finditer(text))
    if len(begins) != 1:
        return None
    b = begins[0]
    ends = list(_end_pattern(b.group("id")).finditer(text, b.end()))
    if len(ends) != 1:
        return None
    end_match = ends[0]
    inner = text[b.end():end_match.start()].strip("\n")
    return Block(block_id=b.group("id"), inner=inner,
                 start=b.end(), end=end_match.start())


def extract_block(text: str) -> str | None:
    """Return the full managed block substring (BEGIN + inner + END), or None.

    Used by `standards adopt` to append the kit's block to an existing file that
    has no managed region yet. None unless exactly one well-formed block exists.
    """
    begins = list(_BEGIN.finditer(text))
    if len(begins) != 1:
        return None
    b = begins[0]
    ends = list(_end_pattern(b.group("id")).finditer(text, b.end()))
    if len(ends) != 1:
        return None
    return text[b.start():ends[0].end()]


def has_begin_marker(text: str) -> bool:
    """True if the text contains any kit-managed BEGIN marker (well-formed or not)."""
    return _BEGIN.search(text) is not None


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
