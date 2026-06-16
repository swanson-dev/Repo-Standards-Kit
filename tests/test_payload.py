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

    def test_optional_lane_templates_are_payload(self):
        from standards.payload import payload_root
        root = payload_root()
        for name in (
            "discovery-note-template.md",
            "discovery-meeting-template.md",
            "discovery-artifact-template.md",
            "design-template.md",
            "incident-template.md",
            "troubleshooting-template.md",
            "guide-template.md",
        ):
            self.assertTrue((root / "docs" / "templates" / name).is_file(), name)

    def test_artifact_template_is_pointer_first(self):
        from standards.payload import payload_root
        body = (
            payload_root()
            / "docs"
            / "templates"
            / "discovery-artifact-template.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "Source:",
            "Owner:",
            "External location:",
            "Sensitivity:",
            "Retention note:",
            "Follow-ups",
        ):
            self.assertIn(expected, body)
        self.assertIn("Do not commit raw binary artifacts by default", body)


if __name__ == "__main__":
    unittest.main()
