"""Tests for the read-only session context summary script."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "session-context" / "session_context.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_context(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(root),
        capture_output=True,
        text=True,
    )


class SessionContextTests(unittest.TestCase):
    def test_fresh_ai_files_produce_context_brief(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            today = date.today().isoformat()
            write(
                root / "ai" / "handoff.md",
                f"---\nwritten: {today}T09:00:00-05:00\nwritten_by: test\nfor: next-session\n---\n\n"
                "# Handoff\n\n## TL;DR\n\nBuilt adoption assistant.\n\n## Open threads\n\n- Pilot doctor.\n",
            )
            write(
                root / "ai" / "current-state.md",
                f"---\nlast_updated: {today}\nlast_updated_by: test\n---\n\n"
                "# Current State\n\n## What's in progress\n\n| Feature | Branch | Owner | Target |\n|---|---|---|---|\n| AI continuity | main | codex | v1.1 |\n\n"
                "## What's blocked\n\n- Nothing blocked.\n",
            )
            write(root / "ai" / "next-actions.md", f"---\nlast_updated: {today}\n---\n\n# Next Actions\n\n1. **Pilot context hook** - Try it.\n")
            write(root / "ai" / "open-questions.md", "# Open Questions\n\n## Q-4: Should hooks be advisory?\n\n- **Status:** open\n")

            result = run_context(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Session Context", result.stdout)
            self.assertIn("Built adoption assistant.", result.stdout)
            self.assertIn("AI continuity", result.stdout)
            self.assertIn("Pilot context hook", result.stdout)
            self.assertIn("Q-4: Should hooks be advisory?", result.stdout)

    def test_missing_files_warn_but_exit_zero(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_context(Path(d), "--hook")

            self.assertEqual(result.returncode, 0)
            self.assertIn("WARN", result.stdout)
            self.assertIn("ai/handoff.md missing", result.stdout)

    def test_stale_handoff_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stale = (date.today() - timedelta(days=10)).isoformat()
            write(root / "ai" / "handoff.md", f"---\nwritten: {stale}T00:00:00-05:00\n---\n\n# Handoff\n\n## TL;DR\n\nOld.\n")

            result = run_context(root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("handoff is stale", result.stdout.lower())

    def test_hook_mode_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))

            result = run_context(root, "--hook")

            after = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
