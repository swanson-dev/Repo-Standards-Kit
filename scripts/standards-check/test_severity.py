"""Unit tests for the checks package shared types + severity resolution."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context, Finding, resolve_severity  # noqa: E402


class ResolveSeverityTests(unittest.TestCase):
    def _ctx(self, adopter: bool, overrides=None) -> Context:
        return Context(root=Path("."), adopter_mode=adopter, overrides=overrides or {})

    def test_kit_mode_uses_default_error(self):
        sev = resolve_severity("links", "error", self._ctx(adopter=False))
        self.assertEqual(sev, "error")
        sev_warn = resolve_severity("links", "warn", self._ctx(adopter=False))
        self.assertEqual(sev_warn, "warn")

    def test_adopter_mode_softens_to_warn(self):
        sev = resolve_severity("links", "error", self._ctx(adopter=True))
        self.assertEqual(sev, "warn")

    def test_adopter_override_escalates_to_error(self):
        sev = resolve_severity("links", "error", self._ctx(adopter=True, overrides={"links": "error"}))
        self.assertEqual(sev, "error")

    def test_finding_is_frozen(self):
        f = Finding(check_id="links", severity="error", message="x")
        with self.assertRaises((TypeError, AttributeError)):
            f.message = "y"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
