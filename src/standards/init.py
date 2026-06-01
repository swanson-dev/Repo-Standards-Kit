"""`standards init` — vendor the kit into a target repo and write the marker."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.managed import (
    block_hash,
    extract_block,
    find_block,
    has_begin_marker,
    splice_block,
)
from standards.manifest import PROFILE_TEMPLATED, SCAFFOLD_ONCE, classify, iter_payload
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root

ADOPT_REPORT_KEYS = ("added", "unchanged", "spliced", "conflicts", "scaffolded")

PROFILE_PLACEHOLDER = "<application | library | infra | data>"

_LEADING_COMMENT_RE = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)


def _stamp_ai_starter(content: str, adopted: str) -> str:
    """Make a scaffolded ai/ file pass the freshness check on day one.

    The starters lead with an HTML comment, which hides the frontmatter from the
    `^---` parser, and carry placeholder dates. Strip the comment and stamp the
    adopted date so `last_updated:` / `written:` are real, parseable, and fresh.
    """
    content = _LEADING_COMMENT_RE.sub("", content, count=1)
    content = content.replace("last_updated: YYYY-MM-DD", f"last_updated: {adopted}")
    content = content.replace(
        "written: YYYY-MM-DDTHH:MM:SS-05:00", f"written: {adopted}"
    )
    return content


def _fill_checklist(content: str, *, profile: str, adopted: str, repo_name: str) -> str:
    """Seed the checklist so a freshly adopted repo is CI-green.

    Tick the universal-core boxes (init provides those files) and fill the header
    metadata. Profile-required/expected rows stay `<placeholder>` (the waiver check
    skips them) for the adopter to fill from docs/STANDARDS.md.
    """
    content = content.replace(PROFILE_PLACEHOLDER, profile)
    content = content.replace("# Standards Checklist — <repo-name>",
                              f"# Standards Checklist — {repo_name}")
    content = content.replace("**Kit version adopted:** <e.g. 0.1.0>",
                              f"**Kit version adopted:** {__version__}")
    content = content.replace("**Last reviewed:** YYYY-MM-DD by <name>",
                              f"**Last reviewed:** {adopted} by standards init")
    out, in_core = [], False
    for line in content.splitlines(keepends=True):
        if line.lstrip().startswith("## "):
            in_core = line.lstrip()[3:].strip().lower().startswith("universal core")
        if in_core:
            line = line.replace("- [ ] ", "- [x] ", 1)
        out.append(line)
    return "".join(out)


def _seed_scaffold_once(target: Path, src_root: Path, *, profile: str,
                        adopted: str) -> list[str]:
    """Seed scaffold-once files into `target` (only those absent). Returns the
    destination paths actually written. Each seed is transformed so a freshly
    adopted repo is CI-green: tick the checklist core boxes, stamp the ai/ dates.
    """
    repo_name = target.resolve().name
    seeded: list[str] = []
    for src_rel, dest_rel in SCAFFOLD_ONCE.items():
        dest = target / dest_rel
        if dest.exists():
            continue
        content = (src_root / src_rel).read_text(encoding="utf-8")
        if dest_rel in PROFILE_TEMPLATED:
            content = _fill_checklist(content, profile=profile, adopted=adopted,
                                      repo_name=repo_name)
        elif dest_rel.startswith("ai/"):
            content = _stamp_ai_starter(content, adopted)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        seeded.append(dest_rel)
    return seeded


def run_init(target: Path, *, profile: str, adopted: str, force: bool = False) -> dict:
    """Copy kit-tracked files + scaffold-once seeds into `target`; write the marker.

    Returns the marker dict. Raises FileExistsError if already adopted and not force.
    """
    target = Path(target)
    if read_marker(target) is not None and not force:
        raise FileExistsError(
            f"{target / MARKER_NAME} exists; pass force=True to re-init"
        )

    if not force:
        collisions: list[str] = []
        for full, rel in iter_payload(payload_root()):
            cls = classify(rel)
            if cls == "scaffold-once-source":
                continue
            dest = target / rel
            if not dest.exists():
                continue
            if cls == "partial":
                differs = block_hash(dest.read_text(encoding="utf-8")) != \
                    block_hash(full.read_text(encoding="utf-8"))
            else:
                differs = sha256_file(dest) != sha256_file(full)
            if differs:
                collisions.append(rel)
        if collisions:
            shown = ", ".join(sorted(collisions)[:5])
            more = "" if len(collisions) <= 5 else f" (+{len(collisions) - 5} more)"
            raise FileExistsError(
                f"{len(collisions)} kit file(s) already exist with different content: "
                f"{shown}{more}. Run `standards adopt` to adopt non-destructively "
                f"(keeps your files, writes .kit-{__version__} sidecars), or re-run "
                f"with force=True to overwrite."
            )

    src_root = payload_root()
    tracked: dict[str, str] = {}
    managed: dict[str, str] = {}

    for full, rel in iter_payload(src_root):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue  # handled in the scaffold-once loop below
        dest = target / rel
        if cls == "partial" and dest.exists() and not force:
            # Preserve downstream content outside the managed block. The pre-flight
            # guard already ensured the existing block matches the payload's, so we
            # record the existing block's hash rather than overwriting the whole file.
            existing_hash = block_hash(dest.read_text(encoding="utf-8"))
            if existing_hash is not None:
                managed[rel] = existing_hash
                continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(full, dest)
        if cls == "partial":
            managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
        else:  # kit-tracked
            tracked[rel] = sha256_file(dest)

    _seed_scaffold_once(target, src_root, profile=profile, adopted=adopted)

    write_marker(target, kit_version=__version__, profile=profile,
                 adopted=adopted, tracked=tracked, managed=managed)
    return read_marker(target)


def run_adopt(target: Path, *, profile: str, adopted: str) -> dict[str, list[str]]:
    """Adopt the kit into an EXISTING repo non-destructively (RFC-0002 / ADR-0013).

    Like `init` but never clobbers: a differing kit-tracked file is kept and the
    kit copy is written as a `<rel>.kit-<version>` sidecar; a partial file with no
    managed block gets the kit block appended; one with a block is spliced to the
    kit's current contract. Writes the marker. Returns a report keyed by
    ADOPT_REPORT_KEYS. Raises FileExistsError if already adopted (use `update`).
    """
    target = Path(target)
    if read_marker(target) is not None:
        raise FileExistsError(
            f"{target / MARKER_NAME} exists; this repo is already adopted — "
            f"run `standards update` instead."
        )

    src_root = payload_root()
    report: dict[str, list[str]] = {k: [] for k in ADOPT_REPORT_KEYS}
    tracked: dict[str, str] = {}
    managed: dict[str, str] = {}

    for full, rel in iter_payload(src_root):
        cls = classify(rel)
        if cls == "scaffold-once-source":
            continue
        dest = target / rel

        if cls == "kit-tracked":
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(full, dest)
                tracked[rel] = sha256_file(dest)
                report["added"].append(rel)
            elif sha256_file(dest) == sha256_file(full):
                tracked[rel] = sha256_file(dest)
                report["unchanged"].append(rel)
            else:  # adopter owns a differing file — keep it, sidecar the kit copy
                sidecar = target / f"{rel}.kit-{__version__}"
                sidecar.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(full, sidecar)
                tracked[rel] = sha256_file(full)  # baseline; update sees theirs as edited
                report["conflicts"].append(rel)
            continue

        # partial: the kit owns a single managed block; the rest is the adopter's.
        src_inner = find_block(full.read_text(encoding="utf-8")).inner
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(full, dest)
            managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
            report["added"].append(rel)
            continue
        cur_text = dest.read_text(encoding="utf-8")
        cur_block = find_block(cur_text)
        if cur_block is not None:  # has our block already — install the current contract
            if cur_block.inner == src_inner:
                report["unchanged"].append(rel)
            else:
                dest.write_text(splice_block(cur_text, src_inner), encoding="utf-8")
                report["spliced"].append(rel)
            managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
        elif not has_begin_marker(cur_text):  # plain file — append the kit block
            kit_block = extract_block(full.read_text(encoding="utf-8"))
            dest.write_text(cur_text.rstrip("\n") + "\n\n" + kit_block + "\n",
                            encoding="utf-8")
            managed[rel] = block_hash(dest.read_text(encoding="utf-8"))
            report["spliced"].append(rel)
        else:  # malformed/duplicate markers — don't guess, sidecar
            sidecar = target / f"{rel}.kit-{__version__}"
            sidecar.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(full, sidecar)
            report["conflicts"].append(rel)

    report["scaffolded"] = _seed_scaffold_once(target, src_root, profile=profile,
                                               adopted=adopted)

    write_marker(target, kit_version=__version__, profile=profile,
                 adopted=adopted, tracked=tracked, managed=managed)
    return report
