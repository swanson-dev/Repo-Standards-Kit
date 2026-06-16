"""Payload enumeration + ownership classification for kit files.

Plan 1 recognizes two classes:
  - kit-tracked  : kit owns it; update may overwrite (Plan 2).
  - scaffold-once: kit seeds it once; downstream owns it thereafter.

The partial / managed-region class arrives in Plan 2; until then AGENTS.md,
CLAUDE.md, and .github/copilot-instructions.md are treated as kit-tracked.

The payload is an explicitly enumerated set (mirrored by the force-include map in
pyproject.toml), NOT "everything under a root" — so .git/, src/, tests/, and the
kit's own ai/ and docs/rfcs/ are never copied into adopters.
"""
from __future__ import annotations

import os
from pathlib import Path

# Directories whose entire contents are payload (relative to payload root).
PAYLOAD_DIRS: tuple[str, ...] = (
    "docs/templates",
    "scripts/_doc_lib",
    "scripts/new-doc",
    "scripts/session-context",
    "scripts/standards-check",
    "scripts/update-handoff",
    ".github/prompts",
    ".claude",
)

# Individual payload files (relative to payload root).
PAYLOAD_FILES: tuple[str, ...] = (
    "docs/STANDARDS.md",
    ".github/workflows/repo-standards.yml",
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
    "AGENTS.md",
    "CLAUDE.md",
)

# Files the kit partially owns: a single managed block is kit-owned, the rest is
# downstream-owned. Handled by update via managed-region splice (ADR-0010).
PARTIAL_FILES: frozenset[str] = frozenset({
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
})

# Source template (relative to payload root) -> target path (relative to repo root).
SCAFFOLD_ONCE: dict[str, str] = {
    "docs/templates/ai-starters/current-state.md": "ai/current-state.md",
    "docs/templates/ai-starters/handoff.md": "ai/handoff.md",
    "docs/templates/ai-starters/next-actions.md": "ai/next-actions.md",
    "docs/templates/ai-starters/open-questions.md": "ai/open-questions.md",
    "docs/templates/STANDARDS-CHECKLIST.md.template": "docs/STANDARDS-CHECKLIST.md",
    # Universal-core docs the adopter owns after seeding (templates carry author
    # guidance; the folder READMEs orient the decisions/discovery/rfcs trees).
    "docs/templates/overview-template.md": "docs/00-overview.md",
    "docs/templates/glossary-template.md": "docs/10-glossary.md",
    "docs/templates/decisions-readme-template.md": "docs/decisions/README.md",
    "docs/discovery/README.md": "docs/discovery/README.md",
    "docs/rfcs/README.md": "docs/rfcs/README.md",
}

# Scaffold-once destinations whose PROFILE_PLACEHOLDER must be substituted at init.
PROFILE_TEMPLATED: frozenset[str] = frozenset({"docs/STANDARDS-CHECKLIST.md"})

# Payload files that are scaffold-once *sources* and must not be copied verbatim
# into the target as kit-tracked files.
_TRACKED_EXCLUSIONS = set(SCAFFOLD_ONCE.keys())


def is_excluded_from_tracked(rel: str) -> bool:
    """True if a payload file is a scaffold-once source (not a verbatim tracked copy)."""
    return rel in _TRACKED_EXCLUSIONS


def classify(rel: str) -> str:
    """Classify a payload-relative path: scaffold-once-source / partial / kit-tracked."""
    if rel in _TRACKED_EXCLUSIONS:
        return "scaffold-once-source"
    if rel in PARTIAL_FILES:
        return "partial"
    return "kit-tracked"


def iter_payload(root: Path):
    """Yield (absolute_path, payload_relative_posix) for every enumerated payload file.

    Only PAYLOAD_DIRS + PAYLOAD_FILES are read; __pycache__ dirs and *.pyc files
    are skipped so build artifacts never leak into adopters.
    """
    root = Path(root)
    for d in PAYLOAD_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for name in files:
                if name.endswith(".pyc"):
                    continue
                full = Path(dirpath) / name
                yield full, full.relative_to(root).as_posix()
    for f in PAYLOAD_FILES:
        full = root / f
        if full.is_file():
            yield full, Path(f).as_posix()
