# `docs/rfcs/`

**Time-boxed technical investigations.** Each RFC answers a specific question with a recommendation, then exits with a known status. Unlike [`docs/discovery/`](../discovery/) (which is *received* and loose), RFCs are *produced* and strict.

## Format

Each RFC lives in its own folder: `docs/rfcs/NNNN-kebab-case-slug/`. The folder lets benchmarks, screenshots, and prototype artifacts live alongside the prose without polluting `docs/templates/` or the repo root.

```
docs/rfcs/
├── README.md
└── 0001-evaluate-graphql-vs-rest/
    ├── rfc.md
    └── artifacts/
        ├── benchmark.csv
        └── prototype-screenshot.png
```

Template: [`../templates/rfc-template.md`](../templates/rfc-template.md).

## Required structure (in `rfc.md`)

- Frontmatter: `status` (`Open` | `Concluded` | `Abandoned`), `opened`, `closed`, `owner`, `time_box`.
- **Question** — exactly one sentence.
- **Why now** — what's downstream of the answer.
- **Approach** — how the investigation will run.
- **Findings** — what was learned. Cite artifacts in `artifacts/`.
- **Recommendation** — one paragraph.
- **Follow-ups** — ADR to write, plan changes, open questions to track.

## Lifecycle rule

Every RFC must reach **one of three terminal states**:

1. **Concluded** — spawned an ADR (or explicitly noted "no ADR needed; recommendation is informational").
2. **Abandoned** — with a one-sentence reason in the frontmatter.
3. **Open question carried forward** — the central question is moved to [`ai/open-questions.md`](../../ai/open-questions.md), the RFC is `Abandoned`, and the abandonment reason links to the open question.

**RFCs do not sit `Open` indefinitely.** A stale `Open` RFC is a signal to either complete it, abandon it, or move the question to `ai/open-questions.md`.

## When to write an RFC vs. an ADR

- **RFC** = the investigation. "Should we use X? What would Y cost? Is Z feasible?"
- **ADR** = the durable decision. "We will use X."

An RFC typically *spawns* an ADR. The ADR is the lasting record; the RFC is the working record of *how* the decision was reached.
