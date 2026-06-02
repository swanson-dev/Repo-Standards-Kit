# Glossary

Kit-specific terms. A term belongs here if its meaning is non-obvious to a smart newcomer in 30 seconds.

| Term | Definition | Source |
|---|---|---|
| **ADR** | Architecture Decision Record. Immutable record of a material technical decision, MADR 3.0 format. | `docs/STANDARDS.md` § "ADRs — MADR 3.0" |
| **AGENTS.md pattern** | Single root `AGENTS.md` as canonical agent contract; thin tool-specific pointers (`CLAUDE.md`, `.github/copilot-instructions.md`) reference it. | ADR [0006](./decisions/0006-adopt-agents-md-pattern.md) |
| **Capture** | Turning raw discovery source material (PDFs, JSON, drafts) in the gitignored intake folders into a tracked markdown note under `docs/discovery/captured/`. Done by `/capture-discovery`. The step before promotion. | ADR [0014](./decisions/0014-capture-stage-for-discovery-gitignore-raw-intake-track-synthesized-markdown.md) |
| **Expected** | Tier in the profile matrix: doc present by default; absence requires an explicit waiver in `STANDARDS-CHECKLIST.md`. | `docs/STANDARDS.md` § "Tier semantics" |
| **Handoff** | The most ephemeral `ai/` file. Written at end of session, read first by the next session. Stale after 7 days. | `docs/STANDARDS.md` § "The ai/ directory contract" |
| **Kit version** | SemVer-tagged release of this kit. Each downstream repo pins one in its local `docs/STANDARDS.md`. | [`versioning-policy.md`](./versioning-policy.md) |
| **MADR** | Markdown Architecture Decision Record. Version 3.0 is the kit's chosen ADR format. | ADR [0002](./decisions/0002-adopt-madr-3.md) |
| **N/A** | Tier in the profile matrix: doc not applicable to this profile. Do not create. No waiver needed. | `docs/STANDARDS.md` § "Tier semantics" |
| **Optional** | Tier in the profile matrix: template exists; create when relevant. No waiver needed if skipped. | `docs/STANDARDS.md` § "Tier semantics" |
| **Profile** | Declared shape of a repo: `application` \| `library` \| `infra` \| `data`. Determines which docs are Required / Expected / Optional / N/A. | ADR [0003](./decisions/0003-adopt-repo-profile-model.md) |
| **Promoted** | Status of a `discovery/` file whose content has been synthesized into a structured doc; `promoted_to:` points to the structured doc. | `docs/STANDARDS.md` § "Discovery folder" |
| **Required** | Tier in the profile matrix: doc must exist. Absence fails CI. | `docs/STANDARDS.md` § "Tier semantics" |
| **RFC** | Time-boxed technical investigation. Lives in `docs/rfcs/NNNN-slug/`. Must reach `Concluded`, `Abandoned`, or have its question carried into `ai/open-questions.md`. | `docs/STANDARDS.md` § "RFCs" |
| **Slice** | A coherent unit of kit work that ships together. Slice 1 = templates + standards content. Slice 2 = AI tooling. Slice 3 = distribution. Slice 4 = deeper CI. | [`README.md`](../README.md) § "Roadmap" |
| **Soft-landing template** | A template whose use is encouraged but not enforced. Discovery starters are soft-landing; numbered-doc templates are not. | `docs/STANDARDS.md` § "Discovery folder" |
| **Stale threshold** | Per-file age past which the standards check warns. `current-state.md` / `next-actions.md`: 14 days. `handoff.md`: 7 days. `open-questions.md`: none. | `docs/STANDARDS.md` § "Ownership and update cadence" |
| **Superseded** | ADR status: this ADR's decision has been replaced by a later ADR. Body stays immutable; status changes to `Superseded by NNNN`. | `docs/STANDARDS.md` § "ADRs — MADR 3.0" |
| **Universal core** | The set of files Required for every profile (README, CHANGELOG, AGENTS.md, etc.). | `docs/STANDARDS.md` § "Universal core" |
| **Waived** | Marker on a `STANDARDS-CHECKLIST.md` line indicating an Expected (or rare Required) doc was intentionally skipped, with a one-line reason. Syntax: `**Waived:** <reason>`. CI parses this. | `docs/STANDARDS.md` § "Waiver mechanism" |
