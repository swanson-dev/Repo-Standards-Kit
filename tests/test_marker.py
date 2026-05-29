import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class MarkerTests(unittest.TestCase):
    def test_sha256_file_is_stable(self):
        from standards.marker import sha256_file
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.txt"
            p.write_bytes(b"hello\n")  # binary write: LF-only, platform-neutral on Windows
            self.assertEqual(
                sha256_file(p),
                "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03",
            )

    def test_write_then_read_round_trip(self):
        from standards.marker import read_marker, write_marker
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_marker(root, kit_version="0.5.0", profile="library",
                         adopted="2026-05-29",
                         tracked={"docs/STANDARDS.md": "abc"})
            data = read_marker(root)
            self.assertEqual(data["kit_version"], "0.5.0")
            self.assertEqual(data["profile"], "library")
            self.assertEqual(data["tracked"], {"docs/STANDARDS.md": "abc"})
            self.assertEqual(data["managed"], {})

    def test_read_missing_returns_none(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(read_marker(Path(d)))


if __name__ == "__main__":
    unittest.main()
