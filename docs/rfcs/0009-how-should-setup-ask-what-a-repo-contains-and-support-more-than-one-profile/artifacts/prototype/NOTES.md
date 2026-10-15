# RFC-0009 prototype notes

**Throwaway.** Once [RFC-0009](../../rfc.md) concludes, delete this folder, or move `setup_logic.py` into `src/standards/` and delete the rest.

## Question

Does a state-aware menu plus "What does this repo contain?" make setting up the kit easy, with no commands, flags, or profile names to remember? Do combined profiles produce sensible requirements?

## Run

From the repo root, in a real terminal:

```bash
python docs/rfcs/0009-how-should-setup-ask-what-a-repo-contains-and-support-more-than-one-profile/artifacts/prototype/standards_menu_prototype.py
```

- Add a repo path to point it at another repo; that repo is only read, never written.
- Add `--as new`, `--as adopted`, or `--as behind` to see each menu without a repo in that state.

## Things to try

- `--as new` on this repo, then on a real app repo. Are the suggestions right?
- Pick `1,3` (application plus infrastructure). Are the combined Required and Expected docs what you'd expect?
- Type `0,1`. Is the "documentation only can't be combined" message clear?
- `--as behind`. Is updating the obvious next step?
- `--as adopted`, then "Change what this repo contains", and add infrastructure. Is the list of changes readable?
- Pipe it (`echo | python .../standards_menu_prototype.py`). It should refuse to show a menu without a terminal.

## Where it departs from the RFC text

- **Enter accepts the default shown in brackets**, and `0` means documentation only. The RFC says Enter means documentation only, but with suggestions on screen, people will press Enter expecting to accept them.
- **"Update" appears only when the repo is behind.** The RFC lists it for every set-up repo.

## Observations from scripted runs (2026-10-15)

- On this repo it suggests `library` from `pyproject.toml`, which is the kit's real profile, and finds all four docs a library needs already present.
- A folder with a `Dockerfile` and `infra/main.tf` gets the suggestion `1, 3`, matching the RFC's mock.
- Application plus infrastructure needs no numbered doc beyond what application alone requires; infrastructure only adds `docs/environments.md`. Changing a library to library plus infrastructure changes six tiers.
- Piped input with no terminal exits 2 without showing a menu.

## Verdict

_To fill in after trying it: what felt right, what felt wrong, and what changes in RFC-0009._
