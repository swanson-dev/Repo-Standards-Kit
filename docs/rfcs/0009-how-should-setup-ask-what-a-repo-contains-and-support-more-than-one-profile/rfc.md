---
status: Concluded
opened: 2026-10-15
closed: 2026-10-17
owner: Josh Swanson
time_box: 2 days (prototype the menu and wizard + review)
---

# 0009. How should setup ask what a repo contains and support more than one profile?

## Question

How should setup ask what a repo contains, allow more than one kind of content in a single repo, and spare users from memorizing commands, flags, and profile names?

## Why now

The owner's biggest complaint about the kit is that setting it up isn't intuitive:

- Running `standards` with no arguments exits with an error instead of offering choices.
- `init` and `adopt` both require `--profile` with exactly one of five names, and the names are hard to remember.
- [`docs/STANDARDS.md`](../../STANDARDS.md) says "Each repo declares exactly one profile," but real repos often hold more than one kind of content, such as an application plus its data pipelines.
- Application and infrastructure are separate profiles, although most infrastructure lives beside the app it deploys.
- After setup, the adopter still copies their profile's rows from the `docs/STANDARDS.md` matrix into `docs/STANDARDS-CHECKLIST.md` by hand.

[RFC-0008](../0008-how-should-the-kit-split-and-distribute-its-repo-content-and-agent-tooling/rfc.md) puts the setup flow in the plugin as well as the CLI, so both front doors need one design. This RFC follows RFC-0007 (automation) and RFC-0008 (distribution).

## Approach

- Trace how a profile flows through the code today.
- Design a terminal menu and setup wizard within the kit's zero-dependency rule.
- Design combinable profiles that stay compatible with existing adopters.

On 2026-10-15 the owner decided that the profile matrix lives as data in the CLI, with a test that keeps the `docs/STANDARDS.md` table in sync. Parsing the table at setup time was ruled out because it breaks whenever an adopter edits or reformats their copy. On 2026-10-17 the owner merged the `infra` profile into `application`, leaving four profiles (see design section 4). The same day the owner tried the throwaway prototype in [`artifacts/prototype/`](artifacts/prototype/NOTES.md) and approved the menu. The owner kept both places where the prototype had departed from this RFC, which the design below now includes, and concluded the RFC.

## Findings

### A profile is a label that flows through six places

| Where | Today |
|---|---|
| `src/standards/cli.py` | `--profile` is required on `init` and `adopt` and takes one of five names |
| `src/standards/marker.py` | `.standards-kit.json` stores `"profile": "library"` |
| `src/standards/init.py` | substitutes the name into `docs/STANDARDS-CHECKLIST.md` |
| `scripts/standards-check/checks/structural.py` | reads `**Profile:**` and keeps only the first word (`.split()[0]`) |
| `src/standards/doctor.py` | tests membership in fixed sets to choose recommendations |
| `src/standards/update.py` | carries the marker's value forward |

The profile does not change which files are copied; only the checklist is profile-templated.

### The matrix is applied by hand

The checklist's Profile-required and Profile-expected sections tell the adopter to copy rows from the `docs/STANDARDS.md` matrix. `init` leaves those rows as placeholders that the waiver check skips. A fresh repo passes CI, but the profile's real requirements aren't recorded until someone copies them in.

### Setup has two commands for one job

`init` refuses an already-adopted repo, and any differing pre-existing file unless `--force`. `adopt` refuses an already-adopted repo but never overwrites: it writes `.kit-` sidecars on conflicts. On an empty folder the two produce the same result, so the choice between them only matters for a deliberate `--force` re-initialization.

### Bare `standards` errors

`add_subparsers(required=True)` makes `standards` with no arguments exit with "the following arguments are required: command".

### Zero dependencies limits the prompt style

Prompts must use stdlib `input()`: numbered choices, with no arrow-key menus.

### The new-doc scripts treated flags as titles

`new-rfc.py --help` and `new-adr.py --help` created an RFC or ADR titled "--help", because both take their first argument as the title. Fixed test-first in the same change as this RFC: `-h`/`--help` now prints usage, and any other title starting with `-` is rejected.

## Proposed design

### 1. Bare `standards` opens a menu

Only in an interactive terminal. Without one (CI, pipes), it prints help and exits non-zero as today, so nothing hangs. The menu reads the repo's state first and recommends one action:

```text
Repo-Standards-Kit 1.4.0 · E:\Projects\my-app
This repo isn't set up yet.

  1) Set up this repo        ← recommended
  2) Check / fix this repo
  3) Create an AI skill
  q) Quit
>
```

For a repo that is already set up, the choices become: check / fix, update to the installed kit version (shown, and recommended, only when the repo is behind), change what this repo contains, and create an AI skill.

### 2. One setup, no init-versus-adopt choice

"Set up this repo" always uses `adopt`'s non-destructive behavior, which matches `init` on an empty folder. `init --force` stays for deliberate re-initialization.

### 3. Ask what the repo contains

```text
What does this repo contain? (pick any, comma-separated)
  0) Documentation only
  1) Application     an app, service, or IaC
  2) Library         a reusable package others import
  3) Data            pipelines, models, data contracts
  Suggested from this repo: 1   (Dockerfile, infra/main.tf)
> [1]
>
```

