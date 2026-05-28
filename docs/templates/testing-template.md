<!--
docs/07-testing.md
  Required (application, library, data)
  Expected (infra — focus on drift detection and preview-plan)
The point of this doc is to make tests reproducible and to declare what coverage means.
-->

# Testing

## Test pyramid for this repo

<!-- Layers, what each catches, rough ratio. Not all repos need all layers. -->

| Layer | Tooling | What it catches | Rough share |
|---|---|---|---|
| Unit | <e.g. Vitest> | logic errors | 70% |
| Integration | <e.g. Pytest + testcontainers> | wiring + contracts | 20% |
| End-to-end | <e.g. Playwright> | user flows | 10% |

## Coverage targets

<!-- A target with teeth. "100%" is rarely the right answer; pick something defensible. -->

- Line coverage target: <e.g. 80%>
- Branch coverage target: <e.g. 70%>
- Critical paths: 100% (list them)

## How to run locally

```
<command>
```

## CI

<!-- Which workflow runs which tests. Link to .github/workflows/. -->

## Flaky-test policy

<!-- What happens when a test goes red intermittently? Quarantine rules, owner, time-to-fix SLA. -->

## Test data

<!-- Fixtures, seeding, secrets policy for tests. -->
