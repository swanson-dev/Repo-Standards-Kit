---
last_updated: 2026-05-28
---

# Next Actions

1. **Finish Slice 1 Phase E** — write `.github/copilot-instructions.md`, `.github/pull_request_template.md`, and `.github/workflows/repo-standards.yml`. Closes out Slice 1.
2. **Run the structural-lint workflow against the kit itself** — confirm the v1 standards check passes on this repo before tagging.
3. **Tag `v0.1.0`** — first cuttable kit release. Mark this commit as the canonical Slice 1 reference point in `CHANGELOG.md` (write `CHANGELOG.md` as part of this step; currently waived as pre-1.0).
4. **Open Slice 2 design** — start with `/gsd:discuss-phase` or a brainstorming session to pick which Skills to build first. Strong candidates: scaffold-new-repo, new-adr, new-rfc, update-handoff, promote-discovery. See `ai/open-questions.md#q-1`.
5. **Decide distribution mechanism (Slice 3)** — see `ai/open-questions.md#q-2`. Open an RFC under `docs/rfcs/0001-distribution-mechanism/` when ready.
6. **Walk one downstream repo per profile through adoption** — validates that the kit actually fits the four profiles. Capture friction as new ADRs or template adjustments.
