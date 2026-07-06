"""Guards: a malformed/missing managed block in payload must fail loud.

The payload's partial files (AGENTS.md, CLAUDE.md, .github/copilot-instructions.md)
always carry exactly one well-formed kit-managed block. If a corrupt wheel or a bad
edit ever breaks that invariant, adoption must raise a clear, file-named error rather
than crash with AttributeError/TypeError deep in the copy loop.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from standards.init import _require_block, _require_hash  # noqa: E402

WELL_FORMED = (
    "intro\n"
    "<!-- BEGIN kit-managed: agents (v1.0.0) -->\n"
    "kit text\n"
    "<!-- END kit-managed: agents -->\n"
)


class RequireBlockGuardTests(unittest.TestCase):
    def test_require_block_raises_naming_file_when_no_block(self):
        with self.assertRaises(ValueError) as cm:
            _require_block("# AGENTS\n\nno managed block here\n", "AGENTS.md")
        self.assertIn("AGENTS.md", str(cm.exception))

    def test_require_block_returns_inner_when_present(self):
        self.assertEqual(_require_block(WELL_FORMED, "AGENTS.md").inner, "kit text")

    def test_require_hash_raises_naming_file_when_no_block(self):
        with self.assertRaises(ValueError) as cm:
            _require_hash("nothing here\n", "CLAUDE.md")
        self.assertIn("CLAUDE.md", str(cm.exception))

    def test_require_hash_returns_stable_hash_when_present(self):
        self.assertEqual(_require_hash(WELL_FORMED, "AGENTS.md"),
                         _require_hash(WELL_FORMED, "AGENTS.md"))


if __name__ == "__main__":
    unittest.main()
