# Versioning Policy

The kit follows **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`). Each downstream repo pins a specific kit version in its local `docs/STANDARDS.md` and upgrades deliberately.

## Versioning scheme

| Change | Bump |
|---|---|
| Breaking change to the public surface defined in [`04-api-and-integrations.md`](./04-api-and-integrations.md) — folder layout, `ai/` contract, profile model, profile matrix cell moving to a stricter tier, ADR/RFC format, waiver syntax, AGENTS.md reading order | **MAJOR** |
| New optional artifact, new profile-specific extra, new tier-respecting cell (e.g., Optional → Expected with grace period), new template, new section in an existing template | **MINOR** |
| Typo fixes, wording clarifications, new examples, new bootstrap ADR, new internal doc | **PATCH** |

## 1.0.0 baseline

As of v1.0.0, downstream consumers can rely on the SemVer guarantees above. The v1.0.0 baseline is guarded by generated downstream fixture repos for all four profiles (`application`, `library`, `infra`, `data`) plus the shipped AI Skills/Hooks and PyPI `standards` CLI distribution mechanism. ADR-0018 records generated fixtures as the release-readiness evidence.

## Public surface

See [`04-api-and-integrations.md`](./04-api-and-integrations.md) § "Public surface" for the explicit list of surfaces governed by this policy.

## Deprecation policy

When a kit-shipped artifact is deprecated:

- The change is announced in the next MINOR release with a `Deprecated` note in `CHANGELOG.md` and (where applicable) a status flip on the relevant ADR.
- The deprecated artifact remains in place for **at least one MINOR release** before removal.
- Removal happens in the next MAJOR after the notice period.
- The CHANGELOG entry for the removal links the deprecation notice and the replacement path.

## Support window

- **Supported versions:** current MAJOR and the previous MAJOR.
- **Security fixes:** N/A — see [`08-security-and-compliance.md`](./08-security-and-compliance.md) for the kit's security posture (no runtime, no secrets).
- **Bug fixes (typos, clarifications):** applied to the current MAJOR only.

## How a downstream repo upgrades

1. Read the CHANGELOG entries between the currently adopted version and the target version.
2. Run the kit's standards check against the repo's current state (it will surface any contract violations introduced by the new version).
3. Update `docs/STANDARDS.md` `Kit version adopted:` to the new version.
4. Re-fill `docs/STANDARDS-CHECKLIST.md` for any new Required/Expected docs.
5. Commit as a single PR with a `chore(standards): upgrade to kit vX.Y.Z` title.
