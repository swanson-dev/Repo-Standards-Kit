---
last_updated: 2026-06-01
---

# Next Actions

1. **Land v0.14.0 (discovery capture)** — merge the `feat/discovery-capture` PR → `main`, then
   `git tag v0.14.0 && git push origin v0.14.0` on the merge commit (fires `release.yml`). Verify
   PyPI serves 0.14.0 and the wheel bundles the discovery payload.
2. **Walk a downstream repo through capture** — drop a real PDF/JSON into a freshly adopted repo's
   discovery intake, run `/capture-discovery` → `/promote-discovery`, and capture any friction as
   template/ADR adjustments.
3. **Backlog (unscheduled):** external-link liveness check, doc-freshness reporting, a `new-skill`
   scaffolder. Pick one when starting the next slice.
