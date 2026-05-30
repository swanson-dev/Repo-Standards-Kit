#!/usr/bin/env python3
"""Standards check — runs structural (v1) + content (v2) checks.

Run from anywhere; walks up from this script to find the repo root (nearest
directory containing docs/STANDARDS.md). Exits 1 iff any error finding; warnings
are advisory and never fail the build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks import structural, links, content  # noqa: E402
# Re-exported so the unchanged test_check.py keeps importing it from `check`.
from checks.structural import parse_frontmatter  # noqa: E402,F401

CHECKS = [structural.run, links.run, content.run]


def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "docs" / "STANDARDS.md").exists():
            return parent
    raise SystemExit("Could not locate repo root (no docs/STANDARDS.md above this script).")


def build_context(root: Path) -> Context:
    """Detect adopter mode + parse the optional severity-override map.

    Kit repos have no .standards-kit.json (only `standards init` writes one), so
    'no marker' => kit mode => new checks run at error severity.
    """
    marker = root / ".standards-kit.json"
    if not marker.exists():
        return Context(root=root, adopter_mode=False, overrides={})
    overrides = {}
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        raw = data.get("check", {})
        if isinstance(raw, dict):
            overrides = {k: v for k, v in raw.items() if v in ("error", "warn")}
    except (OSError, ValueError):
        overrides = {}
    return Context(root=root, adopter_mode=True, overrides=overrides)


def main() -> int:
    root = find_repo_root(Path(__file__).resolve().parent)
    ctx = build_context(root)
    findings: list = []
    for run in CHECKS:
        findings.extend(run(root, ctx))
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warn"]
    print(f"Standards check: {len(errors)} error(s), {len(warnings)} warning(s)")
    for f in errors:
        print(f"  ERROR  [{f.check_id}] {f.message}")
    for f in warnings:
        print(f"  WARN   [{f.check_id}] {f.message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
