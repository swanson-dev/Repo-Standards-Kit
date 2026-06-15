"""Behavioral test for the ai/ freshness thresholds in structural checks."""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks.structural import Report, check_ai_freshness  # noqa: E402


def _write_ai(
    root: Path,
    handoff_days_old: int,
    state_days_old: int,
    next_actions_days_old: int | None = None,
) -> None:
    ai = root / "ai"
    ai.mkdir(parents=True, exist_ok=True)
    h = (date.today() - timedelta(days=handoff_days_old)).isoformat()
    s = (date.today() - timedelta(days=state_days_old)).isoformat()
    n = (date.today() - timedelta(days=next_actions_days_old or state_days_old)).isoformat()
    (ai / "handoff.md").write_text(f"---\nwritten: {h}\n---\n", encoding="utf-8")
    (ai / "current-state.md").write_text(f"---\nlast_updated: {s}\n---\n", encoding="utf-8")
    (ai / "next-actions.md").write_text(f"---\nlast_updated: {n}\n---\n", encoding="utf-8")


class FreshnessThresholdTests(unittest.TestCase):
    def test_handoff_warns_at_6_days(self):
        # 6 days exceeds the new 5-day handoff threshold; 6 is under the 14-day
        # current-state threshold, so only the handoff warns.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ai(root, handoff_days_old=6, state_days_old=6)
            report = Report()
            check_ai_freshness(root, report)
            handoff_warns = [w for w in report.warnings if "handoff" in w]
            state_warns = [w for w in report.warnings if "current-state" in w]
            self.assertEqual(len(handoff_warns), 1, report.warnings)
            self.assertEqual(len(state_warns), 0, report.warnings)

    def test_fresh_handoff_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ai(root, handoff_days_old=1, state_days_old=1)
            report = Report()
            check_ai_freshness(root, report)
            self.assertEqual(report.warnings, [])

    def test_next_actions_warns_when_stale(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ai(root, handoff_days_old=1, state_days_old=1, next_actions_days_old=15)
            report = Report()
            check_ai_freshness(root, report)
            self.assertEqual(len(report.warnings), 1, report.warnings)
            warning = report.warnings[0]
            self.assertIn("ai/next-actions.md", warning)
            self.assertIn("age 15 day(s)", warning)
            self.assertIn("threshold 14 day(s)", warning)
            self.assertIn("Refresh `ai/next-actions.md`", warning)

    def test_freshness_report_includes_all_ai_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ai(root, handoff_days_old=1, state_days_old=2, next_actions_days_old=3)
            report = Report()
            check_ai_freshness(root, report, include_report=True)
            self.assertEqual(report.warnings, [])
            self.assertEqual(len(report.infos), 3, report.infos)
            joined = "\n".join(report.infos)
            for expected in ("ai/current-state.md", "ai/next-actions.md", "ai/handoff.md"):
                self.assertIn(expected, joined)
            self.assertIn("fresh", joined)


if __name__ == "__main__":
    unittest.main()
