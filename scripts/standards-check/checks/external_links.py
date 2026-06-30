"""Opt-in external-link liveness checks.

Default standards checks stay deterministic and offline. This module only runs
when Context.external_links is true.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

from . import Context, Finding, resolve_severity
from ._text import strip_code_and_comments
from .links import _iter_markdown

CHECK_ID = "external-links"
DEFAULT_SEVERITY = "error"
DEFAULT_TIMEOUT = 10.0

_INLINE_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_REFDEF_RE = re.compile(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(\S+)")
_HTTP_RE = re.compile(r"^https?://", re.IGNORECASE)


def extract_external_links(text: str) -> list[tuple[int, str]]:
    """Return [(line_number, url)] for http(s) inline and reference links."""
    cleaned = strip_code_and_comments(text)
    out: list[tuple[int, str]] = []
    for i, line in enumerate(cleaned.splitlines(), 1):
        for pattern in (_INLINE_RE, _REFDEF_RE):
            for match in pattern.finditer(line):
                target = match.group(1).strip("<>")
                if _HTTP_RE.match(target):
                    out.append((i, target))
    return out


def _request_status(url: str, method: str, timeout: float) -> int:
    request = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "repo-standards-kit/standards-check"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def _open_url(
    url: str,
    timeout: float,
    requester: Callable[[str, str, float], int] | None = None,
) -> int:
    """Return the HTTP status for url, using GET as the final authority."""
    request_fn = requester or _request_status
    try:
        head_status = request_fn(url, "HEAD", timeout)
        if 200 <= head_status < 400:
            return head_status
    except Exception:
        pass
    return request_fn(url, "GET", timeout)


def _strip_fragment(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def check_url(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    opener: Callable[[str, float], int] | None = None,
) -> str | None:
    """Return None for live URLs, or a short reason for unreachable URLs."""
    probe = _strip_fragment(url)
    open_fn = opener or _open_url
    try:
        status = open_fn(probe, timeout)
    except Exception as exc:  # noqa: BLE001 - diagnostic check should report and continue.
        return str(exc)
    if 200 <= status < 400:
        return None
    return f"HTTP {status}"


def run(
    root: Path,
    ctx: Context,
    checker: Callable[[str], str | None] | None = None,
) -> list[Finding]:
    if not ctx.external_links:
        return []

    severity = resolve_severity(CHECK_ID, DEFAULT_SEVERITY, ctx)
    findings: list[Finding] = []
    locations: dict[str, list[tuple[str, int]]] = {}

    for path, rel in _iter_markdown(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, url in extract_external_links(text):
            locations.setdefault(url, []).append((rel, line_no))

    results: dict[str, str | None] = {}
    for url in sorted(locations):
        results[url] = checker(url) if checker else check_url(url)

    for url, reason in results.items():
        if reason is None:
            continue
        for rel, line_no in locations[url]:
            findings.append(Finding(
                CHECK_ID,
                severity,
                f"{rel}:{line_no} external link unreachable -> {url} ({reason})",
            ))
    return findings
