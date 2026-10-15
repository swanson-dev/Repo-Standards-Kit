"""PROTOTYPE logic for RFC-0009's setup flow. Throwaway.

Pure functions only (no I/O, no terminal code), so whatever RFC-0009 keeps can
be lifted into `src/standards/` and the TUI shell deleted.
"""
from __future__ import annotations

from fnmatch import fnmatch

# Wizard choices 1-4, in this order. Documentation only is choice 0 and never combines.
PROFILES = {
    "application": "a deployable app or service",
    "library": "a reusable package others import",
    "infra": "IaC, deployment, environments",
    "data": "pipelines, models, data contracts",
}
CHOICES = list(PROFILES)
DOCS_ONLY = "documentation"

TIERS = ["N/A", "Optional", "Expected", "Required"]  # weakest to strongest
COLUMNS = ["application", "library", "infra", "data", "documentation"]

# The docs/STANDARDS.md profile matrix as data; conditional notes are dropped.
MATRIX = {
    "01-prd.md": ("Required", "Optional", "Optional", "Expected", "Expected"),
    "02-architecture.md": ("Required", "Expected", "Required", "Required", "Expected"),
    "03-data-model.md": ("Expected", "N/A", "Optional", "Required", "Optional"),
    "04-api-and-integrations.md": ("Required", "Required", "Expected", "Required", "Required"),
    "05-implementation-plan.md": ("Expected", "Optional", "Expected", "Expected", "Expected"),
    "06-runbook.md": ("Required", "N/A", "Required", "Required", "N/A"),
    "07-testing.md": ("Required", "Required", "Expected", "Required", "Required"),
    "08-security-and-compliance.md": ("Required", "Expected", "Required", "Required", "Expected"),
    "09-deployment.md": ("Required", "N/A", "Required", "Required", "Optional"),
}
EXTRAS = {
    "library": "docs/versioning-policy.md",
    "infra": "docs/environments.md",
    "data": "docs/data-contracts/ (one per dataset)",
    "documentation": "docs/source-map.md",
}

# Rough on purpose. A pattern ending in "/" matches a folder; anything else
# matches a file name.
SIGNALS = {
    "application": ["Dockerfile", "docker-compose.yml", "compose.yaml", "manage.py",
                    "next.config.*", "vite.config.*", "Program.cs", "Procfile"],
    "library": ["pyproject.toml", "setup.py", "Cargo.toml", "*.csproj", "package.json"],
    "infra": ["*.tf", "*.bicep", "Pulumi.yaml", "cdk.json", "Chart.yaml", "kustomization.yaml"],
    "data": ["dbt_project.yml", "dags/", "*.ipynb"],
}


def suggest(paths: list[str]) -> dict[str, list[str]]:
    """Profile -> up to two of the files that suggested it."""
    found: dict[str, list[str]] = {name: [] for name in SIGNALS}
    for path in paths:
        name = path.rsplit("/", 1)[-1]
        for profile, patterns in SIGNALS.items():
            hit = any(
                (path.startswith(p) or f"/{p}" in path) if p.endswith("/") else fnmatch(name, p)
                for p in patterns
            )
            if hit and len(found[profile]) < 2:
                found[profile].append(path)
    if found["application"]:
        found["library"] = []  # apps carry packaging manifests too
    return {profile: files for profile, files in found.items() if files}


def parse_picks(answer: str, default: list[str]) -> list[str]:
    """'1,3' -> profiles, '' -> default, '0' -> documentation only.

    Raises ValueError with a message meant for the user.
    """
    parts = [p for p in answer.replace(" ", "").split(",") if p]
    if not parts:
        return default
    if "0" in parts:
        if len(parts) > 1:
            raise ValueError("Documentation only can't be combined with other kinds.")
        return [DOCS_ONLY]
    picks: list[str] = []
    for part in parts:
        if not part.isdigit() or not 1 <= int(part) <= len(CHOICES):
            raise ValueError(f"'{part}' isn't a choice. Use 0-{len(CHOICES)}.")
        name = CHOICES[int(part) - 1]
        if name not in picks:
            picks.append(name)
    return picks


def combine(profiles: list[str]) -> dict[str, str]:
    """Doc -> the strongest tier any chosen profile gives it."""
    cols = [COLUMNS.index(p) for p in profiles]
    return {doc: max((row[c] for c in cols), key=TIERS.index) for doc, row in MATRIX.items()}


def plan_setup(profiles: list[str], existing: set[str]) -> dict:
    """What setup would create, keep, and list for these profiles."""
    tiers = combine(profiles)
    wanted = [doc for doc, tier in tiers.items() if tier in ("Required", "Expected")]
    return {
        "tiers": tiers,
        "create": [doc for doc in wanted if f"docs/{doc}" not in existing],
        "keep": [doc for doc in wanted if f"docs/{doc}" in existing],
        "extras": [EXTRAS[p] for p in profiles if p in EXTRAS and EXTRAS[p] not in existing],
    }


def requirement_changes(old: list[str], new: list[str]) -> list[tuple[str, str, str]]:
    """(doc, old tier, new tier) for every doc whose tier changes."""
    before, after = combine(old), combine(new)
    return [(doc, before[doc], after[doc]) for doc in MATRIX if before[doc] != after[doc]]


def marker(profiles: list[str], kit_version: str) -> dict:
    """Marker fields setup would write; `profile` keeps older CLIs working."""
    return {"kit_version": kit_version, "profile": profiles[0], "profiles": profiles}


def checklist_header(profiles: list[str]) -> str:
    """`+` keeps older checkers, which read only the first word, valid."""
    return "**Profile:** " + " + ".join(profiles)


def menu(adopted: bool, behind: bool) -> list[tuple[str, str, bool]]:
    """(action, label, recommended) for the repo's state."""
    if not adopted:
        return [("setup", "Set up this repo", True),
                ("check", "Check / fix this repo", False),
                ("skill", "Create an AI skill", False)]
    items = [("check", "Check / fix this repo", False)]
    if behind:
        items.append(("update", "Update to the installed kit version", True))
    items += [("change", "Change what this repo contains", False),
              ("skill", "Create an AI skill", False)]
    return items
