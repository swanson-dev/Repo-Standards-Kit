"""Repo profiles and the docs/STANDARDS.md profile matrix as data (ADR-0025).

A repo declares one or more profiles. Their requirements combine by the strongest
tier, and their extras add up. tests/test_profiles.py keeps MATRIX and EXTRAS in
sync with the tables in docs/STANDARDS.md.
"""
from __future__ import annotations

PROFILES: tuple[str, ...] = ("application", "library", "data", "documentation")
DOCS_ONLY = "documentation"  # code lives elsewhere, so it can't combine with the others
# ADR-0025 merged infra into application; old names still read as the new ones.
PROFILE_ALIASES = {"infra": "application"}

TIERS: tuple[str, ...] = ("N/A", "Optional", "Expected", "Required")  # weakest first

# Numbered doc -> (its template in docs/templates/, its tier for each of PROFILES).
MATRIX: dict[str, tuple[str, tuple[str, ...]]] = {
    "01-prd.md": ("prd-template.md", ("Required", "Optional", "Expected", "Expected")),
    "02-architecture.md": ("architecture-template.md",
                           ("Required", "Expected", "Required", "Expected")),
    "03-data-model.md": ("data-model-template.md", ("Expected", "N/A", "Required", "Optional")),
    "04-api-and-integrations.md": ("api-and-integrations-template.md",
                                   ("Required", "Required", "Required", "Required")),
    "05-implementation-plan.md": ("implementation-plan-template.md",
                                  ("Expected", "Optional", "Expected", "Expected")),
    "06-runbook.md": ("runbook-template.md", ("Required", "N/A", "Required", "N/A")),
    "07-testing.md": ("testing-template.md", ("Required", "Required", "Required", "Required")),
    "08-security-and-compliance.md": ("security-template.md",
                                      ("Required", "Expected", "Required", "Expected")),
    "09-deployment.md": ("deployment-template.md", ("Required", "N/A", "Required", "Optional")),
}
EXTRAS: dict[str, str] = {
    "application": "docs/environments.md",
    "library": "docs/versioning-policy.md",
    "data": "docs/data-contracts/",
    "documentation": "docs/source-map.md",
}


def parse_profiles(value: str | list[str]) -> list[str]:
    """A comma list or a list of names -> known profiles, in order, without repeats.

    Raises ValueError, with a message meant for the user, for an empty list, an
    unknown name, or documentation combined with another profile.
    """
    names = value.split(",") if isinstance(value, str) else value
    if not all(isinstance(name, str) for name in names):
        raise ValueError(f"profiles must be names, got {value!r}")
    profiles: list[str] = []
    for name in (n.strip() for n in names):
        if not name:
            continue
        name = PROFILE_ALIASES.get(name, name)
        if name not in PROFILES:
            raise ValueError(f"unknown profile {name!r}; choose from {', '.join(PROFILES)}")
        if name not in profiles:
            profiles.append(name)
    if not profiles:
        raise ValueError(f"no profile given; choose from {', '.join(PROFILES)}")
    if DOCS_ONLY in profiles and len(profiles) > 1:
        raise ValueError(f"{DOCS_ONLY} can't be combined with other profiles")
    return profiles


def combine(profiles: list[str]) -> dict[str, str]:
    """Numbered doc -> the strongest tier any of the profiles gives it."""
    columns = [PROFILES.index(p) for p in profiles]
    return {doc: max((tiers[c] for c in columns), key=TIERS.index)
            for doc, (_template, tiers) in MATRIX.items()}


def needed_docs(profiles: list[str]) -> tuple[list[str], list[str]]:
    """(Required docs, Expected docs) for the combined profiles, in matrix order."""
    tiers = combine(profiles)
    return ([doc for doc, tier in tiers.items() if tier == "Required"],
            [doc for doc, tier in tiers.items() if tier == "Expected"])
