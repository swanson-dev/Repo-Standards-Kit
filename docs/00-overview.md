# Overview

## What this repo is

The **Team Repository Standards Kit** — a versioned, opinionated set of documentation standards and templates that any repository on the team can adopt. This kit is itself a `library`-profile repo: it ships templates and a spec, not a runtime.

Slice 1 (in progress, version 0.1.0) covers templates and standards content. Slices 2–4 cover AI Skills + Hooks, distribution, and deeper CI enforcement.

## Audience

- **Tech leads and senior engineers** adopting the kit in a new or existing repo.
- **AI agents** (Claude Code, Copilot, Cursor, etc.) following the canonical reading order in `AGENTS.md`.
- **Reviewers** assessing whether a downstream repo conforms to the kit.

## How to read the `docs/` tree

| File / folder | Read it when |
|---|---|
| [`STANDARDS.md`](./STANDARDS.md) | You need the authoritative spec — profiles, matrix, contracts. **Start here for any specific question.** |
| [`STANDARDS-CHECKLIST.md`](./STANDARDS-CHECKLIST.md) | You want to see how the kit applies its own standards to itself. |
| [`02-architecture.md`](./02-architecture.md) | You want the conceptual model — how the artifact types relate. |
| [`04-api-and-integrations.md`](./04-api-and-integrations.md) | You're a consumer (downstream repo) and need the public surface. |
| [`07-testing.md`](./07-testing.md) | You want to know how the kit is verified (mostly structural + walkthrough). |
| [`08-security-and-compliance.md`](./08-security-and-compliance.md) | You want the (small) threat model and posture statement. |
| [`10-glossary.md`](./10-glossary.md) | A kit-specific term is unfamiliar (Profile, Waived, Promoted, etc.). |
| [`versioning-policy.md`](./versioning-policy.md) | You're pinning a kit version in your repo and want the deprecation policy. |
| [`templates/`](./templates/) | You're authoring a new artifact (ADR, RFC, numbered doc) and need a starter. |
| [`decisions/`](./decisions/) | You want to know **why** the kit is shaped this way (ADRs 0001–0006). |
| [`discovery/`](./discovery/) | Raw stakeholder material (none in the kit yet; the folder exists for downstream repos to model). |
| [`rfcs/`](./rfcs/) | Open or concluded technical investigations (none in the kit yet). |

For the AI session contract, read [`../AGENTS.md`](../AGENTS.md) first.
