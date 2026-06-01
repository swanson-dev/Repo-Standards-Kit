"""`standards init` — vendor the kit into a target repo and write the marker."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from standards.__about__ import __version__
from standards.managed import block_hash
from standards.manifest import PROFILE_TEMPLATED, SCAFFOLD_ONCE, classify, iter_payload
from standards.marker import MARKER_NAME, read_marker, sha256_file, write_marker
from standards.payload import payload_root

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
                f"{shown}{more}. Re-run with force=True to overwrite, or adopt into an empty repo."
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

    # Scaffold-once: copy source template -> target path only if absent. Seed each
    # so a freshly adopted repo is CI-green (ADR-0012 / Slice 5): tick the checklist
    # core boxes, stamp the ai/ dates.
    repo_name = target.resolve().name
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

    write_marker(target, kit_version=__version__, profile=profile,
                 adopted=adopted, tracked=tracked, managed=managed)
    return read_marker(target)
