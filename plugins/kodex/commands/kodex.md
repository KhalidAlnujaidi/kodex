---
description: Delegate a mechanical task to a peer CLI agent (default `codex`, configurable via $KODEX_PEER_CMD) with an embedded verification command and independent parent-side verification. Use for scaffolding, bulk edits, codegen from a spec, builds/installs.
argument-hint: <task description, or @path/to/spec.md, or both>
allowed-tools: [Bash, Read]
---

# /kodex

The user invoked: `/kodex $ARGUMENTS`

## Your job

Construct a tightly-scoped peer-CLI invocation following the **kodex skill** prompt anatomy, run it in the background, then **independently verify** the result on the filesystem.

## Steps

1. **Parse `$ARGUMENTS`** to extract:
   - The task verb (what should the peer do?)
   - Any spec file the user pointed at (e.g. `@PLAN.md`, `@docs/spec.yaml`)
   - Implicit constraints (e.g. "empty files only", "no commits")

   If `$ARGUMENTS` is unclear or missing a verb, ask the user one clarifying question before proceeding.

2. **Build the prompt** following the anatomy from the `kodex` skill:
   - cwd anchor (use the current working directory)
   - Spec pointer (if a file was referenced, point at it; do NOT inline the spec)
   - One job verb
   - Numbered STRICT RULES with explicit denials (`Do NOT write code` when scaffolding, `Do NOT git commit`, `Do NOT install dependencies` unless that IS the job, `Do NOT modify <spec>`, plus task-specific denials)
   - Mandatory verification command at the end (e.g. `find … | sort`, `git diff --stat`, `wc -l <files>`, `pytest -v`)
   - Intent restatement

3. **Invoke** via Bash, in background, with the bypass env var and configurable peer command:

   ```bash
   KODEX_BYPASS=1 ${KODEX_PEER_CMD:-codex} -p '<your prompt>'
   ```

   Use `run_in_background: true`. Generous timeout (5–10 minutes for non-trivial tasks).

4. **Wait** for the completion notification. Do not poll.

5. **Read the peer's final output** but **DO NOT TRUST** its self-report.

6. **Independently verify** on the filesystem — re-run the verification command yourself, plus `git status` if applicable. Cross-check against the spec.

7. **Report** based on parent verification, not the peer's claim. If they disagree, surface the discrepancy.

## Reminders

- One verb per delegation. If the task has two verbs, run two `/kodex` invocations.
- Explicit denials beat positive instructions.
- Never delegate judgement — only mechanical work.
- The PreToolUse hook will deny mechanical Bash commands you try to run yourself, which is the point. Delegate, don't bypass.
