# kodex

> Make peer-CLI delegation the **default execution mode** in Claude Code.

A Claude Code [plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugins) hosting one plugin: **kodex**.

## What it does

`kodex` makes the parent Claude Code session a **manager** that delegates mechanical work (builds, installs, scaffolding, bulk file edits) to a **peer CLI agent** (default `codex`, configurable), then independently verifies the result on the filesystem.

See [`plugins/kodex/README.md`](plugins/kodex/README.md) for the full description, hook scope, configuration, and usage examples.

## What's here

```
kodex/
├── .claude-plugin/
│   └── marketplace.json     # this marketplace's manifest
├── plugins/
│   └── kodex/               # the plugin itself
│       ├── README.md        # ← read this for what kodex does
│       ├── skills/, commands/, hooks/, scripts/
│       └── …
├── LICENSE                  # MIT
├── CONTRIBUTING.md
└── .gitignore
```

---

## Prerequisites — set up the peer CLI first

`kodex` delegates to a peer CLI it expects to find on your `PATH` as `codex`. By default that means a second Claude Code instance pointed at a local proxy that routes to whatever model you want (DeepSeek, NVIDIA NIM, OpenRouter, local models, etc.). Without this peer, `kodex` will deny mechanical Bash commands but the suggested fix won't have anywhere to go.

The reference setup uses [free-claude-code](https://github.com/Alishahryar1/free-claude-code) as the proxy and DeepSeek as the model. Three steps:

### 1. Install the proxy

```bash
# Install uv (Python package manager) if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install free-claude-code as a uv tool
uv tool install git+https://github.com/Alishahryar1/free-claude-code.git

# Initialize its config
fcc-init
```

`fcc-init` writes `~/.config/free-claude-code/.env` from a template you'll edit next.

### 2. Get a DeepSeek API key

- Sign up at **[platform.deepseek.com](https://platform.deepseek.com/)**
- Create an API key in the dashboard
- Copy it — you'll paste it into the proxy's `.env`

(You can also use NVIDIA NIM, OpenRouter, LM Studio, llama.cpp, or Ollama — see [free-claude-code's Providers section](https://github.com/Alishahryar1/free-claude-code#choose-a-provider). DeepSeek is just the cheapest cloud option.)

### 3. Configure the proxy and start it

Edit `~/.config/free-claude-code/.env`:

```dotenv
DEEPSEEK_API_KEY="your-deepseek-api-key-here"
MODEL="deepseek/deepseek-chat"          # or another deepseek model
ANTHROPIC_AUTH_TOKEN="freecc"           # any local secret string; reused below
```

Start the proxy:

```bash
free-claude-code
```

It listens on `http://localhost:8082` by default.

### 4. Add the `codex` alias

In your shell rc (`~/.zshrc` or `~/.bashrc`):

```bash
alias codex='ANTHROPIC_AUTH_TOKEN=freecc ANTHROPIC_BASE_URL=http://localhost:8082 claude --dangerously-skip-permissions'
```

Reload your shell. `codex` is now a Claude Code instance backed by DeepSeek through your proxy. `kodex` will use it as the peer.

> **Verify:** `codex -p 'echo hello'` should run a fresh Claude Code session against your local proxy and print a reply. If it errors out, fix the proxy/alias before installing the plugin.

---

## Install kodex

Once the peer CLI is working:

```bash
claude plugin marketplace add github:KhalidAlnujaidi/kodex
claude plugin install kodex@kodex
```

Then **start a new Claude Code session** for the PreToolUse hook to load.

### Install from a local clone

```bash
git clone https://github.com/KhalidAlnujaidi/kodex.git
claude plugin marketplace add ./kodex
claude plugin install kodex@kodex
```

### Configuration

Two environment variables let you change defaults:

| Variable | Default | Purpose |
|---|---|---|
| `KODEX_PEER_CMD` | `codex` | Name of the peer CLI command. Set to `aider`, `gemini`, your own alias, etc. |
| `KODEX_BYPASS` | (unset) | Set to `1` to skip the hook entirely (the slash command sets this automatically when invoking the peer). |

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Common contributions:

- Adding deny patterns for new mechanical command shapes
- Generalizing for additional peer CLIs
- Improving the prompt anatomy in the skill
- Bug reports for false-positive denies or missed mechanical patterns

---

## Sources & further reading

To make sense of the whole stack — what each piece is and where it sits — these are worth bookmarking:

**The proxy + free-tier setup**
- [free-claude-code](https://github.com/Alishahryar1/free-claude-code) — the Anthropic-compatible proxy that routes Claude Code traffic to DeepSeek, NVIDIA NIM, OpenRouter, or local models
- [free-claude-code Providers section](https://github.com/Alishahryar1/free-claude-code#choose-a-provider) — env vars and model identifiers for each supported backend

**The model**
- [DeepSeek platform](https://platform.deepseek.com/) — sign up, get an API key, see pricing
- [DeepSeek API docs](https://api-docs.deepseek.com/) — model IDs, parameters, rate limits

**Claude Code itself**
- [Claude Code docs](https://docs.claude.com/en/docs/claude-code/overview) — official documentation
- [Claude Code plugins](https://docs.claude.com/en/docs/claude-code/plugins) — how plugins work, marketplace format, hook lifecycle
- [Hooks reference](https://docs.claude.com/en/docs/claude-code/hooks) — PreToolUse JSON schema, permission decisions, what kodex's hook is built on
- [Skills reference](https://docs.claude.com/en/docs/claude-code/skills) — what `SKILL.md` is and when Claude invokes one
- [Slash commands](https://docs.claude.com/en/docs/claude-code/slash-commands) — what `commands/*.md` files become

**Related ecosystem**
- [oh-my-claudecode (OMC)](https://github.com/Yeachan-Heo/oh-my-claudecode) — the multi-agent orchestration layer this plugin was inspired by; complementary, not required
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — the official marketplace; useful as reference for plugin shape

## License

MIT — see [`LICENSE`](LICENSE).
