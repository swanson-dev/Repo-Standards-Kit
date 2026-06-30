"""Read/write the `.standards-kit.json` adoption marker."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MARKER_NAME = ".standards-kit.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def read_marker(root: Path) -> dict | None:
    p = Path(root) / MARKER_NAME
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def write_marker(root: Path, *, kit_version: str, profile: str, adopted: str,
                 tracked: dict[str, str], managed: dict[str, str] | None = None) -> dict:
    data = {
        "kit_version": kit_version,
        "profile": profile,
        "adopted": adopted,
        "tracked": dict(sorted(tracked.items())),
        "managed": dict(sorted((managed or {}).items())),
    }
    (Path(root) / MARKER_NAME).write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    return data
