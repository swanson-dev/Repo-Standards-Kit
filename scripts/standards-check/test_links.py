"""Tests for the internal-link check."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.links import run, slugify, extract_links  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None) -> Context:
    return Context(root=root, adopter_mode=adopter, overrides=overrides or {})


class SlugifyTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_strips_punctuation(self):
        self.assertEqual(slugify("What's the Plan?"), "whats-the-plan")

    def test_keeps_existing_hyphen(self):
        self.assertEqual(slugify("kit-tracked files"), "kit-tracked-files")


class ExtractLinksTests(unittest.TestCase):
    def test_inline_link(self):
        links = extract_links("see [the doc](./a.md) here")
        self.assertIn("./a.md", [t for _, t in links])

    def test_skips_images(self):
        links = extract_links("![alt](./img.png)")
        self.assertEqual(links, [])

    def test_skips_external(self):
        links = extract_links("[x](https://example.com) [y](mailto:a@b.c)")
        self.assertEqual(links, [])

    def test_ignores_fenced_code(self):
        text = "```\n[x](./nope.md)\n```\nreal [y](./yes.md)\n"
        targets = [t for _, t in extract_links(text)]
        self.assertEqual(targets, ["./yes.md"])

    def test_reference_definition(self):
        targets = [t for _, t in extract_links("[id]: ./ref.md\n")]
        self.assertIn("./ref.md", targets)


class RunTests(unittest.TestCase):
    def _write(self, root: Path, rel: str, body: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_valid_relative_link_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[b](./b.md)\n")
            self._write(root, "b.md", "# B\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_file_is_error_in_kit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](./gone.md)\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")
            self.assertIn("missing file", findings[0].message)

    def test_missing_file_is_warn_in_adopter(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](./gone.md)\n")
            findings = run(root, _ctx(root, adopter=True))
            self.assertEqual(findings[0].severity, "warn")

    def test_adopter_override_escalates(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](./gone.md)\n")
            findings = run(root, _ctx(root, adopter=True, overrides={"links": "error"}))
            self.assertEqual(findings[0].severity, "error")

    def test_valid_anchor_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[sec](./b.md#the-section)\n")
            self._write(root, "b.md", "# B\n\n## The Section\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_missing_anchor_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[sec](./b.md#nope)\n")
            self._write(root, "b.md", "# B\n\n## The Section\n")
            findings = run(root, _ctx(root))
            self.assertEqual(len(findings), 1)
            self.assertIn("missing anchor", findings[0].message)

    def test_same_file_anchor(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "# A\n\n## Top\n\nback to [top](#top)\n")
            self.assertEqual(run(root, _ctx(root)), [])

    def test_git_dir_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, ".git/x.md", "[gone](./nope.md)\n")
            self._write(root, "a.md", "# A\n")
            self.assertEqual(run(root, _ctx(root)), [])


if __name__ == "__main__":
    unittest.main()
