import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class InitTests(unittest.TestCase):
    def _run(self, target, **kw):
        from standards.init import run_init
        return run_init(target, **kw)

    def test_copies_tracked_and_writes_marker(self):
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="library", adopted="2026-05-29")
            self.assertTrue((target / "docs" / "templates" / "adr-template.md").is_file())
            self.assertTrue((target / "docs" / "STANDARDS.md").is_file())
            marker = read_marker(target)
            self.assertEqual(marker["profile"], "library")
            self.assertIn("docs/STANDARDS.md", marker["tracked"])
            self.assertTrue((target / "ai" / "current-state.md").is_file())
            from standards.marker import sha256_file
            self.assertEqual(
                marker["tracked"]["docs/STANDARDS.md"],
                sha256_file(target / "docs" / "STANDARDS.md"),
            )

    def test_scaffold_once_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "ai").mkdir()
            (target / "ai" / "current-state.md").write_text("MINE\n", encoding="utf-8")
            self._run(target, profile="application", adopted="2026-05-29")
            self.assertEqual(
                (target / "ai" / "current-state.md").read_text(encoding="utf-8"), "MINE\n"
            )

    def test_profile_written_into_checklist(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="infra", adopted="2026-05-29")
            checklist = (target / "docs" / "STANDARDS-CHECKLIST.md").read_text(encoding="utf-8")
            self.assertIn("infra", checklist)

    def test_refuses_reinit_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run(target, profile="data", adopted="2026-05-29")
            with self.assertRaises(FileExistsError):
                self._run(target, profile="data", adopted="2026-05-29")
            self._run(target, profile="data", adopted="2026-05-29", force=True)


if __name__ == "__main__":
    unittest.main()
