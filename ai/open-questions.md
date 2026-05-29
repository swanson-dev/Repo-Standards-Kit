# Open Questions

## Q-1: Which Slice 2 Skills should ship first?

- **Status:** answered
- **Blocking:** Slice 2 plan-phase. Choosing the first Skills shapes how much surface the Hooks need to cover.
- **Context:** The kit's templates and contracts are precise enough to scaffold. The remaining design choice is *which* scaffolding to automate first — the things downstream repos will do most often.
- **Candidate answers:**
  - **scaffold-new-repo** — bootstrap a fresh repo with profile prompt + template copy. Highest leverage (one-shot adoption) but heaviest to build.
  - **new-adr** — auto-number, fill frontmatter, drop the user into the body. Daily use. Easiest to build.
  - **new-rfc** — same shape as new-adr but creates the folder.
  - **update-handoff** — Stop-hook variant that drafts `ai/handoff.md` from the session transcript.
  - **promote-discovery** — list `status: raw` files and offer to flip with `promoted_to:`.
- **Resolution:** **Skills first, Hooks deferred to Slice 2.5** (2026-05-28). `new-adr` and `new-rfc` ship as stdlib Python scripts under `scripts/new-doc/` with dual Claude SKILL.md + Copilot prompt.md wrappers. `scaffold-new-repo` waits on Slice 3 distribution. Form factor recorded in ADR-0007.

## Q-2: What's the kit's distribution mechanism (Slice 3)?

- **Status:** answered
- **Blocking:** Slice 3 in full. Also affects whether we keep `docs/templates/` colocated or split it into a separate distributable.
- **Context:** Downstream repos need to (a) initially adopt the kit and (b) stay current as the kit evolves. Three credible options: a Claude Code plugin, a GitHub template repo, or a `degit`-style copy script. Each implies a different upgrade story.
- **Candidate answers:**
  - **GitHub template repo + manual sync** — simplest. Lowest barrier; weakest upgrade story.
  - **Claude Code plugin** — aligns with Slice 2 Skills; ties distribution to one tool.
  - **Copy script** (`npx repo-standards init`) — tool-neutral; introduces a maintained CLI.
  - **Hybrid:** GitHub template repo for initial adoption + a Skill (Slice 2) for in-place upgrades.
- **Resolution:** **A single zero-dependency Python package on PyPI, run via `pipx run` / `uvx`** (2026-05-29). One `standards` CLI with `init` (adopt) and `update` (stay current); kit content ships as package data and the package version *is* the kit version. Upgrades reconcile via a three-class ownership model (kit-tracked / scaffold-once / partial managed-region) with a `.standards-kit.toml` version+hash marker and non-destructive sidecar conflict handling. `git clone` is the fallback; template-repo, Claude-plugin, `gh`, and npm/npx are recorded as considered-and-deferred. Full rationale in [RFC-0001](../docs/rfcs/0001-what-is-the-kit-s-distribution-and-upgrade-mechanism/rfc.md). Durable decision to be recorded as ADR-0009 when Slice 3 build begins.

## Q-3: Should the kit ship a CHANGELOG.md before 1.0.0?

- **Status:** answered
- **Blocking:** ~~the upgrade-path verification step in `versioning-policy.md`~~ — resolved.
- **Context:** Pre-1.0, the kit may break minor versions; a CHANGELOG documents that explicitly.
- **Candidate answers:**
  - Start CHANGELOG at v0.1.0.
  - Keep waived until v1.0.0.
- **Resolution:** **Start CHANGELOG at v0.1.0** (Phase E, 2026-05-28). The pre-1.0 caveat is recorded in the changelog header itself, so downstream consumers get the credible upgrade story without waiting for 1.0. `STANDARDS-CHECKLIST.md` waiver removed in the same change.
