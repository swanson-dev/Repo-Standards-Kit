# RFC-0007 cross-host hook spike: results

Run 2026-10-14 on Windows 11 for [RFC-0007](../rfc.md). It checks whether one enforce-once Stop hook output is accepted by every target host.

## What was tested

[`spike/stop_hook.py`](spike/stop_hook.py) is a stdlib-only Stop hook implementing RFC-0007 §1:

- `stop_hook_active` false or missing: print `{"decision": "block", "reason": "..."}` and exit 0.
- `stop_hook_active` true: print nothing and exit 0.
- `--wrapped`: also add VS Code's wrapper, `{"hookSpecificOutput": {"hookEventName": "Stop", "decision": "block", "reason": "..."}}`, in the same object.
- Every run appends its input and output to `spike-hook.log` beside the script.

The fixed reason tells the agent to reply `SPIKE-ACK <format> <event>` and then stop. Seeing that line proves the turn continued and the agent read the reason. A second log entry with `stop_hook_active: true` and no output proves the second stop passed. [`spike/test_stop_hook.py`](spike/test_stop_hook.py) checks both branches.

Per-host config, written so the contents of `spike/` can be copied into the root of a throwaway repo:

| Host | File |
|---|---|
| Claude Code | [`spike/.claude/settings.json`](spike/.claude/settings.json) |
| Codex CLI | [`spike/.codex/hooks.json`](spike/.codex/hooks.json) |
| Copilot in VS Code, Copilot CLI, Copilot cloud agent | [`spike/.github/hooks/standards.json`](spike/.github/hooks/standards.json) (Copilot format, `version: 1`, PascalCase `Stop`) |

## Results

| Host | Output format | Hook ran | Turn continued | Agent saw reason | Second stop passed | Status |
|---|---|---|---|---|---|---|
| Claude Code 2.1.286 | top-level | yes | yes | yes, `SPIKE-ACK top-level Stop` | yes | **Verified** |
| Claude Code 2.1.286 | top-level + wrapper | yes | yes | yes, `SPIKE-ACK wrapped Stop` | yes | **Verified** |
| Codex CLI 0.159.3 (`codex exec`) | top-level | yes | yes | yes, `SPIKE-ACK top-level Stop` | yes | **Verified** (repo trusted, hook trust bypassed) |
| Codex CLI 0.159.3 (`codex exec`) | top-level + wrapper | yes, printed a block | **no** | no | n/a, turn ended after the first stop | **Verified: rejected, fails open silently** |
| Codex CLI interactive (TUI trust and `/hooks` review) | top-level | | | | | Pending (manual test D) |
| Copilot in VS Code | top-level | | | | | Pending (manual test A) |
| Copilot in VS Code | top-level + wrapper | | | | | Pending (manual test A) |
| Copilot CLI | top-level | | | | | Pending (manual test B) |
| Copilot CLI | top-level + wrapper | | | | | Pending (manual test B) |
| Copilot cloud agent | top-level | | | | | Pending (manual test C) |
| Copilot cloud agent | top-level + wrapper | | | | | Pending (manual test C) |

### Claude Code details

- Both runs: first Stop input had `stop_hook_active: false` and `last_assistant_message: "READY"`, and the hook blocked. Claude received the reason as a user turn starting `Stop hook feedback:` and replied with the ACK line. The second Stop input had `stop_hook_active: true` and the ACK as `last_assistant_message`. The hook printed nothing and the run ended (`num_turns: 2`).
- Claude Code accepts the extra `hookSpecificOutput` on Stop without complaint (`outcome: success`).
- A block also raises a `Stop hook error occurred` notification. That label is cosmetic; the docs say `decision: block` is shown as a hook error.
- Project hooks ran in `-p` mode with no trust prompt, as documented.

### Codex details

- Stop input fields: `cwd`, `hook_event_name` (`Stop`), `last_assistant_message`, `model`, `permission_mode`, `session_id`, `stop_hook_active`, `transcript_path`, `turn_id`.
- **The wrapper breaks Codex.** Codex parses Stop output into `StopCommandOutputWire`, which is `#[serde(deny_unknown_fields)]` (`codex-rs/hooks/src/schema.rs` in `openai/codex`). Any `hookSpecificOutput` key makes the whole output invalid, so the block is dropped and the turn ends. `codex exec --json` reported no warning.
- **Trust gates everything, silently.** In `codex exec` the project hook ran only when the repo was trusted in `config.toml` *and* the hook was trusted. Hook trust was bypassed here with `--dangerously-bypass-hook-trust`. Untrusted repo with or without the bypass, or trusted repo without it: the hook never ran and no warning appeared in the event stream.
- `commandWindows` with `$(git rev-parse --show-toplevel)` resolved correctly on Windows.
- `codex exec --json` emits no hook events, so the hook log was the only way to see the hook ran.

### What this settles, and what it leaves open

1. **Top-level `decision`/`reason` is the only shape verified on both runnable hosts.**
2. **One object carrying both shapes is out.** Codex rejects it. If VS Code needs the wrapper, the wrapper must reach VS Code alone, which means a per-host shim.
3. **The shim decision hinges on tests A to C,** because VS Code, Copilot CLI, and the cloud agent all read the same `.github/hooks/*.json` files:

