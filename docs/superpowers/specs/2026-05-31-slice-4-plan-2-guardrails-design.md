# Slice 4 Plan 2 Design — Guardrails (version-coherence, freshness teeth, discovery)

**Status:** Approved (brainstorming, 2026-05-31)
**Slice:** 4 (deeper CI enforcement). **Plan:** 2 of 3.
**Builds on:** Plan 1 (the `checks/` package + kit-vs-adopter severity model, shipped as v0.7.0). Plan 2 adds release/process guardrails.

## Goal

Three independent "guardrails," all small:

1. **Version-coherence** (kit-only) — a tool + CI/release gates that keep the kit's version strings in lockstep and block a mis-tagged publish.
2. **AI-freshness teeth** — tighten the handoff staleness threshold and make the Stop-hook nudge louder, so `ai/` docs don't drift.
3. **Discovery `promoted_to`-existence** — a shipped check that a promoted discovery item points at a real file.

Ships as **v0.8.0** (a new adopter-facing discovery check + a stricter freshness warning = minor bump — which the new coherence guard then self-verifies).

## Decisions (from brainstorming)

1. **Coherence lives in a standalone tool + release gate**, not the shipped check package: `repo-standards.yml` ships to adopters (they lack `__about__.py`), so the kit-only guard goes in a **non-shipped** `kit-guards.yml` (PR-time) plus a `release.yml` step (tag-time).
2. **Freshness thresholds → 14d / 5d**: leave `CURRENT_STATE_STALE_DAYS` at 14; lower `HANDOFF_STALE_DAYS` 7 → 5 (the handoff is the per-session artifact that goes stale fastest). Stays a **warning** — staleness must never fail CI for calendar time.
3. **`tests/test_version.py` refactors to the coherence check** — replace the hardcoded `assertEqual(__version__, "0.7.0")` with `assert find_incoherences(repo) == []`. No literal to bump each release.
4. **Discovery check is shipped** (adopters use `docs/discovery/` too): a new `checks/discovery.py` in the Plan 1 framework, error-in-kit / warn-in-adopter via `resolve_severity`.
5. **Release gate also asserts tag == version** (`--tag` arg), closing the mis-tagged-publish gap that exists today.

## § A — Version-coherence (kit-only, NOT shipped to adopters)

### A1. `tools/check_version_coherence.py` (new)

Source of truth: `src/standards/__about__.py` `__version__` (pyproject reads it dynamically via `[tool.hatch.version]`).

```python
def read_about_version(root: Path) -> str | None: ...
def find_incoherences(root: Path, tag: str | None = None) -> list[str]:
    """Return human-readable mismatch messages; empty list == coherent."""
```

