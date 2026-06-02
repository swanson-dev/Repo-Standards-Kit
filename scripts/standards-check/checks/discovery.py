"""Discovery promoted_to-existence check: every `status: promoted` item under
docs/discovery/ must have a `promoted_to:` path that exists. Forward-looking —
catches a promotion pointing at a deleted or renamed doc.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "discovery"
DEFAULT_SEVERITY = "error"

# Raw intake folders (ADR-0014) hold gitignored source material, not tracked promoted
# notes — exclude them from the promoted_to integrity check.
INTAKE_KINDS = ("meetings", "requirements", "use-cases", "notes")

# Allow a leading HTML comment (discovery templates ship one) before the frontmatter.
_FRONTMATTER_RE = re.compile(r"\A(?:\s*<!--.*?-->\s*)?---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        hash_pos = val.find("#")
        if hash_pos != -1:
            val = val[:hash_pos]
        fm[key.strip()] = val.strip()
    return fm


def _iter_discovery(root: Path):
    base = root / "docs" / "discovery"
    if not base.is_dir():
        return
    for path in sorted(base.rglob("*.md")):
        if path.name == "README.md":
            continue
        if "templates" in path.parts:
            continue
        rel_parts = path.relative_to(base).parts
        if rel_parts and rel_parts[0] in INTAKE_KINDS:
            continue
        yield path


def run(root: Path, ctx: Context) -> list:
    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    findings = []
    for path in _iter_discovery(root):
        rel = path.relative_to(root).as_posix()
        fm = _parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if fm.get("status") != "promoted":
            continue
        target = fm.get("promoted_to", "")
        if not target:
            findings.append(Finding(CHECK_ID, severity, f"{rel}: status: promoted but promoted_to: is empty"))
            continue
        if not (root / target).exists():
            findings.append(Finding(CHECK_ID, severity, f"{rel}: promoted_to: {target} does not exist"))
    return findings
