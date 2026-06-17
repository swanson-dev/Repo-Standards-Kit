<!--
docs/04-api-and-integrations.md
  Required (application, library, data, documentation)
  Expected (infra)
For libraries: this is the public API contract.
For applications: this is the consumer-facing surface + dependencies.
For data: this is sources + sinks (input contracts + output contracts).
For documentation: this is linked source repos, canonical references, and upstream/downstream doc contracts.
-->

# API and Integrations

## Public surface

<!-- The contract consumers can rely on. Reference code or generated docs; don't duplicate signatures here. -->

## Consumers

<!-- Who calls us. Listed so breaking changes can be coordinated. -->

| Consumer | What they use | Coordination contact |
|---|---|---|

## Integration contracts

<!-- For each external system we call or are called by: protocol, auth, error semantics, retry policy, idempotency. -->

### <Integration A>

- **Protocol:** <REST / gRPC / message bus / file drop / …>
- **Auth:** <mechanism>
- **Idempotency:** <key, scope>
- **Retry policy:** <policy>
- **Error model:** <how errors are signaled and what consumers should do>

## Versioning

<!-- How the API surface is versioned. For libraries, point to docs/versioning-policy.md. -->

## Error model

<!-- Shape of errors consumers will see. Codes, messages, retriability hints. -->
