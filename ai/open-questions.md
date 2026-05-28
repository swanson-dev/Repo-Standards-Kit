# Open Questions

## Q-1: Which Slice 2 Skills should ship first?

- **Status:** open
- **Blocking:** Slice 2 plan-phase. Choosing the first Skills shapes how much surface the Hooks need to cover.
- **Context:** The kit's templates and contracts are precise enough to scaffold. The remaining design choice is *which* scaffolding to automate first — the things downstream repos will do most often.
- **Candidate answers:**
  - **scaffold-new-repo** — bootstrap a fresh repo with profile prompt + template copy. Highest leverage (one-shot adoption) but heaviest to build.
  - **new-adr** — auto-number, fill frontmatter, drop the user into the body. Daily use. Easiest to build.
  - **new-rfc** — same shape as new-adr but creates the folder.
  - **update-handoff** — Stop-hook variant that drafts `ai/handoff.md` from the session transcript.
  - **promote-discovery** — list `status: raw` files and offer to flip with `promoted_to:`.
- **Resolution:** TBD in Slice 2 discuss-phase.

## Q-2: What's the kit's distribution mechanism (Slice 3)?

- **Status:** open
- **Blocking:** Slice 3 in full. Also affects whether we keep `docs/templates/` colocated or split it into a separate distributable.
- **Context:** Downstream repos need to (a) initially adopt the kit and (b) stay current as the kit evolves. Three credible options: a Claude Code plugin, a GitHub template repo, or a `degit`-style copy script. Each implies a different upgrade story.
- **Candidate answers:**
  - **GitHub template repo + manual sync** — simplest. Lowest barrier; weakest upgrade story.
  - **Claude Code plugin** — aligns with Slice 2 Skills; ties distribution to one tool.
  - **Copy script** (`npx repo-standards init`) — tool-neutral; introduces a maintained CLI.
  - **Hybrid:** GitHub template repo for initial adoption + a Skill (Slice 2) for in-place upgrades.
- **Resolution:** Open an RFC under `docs/rfcs/` when Slice 2 is far enough along to inform the distribution choice.

## Q-3: Should the kit ship a CHANGELOG.md before 1.0.0?

- **Status:** open
- **Blocking:** the upgrade-path verification step in `versioning-policy.md`.
- **Context:** Pre-1.0, the kit may break minor versions; a CHANGELOG documents that explicitly. Currently waived in `STANDARDS-CHECKLIST.md` as "starts at first tagged release."
- **Candidate answers:**
  - Start CHANGELOG at v0.1.0 (recommended on reflection — gives downstream consumers a credible upgrade story even pre-1.0).
  - Keep waived until v1.0.0.
- **Resolution:** decide before tagging v0.1.0 in Next Action 3.
