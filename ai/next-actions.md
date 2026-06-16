---
last_updated: 2026-06-16
---

# Next Actions

1. **Review and commit the v1.1.0 adoption-assistant and AI-continuity slice** - confirm the diff is limited to `doctor`, `new-skill`, command discovery, optional templates, continuity hooks/commands, and the related docs/decision records.
2. **Publish v1.1.0 if this slice is approved for release** - follow `docs/RELEASING.md` after final review; local build artifacts already proved the package can build.
3. **Pilot `standards doctor --recommend` and `standard-get-session-context` in one real downstream repo** - capture whether recommendations and context summaries are useful, noisy, or missing important signals.
