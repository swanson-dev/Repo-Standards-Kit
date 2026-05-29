"""`standards init` — vendor the kit into a target repo and write the marker."""
from __future__ import annotations

import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.managed import block_hash
from standards.manifest import PROFILE_TEMPLATED, SCAFFOLD_ONCE, classify, iter_payload
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root

PROFILE_PLACEHOLDER = "<application | library | infra | data>"


def run_init(target: Path, *, profile: str, adopted: str, force: bool = False) -> dict:
    """Copy kit-tracked files + scaffold-once seeds into `target`; write the marker.

    Returns the marker dict. Raises FileExistsError if already adopted and not force.
    """
    target = Path(target)
    if read_marker(target) is not None and not force:
        raise FileExistsError(
            f"{target / MARKER_NAME} exists; pass force=True to re-init"
        )

    src_root = payload_root()
    tracked: dict[str, str] = {}
    managed: dict[str, str] = {}

    for full, rel in iter_payload(src_root):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue  # handled in the scaffold-once loop below
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(full, dest)
        if cls == "partial":
            managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
        else:  # kit-tracked
            tracked[rel] = sha256_file(dest)

    # Scaffold-once: copy source template -> target path only if absent.
    for src_rel, dest_rel in SCAFFOLD_ONCE.items():
        dest = target / dest_rel
        if dest.exists():
            continue
        content = (src_root / src_rel).read_text(encoding="utf-8")
        if dest_rel in PROFILE_TEMPLATED:
            content = content.replace(PROFILE_PLACEHOLDER, profile)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    write_marker(target, kit_version=__version__, profile=profile,
                 adopted=adopted, tracked=tracked, managed=managed)
    return read_marker(target)
