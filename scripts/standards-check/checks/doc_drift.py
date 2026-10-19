"""CI drift check (ADR-0023): flag a pull request whose changes left a doc behind.

Opt in with `--drift-base REF`, the PR's target branch (for example
`origin/main`). Only the PR's own commits count, so drift already on the base
branch isn't blamed on the PR. A `Docs-Unaffected:` commit trailer waives that
commit; the same line in the PR description, passed in the `STANDARDS_PR_BODY`
environment variable, waives the doc for the whole PR. If history can't be read,
for example in a shallow clone, that is always an error: an opted-in check that
can't run is a broken setup, and must not pass quietly as a warning.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from . import Context, Finding, resolve_severity

CHECK_ID = "drift"
DEFAULT_SEVERITY = "error"
ENGINE_DIR = Path(__file__).resolve().parents[2] / "drift"


def run(root: Path, ctx: Context) -> list[Finding]:
    if not ctx.drift_base:
        return []
    sys.path.insert(0, str(ENGINE_DIR))
    import drift as engine  # imported only when opted in, so other checks never depend on it

    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    waivers = engine.WAIVER_RE.findall(os.environ.get("STANDARDS_PR_BODY", ""))
    try:
        found = engine.find_drift(root, waivers=waivers, base=ctx.drift_base)
    except engine.DriftError as exc:
        return [Finding(CHECK_ID, "error", f"can't check drift against {ctx.drift_base}: {exc}")]
    return [Finding(CHECK_ID, severity, f"{doc} is behind this PR's changes: " + "; ".join(reasons))
            for doc, reasons in found.items()]
