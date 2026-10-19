"""Read/write the `.standards-kit.json` adoption marker."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MARKER_NAME = ".standards-kit.json"
# ADR-0025 merged infra into application; old names still read as the new ones.
PROFILE_ALIASES = {"infra": "application"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def read_marker(root: Path) -> dict | None:
    p = Path(root) / MARKER_NAME
    if not p.is_file():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict) and data.get("profile") in PROFILE_ALIASES:
        data["profile"] = PROFILE_ALIASES[data["profile"]]
    return data


def write_marker(root: Path, *, kit_version: str, profile: str, adopted: str,
                 tracked: dict[str, str], managed: dict[str, str] | None = None,
                 keep: dict[str, object] | None = None) -> dict:
    data: dict[str, object] = {
        "kit_version": kit_version,
        "profile": profile,
        "adopted": adopted,
        "tracked": dict(sorted(tracked.items())),
        "managed": dict(sorted((managed or {}).items())),
    }
    # Carry adopter-owned keys (such as the `check` severity map) forward; the
    # kit's own fields above always win.
    for key, value in (keep or {}).items():
        data.setdefault(key, value)
    (Path(root) / MARKER_NAME).write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    return data
