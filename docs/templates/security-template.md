<!--
docs/08-security-and-compliance.md
  Required (application, infra, data)
  Expected (library, documentation)
Even minimal repos benefit from a written threat-model summary and a secrets policy.
-->

# Security and Compliance

## Threat model summary

<!-- Two paragraphs maximum. STRIDE-style or attacker-goal-style. Detail belongs in a separate threat-model doc if the system warrants it. -->

- **Assets:** <what we protect>
- **Adversaries:** <who we protect from>
- **Trust boundaries:** <reference 02-architecture.md>
- **Top risks:** <bulleted, ranked>

## Secrets handling

- **Storage:** <Key Vault / AWS Secrets Manager / GitHub Secrets / …>
- **Rotation policy:** <how often, how>
- **Local development:** <how devs get the secrets, how they're scrubbed>

## Authentication and authorization

- **AuthN mechanism:** <…>
- **AuthZ model:** <RBAC / ABAC / scoped tokens / …>
- **Where decisions are enforced:** <code path, middleware, gateway>

## Compliance scope

- **Standards:** <SOC 2 / HIPAA / PCI / GDPR / none — and why>
- **Data classification:** <what data we handle, classification level>
- **Audit logging:** <where, retention>

## Reviews

- **Last security review:** YYYY-MM-DD by <name>
- **Next review due:** YYYY-MM-DD
- **Dependency-scan cadence:** <e.g. weekly via Dependabot / monthly via Snyk>
