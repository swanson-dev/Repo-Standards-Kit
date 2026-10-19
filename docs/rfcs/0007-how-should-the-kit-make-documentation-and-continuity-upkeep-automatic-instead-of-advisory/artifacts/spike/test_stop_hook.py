"""Checks the spike hook's two branches: `python test_stop_hook.py`."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).with_name("stop_hook.py")


def run(payload, *args):
    return subprocess.run(
        [sys.executable, str(HOOK), *args, "--no-log"],
        input=json.dumps(payload), capture_output=True, text=True,
    )


class StopHookTest(unittest.TestCase):
    def test_blocks_first_stop_with_top_level_fields(self):
        r = run({"hook_event_name": "Stop", "stop_hook_active": False})
        self.assertEqual(r.returncode, 0)
        out = json.loads(r.stdout)
        self.assertEqual(out["decision"], "block")
        self.assertIn("SPIKE-ACK top-level Stop", out["reason"])
        self.assertNotIn("hookSpecificOutput", out)

    def test_allows_second_stop_silently(self):
        r = run({"stop_hook_active": True})
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_wrapped_variant_emits_both_shapes(self):
        r = run({"hookEventName": "agentStop", "stop_hook_active": False}, "--wrapped")
        out = json.loads(r.stdout)
        self.assertEqual(out["decision"], "block")
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "Stop")
        self.assertEqual(out["hookSpecificOutput"]["decision"], "block")
        self.assertEqual(out["hookSpecificOutput"]["reason"], out["reason"])
        self.assertIn("SPIKE-ACK wrapped agentStop", out["reason"])

    def test_empty_stdin_still_blocks(self):
        r = subprocess.run([sys.executable, str(HOOK), "--no-log"], input="", capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout)["decision"], "block")


if __name__ == "__main__":
    unittest.main()