- Every repo already gets the documentation core, so "documentation plus an application plus data pipelines" is `1, 3`.
- Enter accepts the default in brackets: the current answers when changing what a repo contains, otherwise the suggestions, otherwise documentation only. People press Enter expecting to accept what's on screen.
- `0` means documentation only: the code lives elsewhere, so the repo also gets `docs/source-map.md`. Documentation only cannot be combined with the others.
- Suggestions come from a few file signals, such as a `Dockerfile` or Terraform files for an application, or `dbt_project.yml` for data. The user confirms them; nothing is applied silently.
- Setup shows a one-screen summary before writing anything.

Scripts and CI keep using flags, and `--profile` now accepts a comma list: `standards adopt --profile application,data .`

Setup also asks which agents the team uses (Claude, Copilot), suggesting the ones it finds on this machine, and records the answer as `agents` in `.standards-kit.json`. The answer picks the repo's one hook file: `.claude/settings.json` when Claude is in the list, since every Copilot host reads it too, or `.github/hooks/standards.json` for Copilot alone (RFC-0007 test B2). The owner asked for this on 2026-10-16; `init` and `adopt` already take it as `--agents claude,copilot`, with detection as the default.

### 4. Four profiles, and they combine

- **Infra merges into application.** The owner decided on 2026-10-17 that infrastructure isn't a separate profile; the wizard's "Application" means an app, service, or IaC. The profiles become application, library, data, and documentation. The application column of the matrix is unchanged, and `docs/environments.md` becomes an application extra. An IaC-only repo now takes application's tiers, so `01-prd.md`, `04-api-and-integrations.md`, and `07-testing.md` become Required for it; the owner accepted that cost for one fewer choice.
- **Marker.** Write `"profiles": ["application", "data"]` and keep `"profile"` as the first entry, so older CLIs still read a valid single profile. Read `profiles` when present, otherwise `[profile]`.
- **Checklist header.** Write `**Profile:** application + data`. Older checkers keep only the first word and still see a valid profile; newer ones parse the whole list.
- **Requirements combine by strongest tier.** Required beats Expected, which beats Optional, which beats N/A. For a library plus data, `01-prd.md` is Expected (data) even though it is Optional for a library. Profile extras add up.
- **`doctor`** checks whether the profiles overlap its sets instead of whether one profile is in them.
- **`docs/STANDARDS.md`** changes "Each repo declares exactly one profile" to one or more, with documentation only as the exclusive choice.

### 5. Create and tick the docs the profiles need

Instead of leaving placeholders, setup creates the combined Required and Expected docs from their templates, ticks them in the checklist, and lists the profile extras. A fresh repo stays CI-green, and every doc the profiles need exists from the start, ready for RFC-0007's hooks to keep current. Existing docs are never overwritten. This automates step 7 of the adoption procedure in `docs/STANDARDS.md`, which today the adopter does by hand.

### 6. Check, fix, and change

- **Check / fix** runs `standards check` and `doctor`, shows the findings, and offers `update` when the repo is behind the installed kit. The CLI has no auto-fixer; in the plugin, the agent is the fixer, and the setup skill hands it the findings.
- **Change what this repo contains** re-asks the profile question with the current answers preselected, then updates the marker, the checklist, and any newly required docs. Together with setup on an existing repo, this covers "add to a repo."

### 7. Two front doors, one engine

Per RFC-0008, the plugin's setup skill inspects the repo, proposes what it contains in conversation, and calls the CLI with explicit flags. The terminal menu is the same flow for people without an agent. Both end in the same CLI calls, so their behavior can't drift apart.

### 8. Compatibility

- Old markers with a single `profile` keep working, and new markers stay readable by older CLIs.
- `--profile` still accepts a single name.
- `infra` stays accepted as an alias for `application` in `--profile`, markers, and checklist headers, so existing infra adopters keep working; `update` rewrites it to `application`.
- Allowing more than one profile is additive, so this ships as a minor release.

## Recommendation

Give bare `standards` a state-aware menu, replace the init-versus-adopt choice with one non-destructive setup, and ask what the repo contains with descriptions and suggestions. Make profiles combinable by strongest tier, using marker and checklist formats that older versions still read. Have setup create and tick the docs the chosen profiles need instead of leaving placeholders. Merge infra into application. Concluded 2026-10-17 after the owner tried the prototype.

## Follow-ups

- **ADR to write:** yes, [ADR-0025](../../decisions/0025-set-up-repos-through-a-guided-menu-with-four-combinable-profiles.md). It supersedes ADR-0003 (the profile model, which defined `infra`) and replaces the one-profile rule. ADR-0021 (the documentation profile) stands. ADR-0022 and ADR-0024 are reserved for the parked changelog branch and RFC-0008. ADR-0022 to ADR-0024 are already reserved.
- **Implementation plan changes:** added "M9 — Setup wizard" to `docs/05-implementation-plan.md`. The terminal menu and wizard don't depend on distribution; the plugin's setup skill (section 7) lands with RFC-0008's distribution work.
- **New open questions:** none.
- **Discovery to promote:** none
