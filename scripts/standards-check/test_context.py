"""Tests for check.build_context: kit vs adopter detection + override parsing."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check import build_context  # noqa: E402


class BuildContextTests(unittest.TestCase):
    def test_no_marker_is_kit_mode(self):
        with tempfile.TemporaryDirectory() as d:
            ctx = build_context(Path(d))
            self.assertFalse(ctx.adopter_mode)
            self.assertEqual(ctx.overrides, {})

    def test_marker_present_is_adopter_mode(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".standards-kit.json").write_text("{}", encoding="utf-8")
            ctx = build_context(Path(d))
            self.assertTrue(ctx.adopter_mode)

    def test_override_map_parsed(self):
        with tempfile.TemporaryDirectory() as d:
            marker = {"check": {"links": "error", "placeholder": "warn", "bogus": "loud"}}
            (Path(d) / ".standards-kit.json").write_text(json.dumps(marker), encoding="utf-8")
            ctx = build_context(Path(d))
            self.assertEqual(ctx.overrides, {"links": "error", "placeholder": "warn"})

    def test_garbled_marker_is_tolerated(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".standards-kit.json").write_text("{not json", encoding="utf-8")
            ctx = build_context(Path(d))
            self.assertTrue(ctx.adopter_mode)
            self.assertEqual(ctx.overrides, {})


if __name__ == "__main__":
    unittest.main()
