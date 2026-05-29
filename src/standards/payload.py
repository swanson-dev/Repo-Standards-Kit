"""Locate the kit content: bundled `_payload` in a wheel, or the repo root in dev."""
from __future__ import annotations

from importlib import resources
from pathlib import Path

_SENTINEL = "docs/STANDARDS.md"


def _repo_root_from_source() -> Path:
    """Walk up from this file to the dir containing the sentinel (the repo root)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / _SENTINEL).is_file():
            return parent
    return here.parents[2]  # src/standards/payload.py -> repo root by layout


def payload_root() -> Path:
    """Directory holding the kit payload.

    An installed wheel bundles the content under `standards/_payload` (ADR-0009).
    Running from source there is no `_payload`, so fall back to the repo root,
    whose real files ARE the payload (kept DRY — no duplicated content).
    """
    bundled = Path(str(resources.files("standards") / "_payload"))
    if (bundled / _SENTINEL).is_file():
        return bundled
    return _repo_root_from_source()
