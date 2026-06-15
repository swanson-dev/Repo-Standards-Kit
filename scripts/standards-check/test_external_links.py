"""Tests for opt-in external-link liveness checking."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import Context  # noqa: E402
from checks.external_links import _open_url, check_url, extract_external_links, run  # noqa: E402


def _ctx(root: Path, adopter: bool = False, overrides=None, external_links: bool = False) -> Context:
    return Context(
        root=root,
        adopter_mode=adopter,
        overrides=overrides or {},
        external_links=external_links,
    )


class ExtractExternalLinksTests(unittest.TestCase):
    def test_extracts_http_and_https_only(self):
        text = (
            "[site](https://example.com/a) "
            "[mail](mailto:a@example.com) "
            "[tel](tel:123) "
            "[rel](./local.md)\n"
            "[ref]: http://example.com/ref\n"
        )
        targets = [target for _, target in extract_external_links(text)]
        self.assertEqual(targets, ["https://example.com/a", "http://example.com/ref"])

    def test_ignores_fenced_code(self):
        text = "```\n[x](https://example.com/nope)\n```\n[y](https://example.com/yes)\n"
        targets = [target for _, target in extract_external_links(text)]
        self.assertEqual(targets, ["https://example.com/yes"])


class CheckUrlTests(unittest.TestCase):
    def test_2xx_status_is_ok(self):
        def opener(_url: str, _timeout: float):
            return 204

        self.assertIsNone(check_url("https://example.com", opener=opener))

    def test_3xx_status_is_ok(self):
        def opener(_url: str, _timeout: float):
            return 301

        self.assertIsNone(check_url("https://example.com", opener=opener))

    def test_4xx_status_is_reported(self):
        def opener(_url: str, _timeout: float):
            return 404

        self.assertEqual(check_url("https://example.com/missing", opener=opener), "HTTP 404")

    def test_exception_is_reported(self):
        def opener(_url: str, _timeout: float):
            raise OSError("connection refused")

        self.assertEqual(
            check_url("https://example.com/down", opener=opener),
            "connection refused",
        )

    def test_head_error_falls_back_to_get(self):
        calls = []

        def requester(_url: str, method: str, _timeout: float):
            calls.append(method)
            if method == "HEAD":
                return 403
            return 200

        self.assertEqual(_open_url("https://example.com/head-blocked", 10.0, requester), 200)
        self.assertEqual(calls, ["HEAD", "GET"])


class RunTests(unittest.TestCase):
    def _write(self, root: Path, rel: str, body: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_external_links_are_skipped_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](https://example.com/gone)\n")
            findings = run(root, _ctx(root))
            self.assertEqual(findings, [])

    def test_broken_external_link_is_error_in_kit_when_enabled(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](https://example.com/gone)\n")

            def checker(_url: str):
                return "HTTP 404"

            findings = run(root, _ctx(root, external_links=True), checker=checker)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "error")
            self.assertEqual(findings[0].check_id, "external-links")
            self.assertIn("a.md:1 external link unreachable", findings[0].message)

    def test_broken_external_link_is_warn_in_adopter_when_enabled(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](https://example.com/gone)\n")

            def checker(_url: str):
                return "HTTP 404"

            findings = run(root, _ctx(root, adopter=True, external_links=True), checker=checker)
            self.assertEqual(findings[0].severity, "warn")

    def test_adopter_override_escalates(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[gone](https://example.com/gone)\n")

            def checker(_url: str):
                return "HTTP 404"

            findings = run(
                root,
                _ctx(root, adopter=True, overrides={"external-links": "error"}, external_links=True),
                checker=checker,
            )
            self.assertEqual(findings[0].severity, "error")

    def test_duplicate_urls_are_checked_once_but_reported_at_each_location(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._write(root, "a.md", "[one](https://example.com/gone)\n")
            self._write(root, "b.md", "[two](https://example.com/gone)\n")
            calls = []

            def checker(url: str):
                calls.append(url)
                return "HTTP 404"

            findings = run(root, _ctx(root, external_links=True), checker=checker)
            self.assertEqual(calls, ["https://example.com/gone"])
            self.assertEqual(len(findings), 2)


if __name__ == "__main__":
    unittest.main()
