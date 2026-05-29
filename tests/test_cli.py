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


if __name__ == "__main__":
    unittest.main()
