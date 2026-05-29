import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class VersionTests(unittest.TestCase):
    def test_version_is_semver_string(self):
        from standards.__about__ import __version__
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
        self.assertEqual(__version__, "0.5.0")


if __name__ == "__main__":
    unittest.main()
