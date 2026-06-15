from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import check_v1_readiness  # noqa: E402


class V1ReadinessTests(unittest.TestCase):
    def test_gate_validates_all_profiles_through_init_check_update(self):
        res = subprocess.run(
            [sys.executable, str(REPO / "tools" / "check_v1_readiness.py")],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        for profile in ("application", "library", "infra", "data"):
            self.assertIn(f"{profile}: init/check/update OK", res.stdout)
        self.assertIn("V1 readiness: OK", res.stdout)

    def test_profile_failure_includes_check_findings(self):
        original = check_v1_readiness._seed_downstream_repo

        def missing_changelog(target: Path) -> None:
            original(target)
            (target / "CHANGELOG.md").unlink()

        with tempfile.TemporaryDirectory() as d:
            try:
                check_v1_readiness._seed_downstream_repo = missing_changelog
                result = check_v1_readiness.validate_profile("library", Path(d))
            finally:
                check_v1_readiness._seed_downstream_repo = original

        self.assertFalse(result.ok)
        details = "\n".join(result.details)
        self.assertIn("after init", details)
        self.assertIn("CHANGELOG.md", details)


if __name__ == "__main__":
    unittest.main()
