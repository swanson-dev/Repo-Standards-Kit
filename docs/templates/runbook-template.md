<!--
docs/06-runbook.md — Required (application, infra, data), N/A (library, documentation unless the docs site has operations)
For the on-call human or AI agent at 2am. Optimize for "I am tired and need to fix this fast."
-->

# Runbook

## Start / stop

### Local

```
<command to start locally>
<command to stop>
```

### Each environment

| Environment | Start | Stop | Notes |
|---|---|---|---|

## Health checks

- **Liveness:** <endpoint or signal> — green means: <…>
- **Readiness:** <endpoint or signal>
- **Dashboards:** <links>
- **Alerts:** <links>

## Common incidents

### <Incident: short symptom>

- **Symptom:** <what someone observes>
- **Likely cause:** <one or two leading hypotheses>
- **Diagnosis:** <how to confirm>
- **Mitigation:** <safe first steps>
- **Resolution:** <durable fix or escalation>

## Escalation

| Severity | Who to page | Channel | SLA |
|---|---|---|---|

## Backups and recovery

<!-- What's backed up, where, how to restore, last tested when. -->
