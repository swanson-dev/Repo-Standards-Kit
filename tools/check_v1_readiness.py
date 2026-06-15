#!/usr/bin/env python3
"""Validate the kit's v1.0 downstream-readiness gate.

The gate creates generated downstream repos for every supported profile and
proves the public adoption path stays clean through init, check, update, check.
"""
from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "standards-check"))

from standards.init import run_init  # noqa: E402
from standards.update import run_update  # noqa: E402
import check as check_mod  # noqa: E402

PROFILES = ("application", "library", "infra", "data")

CHANGELOG_STUB = (
    "# Changelog\n\n"
    "All notable changes to this project are documented here.\n\n"
    "## [0.1.0] - 2026-06-01\n\n"
    "### Added\n"
    "- Initial adoption of the Repo-Standards-Kit.\n"
)


@dataclass
class ProfileResult:
    profile: str
    ok: bool
    details: list[str]


def _seed_downstream_repo(target: Path) -> None:
    """Seed files every realistic downstream repo is expected to own already."""
    (target / "README.md").write_text("# Test repo\n", encoding="utf-8")
    (target / "CHANGELOG.md").write_text(CHANGELOG_STUB, encoding="utf-8")


def _finding_details(target: Path) -> list[str]:
    ctx = check_mod.build_context(target)
    findings = check_mod.run_checks(target, ctx)
    return [
        f"{f.severity.upper()} [{f.check_id}] {f.message}"
        for f in findings
    ]


def validate_profile(profile: str, root: Path) -> ProfileResult:
    target = root / profile
    target.mkdir(parents=True)
    _seed_downstream_repo(target)

    run_init(target, profile=profile, adopted=date.today().isoformat())
    after_init = _finding_details(target)
    if after_init:
        return ProfileResult(profile, False, ["after init:", *after_init])

    report = run_update(target)
    if report["conflicts"] or report["removed"]:
        details = []
        for key in ("conflicts", "removed"):
            if report[key]:
                details.append(f"update {key}: {', '.join(report[key])}")
        return ProfileResult(profile, False, details)

    after_update = _finding_details(target)
    if after_update:
        return ProfileResult(profile, False, ["after update:", *after_update])

    return ProfileResult(profile, True, [])


def validate_all(root: Path) -> list[ProfileResult]:
    return [validate_profile(profile, root) for profile in PROFILES]


def main(argv: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="repo-standards-v1-") as tmp:
        results = validate_all(Path(tmp))

    failed = [result for result in results if not result.ok]
    for result in results:
        if result.ok:
            print(f"{result.profile}: init/check/update OK")
        else:
            print(f"{result.profile}: FAIL")
            for detail in result.details:
                print(f"  {detail}")

    if failed:
        print("V1 readiness: FAIL")
        return 1
    print("V1 readiness: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
