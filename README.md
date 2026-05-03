# kodex

> Make peer-CLI delegation the **default execution mode** in Claude Code.

A Claude Code [plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugins) hosting one plugin: **kodex**.

## What's here

```
kodex/
├── .claude-plugin/
│   └── marketplace.json     # this marketplace's manifest
├── plugins/
│   └── kodex/               # the plugin itself
│       ├── README.md        # ← read this for what kodex does
│       ├── SKILL.md, commands/, hooks/, scripts/
│       └── …
├── LICENSE                  # MIT
├── CONTRIBUTING.md
└── .gitignore
```

## Install

### From this GitHub repo

```bash
claude plugin marketplace add github:<owner>/<repo>
claude plugin install kodex@kodex
```

(Replace `<owner>/<repo>` with this repo's GitHub path once it's published.)

### From a local clone

```bash
git clone https://github.com/<owner>/<repo>.git
claude plugin marketplace add ./kodex   # or wherever you cloned to
claude plugin install kodex@kodex
```

After install, **start a new Claude Code session** for the PreToolUse hook to load.

## What it does

See [`plugins/kodex/README.md`](plugins/kodex/README.md) for the full description, hook scope, configuration, and usage examples.

In one sentence: it makes the parent Claude Code session a **manager** that delegates mechanical work (builds, installs, scaffolding, bulk file edits) to a **peer CLI agent** (default `codex`, configurable), then independently verifies the result on the filesystem.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Common contributions:

- Adding deny patterns for new mechanical command shapes
- Generalizing for additional peer CLIs
- Improving the prompt anatomy in the skill
- Bug reports for false-positive denies or missed mechanical patterns

## License

MIT — see [`LICENSE`](LICENSE).
