---
status: Concluded
opened: 2026-06-02
closed: 2026-06-02
owner: swanson-dev
time_box: 0.5 day
---

# 0003. How should the kit standardize a longitudinal milestone roadmap

## Question

How should the kit give a repository a standard home for a longitudinal, multi-milestone
roadmap, given it already ships per-effort sequencing in `05-implementation-plan.md`?

## Why now

The kit's thesis is that it standardizes the artifacts teams otherwise improvise
inconsistently — yet it improvises its own roadmap in two drifting places: the roadmap table
in [`README.md`](../../../README.md) and the "queued slices" prose in
[`AGENTS.md`](../../../AGENTS.md). Neither is a defined artifact; both must be hand-kept in
sync.

Downstream repos have no standard place to answer "where is this repo headed over the next
several milestones." The two planning surfaces that exist cover different horizons:
[`ai/next-actions.md`](../../../ai/next-actions.md) is capped at **7 tactical steps**
(`docs/STANDARDS.md` → "maximum 7 entries"), and
[`docs/05-implementation-plan.md`](../../templates/implementation-plan-template.md) slices a
**single build effort**. The longitudinal milestone horizon — the one this kit itself needs —
has no contract. This is genuinely-future work, so per the `AGENTS.md` end-of-session contract
it opens with an RFC before any change.

## Approach

1. Map the existing planning surface across horizons (tactical → per-effort → longitudinal) to
   locate the actual gap rather than restate one already covered.
2. Weigh three artifact shapes against the kit's lean philosophy, its profile/tier model, and
   its SemVer cost: (a) a new standalone roadmap doc above `05-plan`; (b) extend `05-plan`;
   (c) a minimal root `ROADMAP.md` peer of `CHANGELOG.md`.
3. Choose the section structure that prevents two horizons (slow milestones, fast slices) from
   drifting once they share one file.

## Findings

- **`05-implementation-plan.md` already provides sequencing**, not just a task list: vertical
  slices with owners and per-slice verification, plus a dependency/critical-path Mermaid graph.
  The missing piece is purely the *longitudinal milestone* horizon above it — so a brand-new
  artifact would duplicate most of `05-plan`'s machinery to add one table.
- **The kit's own improvisation is the proof of need.** A README roadmap table plus an
  `AGENTS.md` "queued slices" list, kept in sync by hand, is exactly the inconsistency the kit
  exists to remove — and it has no standard home to remove it into.
- **A new top-level or numbered artifact is not free.** It costs a profile-matrix row, a
  likely new `standards-check` rule, and adopter cognitive load. Extending `05-plan` costs only
  a template-structure change — a Minor bump under the kit's
  [versioning policy](../../STANDARDS.md) — and requires **zero** new profile gating, because
  `05-plan` is already tiered (Expected for application/infra/data, Optional for library).
- **The one risk of folding two horizons into one file — they change at different speeds — is
  structural, so it gets a structural fix.** Binding the existing `## Slices` section to the
  single milestone marked `active` makes the milestone table the slow strategic layer and
  `## Slices` the fast layer for exactly one milestone. There is then only one place the
  fast-moving detail can live, enforced by an "exactly one `active`" invariant rather than by
  discipline.

## Recommendation

**Concluded → extend `05-implementation-plan.md`; do not add a new artifact.** Add a
`## Roadmap` section to `docs/templates/implementation-plan-template.md`, above `## Approach`,
containing a milestone table (`Milestone | Outcome | Target | Status`) with the status
vocabulary `planned | active | shipped | dropped` and an **exactly-one-`active`** invariant;
an "Active milestone" pointer line ties the table to the breakdown below. Reframe the existing
`## Approach` / `## Slices` / `## Sequencing` sections as the breakdown of the active
milestone. No new profile-matrix row and **no new `standards-check` rule** — internal section
structure of numbered docs is intentionally not linted (YAGNI; the existing placeholder check
already prevents committed scaffolding). Ship as a Minor version bump. Dogfood it in this repo:
create `docs/05-implementation-plan.md` (this kit is `library`, where `05-plan` is Optional, so
this is allowed) from the README/`AGENTS.md` roadmap as the single source of truth, and reduce
the README table to a condensed view that links to it.

## Follow-ups

- **ADR to write:** yes — `docs/decisions/0016-add-roadmap-section-to-implementation-plan.md`,
  recording the decision and *why extend vs. new artifact* so the road not taken is captured.
- **Implementation plan changes:** edit `docs/templates/implementation-plan-template.md` (add
  `## Roadmap`); create `docs/05-implementation-plan.md` (dogfood, migrating the README +
  `AGENTS.md` roadmap); no `docs/STANDARDS.md` change (it is a tier matrix with no per-doc description; the template
  comment is the doc's structural spec); a Minor release cut moves the version coherently across `src/standards/__about__.py`,
  the `CHANGELOG.md` top entry, and the `AGENTS.md` kit-version (enforced by
  `tools/check_version_coherence.py`).
- **New open questions:** none. A section-presence lint for the `## Roadmap` block is
  explicitly deferred as YAGNI; revisit only if drift is observed in practice.
- **Discovery to promote:** none.
