<!--
docs/03-data-model.md — Required (data), Expected if state-bearing (application), Optional (infra, documentation), N/A (library)
Describes the entities the system owns, their invariants, and how they change over time.
-->

# Data Model

## Entities

<!-- One subsection per significant entity. Keep field-level schemas in code; this doc explains intent. -->

### <Entity A>

- **Purpose:** <one sentence>
- **Key fields:** <name, type, meaning>
- **Owner:** <team or service>

## Invariants

<!-- What MUST always be true about the data. Enforced where? -->

- <invariant — enforced by: <DB constraint | service-layer check | scheduled job>>

## Ownership

<!-- Who can write each entity. Who reads. Who governs schema changes. -->

| Entity | Owner | Writers | Readers |
|---|---|---|---|

## Lifecycle

<!-- Creation, mutation, archival, deletion. Retention requirements. -->

## Migration policy

<!-- How schema changes are introduced (online/offline, additive-first, backfill strategy). Link to deployment doc for the mechanics. -->
