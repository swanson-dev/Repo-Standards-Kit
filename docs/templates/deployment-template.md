<!--
docs/09-deployment.md — Required (application, infra, data), N/A (library)
For libraries, publishing policy lives in CHANGELOG.md + docs/versioning-policy.md.
-->

# Deployment

## Environments

| Environment | Purpose | URL / identifier | Owner |
|---|---|---|---|

## Pipeline

<!-- Stages from commit to production. Cite the workflow file. -->

```mermaid
flowchart LR
  Commit --> CI[CI checks] --> Build --> Stage --> Prod
```

- **Workflow:** `.github/workflows/<name>.yml`
- **Required approvals:** <…>
- **Auto-deploy gates:** <…>

## Rollback

- **Mechanism:** <e.g. redeploy previous tag, feature flag, blue/green swap>
- **RTO:** <minutes>
- **Last drill:** YYYY-MM-DD

## Change windows

- **Routine deploys:** <hours / days>
- **Freeze windows:** <when, why>

## Feature flags

- **System:** <e.g. LaunchDarkly, ConfigCat, in-house>
- **Naming convention:** <…>
- **Cleanup policy:** <flags older than N days require an issue>
