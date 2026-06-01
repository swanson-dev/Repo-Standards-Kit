"""Dogfooding gate: `standards init --profile X` must yield an error-clean repo.

For every profile, scaffold into a temp dir (seeding the README/CHANGELOG a real
repo always supplies) and assert the standards check reports zero ERROR findings.
This exercises all four profiles end-to-end, not just the `library` profile the
kit self-applies.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts" / "standards-check"))

from standards.init import run_init  # noqa: E402
import check as check_mod  # noqa: E402

PROFILES = ("application", "library", "infra", "data")

CHANGELOG_STUB = (
    "# Changelog\n\n"
    "All notable changes to this project are documented here.\n\n"
    "## [0.1.0] - 2026-06-01\n\n"
    "### Added\n"
    "- Initial adoption of the Repo-Standards-Kit.\n"
)


class ProfileScaffoldTests(unittest.TestCase):
    def _findings_for(self, profile: str):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            # Adopter-supplied minimum that every real repo already has.
            (target / "README.md").write_text("# Test repo\n", encoding="utf-8")
            (target / "CHANGELOG.md").write_text(CHANGELOG_STUB, encoding="utf-8")
            # Adopt "today" so the ai/ freshness assertion stays robust over time.
            run_init(target, profile=profile, adopted=date.today().isoformat())
            ctx = check_mod.build_context(target)
            return check_mod.run_checks(target, ctx)

    def test_each_profile_scaffolds_clean(self):
        # `standards init --profile X` must yield a repo that passes the standards
        # check with zero errors AND zero warnings, for every profile.
        for profile in PROFILES:
            with self.subTest(profile=profile):
                findings = self._findings_for(profile)
                detail = "; ".join(
                    f"{f.severity.upper()} [{f.check_id}] {f.message}" for f in findings
                )
                self.assertEqual(findings, [], f"{profile}: {detail}")


if __name__ == "__main__":
    unittest.main()
