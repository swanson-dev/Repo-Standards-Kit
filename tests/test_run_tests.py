import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from run_tests import discover, run  # noqa: E402

_PASS = ("import unittest\n"
         "class T(unittest.TestCase):\n"
         "    def test_a(self):\n"
         "        self.assertTrue(True)\n"
         "if __name__ == '__main__':\n"
         "    unittest.main()\n")
_FAIL = _PASS.replace("self.assertTrue(True)", "self.assertTrue(False)")


class RunTestsTests(unittest.TestCase):
    def _write(self, d, name, body):
        p = Path(d) / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_all_passing_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            ok = self._write(d, "test_ok.py", _PASS)
            self.assertEqual(run([ok]), 0)

    def test_a_failing_suite_exits_one(self):
        with tempfile.TemporaryDirectory() as d:
            ok = self._write(d, "test_ok.py", _PASS)
            bad = self._write(d, "test_bad.py", _FAIL)
            self.assertEqual(run([ok, bad]), 1)

    def test_discover_finds_repo_suites(self):
        root = Path(__file__).resolve().parents[1]
        names = {p.name for p in discover(root)}
        self.assertIn("test_update.py", names)
        self.assertIn("test_check.py", names)
        self.assertIn("test_promote_discovery.py", names)


if __name__ == "__main__":
    unittest.main()
