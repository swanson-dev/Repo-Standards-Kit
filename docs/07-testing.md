# Testing

The kit has no runtime, so there are no unit tests in the traditional sense. Verification is **structural** (does the artifact set match the spec?) and **walkthrough** (does adopting the kit actually work for the four profiles?).

## Test pyramid for this repo

| Layer | What it catches | Tooling |
|---|---|---|
| Structural lint | Filename conventions, status vocabulary, frontmatter presence | `.github/workflows/repo-standards.yml` (Phase E) |
| Opt-in link liveness | Stale or missing external `http(s)` destinations | `standards check --external-links` |
| Opt-in freshness report | Current age/status for rolling `ai/` docs | `standards check --freshness-report` |
| Adoption diagnostics | Can adopters identify marker, check, sidecar, managed-region, and optional-lane issues without mutation? | `standards doctor --recommend` + CLI tests |
| AI continuity | Can hooks and commands read context, refresh handoffs, and capture compact snapshots safely? | `scripts/session-context/test_session_context.py`, `scripts/update-handoff/test_update_handoff.py` |
| Command discovery | Can adopters find the right command and command-specific examples? | `standards commands`, `standards help <command>` |
| Optional lane payload | Do optional discovery/design/support templates ship without becoming required scaffold output? | Payload and init tests |
| Self-application check | Does the kit conform to its own library-profile requirements? | The kit's own `STANDARDS-CHECKLIST.md` parsed by the same workflow |
| V1 readiness | Can generated downstream repos for every profile pass init/check/update/check? | `python tools/check_v1_readiness.py` |
| Walkthrough | Can a contributor adopt the kit in a real repo of each profile? | Manual, recorded in `docs/discovery/` of a real downstream repo |
| Cross-tool agent check | Do Claude Code, Copilot, and one other tool all land on `AGENTS.md` and follow the canonical reading order? | Manual, per release |

## Coverage targets

- **Structural lint:** 100% of files matched by the workflow rules.
- **Self-application:** every Required and Expected doc for the `library` profile present (or waived) in this kit.
- **V1 readiness:** generated downstream fixture repos for all four profiles pass `init`, `check`, `update`, and `check` again before the kit cuts v1.0.0.
- **Walkthrough:** at least one real downstream repo per profile over time; useful evidence, but not a v1.0.0 release blocker.

## How to run locally

The standards check workflow can be run manually once Phase E lands:

```
gh workflow run repo-standards.yml
```

Or run the underlying script locally (Phase E adds the script under `scripts/`).

External-link liveness is intentionally opt-in because it depends on the network:

```
python scripts/standards-check/check.py --external-links
```

Freshness status reporting is also opt-in:

```
python scripts/standards-check/check.py --freshness-report
```

The adoption doctor is read-only:

```
standards doctor --recommend .
```

The session context hook is also read-only and advisory:

```
python scripts/session-context/session_context.py --hook
```

The v1 readiness gate validates generated downstream repos for all profiles:

```
python tools/check_v1_readiness.py
```

## CI

`.github/workflows/repo-standards.yml` runs the structural lint and self-application check on every push and PR to `main`. `.github/workflows/kit-guards.yml` runs version coherence and the v1 readiness gate. `.github/workflows/external-links.yml` is manual-only for networked external-link audits.

## Flaky-test policy

Structural lint should never be flaky — it's deterministic markdown parsing. If a check goes red intermittently, treat it as a real bug (likely a parser ambiguity or a frontmatter edge case) rather than a transient.

External-link liveness can be affected by network availability or remote service behavior; run it deliberately when validating release notes or docs with important outbound links.

## Test data

The kit is its own test data — the structural lint runs against this very repo's files. The kit therefore must always pass its own standards check before a release tag is cut.
