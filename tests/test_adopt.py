"""`standards adopt` — non-destructive adoption onto an existing repo (RFC-0002)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts" / "standards-check"))

from standards.__about__ import __version__  # noqa: E402
from standards.init import run_adopt  # noqa: E402
from standards.managed import find_block  # noqa: E402
from standards.marker import read_marker  # noqa: E402

CHANGELOG_STUB = (
    "# Changelog\n\n## [0.1.0] - 2026-06-01\n\n### Added\n- Initial.\n"
)


def _seed_repo(target: Path) -> None:
    (target / "README.md").write_text("# Existing repo\n", encoding="utf-8")
    (target / "CHANGELOG.md").write_text(CHANGELOG_STUB, encoding="utf-8")


class AdoptTests(unittest.TestCase):
    def test_adopt_blank_repo_is_check_clean(self):
        import check as check_mod
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _seed_repo(target)
            run_adopt(target, profile="library", adopted=date.today().isoformat())
            ctx = check_mod.build_context(target)
            findings = check_mod.run_checks(target, ctx)
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(errors, [], "; ".join(f.message for f in errors))

    def test_adopt_preserves_conflicting_tracked_file(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _seed_repo(target)
            (target / "docs").mkdir()
            (target / "docs" / "STANDARDS.md").write_text("MINE\n", encoding="utf-8")
            report = run_adopt(target, profile="library", adopted="2026-06-01")
            # Their file is untouched; the kit copy lands as a sidecar.
            self.assertEqual((target / "docs" / "STANDARDS.md").read_text(encoding="utf-8"), "MINE\n")
            self.assertTrue((target / f"docs/STANDARDS.md.kit-{__version__}").is_file())
            self.assertIn("docs/STANDARDS.md", report["conflicts"])
            self.assertIsNotNone(read_marker(target))

    def test_adopt_appends_block_to_blockless_agents(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _seed_repo(target)
            (target / "AGENTS.md").write_text("# My agents\n\nlocal rules\n", encoding="utf-8")
            report = run_adopt(target, profile="library", adopted="2026-06-01")
            after = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("local rules", after)              # their content preserved
            self.assertIsNotNone(find_block(after))           # kit block now present
            self.assertIn("AGENTS.md", report["spliced"])
            self.assertIn("AGENTS.md", read_marker(target)["managed"])

    def test_adopt_scaffolds_discovery_intake_structure(self):
        # ADR-0014: adopt seeds the same discovery scaffold as init (scaffold-once).
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _seed_repo(target)
            report = run_adopt(target, profile="library", adopted="2026-06-01")
            disc = target / "docs" / "discovery"
            self.assertTrue((disc / "captured" / "README.md").is_file())
            self.assertTrue((disc / "notes" / ".gitkeep").is_file())
            self.assertTrue((disc / ".gitignore").is_file())
            self.assertIn("docs/discovery/.gitignore", report["scaffolded"])

    def test_adopt_refuses_if_already_adopted(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _seed_repo(target)
            run_adopt(target, profile="library", adopted="2026-06-01")
            with self.assertRaises(FileExistsError):
                run_adopt(target, profile="library", adopted="2026-06-01")

    def test_adopt_then_update_is_nonconflicting_for_seeded_files(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _seed_repo(target)
            run_adopt(target, profile="library", adopted="2026-06-01")
            rep = run_update(target)
            # Files the kit wrote during adopt must reconcile cleanly (no new sidecars).
            self.assertEqual(rep["conflicts"], [], rep["conflicts"])


if __name__ == "__main__":
    unittest.main()
