"""Read-only diagnostics for adopted Repo-Standards-Kit repositories."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

from standards.__about__ import __version__
from standards.managed import block_hash
from standards.marker import MARKER_NAME
from standards.payload import payload_root

CheckRunner = Callable[[Path], subprocess.CompletedProcess]


PARTIAL_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_marker(root: Path) -> tuple[dict | None, str | None]:
    marker_path = root / MARKER_NAME
    if not marker_path.is_file():
        return None, None
    try:
        return json.loads(marker_path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, f"{MARKER_NAME} could not be read: {exc}"


def _run_standards_check(root: Path) -> subprocess.CompletedProcess:
    check_py = payload_root() / "scripts" / "standards-check" / "check.py"
    return subprocess.run(
        [sys.executable, str(check_py), str(root)],
        capture_output=True,
        text=True,
    )


def _check_lines(result: subprocess.CompletedProcess) -> list[str]:
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    lines.extend(line for line in result.stderr.splitlines() if line.strip())
    return lines


def _sidecars(root: Path) -> list[str]:
    return sorted(
        _rel(path, root)
        for path in root.rglob("*.kit-*")
        if path.is_file()
    )


def _managed_drift(root: Path, marker: dict) -> list[str]:
    managed = marker.get("managed", {})
    if not isinstance(managed, dict):
        return ["marker managed table is not an object"]

    drift: list[str] = []
    for rel in PARTIAL_FILES:
        expected = managed.get(rel)
        path = root / rel
        if expected is None:
            drift.append(f"{rel} missing from marker managed table")
            continue
        if not path.is_file():
            drift.append(f"{rel} missing")
            continue
        current = block_hash(path.read_text(encoding="utf-8", errors="replace"))
        if current is None:
            drift.append(f"{rel} has no valid managed block")
        elif current != expected:
            drift.append(f"{rel} managed block hash changed")
    return drift


def _recommendations(root: Path, marker: dict | None) -> list[str]:
    profile = marker.get("profile") if marker else None
    recs: list[str] = []

    discovery = root / "docs" / "discovery"
    if discovery.exists():
        if not (discovery / "meetings").exists():
            recs.append(
                "Consider docs/discovery/meetings for recurring stakeholder or customer conversations."
            )
        if not (discovery / "notes").exists():
            recs.append(
                "Consider docs/discovery/notes for lightweight research and reconnaissance notes."
            )
        if not (discovery / "artifacts").exists():
            recs.append(
                "Consider docs/discovery/artifacts for markdown indexes that point to external files."
            )

    if not (root / "docs" / "design").exists():
        design_signal = (root / "docs" / "01-prd.md").exists() or profile == "application"
        if design_signal:
            recs.append("Consider docs/design for product, UX, or system design notes.")

    support_signal = (
        profile in {"application", "infra", "data"}
        or (root / "docs" / "06-runbook.md").exists()
        or (root / "docs" / "09-deployment.md").exists()
    )
    if support_signal:
        if not (root / "support" / "incidents").exists():
            recs.append("Consider support/incidents for operational incident notes.")
        if not (root / "support" / "troubleshooting").exists():
            recs.append("Consider support/troubleshooting for recurring failure modes.")
        if not (root / "support" / "guides").exists():
            recs.append("Consider support/guides for user, admin, or operator guides.")

    return recs


def doctor_lines(
    target: Path,
    *,
    recommend: bool = False,
    check_runner: CheckRunner | None = None,
) -> tuple[int, list[str]]:
    """Return (exit_code, output_lines) for a read-only doctor run."""
    root = Path(target).resolve()
    marker, marker_error = _read_marker(root)
    lines: list[str] = [f"Target: {root}"]
    issues = 0

    if marker_error:
        lines.insert(0, "Doctor: issues found")
        lines.append(f"Adoption: invalid marker - {marker_error}")
        return 1, lines

    if marker is None:
        lines.insert(0, "Doctor: issues found")
        lines.append("Adoption: not adopted")
        lines.append("Next: run `standards init --profile <profile> <target>` for a new repo.")
        lines.append("Next: run `standards adopt --profile <profile> <target>` for an existing repo.")
        return 1, lines

    profile = marker.get("profile", "unknown")
    kit_version = marker.get("kit_version", "unknown")
    lines.append(f"Adoption: adopted profile={profile} kit_version={kit_version}")
    if kit_version != __version__:
        lines.append(f"Version: installed CLI is {__version__}; marker records {kit_version}")

    runner = check_runner or _run_standards_check
    check = runner(root)
    check_status = "passing" if check.returncode == 0 else "failing"
    lines.append(f"Standards check: {check_status}")
    check_details = _check_lines(check)
    for detail in check_details:
        if detail.startswith("  ERROR") or detail.startswith("  WARN"):
            lines.append(detail)
    if check.returncode != 0:
        issues += 1

    sidecars = _sidecars(root)
    if sidecars:
        issues += 1
        lines.append("Sidecar conflicts:")
        lines.extend(f"  {path}" for path in sidecars)

    drift = _managed_drift(root, marker)
    if drift:
        issues += 1
        lines.append("Managed region drift:")
        lines.extend(f"  {item}" for item in drift)

    if recommend:
        recs = _recommendations(root, marker)
        lines.append("Recommendations:")
        if recs:
            lines.extend(f"  {rec}" for rec in recs)
        else:
            lines.append("  No optional lane recommendations right now.")

    if issues:
        lines.insert(0, "Doctor: issues found")
        lines.append("Next: run `standards check <target>` after resolving issues.")
        return 1, lines

    lines.insert(0, "Doctor: healthy")
    lines.append("Next: run `standards update --dry-run <target>` before upgrading the kit.")
    return 0, lines
