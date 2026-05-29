import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class PayloadTests(unittest.TestCase):
    def test_payload_root_contains_known_files(self):
        from standards.payload import payload_root
        root = payload_root()
        self.assertTrue((root / "docs" / "templates" / "adr-template.md").is_file())
        self.assertTrue((root / "docs" / "STANDARDS.md").is_file())
        self.assertTrue((root / "scripts" / "standards-check" / "check.py").is_file())


if __name__ == "__main__":
    unittest.main()
