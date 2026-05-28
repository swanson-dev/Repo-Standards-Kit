# Security and Compliance

The kit has **no runtime, no secrets, no PII, and no external integrations**. This document exists to declare that posture explicitly and to name the small surface that does need attention.

## Threat model summary

- **Assets:** the kit's documentation content (templates, standards, ADRs). The risk is **content tampering** — a malicious or accidental change that weakens the standards downstream consumers rely on.
- **Adversaries:** primarily **mistake-driven** drift (a well-meaning PR that breaks a contract). Malicious adversaries are out of scope for a small internal kit.
- **Trust boundary:** the kit is consumed by being **read and copied**, not executed. Downstream repos that copy templates inherit the content as-is.
- **Top risks:**
  1. A breaking change to the contract (e.g., waiver syntax) lands without a kit-version bump → downstream CI breaks unexpectedly. *Mitigated by:* SemVer policy in [`versioning-policy.md`](./versioning-policy.md) and `STANDARDS-CHECKLIST.md` review gate.
  2. A consumer copies an out-of-date template after the kit evolves. *Mitigated by:* per-repo `Kit version adopted:` field in `docs/STANDARDS.md`; upgrades are deliberate.
  3. `ai/*.md` files in downstream repos accidentally include sensitive context (customer names, incident details, credentials). *Mitigated by:* ADR [0004](./decisions/0004-define-ai-directory-contract.md) consequence note; downstream repos are responsible for their own `.gitignore` and review hygiene.

## Secrets handling

- The kit ships **no secrets**.
- The kit's CI (`.github/workflows/repo-standards.yml`) requires no tokens or credentials beyond what GitHub provides by default.

## Authentication and authorization

- The kit has no auth model. Access is governed by GitHub repo permissions.

## Compliance scope

- **Standards:** none. The kit handles no regulated data.
- **Data classification:** all content is internal-team documentation. Treat as confidential by default; do not include customer data, incident details, or credentials in any kit-shipped file.

## Reviews

- **Last security review:** 2026-05-28 (this document is the first review).
- **Next review due:** at v1.0.0 cut, or when the kit gains a runtime component (Slice 2 Skills may introduce dependencies worth re-reviewing).
- **Dependency-scan cadence:** N/A — no code dependencies.

## What changes the threat model

Adding any of the following triggers a re-review of this document:

- A runtime component (a CLI, a Skill that executes code, a hook that runs in CI).
- An external integration (a webhook, an API call to a third-party service).
- Any non-markdown asset format that requires a binary tool to render.
