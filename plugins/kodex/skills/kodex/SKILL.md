---
name: kodex
description: Use as the DEFAULT execution mode for any mechanical task — scaffolding, bulk file edits, codegen from a spec, build/install commands, large refactors, repetitive searches. Constructs a tightly-scoped peer-CLI prompt (default peer command is `codex`, configurable via KODEX_PEER_CMD) with embedded self-verification, runs it in the background, then independently verifies on the filesystem before claiming completion. Reasoning, design, judgement, and user dialogue stay with the parent session.
version: 0.1.0
---

# Kodex

## Default-mode policy

**This is the default execution mode in this environment.** For any task that is *doing* rather than *thinking*, the parent Claude session must:

1. Plan the work (parent reasoning).
2. Construct a delegation prompt for the peer CLI.
3. Invoke `${KODEX_PEER_CMD:-codex} -p '<prompt>'` in the background, with `KODEX_BYPASS=1` set so the peer's own Bash calls aren't re-intercepted.
4. Wait for the completion notification.
5. **Independently verify** the result on the filesystem — never trust the peer's self-report.
6. Report based on parent verification.

The PreToolUse hook bundled with this plugin will block clearly-mechanical Bash commands (build/install, `find -exec`, `sed -i`, `rm -rf`, `cp -r`, multi-`mv`, chained `mkdir`, bulk `touch`, etc.) — that's the safety net. The skill is the proactive recipe.

## When this skill applies

**Always**, for tasks involving:
- Creating multiple files or directory scaffolding
- Bulk renames, refactors, or repetitive edits
- Code generation from a spec (PLAN.md, schema, OpenAPI, etc.)
- Running builds, installs, tests, or compilers
- Large directory searches with actions
- Anything where the unit of work is mechanical, not cognitive

## When this skill does NOT apply

Keep with the parent session:
- Reasoning, design, architecture decisions
- Reading and understanding existing code (you need to see the content yourself)
- Single-file edits to your own config (`.claude/settings.json`, etc.)
- Status checks (`git status`, `git log`, `ls`)
- Trivial single commands where delegation overhead exceeds the work
- Talking with the user

## The delegation prompt anatomy

Every delegation MUST follow this exact structure:

1. **cwd anchor** — `You are working inside <abs_path>.`
2. **Spec pointer** — `Read <spec_file>. Section X describes the work.` (Don't re-state the spec inline; point to the source of truth.)
3. **One job verb** — `Your ONLY job is to <verb>.`
4. **Numbered STRICT RULES** — explicit denials of every likely scope-creep:
   - "Do NOT write code/content/boilerplate" (when scaffolding empty files)
   - "Do NOT git commit"
   - "Do NOT install dependencies" (unless that's the job)
   - "Do NOT modify <spec_file>"
   - "Do NOT create out-of-scope paths"
   - Add task-specific denials
5. **Mandatory verification command** — `When finished, run exactly: <cmd> — and show the output.` This produces deterministic evidence the parent can re-verify.
6. **Intent restatement** — one sentence so the model doesn't lose the thread.

## Invocation pattern

```bash
KODEX_BYPASS=1 ${KODEX_PEER_CMD:-codex} -p '<prompt-following-anatomy-above>'
```

Run it via the Bash tool with `run_in_background: true`. Do not poll — the runtime will notify you on completion.

**Why `KODEX_BYPASS=1`:** the PreToolUse hook checks this env var and exits early when set. Without it, the peer's own Bash calls would be re-intercepted by the same hook (infinite loop / lockup). Setting it for the peer's process tree breaks the loop.

**Why `${KODEX_PEER_CMD:-codex}`:** the peer command is configurable. If the user has set `KODEX_PEER_CMD=aider` (or any other CLI), the same delegation pattern works. Default is `codex`.

## Verification — non-negotiable

The peer's last line will often be `"Done. Created N files."` or similar. **This is a claim, not evidence.**

1. Re-run the verification command yourself (the one you embedded in the prompt).
2. Cross-check against the spec: files exist, sizes look right, no out-of-scope changes.
3. If applicable, run `git status` to confirm only the intended changes happened.
4. If parent verification disagrees with the peer's self-report, **report the discrepancy** — do not paper over it.

## Rules

- **One verb per delegation.** Two verbs → two delegations.
- **Explicit denials beat positive instructions.** Helpful agents naturally over-reach.
- **Verification command in the prompt itself.** Non-negotiable.
- **Parent verifies independently.** Filesystem is ground truth, not the agent's text.
- **Never delegate judgement.** Mechanical only.
- **Never re-state a spec inline.** Point at the file. Re-stating drifts.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Peer added code where you wanted empty files | Missing explicit denial | Add `Do NOT write code` to STRICT RULES; re-delegate |
| Peer committed changes | Missing `Do NOT git commit` | Add denial; `git reset HEAD` to undo; re-delegate |
| Verification mismatch | Agent hallucinated completion | Re-delegate with smaller subtask |
| Hook blocks peer's own Bash calls | `KODEX_BYPASS=1` not set | Always prefix peer invocation with the env var |
| Hook blocks parent's tiny single-shot command | False positive in deny patterns | Use `KODEX_BYPASS=1` prefix as escape hatch; consider tightening pattern |
| `command not found: codex` | Peer CLI not installed or not on PATH | Install your preferred peer CLI and either alias it to `codex` or set `KODEX_PEER_CMD=<your-cmd>` |

## Slash command shortcut

For one-line manual delegation, use `/kodex <task description>` — that command wraps the prompt anatomy, sets the env var, and backgrounds the call automatically.

## Example: scaffolding

Parent task: "create the empty file/folder skeleton from PLAN.md §2."

Delegation:

```
KODEX_BYPASS=1 codex -p 'You are working inside /path/to/your/project. Read "PLAN.md" — Section 2 lists the directory tree. Your ONLY job is to create that file/folder skeleton.

STRICT RULES:
1. Every file MUST be empty (zero bytes).
2. Do NOT write any code, content, or boilerplate.
3. Do NOT create the data/ folder.
4. Do NOT modify PLAN.md.
5. Do NOT git commit.
6. Do NOT install dependencies.
7. When finished, run exactly:  find . -type f -not -path "*/data/*" | sort
   and show me the listing.

Work fast and minimally.'
```

Parent verifies after:

```bash
find /path/to/your/project -type f -not -path "*/data/*" | sort
find /path/to/your/project -type f -not -path "*/data/*" -exec wc -c {} \;  # confirm zero bytes
git -C /path/to/your/project status                                          # confirm no commits
```
