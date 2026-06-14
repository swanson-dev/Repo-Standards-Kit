import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _adopt(target):
    """init the kit then roll the marker's kit_version back to simulate an older adoption."""
    from standards.init import run_init
    from standards.marker import MARKER_NAME
    run_init(target, profile="library", adopted="2026-05-29")
    marker_path = target / MARKER_NAME
    data = json.loads(marker_path.read_text(encoding="utf-8"))
    data["kit_version"] = "0.5.0"
    marker_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class UpdateTests(unittest.TestCase):
    def test_unchanged_kit_tracked_is_not_a_conflict(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            report = run_update(target)
            self.assertNotIn("docs/STANDARDS.md", report["conflicts"])

    def test_edited_kit_tracked_produces_sidecar_not_overwrite(self):
        from standards.update import run_update
        from standards.__about__ import __version__
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            edited = target / "docs" / "STANDARDS.md"
            edited.write_text("MY LOCAL EDITS\n", encoding="utf-8")
            report = run_update(target)
            self.assertIn("docs/STANDARDS.md", report["conflicts"])
            self.assertEqual(edited.read_text(encoding="utf-8"), "MY LOCAL EDITS\n")
            self.assertTrue((target / f"docs/STANDARDS.md.kit-{__version__}").is_file())

    def test_partial_unedited_block_is_spliced(self):
        from standards.update import run_update
        from standards.managed import find_block
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            agents = target / "AGENTS.md"
            text = agents.read_text(encoding="utf-8")
            agents.write_text(text + "\n## My team notes\nlocal\n", encoding="utf-8")
            report = run_update(target)
            self.assertIn("AGENTS.md", report["spliced"])
            after = agents.read_text(encoding="utf-8")
            self.assertIn("## My team notes", after)
            self.assertIsNotNone(find_block(after))

    def test_partial_edited_block_produces_sidecar(self):
        from standards.update import run_update
        from standards.managed import splice_block
        from standards.__about__ import __version__
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            agents = target / "AGENTS.md"
            agents.write_text(splice_block(agents.read_text(encoding="utf-8"),
                                           "I HACKED THE CONTRACT"), encoding="utf-8")
            report = run_update(target)
            self.assertIn("AGENTS.md", report["conflicts"])
            self.assertTrue((target / f"AGENTS.md.kit-{__version__}").is_file())

    def test_update_reports_removed_discovery_workflow_payload(self):
        from standards.update import run_update
        from standards.marker import MARKER_NAME
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            marker_path = target / MARKER_NAME
            data = json.loads(marker_path.read_text(encoding="utf-8"))
            data["tracked"]["docs/discovery/captured/README.md"] = "old"
            marker_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            report = run_update(target)
            self.assertIn("docs/discovery/captured/README.md", report["removed"])

    def test_scaffold_once_never_touched(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            cs = target / "ai" / "current-state.md"
            cs.write_text("MY STATE\n", encoding="utf-8")
            run_update(target)
            self.assertEqual(cs.read_text(encoding="utf-8"), "MY STATE\n")

    def test_dry_run_writes_nothing(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            edited = target / "docs" / "STANDARDS.md"
            edited.write_text("LOCAL\n", encoding="utf-8")
            before = sorted(p.name for p in target.rglob("*"))
            run_update(target, dry_run=True)
            after = sorted(p.name for p in target.rglob("*"))
            self.assertEqual(before, after)
            self.assertEqual(edited.read_text(encoding="utf-8"), "LOCAL\n")

    def _make_markerless_pre060(self, target):
        """Simulate a 0.5.0 adoption: a partial file was kit-tracked and markerless."""
        from standards.marker import MARKER_NAME, sha256_file
        agents = target / "AGENTS.md"
        agents.write_text("# AGENTS.md\n\nold markerless 0.5.0 contract\n", encoding="utf-8")
        data = json.loads((target / MARKER_NAME).read_text(encoding="utf-8"))
        data["managed"].pop("AGENTS.md", None)
        data["tracked"]["AGENTS.md"] = sha256_file(agents)  # recorded as untouched kit-tracked
        (target / MARKER_NAME).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return agents

    def test_migrates_untouched_markerless_partial_file(self):
        from standards.update import run_update
        from standards.managed import find_block
        from standards.marker import read_marker
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            agents = self._make_markerless_pre060(target)
            report = run_update(target)
            self.assertNotIn("AGENTS.md", report["conflicts"])
            self.assertIn("AGENTS.md", report["updated"])
            self.assertIsNotNone(find_block(agents.read_text(encoding="utf-8")))  # now has markers
            m = read_marker(target)
            self.assertIn("AGENTS.md", m["managed"])
            self.assertNotIn("AGENTS.md", m["tracked"])

    def test_edited_markerless_partial_file_is_a_conflict(self):
        from standards.update import run_update
        from standards.__about__ import __version__
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            _adopt(target)
            self._make_markerless_pre060(target)
            # further hand-edit so it no longer matches the recorded tracked hash
            (target / "AGENTS.md").write_text("# AGENTS.md\n\nUSER HAND-EDITED\n", encoding="utf-8")
            report = run_update(target)
            self.assertIn("AGENTS.md", report["conflicts"])
            self.assertTrue((target / f"AGENTS.md.kit-{__version__}").is_file())
            self.assertIn("USER HAND-EDITED", (target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_no_marker_raises(self):
        from standards.update import run_update
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                run_update(Path(d))


if __name__ == "__main__":
    unittest.main()
