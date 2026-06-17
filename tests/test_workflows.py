from __future__ import annotations

import json
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

    def test_claude_hooks_include_read_only_session_start_and_stop_check(self):
        data = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        hooks = data["hooks"]
        session_start = hooks["SessionStart"][0]["hooks"][0]["command"]
        stop = [hook["command"] for hook in hooks["Stop"][0]["hooks"]]

        self.assertEqual(session_start, "python scripts/session-context/session_context.py --hook")
        self.assertIn("python scripts/update-handoff/update_handoff.py --check", stop)
        self.assertIn("python scripts/changelog/check_changelog.py --check", stop)
        self.assertNotIn("compact-snapshot", session_start)
        self.assertNotIn("--force", session_start)


if __name__ == "__main__":
    unittest.main()
