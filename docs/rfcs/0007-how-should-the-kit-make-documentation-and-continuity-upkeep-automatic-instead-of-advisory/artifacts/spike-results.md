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
| Copilot in VS Code 1.141.2 | top-level | yes | yes | yes, `SPIKE-ACK top-level Stop` | yes | **Verified** (2026-10-16, manual test A) |
| Copilot in VS Code | top-level + wrapper | | | | | Not run: top-level works, so VS Code doesn't need the wrapper |
| Copilot CLI 1.0.98 (interactive) | top-level | yes | yes | yes, `SPIKE-ACK top-level Stop` | yes | **Verified** (2026-10-16, manual test B) |
| Copilot CLI | top-level + wrapper | | | | | Not run: no Copilot host needs the wrapper, so whether the CLI tolerates it doesn't matter |
| Copilot cloud agent | top-level | yes, `python3` on Linux | yes | yes: replied right after each block (text not in the logs) | yes, within each turn | **Verified, but it re-blocks on every agent turn, which failed the job** (2026-10-16, manual test C) |
| Copilot cloud agent, once per session (test C2) | top-level | yes | yes | yes, one block | yes | **Verified: one block, and the job succeeded** (2026-10-16) |
| Copilot cloud agent | top-level + wrapper | | | | | Not run: no Copilot host needs the wrapper |

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

### Copilot in VS Code details

- Stop input fields: `cwd`, `hook_event_name` (`Stop`), `session_id`, `stop_hook_active`, `stop_reason`, `timestamp`, `transcript_path`. They're snake_case, with the same `stop_hook_active` guard as Claude Code and Codex, so `drift.py --hook` reads them unchanged. There is no `last_assistant_message`.
- First stop: `stop_hook_active: false`, so the hook blocked and the agent replied with the ACK. Second stop: `stop_hook_active: true`, no output, and the chat ended.
- **VS Code picks up more hook files than this test assumed.** Its default `chat.hookFilesLocations` covers `.github/hooks`, `.claude/settings.json`, `.claude/settings.local.json`, `~/.copilot/hooks`, and `~/.claude/settings.json`. That holds even with `chat.useClaudeHooks` at its default `false`. VS Code also lists hooks from agent plugins under `~/.vscode/agent-plugins` (`chat.plugins.enabled`, on by default). On the first try, **Chat: Configure Hooks** listed five Stop hooks: the spike's copies in `.github/hooks` and `.claude/`, plus three from an installed plugin. The run that counted had `.claude/` and `.codex/` moved aside and `"chat.plugins.enabled": false` in workspace settings, which left one.
- What this means for adopters: if a repo ships the drift hook in both `.claude/settings.json` and `.github/hooks/`, VS Code will list it twice for each stop.

### Copilot CLI details

- The CLI sends the same Stop input fields as VS Code, all in snake_case, with `hook_event_name: "Stop"` and `stop_reason: "end_turn"`. The PascalCase `Stop` key in `.github/hooks/standards.json` was enough, so the `agentStop` fallback wasn't needed.
- First stop: `stop_hook_active: false`, so the hook blocked. Second stop: `stop_hook_active: true`, no output, and the session went idle. The CLI shows the block reason in the transcript before the agent replies.
- The run used the interactive `copilot` session in a trusted folder, with `.claude/` and `.codex/` still moved aside from test A.

### Copilot cloud agent details

