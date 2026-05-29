"""`standards update` — reconcile a vendored kit against the running version.

Non-destructive: downstream edits never get clobbered. Conflicts are written as
`<rel>.kit-<version>` sidecars and reported. See ADR-0009 / ADR-0010.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.managed import block_hash, find_block, splice_block
from standards.manifest import classify, iter_payload
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root

REPORT_KEYS = ("updated", "unchanged", "spliced", "conflicts", "added", "removed")


def _empty_report() -> dict[str, list[str]]:
    return {k: [] for k in REPORT_KEYS}


def _sidecar(target: Path, rel: str, src_full: Path, dry_run: bool) -> None:
    if dry_run:
        return
    dest = target / f"{rel}.kit-{__version__}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_full, dest)


def run_update(target: Path, *, dry_run: bool = False) -> dict[str, list[str]]:
    """Reconcile `target` against the payload. Returns a report keyed by REPORT_KEYS.

    Raises FileNotFoundError if `target` has no adoption marker.
    """
    target = Path(target)
    marker = read_marker(target)
    if marker is None:
        raise FileNotFoundError(
            f"{target / MARKER_NAME} not found; run `standards init` first"
        )

    src_root = payload_root()
    report = _empty_report()
    tracked = dict(marker.get("tracked", {}))
    managed = dict(marker.get("managed", {}))
    seen: set[str] = set()

    for full, rel in iter_payload(src_root):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue
        seen.add(rel)
        dest = target / rel

        if cls == "kit-tracked":
            if not dest.exists():
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(full, dest)
                    tracked[rel] = sha256_file(dest)
                report["added"].append(rel)
                continue
            dest_hash = sha256_file(dest)
            src_hash = sha256_file(full)
            if dest_hash == src_hash:
                tracked[rel] = dest_hash
                report["unchanged"].append(rel)
            elif dest_hash == tracked.get(rel):   # untouched since last sync
                if not dry_run:
                    shutil.copyfile(full, dest)
                    tracked[rel] = sha256_file(dest)
                report["updated"].append(rel)
            else:                                  # downstream edited it
                _sidecar(target, rel, full, dry_run)
                report["conflicts"].append(rel)

        elif cls == "partial":
            if not dest.exists():
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(full, dest)
                    managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
                report["added"].append(rel)
                continue
            cur_text = dest.read_text(encoding="utf-8")
            cur_block = block_hash(cur_text)
            if cur_block is not None and cur_block == managed.get(rel):
                # Block is untouched since last sync — apply kit update (idempotent if
                # content is identical, e.g. running from dev source).
                if not dry_run:
                    new_inner = find_block(full.read_text(encoding="utf-8")).inner
                    dest.write_text(splice_block(cur_text, new_inner), encoding="utf-8")
                    managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
                report["spliced"].append(rel)
            elif cur_block == block_hash(full.read_text(encoding="utf-8")):
                # Block matches source and is apparently fresh (not in managed table).
                managed[rel] = cur_block
                report["unchanged"].append(rel)
            else:                                  # block edited, or markers gone
                _sidecar(target, rel, full, dry_run)
                report["conflicts"].append(rel)

    for rel in list(tracked) + list(managed):
        if rel not in seen:
            report["removed"].append(rel)

    if not dry_run:
        write_marker(target, kit_version=__version__, profile=marker["profile"],
                     adopted=marker["adopted"], tracked=tracked, managed=managed)
    return report
