# kodex

> Make peer-CLI delegation the **default execution mode** in Claude Code.
> Parent session reasons and verifies. Peer CLI does the mechanical work.

## What it does

`kodex` reframes how Claude Code does mechanical work. Instead of the parent session running every `find`, `sed`, `npm install`, and bulk file edit itself, it delegates that work to a **peer CLI agent** running in a separate process — and then independently verifies the result on the filesystem before claiming completion.

| | Parent session (manager) | Peer CLI (employee) |
|---|---|---|
| Plans the work | ✓ | |
| Talks to the user | ✓ | |
| Makes design decisions | ✓ | |
| Writes the delegation prompt | ✓ | |
| Verifies the result on disk | ✓ | |
| Runs `npm install` / `find -exec` / `sed -i` / scaffolding / codegen | | ✓ |
| Returns a self-report (manager never trusts blindly) | | ✓ |

## Components

| File | Type | Purpose |
|---|---|---|
| `skills/kodex/SKILL.md` | Skill | Recipe for constructing a tightly-scoped delegation prompt with embedded self-verification. Auto-invokable when relevant. |
| `commands/kodex.md` | Slash command | `/kodex <task>` — explicit one-line delegation. |
| `hooks/hooks.json` + `scripts/pre-tool-kodex.py` | PreToolUse hook | Intercepts mechanical Bash patterns and forces delegation. |

## Hook scope

The hook **denies** Bash commands matching clearly-mechanical bulk patterns:

- **Build / install:** `npm install`, `pnpm install`, `yarn install`, `pip install`, `bundle install`, `cargo build/test`, `go build/test`, `make`, `gradle`, `mvn`, `cmake`, `tsc`, `webpack`, `vite build`, `next build`, `rollup`
- **Bulk file ops:** `find … -exec`, `find … -delete`, `sed -i`, `rm -rf`, `cp -r`, multi-arg `mv`, chained `mkdir -p`, bulk `touch` (4+ files)

Everything else passes through silently — `ls`, `cat`, `grep`, `find` without actions, `git status/log/diff`, single-file ops, etc. are unaffected.

## Configuration

Two environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `KODEX_PEER_CMD` | `codex` | Command name of the peer CLI. Set to `aider`, `gemini`, your own alias, etc. |
| `KODEX_BYPASS` | (unset) | Set to `1` to skip the hook entirely. Required when invoking the peer (so the peer's own Bash calls aren't re-intercepted). |

The peer CLI must support a non-interactive print mode that takes a prompt as an argument. The default `codex` assumes you have an alias like:

```bash
# in your shell rc
alias codex='claude --dangerously-skip-permissions'
```

…or any equivalent that accepts `codex -p '<prompt>'` and runs to completion. The peer can be backed by **any model** your CLI is configured to use (Claude, DeepSeek, GPT, local Llama, anything).

## Bootstrap-loop bypass

When the slash command (or anything else) invokes the peer, it prefixes the call with `KODEX_BYPASS=1`. The hook checks this env var and exits early, so the peer's own Bash calls aren't re-intercepted by the same hook.

## Manual bypass

If you absolutely need to run a denied command yourself:

```bash
KODEX_BYPASS=1 <your command>
```

Or disable the plugin temporarily:

```bash
claude plugin disable kodex@kodex
```

## Requirements

- A peer CLI on `PATH` that accepts `<peer> -p '<prompt>'` (default name: `codex`).
- Python 3 (preinstalled on macOS and most Linux distros).
- Claude Code (the host that loads the plugin).

## Install

> See the top-level repo `README.md` for the full setup, including the peer-CLI prerequisites. Short version:

```bash
git clone https://github.com/KhalidAlnujaidi/kodex.git
cd kodex
claude plugin marketplace add .
claude plugin install kodex@kodex
```

Restart Claude Code after installing so the PreToolUse hook loads.

## Uninstall

```bash
claude plugin uninstall kodex@kodex
claude plugin marketplace remove kodex
```

## License

MIT — see `LICENSE`.
