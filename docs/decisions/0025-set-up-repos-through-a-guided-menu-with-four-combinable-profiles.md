---
status: Accepted
date: 2026-10-17
deciders: Josh Swanson
consulted: Claude (RFC-0009 prototype)
informed: Repo-Standards-Kit adopters
---

# 0025. Set up repos through a guided menu with four combinable profiles

## Context and Problem Statement

[ADR-0003](./0003-adopt-repo-profile-model.md) gave every repo exactly one profile (application, library, infra, or data), each with a tier per numbered doc. [ADR-0021](./0021-add-a-documentation-repo-profile.md) added a documentation profile. Setting up the kit means remembering a command, choosing between `init` and `adopt`, and passing `--profile` with one of five names. Running `standards` with no arguments errors. Real repos often hold more than one kind of content, and after setup the adopter still copies the profile's rows from the `docs/STANDARDS.md` matrix into the checklist by hand.

[RFC-0009](../rfcs/0009-how-should-setup-ask-what-a-repo-contains-and-support-more-than-one-profile/rfc.md) traced how a profile flows through the code, designed a menu and setup wizard, and prototyped them. The owner tried the prototype and concluded the RFC on 2026-10-17. The question is how setup should ask what a repo contains, and how a repo can hold more than one kind of content.

## Decision Drivers

- Nobody should need to remember commands, flags, or profile names to set up a repo.
- A repo can hold more than one kind of content.
- The runtime stays zero-dependency, so prompts use the stdlib `input()`.
- Scripts and CI must never hang on a prompt.
- Existing adopters and older CLIs keep working.

## Considered Options

- **Keep flags only** — better help text, same five single profiles.
- **A guided menu over the existing profiles** — easier to start, but one profile per repo.
- **A guided menu with four combinable profiles** — infra merges into application, and profiles combine by strongest tier.

## Decision Outcome

Chosen option: **A guided menu with four combinable profiles**, because it removes everything an adopter has to remember while matching how real repos are built.

- **Menu.** In an interactive terminal, bare `standards` reads the repo's state and offers numbered actions, marking one as recommended: set up, check / fix, change what the repo contains, and create an AI skill. "Update to the installed kit version" appears only when the repo is behind. Without a terminal it prints help and exits non-zero, as today.
- **One setup.** "Set up this repo" always uses `adopt`'s non-destructive behavior. `init --force` stays for deliberate re-initialization.
- **The wizard asks what the repo contains.** Choices are numbered and comma-separated. Suggestions come from file signals such as a `Dockerfile`, Terraform files, or `dbt_project.yml`. Enter accepts the default in brackets: the current answers when changing, otherwise the suggestions, otherwise documentation only. `0` means documentation only, which can't be combined with the others. Setup shows a summary before writing anything. It also asks which agents the team uses and records `agents`, which picks the repo's one hook file (RFC-0007 test B2).
- **Four profiles.** The profiles are application (an app, service, or IaC), library, data, and documentation. Infra merges into application. The application column of the matrix is unchanged, and `docs/environments.md` becomes an application extra.
- **Profiles combine by strongest tier.** Required beats Expected, Optional, and N/A, in that order, and profile extras add up. The marker writes `"profiles": [...]` with `"profile"` kept as the first entry, and the checklist header joins names with ` + `, so older CLIs and checkers still read a valid single profile.
- **The matrix lives in the CLI as data.** A test keeps it in sync with the `docs/STANDARDS.md` table.
- **Setup creates and ticks the docs the profiles need.** It creates the combined Required and Expected docs from their templates instead of leaving placeholders, and never overwrites existing files.
- **Flags stay.** `--profile` accepts a comma list. `infra` stays an alias for `application` in flags, markers, and checklist headers, and `update` rewrites it. The plugin's setup skill (RFC-0008) proposes answers in conversation and calls the CLI with explicit flags, so both front doors share one engine.
- **Release.** All of this is additive, so it ships as a minor release.

### Consequences

- **Good:** Setup needs no commands, flags, or profile names, and a repo can declare everything it contains.
- **Good:** Every doc the profiles need exists from the start, ready for ADR-0023's hooks to keep current.
- **Bad:** An IaC-only repo now takes application's tiers, so `01-prd.md`, `04-api-and-integrations.md`, and `07-testing.md` become Required for it. The owner accepted that cost for one fewer choice.
- **Bad:** The matrix exists in two places, held together by a sync test.
- **Neutral:** `infra` survives only as an alias for compatibility.

## More Information

- Related RFC: `docs/rfcs/0009-how-should-setup-ask-what-a-repo-contains-and-support-more-than-one-profile/` (concluded 2026-10-17). The prototype and the owner's verdict are in its `artifacts/prototype/`.
- Supersedes: ADR-0003. ADR-0021 (the documentation profile) stands.
- Related: ADR-0013 (non-destructive `adopt`), ADR-0023 (block-once Stop hooks).
- Implementation: milestone M9 — Setup wizard in `docs/05-implementation-plan.md`.