`find_incoherences` asserts `__about__` equals every derived site:
- CHANGELOG.md top version section heading `## [x.y.z]` (first one that isn't `[Unreleased]`).
- `AGENTS.md` `Kit version: **x.y.z**` line.
- `AGENTS.md` sentinel tag `<!-- BEGIN kit-managed: agents-core (vx.y.z) -->`.
- If `tag` is given (e.g. `v0.8.0`): the tag with its leading `v` stripped must equal `__about__`.

Each mismatch is one message like `AGENTS.md Kit-version 0.7.0 != __about__ 0.8.0`. `main()` prints them and exits `1` if any, else `0`. Pure stdlib; importable for tests.

### A2. `.github/workflows/kit-guards.yml` (new — must NOT be added to the payload manifest)

A kit-only workflow, `on: {push: {branches:[main]}, pull_request: {}}`, `permissions: contents: read`, one job `coherence` (`runs-on: ubuntu-latest`): checkout → setup-python → `python tools/check_version_coherence.py`. Because it is not listed in `manifest.py` `PAYLOAD_FILES` (and lives directly under `.github/workflows/`, which is not a wholesale `PAYLOAD_DIR`), adopters never receive it.

### A3. `.github/workflows/release.yml` (modify)

Add a step **before** the build, after checkout/setup-python:
```yaml
      - name: Verify version coherence + tag
        run: python tools/check_version_coherence.py --tag "${{ github.ref_name }}"
```
A mis-tagged or incoherent state now blocks the publish.

### A4. `tests/test_version.py` (refactor)

Replace the hardcoded literal assertion with:
```python
from tools_check import find_incoherences  # via sys.path insert to repo root
...
    def test_kit_version_is_coherent(self):
        self.assertEqual(find_incoherences(REPO_ROOT), [])
```
(Import detail handled in the plan — likely `sys.path.insert` of the repo root + `from tools.check_version_coherence import find_incoherences`, or import by file path. The plan picks one.) The test no longer needs editing on each release.

## § B — AI-freshness teeth

### B1. `scripts/standards-check/checks/structural.py` (modify)

Change `HANDOFF_STALE_DAYS = 7` → `5`. Leave `CURRENT_STATE_STALE_DAYS = 14`. This only tightens a **warning**; the kit's own `ai/handoff.md` is dated within 5 days so it stays green.

### B2. `scripts/update-handoff/update_handoff.py` `--check` (modify)

Today the Stop-hook `--check` nudges only when there are commits/modified files since the last handoff. Strengthen it:
- Make the nudge wording more prominent (clear call to run `/update-handoff`).
- **Also** fire the nudge when the handoff itself is stale (its `written` date older than `HANDOFF_STALE_DAYS = 5`), even with no pending work — so a long-lived session that stopped committing still gets reminded.
- Hook mode invariants unchanged: still exits 0 always (never breaks the session), still silent when there's genuinely nothing to nudge about.

Update `scripts/update-handoff/test_update_handoff.py` to cover the new staleness trigger and keep the existing behavior green.

## § C — Discovery `promoted_to`-existence (shipped check)

### C1. `scripts/standards-check/checks/discovery.py` (new)

For every markdown file under `docs/discovery/` (excluding `README.md` and any `templates/` subtree, mirroring `promote_discovery.py`'s walk) whose frontmatter is `status: promoted`: the `promoted_to:` value must be a non-empty repo-relative path that exists. Findings:
- missing/empty `promoted_to:` on a promoted item → `discovery` Finding.
- `promoted_to:` path does not exist → `discovery` Finding.

Severity via `resolve_severity("discovery", "error", ctx)` — error in kit, warn in adopters. Reuse the frontmatter-parsing approach already in the package (a small local parser like the other check modules use). Wire `discovery.run` into `check.py` `CHECKS`. Ships to adopters automatically via the wholesale `scripts/` payload walk (asserted by extending the Plan 1 payload test).

### C2. `scripts/standards-check/test_discovery.py` (new)

TDD: a promoted item with an existing target passes; a promoted item with a missing target is flagged (error in kit, warn in adopter, escalatable via override); a `status: raw` item is ignored; missing `docs/discovery/` is silent.

## Components & files

| Path | Action | Responsibility |
|---|---|---|
| `tools/check_version_coherence.py` | new | Kit-only version-coherence tool (`find_incoherences` + CLI + `--tag`). |
| `.github/workflows/kit-guards.yml` | new (NOT shipped) | PR-time coherence gate. |
| `.github/workflows/release.yml` | modify | Add coherence + tag==version gate before build. |
| `tests/test_version.py` | refactor | Assert coherence instead of a hardcoded literal. |
| `scripts/standards-check/checks/structural.py` | modify | `HANDOFF_STALE_DAYS` 7 → 5. |
| `scripts/update-handoff/update_handoff.py` | modify | Louder `--check` nudge + staleness trigger. |
| `scripts/update-handoff/test_update_handoff.py` | modify | Cover the new nudge behavior. |
| `scripts/standards-check/checks/discovery.py` | new | Shipped `promoted_to`-existence check. |
| `scripts/standards-check/test_discovery.py` | new | TDD for the discovery check. |
| `scripts/standards-check/check.py` | modify | Add `discovery.run` to `CHECKS`. |
| `tests/test_payload_includes_checks.py` | modify | Assert `checks/discovery.py` ships. |
| `docs/STANDARDS.md` | modify | Document the discovery check, freshness change, and the coherence guard. |
| `CHANGELOG.md` / `src/standards/__about__.py` / `AGENTS.md` | modify | Bump to v0.8.0 (coherently — the new tool verifies it). |

## Testing strategy

- TDD per unit: `find_incoherences` (tool-level test in `tests/`), the discovery check (`test_discovery.py`), the freshness threshold (covered by the existing structural behavior; the kit stays green), and the hook nudge (`test_update_handoff.py`).
- Dogfood: `python tools/check_version_coherence.py` → coherent at 0.8.0; `python scripts/standards-check/check.py` → 0 errors (the kit's promoted discovery items, if any, must point at real files — fix at source if not); `python tools/run_tests.py` → all suites pass on the CI matrix (py3.9–3.12).
- The coherence tool self-verifies the v0.8.0 bump made in this very plan.

## Out of scope (later / dropped)

- External-link liveness and doc-freshness *reports* (still future).
- Surfacing stale `status: raw` items in CI (kept to the existing SessionStart hook — the monotonic status field already prevents reprocessing).
- Escalating freshness to a CI **error** (rejected: punishes unrelated PRs for calendar time).
- Plan 3: polishing the four skill wrappers + a `/standards-check` local-fix command.

## Version

Minor bump → **v0.8.0** (new shipped discovery check + stricter freshness warning; both backward-compatible for adopters since the discovery check defaults to `warn` there).
