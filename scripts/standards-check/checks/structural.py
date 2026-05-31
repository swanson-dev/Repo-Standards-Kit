"""Structural checks (standards-check v1) — relocated verbatim from check.py.

These predate the content checks and keep their historical severities: most are
errors; the ai/ staleness findings are warnings. They bypass the kit/adopter
severity softening (resolve_severity is only for the new content checks).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from . import Context, Finding

ALLOWED_PROFILES = {"application", "library", "infra", "data"}
ADR_STATUSES = {"Proposed", "Accepted", "Deprecated"}
RFC_STATUSES = {"Open", "Concluded", "Abandoned"}

ADR_FILENAME_RE = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
RFC_SLUG_RE = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SUPERSEDED_RE = re.compile(r"^Superseded by \d{4}$")

UNIVERSAL_CORE = [
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/STANDARDS.md",
    "docs/STANDARDS-CHECKLIST.md",
    "docs/00-overview.md",
    "docs/10-glossary.md",
    "docs/decisions/README.md",
    "docs/discovery/README.md",
    "docs/rfcs/README.md",
    "docs/templates/README.md",
    "ai/current-state.md",
    "ai/next-actions.md",
    "ai/open-questions.md",
    "ai/handoff.md",
    ".github/copilot-instructions.md",
    ".github/pull_request_template.md",
    ".github/workflows/repo-standards.yml",
]

CURRENT_STATE_STALE_DAYS = 14
HANDOFF_STALE_DAYS = 5


@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            val = re.sub(r"\s+#.*$", "", val)
            fm[key.strip()] = val.strip()
    return fm


def check_universal_core(root: Path, report: Report) -> None:
    for rel in UNIVERSAL_CORE:
        if not (root / rel).exists():
            report.err(f"[core] Universal core file missing: {rel}")


def check_profile(root: Path, report: Report):
    checklist = root / "docs/STANDARDS-CHECKLIST.md"
    if not checklist.exists():
        return None
    text = checklist.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Profile:\*\*\s+([^\n<]+)", text)
    if not m:
        report.err("[profile] docs/STANDARDS-CHECKLIST.md does not declare a Profile field.")
        return None
    profile = m.group(1).strip().split()[0]
    if profile not in ALLOWED_PROFILES:
        report.err(
            f"[profile] Declared profile '{profile}' is not in allowed set {sorted(ALLOWED_PROFILES)}."
        )
        return None
    return profile


def check_waivers(root: Path, report: Report) -> None:
    checklist = root / "docs/STANDARDS-CHECKLIST.md"
    if not checklist.exists():
        return
    in_optional_section = False
    in_na_section = False
    for i, raw in enumerate(checklist.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if raw.startswith("#"):
            h = raw.lower()
            in_optional_section = "optional" in h
            in_na_section = ("n/a" in h) or ("not applicable" in h)
            continue
        if in_optional_section or in_na_section:
            continue
        m = re.match(r"^\s*-\s*\[\s*\]\s*(.+)$", raw)
        if not m:
            continue
        body = m.group(1).strip()
        if body.startswith("<") and body.endswith(">"):
            continue
        if "**Waived:**" not in body:
            report.err(
                f"[waiver] docs/STANDARDS-CHECKLIST.md:{i} unchecked box has no `**Waived:**` reason: {body}"
            )


def _check_date_field(path, field_name, raw, stale_days, today, report, file_label) -> None:
    if not raw:
        report.err(f"[ai] {file_label} missing `{field_name}:` frontmatter.")
        return
    date_part = raw.split("T")[0]
    try:
        parsed = date.fromisoformat(date_part)
    except ValueError:
        report.err(f"[ai] {file_label} `{field_name}:` is not a valid ISO 8601 date: {raw}")
        return
    if today - parsed > timedelta(days=stale_days):
        report.warn(f"[ai] {file_label} `{field_name}: {date_part}` is older than {stale_days} days.")


def check_ai_freshness(root: Path, report: Report) -> None:
    today = date.today()
    cs = root / "ai/current-state.md"
    if cs.exists():
        fm = parse_frontmatter(cs.read_text(encoding="utf-8", errors="replace"))
        _check_date_field(cs, "last_updated", fm.get("last_updated"), CURRENT_STATE_STALE_DAYS, today, report, "ai/current-state.md")
    ho = root / "ai/handoff.md"
    if ho.exists():
        fm = parse_frontmatter(ho.read_text(encoding="utf-8", errors="replace"))
        _check_date_field(ho, "written", fm.get("written"), HANDOFF_STALE_DAYS, today, report, "ai/handoff.md")


def check_adrs(root: Path, report: Report) -> None:
    decisions = root / "docs/decisions"
    if not decisions.exists():
        return
    for adr in sorted(decisions.glob("*.md")):
        if adr.name in {"README.md", "template.md"}:
            continue
        if not ADR_FILENAME_RE.match(adr.name):
            report.err(f"[adr] Filename does not match NNNN-kebab-case.md: docs/decisions/{adr.name}")
            continue
        fm = parse_frontmatter(adr.read_text(encoding="utf-8", errors="replace"))
        status = fm.get("status", "").strip()
        if status in ADR_STATUSES or SUPERSEDED_RE.match(status):
            continue
        report.err(f"[adr] docs/decisions/{adr.name} has invalid status: {status!r}")


def check_rfcs(root: Path, report: Report) -> None:
    rfcs = root / "docs/rfcs"
    if not rfcs.exists():
        return
    for entry in sorted(rfcs.iterdir()):
        if entry.is_file():
            continue
        if not RFC_SLUG_RE.match(entry.name):
            report.err(f"[rfc] RFC folder name does not match NNNN-kebab-case: docs/rfcs/{entry.name}")
            continue
        rfc_md = entry / "rfc.md"
        if not rfc_md.exists():
            report.err(f"[rfc] docs/rfcs/{entry.name}/ missing rfc.md")
            continue
        fm = parse_frontmatter(rfc_md.read_text(encoding="utf-8", errors="replace"))
        status = fm.get("status", "").strip()
        if status not in RFC_STATUSES:
            report.err(f"[rfc] docs/rfcs/{entry.name}/rfc.md has invalid status: {status!r}")


def run(root: Path, ctx: Context) -> list:
    """Run all v1 structural checks; return Findings at their historical severities."""
    # ctx is unused: structural (v1) checks emit fixed severities, bypassing resolve_severity.
    report = Report()
    check_universal_core(root, report)
    check_profile(root, report)
    check_waivers(root, report)
    check_ai_freshness(root, report)
    check_adrs(root, report)
    check_rfcs(root, report)
    findings = [Finding("structural", "error", m) for m in report.errors]
    findings += [Finding("structural", "warn", m) for m in report.warnings]
    return findings
