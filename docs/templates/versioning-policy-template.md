<!--
docs/versioning-policy.md — library-profile extra.
Declares SemVer commitments, deprecation cadence, and support window for the public API.
-->

# Versioning Policy

## Versioning scheme

This package follows **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).

| Change | Bump |
|---|---|
| Breaking change to public API surface | MAJOR |
| Backward-compatible additions | MINOR |
| Backward-compatible bug fixes, doc-only, internal refactors | PATCH |

## Public API surface

<!-- Be explicit. What IS the API? What is internal? -->

- **Public:** <namespace / exported symbols / endpoints>
- **Internal:** <anything not enumerated above; subject to change without notice>

## Deprecation policy

- **Notice period:** <e.g. one minor release> before a deprecated API is removed.
- **Deprecation signal:** <`@deprecated` JSDoc, runtime warning, etc.>
- **Removal:** in the next MAJOR after the notice period.

## Support window

- **Supported versions:** <e.g. current MAJOR and previous MAJOR>
- **Security fixes:** <which versions get back-ported>

## Pre-1.0 caveat (delete after 1.0)

While the package is pre-1.0, MINOR bumps may include breaking changes. The notice mechanism above still applies.
