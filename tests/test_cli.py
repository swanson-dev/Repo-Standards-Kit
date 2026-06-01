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

    def test_adopt_subcommand_is_nondestructive(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("MINE\n", encoding="utf-8")
            res = self._run("adopt", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual((target / "docs" / "STANDARDS.md").read_text(encoding="utf-8"), "MINE\n")
            self.assertTrue((target / ".standards-kit.json").is_file())
            self.assertIn("conflicts", (res.stdout + res.stderr).lower())

    def test_check_clean_repo_exits_zero(self):
        # The kit repo itself is self-clean (0 errors); `standards check` on it passes.
        res = self._run("check", str(REPO), cwd=REPO)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("standards check", (res.stdout + res.stderr).lower())

    def test_check_reports_violations_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            init = self._run("init", "--profile", "library", str(target), cwd=REPO)
            self.assertEqual(init.returncode, 0, init.stderr)
            # Remove a universal-core file -> structural check must error -> exit 1.
            (target / "AGENTS.md").unlink()
            res = self._run("check", str(target), cwd=REPO)
            self.assertEqual(res.returncode, 1, res.stdout + res.stderr)


if __name__ == "__main__":
    unittest.main()
