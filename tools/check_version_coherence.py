#!/usr/bin/env python3
"""Version-coherence guard (kit-only). Verifies the kit's version strings agree.

Source of truth: src/standards/__about__.py __version__ (pyproject reads it via
[tool.hatch.version]). Asserts the CHANGELOG top version section, the AGENTS.md
Kit-version line, and the AGENTS.md agents-core sentinel tag all match. With
--tag vX.Y.Z, also asserts the release tag matches. Exit 1 on any mismatch.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ABOUT_RE = re.compile(r"""__version__\s*=\s*["']([^"']+)["']""")
_CHANGELOG_RE = re.compile(r"(?m)^##\s+\[(\d+\.\d+\.\d+)\]")
_KITVER_RE = re.compile(r"(?m)^-\s*Kit version:\s*\*\*([^*]+)\*\*")
_SENTINEL_RE = re.compile(r"kit-managed:\s*agents-core\s*\(v([^)]+)\)")


def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "src" / "standards" / "__about__.py").exists():
            return parent
    raise SystemExit("Could not locate kit root (no src/standards/__about__.py above this script).")


def read_about_version(root: Path):
    text = (root / "src" / "standards" / "__about__.py").read_text(encoding="utf-8")
    m = _ABOUT_RE.search(text)
    return m.group(1) if m else None


def find_incoherences(root: Path, tag: str = None) -> list:
    """Return human-readable mismatch messages; empty list means coherent."""
    about = read_about_version(root)
    if about is None:
        return ["src/standards/__about__.py: no __version__ found"]
    msgs = []

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    m = _CHANGELOG_RE.search(changelog)  # first numeric version section ([Unreleased] is skipped)
    if not m:
        msgs.append("CHANGELOG.md: no version section (## [x.y.z]) found")
    elif m.group(1) != about:
        msgs.append(f"CHANGELOG.md top version {m.group(1)} != __about__ {about}")

    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    m = _KITVER_RE.search(agents)
    if not m:
        msgs.append("AGENTS.md: no `- Kit version: **x.y.z**` line found")
    elif m.group(1).strip() != about:
        msgs.append(f"AGENTS.md Kit-version {m.group(1).strip()} != __about__ {about}")

    m = _SENTINEL_RE.search(agents)
    if not m:
        msgs.append("AGENTS.md: no agents-core sentinel version tag found")
    elif m.group(1) != about:
        msgs.append(f"AGENTS.md sentinel (v{m.group(1)}) != __about__ {about}")

    if tag is not None:
        tag_ver = tag[1:] if tag.startswith("v") else tag
        if tag_ver != about:
            msgs.append(f"release tag {tag} != __about__ {about}")

    return msgs


def main(argv) -> int:
    parser = argparse.ArgumentParser(prog="check-version-coherence")
    parser.add_argument("--tag", default=None, help="release tag (e.g. v0.8.0) to verify against __about__")
    args = parser.parse_args(argv[1:])
    root = find_repo_root(Path(__file__).resolve().parent)
    msgs = find_incoherences(root, tag=args.tag)
    if msgs:
        print("Version coherence: FAIL")
        for m in msgs:
            print(f"  {m}")
        return 1
    print("Version coherence: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
