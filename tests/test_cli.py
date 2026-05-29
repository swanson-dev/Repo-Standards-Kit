import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def _run(self, *args, cwd):
        full_env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
        return subprocess.run(
            [sys.executable, "-m", "standards.cli", *args],
            cwd=str(cwd), capture_output=True, text=True, env=full_env,
        )

    def test_init_subcommand_creates_repo(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            result = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".standards-kit.json").is_file())
            self.assertTrue((target / "docs" / "STANDARDS.md").is_file())

    def test_rejects_unknown_profile(self):
        with tempfile.TemporaryDirectory() as d:
            result = self._run("init", "--profile", "bogus", d, cwd=REPO)
            self.assertNotEqual(result.returncode, 0)

    def test_update_after_init(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            res = self._run("update", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("unchanged", (res.stdout + res.stderr).lower())

    def test_update_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            self._run("init", "--profile", "library", str(target), cwd=REPO)
            (target / "docs" / "STANDARDS.md").write_text("LOCAL\n", encoding="utf-8")
            before = sorted(p.name for p in target.rglob("*"))
            res = self._run("update", "--dry-run", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(before, sorted(p.name for p in target.rglob("*")))

    def test_update_without_marker_errors(self):
        with tempfile.TemporaryDirectory() as d:
            res = self._run("update", d, cwd=REPO)
            self.assertNotEqual(res.returncode, 0)


if __name__ == "__main__":
    unittest.main()
