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
    "scripts/changelog",
    "scripts/drift",
    "scripts/session-context",
    "scripts/standards-check",
    "scripts/update-handoff",
    ".github/prompts",
    # Not all of .claude: it also holds machine-local files (settings.local.json,
    # worktrees/) that must never reach adopters.
    ".claude/skills",
)

# Individual payload files (relative to payload root).
PAYLOAD_FILES: tuple[str, ...] = (
    "docs/STANDARDS.md",
    ".github/workflows/repo-standards.yml",
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".claude/settings.json",
    ".github/hooks/standards.json",
)

# Agent hosts a repo's team uses (`agents` in the marker) and the one hook file it
# gets. Every Copilot host also reads Claude's file (RFC-0007 test B2), so a repo
# that uses Claude gets only that; shipping both would run every hook twice.
AGENTS: tuple[str, ...] = ("claude", "copilot")
CLAUDE_HOOKS = ".claude/settings.json"
COPILOT_HOOKS = ".github/hooks/standards.json"

# Payload files whose source sits at another path in the kit's own repo (target ->
# source). The kit uses Claude, so a live .github/hooks/ here would run twice too.
PAYLOAD_SOURCES: dict[str, str] = {COPILOT_HOOKS: "docs/templates/copilot-hooks.json"}

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
    "docs/templates/repo-readme-template.md": "README.md",
    "docs/templates/changelog-template.md": "CHANGELOG.md",
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
_TRACKED_EXCLUSIONS = set(SCAFFOLD_ONCE.keys()) | set(PAYLOAD_SOURCES.values())


def is_excluded_from_tracked(rel: str) -> bool:
    """True if a payload file is a source for another path (not a verbatim tracked copy)."""
    return rel in _TRACKED_EXCLUSIONS


def recorded_agents(value: object) -> list[str] | None:
    """A marker's `agents` if it is a non-empty list of known agents, else None."""
    if isinstance(value, list) and value and all(a in AGENTS for a in value):
        return value
    return None


def hook_file(agents) -> str:
    """The one hook config file a repo with these agents gets."""
    return CLAUDE_HOOKS if "claude" in agents else COPILOT_HOOKS


def unused_hook_file(agents) -> str:
    return COPILOT_HOOKS if hook_file(agents) == CLAUDE_HOOKS else CLAUDE_HOOKS


def classify(rel: str) -> str:
    """Classify a payload-relative path: scaffold-once-source / partial / kit-tracked."""
    if rel in _TRACKED_EXCLUSIONS:
        return "scaffold-once-source"
    if rel in PARTIAL_FILES:
        return "partial"
    return "kit-tracked"


def iter_payload(root: Path, agents=None):
    """Yield (absolute_path, payload_relative_posix) for every enumerated payload file.

    Only PAYLOAD_DIRS + PAYLOAD_FILES are read; __pycache__ dirs and *.pyc files
    are skipped so build artifacts never leak into adopters. With `agents`, only
    that repo's hook file is yielded; without, every payload file is.
    """
    root = Path(root)
    skip = set() if agents is None else {unused_hook_file(agents)}
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
                rel = full.relative_to(root).as_posix()
                if rel not in skip:
                    yield full, rel
    for f in PAYLOAD_FILES:
        full = root / PAYLOAD_SOURCES.get(f, f)
        if full.is_file() and f not in skip:
            yield full, Path(f).as_posix()
