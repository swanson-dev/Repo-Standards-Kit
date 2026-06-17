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
        for profile in ("application", "library", "infra", "data", "documentation"):
            self.assertIn(f"{profile}: init/check/update OK", res.stdout)
        self.assertIn("V1 readiness: OK", res.stdout)

    def test_profile_failure_includes_check_findings(self):
        original = check_v1_readiness.run_init

        def init_without_changelog(target: Path, **kwargs):
            marker = original(target, **kwargs)
            (target / "CHANGELOG.md").unlink()
            return marker

        with tempfile.TemporaryDirectory() as d:
            try:
                check_v1_readiness.run_init = init_without_changelog
                result = check_v1_readiness.validate_profile("library", Path(d))
            finally:
                check_v1_readiness.run_init = original

        self.assertFalse(result.ok)
        details = "\n".join(result.details)
        self.assertIn("after init", details)
        self.assertIn("CHANGELOG.md", details)


if __name__ == "__main__":
    unittest.main()
