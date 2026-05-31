"""Version sanity: semver shape + cross-file coherence (no hardcoded literal)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from standards.__about__ import __version__  # noqa: E402
from check_version_coherence import find_incoherences  # noqa: E402


class VersionTests(unittest.TestCase):
    def test_version_is_semver_string(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")

    def test_kit_version_is_coherent(self):
        # __about__ must agree with CHANGELOG top, AGENTS.md Kit-version + sentinel.
        self.assertEqual(find_incoherences(REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
