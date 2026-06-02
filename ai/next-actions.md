---
last_updated: 2026-06-02
---

# Next Actions

1. **Review + merge PR #18 (milestone roadmap)** — `feat/roadmap-milestones` → `main`. Adds the
   template `## Roadmap` section + dogfood `docs/05-implementation-plan.md` (RFC-0003, ADR-0016).
   It bundles the unrelated Node 24 CI chore (`6497ffd`); split it onto its own branch first if a
   clean, atomic PR is wanted.
2. **Cut v0.16.0** — after merge: bump `src/standards/__about__.py` → `0.16.0`, promote CHANGELOG
   `[Unreleased]` → `[0.16.0]`, bump the `AGENTS.md` Kit-version line + agents-core sentinel, and
   also bump the (coherence-unguarded) `docs/STANDARDS.md` + `docs/STANDARDS-CHECKLIST.md` version
   strings. Run `python tools/check_version_coherence.py`, then `git tag v0.16.0` on the merge
   commit (fires `release.yml`); verify PyPI serves 0.16.0.
3. **Backlog (unscheduled):** external-link liveness check, doc-freshness reporting, a `new-skill`
   scaffolder. Pick one when starting the next slice.