| VS Code (test A) | Copilot CLI and cloud agent tolerate the wrapper (tests B, C) | Contract |
|---|---|---|
| accepts top-level | n/a | One format everywhere: top-level only. |
| needs wrapper | yes | `.github/hooks/standards.json` passes `--wrapped`; Claude Code and Codex stay top-level. |
| needs wrapper | no | The shared file cannot serve both. The hook must detect VS Code at runtime, or VS Code gets its hook another way (for example the plugin, or `.claude/settings.json` with `chat.useClaudeHooks`). Needs a further test. |

## Manual tests for the owner

### Common setup

1. Make an empty folder outside any repo and copy in the contents of `spike/`: `stop_hook.py`, `.claude/`, `.codex/`, `.github/`. Then `git init` and commit. Keep `test_stop_hook.py` out; it is not needed.
2. The prompt for every test: `Reply with the single word READY. Do not use any tools.`
3. To switch to the wrapped variant, add ` --wrapped` to the end of every command string in the host's config file. Start a new chat or session after editing.
4. Before each test, delete or rename `spike-hook.log` so the log shows only that run.
5. For every test, record:
   - Hook ran: does `spike-hook.log` have a first line?
   - `stop_hook_active` in the first and second entries, and the `hook_event_name` value (or its absence).
   - Turn continued: did the agent post a second message after `READY`?
   - Agent saw reason: was that message `SPIKE-ACK ...`? Copy it exactly.
   - Second stop passed: did the session end after the ACK, with a second log entry whose `output` is `null`?
6. If the agent keeps posting ACK lines, stop the session. That means the host did not set `stop_hook_active` on the continued turn; record how many blocks happened.

### Test A: Copilot in VS Code

Needs VS Code with GitHub Copilot Chat signed in (1.141.2 is installed on this machine). `chat.useHooks` is on by default. Leave `chat.useClaudeHooks` off so the `.claude/` file is not also loaded.

1. Open the throwaway folder in VS Code and trust the workspace. Hook files are subject to Workspace Trust.
2. Run **Chat: Configure Hooks** from the Command Palette. Confirm `.github/hooks/standards.json` is listed with a Stop hook. If it is not listed, record that, change the event key from `Stop` to `agentStop`, and check again.
3. Open Copilot Chat in **Agent** mode and send the prompt.
4. Open **Output** and select **GitHub Copilot Chat Hooks**. Copy the hook's stdout and any parse warning.
5. Record the results from the common setup. Expected if top-level is accepted: `SPIKE-ACK top-level Stop`. Expected if it is ignored: the chat ends after `READY` while the log still shows a block.
6. Switch to the wrapped variant, open a new chat, and repeat. Expected if the wrapper works: `SPIKE-ACK wrapped Stop`.

### Test B: Copilot CLI

Needs Node.js 22 or later, then `npm install -g @github/copilot` and `/login` inside `copilot`. Not installed on this machine.

1. In the throwaway folder run `copilot` and trust the folder when asked. Send the prompt. Or run it non-interactively with `copilot -p "Reply with the single word READY. Do not use any tools."`.
2. Record the results. With the PascalCase `Stop` key the CLI should send snake_case input with `hook_event_name`, so the ACK should read `SPIKE-ACK top-level Stop`.
3. Switch to the wrapped variant and repeat. This answers whether the CLI tolerates the wrapper, the middle row of the table above.
4. If `Stop` never runs the hook, change the key to `agentStop` and repeat step 1. The input is then camelCase without an event name, so the ACK reads `SPIKE-ACK top-level unnamed`.

### Test C: Copilot cloud agent

Needs a throwaway private GitHub repo with the Copilot cloud agent enabled. Each block costs an extra agent turn against the job's time limit. The cloud agent runs `bash` on Linux, so the hook runs with `python3`, and `spike-hook.log` is discarded when the job ends. The ACK line in the session log is the evidence.

1. Push `stop_hook.py` and `.github/hooks/standards.json` to the default branch.
2. Open an issue: `Create a file named hello.txt containing READY. Make no other changes.` Assign it to Copilot.
3. Open the draft PR and select **View session**. Look for the hook run, an agent message `SPIKE-ACK top-level Stop`, and the job finishing after it rather than repeating ACKs.
4. Push the wrapped variant to the default branch, open a new issue, and repeat.
5. If there is no ACK and no hook output in the session log, change the key to `agentStop`, push, and repeat. If the session log shows `python3` failing, record that; it is the interpreter risk the RFC already lists.

### Test D: Codex CLI, interactive trust

The automated run bypassed hook trust. This confirms the path a real adopter takes.

1. In the throwaway folder run `codex`. Accept the prompt to trust the folder.
2. Run `/hooks`, review the Stop hook from `.codex/hooks.json`, and trust it.
3. Send the prompt. Expected: `SPIKE-ACK top-level Stop`, then the session idles. Record whether Codex warned about the unreviewed hook before step 2.

## Reproduce the automated runs

From a throwaway repo prepared as in the common setup:

```bash
# Claude Code: project settings only, so user-level hooks and plugins do not interfere
claude -p "Reply with the single word READY. Do not use any tools." --setting-sources project --output-format stream-json --verbose --include-hook-events --model haiku

# Codex: the repo must be trusted for its .codex/ layer to load (lowercase Windows path)
codex exec --json --ephemeral -s read-only --dangerously-bypass-hook-trust -c "projects={'r:\path\to\repo'={trust_level=\"trusted\"}}" "Reply with the single word READY. Do not run any commands."
```

Models used: Claude Haiku 4.5 through the `haiku` alias, and Codex's configured default. The model does not affect hook handling. User-level Codex hooks had no Stop entry and failed to load anyway, so only the spike hook ran.
