# Contributing to kodex

Thanks for your interest. This document covers the most common contribution shapes.

## Repo layout

```
kodex/                                    # marketplace root
├── .claude-plugin/marketplace.json       # marketplace manifest
└── plugins/kodex/                        # the plugin
    ├── .claude-plugin/plugin.json
    ├── README.md
    ├── skills/kodex/SKILL.md             # delegation recipe
    ├── commands/kodex.md                 # /kodex slash command
    ├── hooks/hooks.json                  # PreToolUse hook config
    └── scripts/pre-tool-kodex.py         # the hook script
```

## Common contributions

### 1. Add a deny pattern (most common)

The hook lives at `plugins/kodex/scripts/pre-tool-kodex.py`. Add a tuple to `DENY_PATTERNS`:

```python
(re.compile(r"\byour-pattern\b"), "human-readable label"),
```

**Before submitting:**
- Test it intercepts the intended commands (see "Testing the hook" below).
- Test it does NOT false-positive on similar but legitimate commands.
- Keep the regex anchored with `\b` word boundaries to avoid matching substrings.

### 2. Add a peer CLI to the docs

The hook is already peer-agnostic via `KODEX_PEER_CMD`. To make a new peer first-class, add a section to `plugins/kodex/README.md` showing how to set it up (alias, env var, dependencies).

### 3. Improve the prompt anatomy

The delegation prompt template lives in `plugins/kodex/skills/kodex/SKILL.md`. Changes to the anatomy should:
- Be motivated by an observed failure mode (cite it in the PR).
- Stay terse — the prompt is read by a model on every delegation.
- Not break the `KODEX_BYPASS=1` and `${KODEX_PEER_CMD:-codex}` patterns.

## Testing the hook

The hook is a Python script that reads JSON on stdin and emits JSON (or nothing) on stdout. Test it directly:

```bash
HOOK="plugins/kodex/scripts/pre-tool-kodex.py"

# Deny case
echo '{"tool_name":"Bash","tool_input":{"command":"npm install foo"}}' | python3 "$HOOK"
# Expect: JSON with permissionDecision: "deny"

# Allow case
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python3 "$HOOK"
# Expect: no output, exit 0

# Bypass case
KODEX_BYPASS=1 bash -c 'echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"npm install foo\"}}" | python3 "$0"' "$HOOK"
# Expect: no output, exit 0

# Configurable peer
KODEX_PEER_CMD=aider bash -c 'echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"npm install foo\"}}" | python3 "$0"' "$HOOK"
# Expect: deny message references "aider" instead of "codex"
```

## Validating manifests

```bash
claude plugin validate plugins/kodex          # plugin manifest
claude plugin validate .                      # marketplace manifest
```

Both should print `✔ Validation passed`.

## Local install for development

```bash
claude plugin marketplace add /absolute/path/to/this/repo
claude plugin install kodex@kodex
```

After editing files in this repo, reinstall to pick up changes:

```bash
claude plugin uninstall kodex@kodex
claude plugin install kodex@kodex
```

Then start a fresh Claude Code session — hooks load at session-start.

## PR checklist

- [ ] Hook unit tests pass (deny + allow + bypass + configurable peer cases).
- [ ] `claude plugin validate` passes for both manifests.
- [ ] No personal paths, secrets, or env tokens added.
- [ ] README / SKILL.md updated if user-visible behavior changed.
- [ ] Commit messages describe the *why*, not just the *what*.

## Versioning

`plugin.json` follows semver. Bump:
- **patch** for bug fixes / pattern tweaks
- **minor** for new features (additional deny patterns, new env vars)
- **major** for breaking changes (rename env vars, change hook output shape)
