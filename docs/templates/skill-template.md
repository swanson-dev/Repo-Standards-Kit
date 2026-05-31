<!--
Skill template (Claude). Copy to .claude/skills/<name>/SKILL.md.
`name` MUST equal the directory name (kebab-case). Pair it with a Copilot twin at
.github/prompts/<name>.prompt.md (see skill-prompt-template.md) and add a row to the
AGENTS.md `## Available skills` index.
-->
---
name: <skill-name>
description: <one line — what it does and when to reach for it>
---

# <skill-name>

## When to invoke

<The trigger. If it satisfies an AGENTS.md end-of-session contract item, name it.>

## How to invoke

Run from the repo root:

`python scripts/<path-to-script>.py <args>`

<What the script does / prints.>

## After

<What the agent does with the result — fill fields, paste an index row, re-run, etc.>
