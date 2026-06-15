from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_release_workflow_runs_v1_readiness_gate(self):
        text = (REPO / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python tools/check_v1_readiness.py", text)

    def test_external_links_workflow_is_manual_only(self):
        text = (REPO / ".github" / "workflows" / "external-links.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("python scripts/standards-check/check.py --external-links", text)


if __name__ == "__main__":
    unittest.main()
