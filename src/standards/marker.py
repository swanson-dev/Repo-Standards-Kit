"""Read/write the `.standards-kit.json` adoption marker."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from standards.profiles import PROFILE_ALIASES

MARKER_NAME = ".standards-kit.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def read_marker(root: Path) -> dict | None:
    p = Path(root) / MARKER_NAME
    if not p.is_file():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("profile"), str):
        # Markers before ADR-0025 have only `profile`; `profile` is always profiles[0].
        names = data.get("profiles")
        if not (isinstance(names, list) and names and all(isinstance(n, str) for n in names)):
            names = [data["profile"]]
        names = list(dict.fromkeys(PROFILE_ALIASES.get(n, n) for n in names))
        data["profile"], data["profiles"] = names[0], names
    return data


def write_marker(root: Path, *, kit_version: str, profile: str | list[str], adopted: str,
                 tracked: dict[str, str], managed: dict[str, str] | None = None,
                 keep: dict[str, object] | None = None) -> dict:
    # `profile` stays the first entry so older CLIs still read one valid profile.
    profiles = [profile] if isinstance(profile, str) else list(profile)
    data: dict[str, object] = {
        "kit_version": kit_version,
        "profile": profiles[0],
        "profiles": profiles,
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