- Run: issue 1 in a private throwaway repo, assigned to Copilot. The default branch held only `stop_hook.py` and `.github/hooks/standards.json`. The Actions run "Running Copilot cloud agent" (model `gpt-6-luna`) failed after 1m22s with `Failed to get a valid PR summary after 3 attempts`.
- Evidence: the hook wrote `spike-hook.log` into the working tree, and the agent pushed it to the PR branch, so the full hook log survived. It has eight entries in four block-then-pass pairs. Every entry has the same input fields as VS Code and the CLI: snake_case, `hook_event_name: "Stop"`, `stop_reason: "end_turn"`. All eight share one `session_id`. In the run log's `[cca-engine]` turn trace, each block appears as a 118-char `user.message`, exactly the length of the spike's reason.
- Side effect: any file a hook writes into the working tree ends up in the cloud agent's PR.
- Main task: the agent finished in turn 9, and the hook blocked with `stop_hook_active: false`. The agent replied (a 9-char message whose text isn't logged), the next stop had `stop_hook_active: true`, the hook passed, and the session went idle.
- **The engine reprompts the same session for the PR description, and the Stop hook runs on that turn too.** Each of those prompts starts a new turn, so `stop_hook_active` is false again and the hook blocks again. The agent's reply to the block becomes its last message, the engine rejects it as the PR description (`Invalid PR description response`), and retries. That happened three times (four blocks in total) before the job failed.
- What this means for the drift hook: in the cloud agent, a hook that keeps blocking fails the job, because the block lands on the engine's own follow-up turns. If the agent fixes the drift in its main turn, the next stops pass. If the drift persists, every PR-description attempt is hijacked.
- `python3` and the PascalCase `Stop` key both work in the cloud agent; `agentStop` wasn't needed.
- **Test C2, once per session.** The spike hook got a guard: when `GITHUB_ACTIONS` is `true`, it blocks once per `session_id` and records the block in `RUNNER_TEMP`. The task ran from a branch (`gh agent-task create --base`), so the default branch wasn't touched. Hooks see `GITHUB_ACTIONS=true`, `RUNNER_TEMP=/home/runner/work/_temp`, and about 40 `COPILOT_*` variables, including `COPILOT_AGENT_SESSION_ID`. The session blocked once (the 118-char message), and the next stop passed. The PR-description turn then went through without a block, and the job succeeded with a real PR description.

### What this settles, and what it leaves open

1. **Top-level `decision`/`reason` is the only shape verified on both runnable hosts.**
2. **One object carrying both shapes is out.** Codex rejects it. If VS Code needs the wrapper, the wrapper must reach VS Code alone, which means a per-host shim.
3. **The shim decision hinges on tests A to C,** because VS Code, Copilot CLI, and the cloud agent all read the same `.github/hooks/*.json` files:

| VS Code (test A) | Copilot CLI and cloud agent tolerate the wrapper (tests B, C) | Contract |
|---|---|---|
| accepts top-level | n/a | One format everywhere: top-level only. |
| needs wrapper | yes | `.github/hooks/standards.json` passes `--wrapped`; Claude Code and Codex stay top-level. |
| needs wrapper | no | The shared file cannot serve both. The hook must detect VS Code at runtime, or VS Code gets its hook another way (for example the plugin, or `.claude/settings.json` with `chat.useClaudeHooks`). Needs a further test. |

4. **Tests A to C settle it: top-level output everywhere, so no output adapter.** VS Code, the Copilot CLI, and the cloud agent all accept top-level output. They also send the same snake_case input, with `stop_hook_active`. The one Copilot-specific behavior is that the cloud agent's engine reprompts the session, so `drift.py --hook` blocks at most once per session on CI runners (test C2).

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

Needs VS Code with GitHub Copilot Chat signed in (1.141.2 is installed on this machine). `chat.useHooks` is on by default. VS Code also reads `.claude/settings.json` by default, so move `.claude/` and `.codex/` aside. Add `"chat.plugins.enabled": false` to the workspace's `.vscode/settings.json` too, so hooks from installed plugins don't run (see Copilot in VS Code details).

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

Needs a throwaway private GitHub repo with the Copilot cloud agent enabled. Each block costs an extra agent turn against the job's time limit. The cloud agent runs `bash` on Linux, so the hook runs with `python3`, and the agent pushes `spike-hook.log` to its PR branch along with its change. That log, and the `[cca-engine]` turn trace in the Actions run log, are the evidence.

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
