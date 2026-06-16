# `scripts/session-context/`

Stdlib-only Python script that prints a read-only AI context brief from the
canonical `ai/` files.

## Modes

| Invocation | Mode | What it does |
|---|---|---|
| `python scripts/session-context/session_context.py` | manual | Prints handoff, current-state, next-actions, and open-question highlights. |
| `python scripts/session-context/session_context.py --hook` | hook | Same summary, but always exits 0 and never blocks session start. |

The script never writes files, never calls the network, and never calls an LLM.

## Hook surface

The optional Claude Code `SessionStart` hook in `.claude/settings.json` invokes
`--hook`. Tools without session-start hooks should follow the `AGENTS.md`
canonical reading order manually or invoke the script directly.

## Tests

```
python scripts/session-context/test_session_context.py
```
