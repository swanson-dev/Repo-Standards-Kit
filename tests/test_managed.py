import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

WRAPPED = (
    "# Title\n\n"
    "<!-- BEGIN kit-managed: agents-core (v0.6.0) -->\n"
    "contract body\n"
    "<!-- END kit-managed: agents-core -->\n\n"
    "## About this repository\n"
    "downstream stuff\n"
)


class ManagedTests(unittest.TestCase):
    def test_find_block_returns_inner(self):
        from standards.managed import find_block
        block = find_block(WRAPPED)
        self.assertIsNotNone(block)
        self.assertEqual(block.inner, "contract body")
        self.assertEqual(block.block_id, "agents-core")

    def test_find_block_none_when_absent(self):
        from standards.managed import find_block
        self.assertIsNone(find_block("# Title\n\nno markers here\n"))

    def test_find_block_none_when_unterminated(self):
        from standards.managed import find_block
        self.assertIsNone(find_block("<!-- BEGIN kit-managed: x (v1) -->\nbody\n"))

    def test_splice_replaces_only_inner(self):
        from standards.managed import splice_block
        out = splice_block(WRAPPED, "NEW BODY")
        self.assertIn("NEW BODY", out)
        self.assertNotIn("contract body", out)
        self.assertTrue(out.startswith("# Title\n\n"))
        self.assertIn("## About this repository\ndownstream stuff\n", out)

    def test_block_hash_stable_and_changes_with_content(self):
        from standards.managed import block_hash, splice_block
        h1 = block_hash(WRAPPED)
        self.assertEqual(h1, block_hash(WRAPPED))
        self.assertNotEqual(h1, block_hash(splice_block(WRAPPED, "different")))

    def test_block_hash_none_when_absent(self):
        from standards.managed import block_hash
        self.assertIsNone(block_hash("no markers"))


if __name__ == "__main__":
    unittest.main()
