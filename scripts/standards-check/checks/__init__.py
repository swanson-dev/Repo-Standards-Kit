"""standards-check check modules: shared types + severity resolution.

Each check module exposes `run(root, ctx) -> list[Finding]`. The orchestrator
(check.py) builds one Context, runs every module, and exits 1 iff any error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# "error" | "warn" | "info" - kept as plain str for 3.9 friendliness.
Severity = str


@dataclass(frozen=True)
class Finding:
    """A single diagnostic result produced by a check module."""
    check_id: str
    severity: Severity
    message: str


@dataclass
class Context:
    """Resolved run context shared by all checks."""
    root: Path
    adopter_mode: bool                    # True iff .standards-kit.json present at root
    overrides: dict[str, Severity] = field(default_factory=dict)
    external_links: bool = False          # Opt-in networked liveness check.
    freshness_report: bool = False        # Opt-in ai/ freshness status output.


def resolve_severity(check_id: str, default: Severity, ctx: Context) -> Severity:
    """Severity for a NEW content-check finding.

    Kit mode (not adopter): the default (error). Adopter mode: warn, unless the
    adopter's marker escalates this check_id to error. v1 structural checks do
    NOT call this — they emit their fixed historical severities directly.
    """
    if not ctx.adopter_mode:
        return default
    return ctx.overrides.get(check_id, "warn")
