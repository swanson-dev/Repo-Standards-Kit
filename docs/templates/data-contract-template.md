<!--
docs/data-contracts/<dataset>.md — data-profile extra.
One file per dataset (input or output) that this repo owns or consumes as a stable contract.
-->

# Data contract: <dataset name>

## Identity

- **Dataset:** <fully qualified name>
- **Owner:** <team>
- **Producer:** <repo / system>
- **Consumers:** <list>

## Schema

<!-- Field-level schema. Link to a schema file in code if one exists. -->

| Field | Type | Required | Description |
|---|---|---|---|

## Semantics

<!-- What each row means. What it does NOT mean. Common misuses to avoid. -->

## Freshness SLO

- **Target:** <e.g. updated within 1 hour of source>
- **Maximum acceptable lag:** <e.g. 4 hours>
- **Detection:** <how lag is monitored>

## Lineage

<!-- Upstream sources and downstream consumers. Diagram if non-trivial. -->

## Change management

- **Backward-compatible changes:** <e.g. added optional fields — no notice required>
- **Breaking changes:** <e.g. removed/renamed fields — N days notice via <channel>>
- **Versioning:** <if this dataset is versioned, how>

## Data quality checks

- <check> — frequency: <…> — alert: <…>
