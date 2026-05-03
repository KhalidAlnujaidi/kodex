#!/usr/bin/env python3
"""
PreToolUse hook for the kodex plugin.

Intercepts mechanical Bash patterns and denies them with a redirect to the
configured peer CLI. Reads the Claude Code PreToolUse JSON payload from stdin;
emits a JSON permissionDecision on stdout (or exits 0 silently to allow the
tool call).

Bypass: if the env var KODEX_BYPASS=1 is set, exit immediately. This prevents
lockup when the peer CLI itself (which may also be a Claude Code instance)
inherits this plugin and would otherwise re-intercept its own Bash calls.

Configuration:
    KODEX_PEER_CMD   Name of the peer CLI command (default: "codex").
                     Used only in the deny message — actual invocation is
                     done by the parent Claude session.
    KODEX_BYPASS     Set to "1" to skip the hook entirely.
"""

import json
import os
import re
import sys

# --- Bypass for delegated child processes ----------------------------------
if os.environ.get("KODEX_BYPASS") == "1":
    sys.exit(0)

PEER_CMD = os.environ.get("KODEX_PEER_CMD", "codex")

# --- Read PreToolUse payload -----------------------------------------------
try:
    payload = json.load(sys.stdin)
except Exception:
    # Malformed payload → don't block; let the tool through and let CC handle.
    sys.exit(0)

if payload.get("tool_name") != "Bash":
    sys.exit(0)

cmd = ((payload.get("tool_input") or {}).get("command") or "").strip()
if not cmd:
    sys.exit(0)

# --- Mechanical-bulk patterns: deny + redirect to peer CLI -----------------
# Each entry: (compiled regex, human-readable label)
DENY_PATTERNS = [
    # Package managers / installs
    (re.compile(r"\bnpm\s+(install|i|ci|run\s+build|run\s+test:e2e)\b"), "npm install/build"),
    (re.compile(r"\bpnpm\s+(install|i|add|build|test)\b"),               "pnpm install/build"),
    (re.compile(r"\byarn\s+(install|add|build|test)\b"),                 "yarn install/build"),
    (re.compile(r"\bpip\s+install\b"),                                   "pip install"),
    (re.compile(r"\bpip3\s+install\b"),                                  "pip3 install"),
    (re.compile(r"\buv\s+(pip\s+install|sync|add)\b"),                   "uv install/sync"),
    (re.compile(r"\bbundle\s+install\b"),                                "bundle install"),
    (re.compile(r"\bcargo\s+(build|test|run|install)\b"),                "cargo build/test"),
    (re.compile(r"\bgo\s+(build|test|mod\s+download|install)\b"),        "go build/test"),
    # Build tools
    (re.compile(r"\b(make|gradle|gradlew|mvn|cmake|ninja)\s"),           "build tool"),
    (re.compile(r"\b(tsc|webpack|rollup)\b"),                            "compiler/bundler"),
    (re.compile(r"\bvite\s+build\b"),                                    "vite build"),
    (re.compile(r"\bnext\s+build\b"),                                    "next build"),
    # Bulk file mutations
    (re.compile(r"\bsed\s+-i\b"),                                        "in-place sed (bulk file edit)"),
    (re.compile(r"\bfind\s+\S+.*\s-(exec|delete|ok)\b"),                 "find with -exec/-delete (bulk action)"),
    (re.compile(r"\brm\s+-r[f]?\b"),                                     "recursive rm"),
    (re.compile(r"\bcp\s+-r\b"),                                         "recursive cp"),
    # Multi-arg mv (looks like bulk move; single rename `mv a b` is allowed)
    (re.compile(r"\bmv\s+\S+\s+\S+\s+\S+"),                              "multi-arg mv"),
    # Chained mkdirs (scaffolding) — 2+ `mkdir` joined with && or ;
    (re.compile(r"(mkdir(\s+-p)?\s+\S+\s*[;&]+\s*){2,}mkdir"),           "chained mkdirs"),
    # Bulk touch (4+ files in one call)
    (re.compile(r"\btouch(\s+\S+){4,}"),                                 "bulk touch (4+ files)"),
]


def build_deny_reason(label: str, cmd: str, peer: str) -> str:
    return (
        f"[KODEX] This Bash command matches a mechanical-bulk pattern "
        f"({label}). Per the kodex default-mode policy, hand this work to the "
        f"`{peer}` peer CLI instead of running it yourself.\n\n"
        f"Blocked command: {cmd[:200]}{'…' if len(cmd) > 200 else ''}\n\n"
        f"How to delegate (see the kodex skill for the full prompt anatomy):\n\n"
        f"    KODEX_BYPASS=1 {peer} -p '<prompt with cwd anchor, one verb, "
        f"STRICT RULES, embedded verification command>'\n\n"
        f"Then independently verify the result on the filesystem before "
        f"claiming completion.\n\n"
        f"Manual bypass: prefix the bash command with `KODEX_BYPASS=1 ` if "
        f"you really must run it yourself (e.g. you ARE the delegated peer "
        f"session, or this is a one-off escape hatch).\n\n"
        f"Configuration: set `KODEX_PEER_CMD=<your-cli>` to use a peer other "
        f"than `codex`."
    )


for pattern, label in DENY_PATTERNS:
    if pattern.search(cmd):
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": build_deny_reason(label, cmd, PEER_CMD),
            }
        }
        sys.stdout.write(json.dumps(out))
        sys.exit(0)

# No match → silent allow.
sys.exit(0)
