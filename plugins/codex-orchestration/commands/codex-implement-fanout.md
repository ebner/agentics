---
description: Fan out an approved plan to OpenAI Codex — decompose into file-disjoint units, implement each in an isolated git worktree (parallel), and a verify/merge gate integrates them
argument-hint: "[path/to/plan.md] [--base <branch>] [--integration <branch>]"
allowed-tools: ["Read", "Bash", "AskUserQuestion", "Workflow"]
---

# Codex Implement (fan-out)

Launcher for the `codex-implement-fanout` workflow. Use this for **large, decomposable** plans (many
independent, mostly file-disjoint units); for small or strictly-sequential plans use
`/codex-orchestration:codex-implement` instead.

**Invoking this command is itself the opt-in to the multi-agent Workflow runner** — you do not need
the `ultracode` keyword, and you do not need to know any file path. This command discovers the
installed workflow script and launches it for you.

> Prerequisites (per the `calling-codex` skill): the `codex` CLI installed and logged in
> (`codex login status`), the repo trusted in `~/.codex/config.toml`, and a Codex model that supports
> `xhigh`. A plan must already exist and be approved — this launches *implementation*, it does not plan.

## Steps

1. **Resolve the plan**, in order: the path in `$ARGUMENTS` → the current session's plan file
   (`~/.claude/plans/<branch>.md`) → a plan created earlier in this conversation → otherwise ask with
   `AskUserQuestion`. Read it to confirm it exists; use its **absolute** path.
2. **Resolve the base branch:** a `--base <branch>` value in `$ARGUMENTS` if present; otherwise
   `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`; otherwise
   `main`. Resolve `--integration <branch>` the same way if present (default `codex-fanout/integration`).
3. **Discover the installed workflow script** (plugins are copied to an unpredictable cache path, so
   discover it dynamically):

   ```bash
   WF=$(find ~/.claude -path '*codex-orchestration/workflows/codex-implement-fanout.mjs' -print -quit)
   [ -z "$WF" ] && { echo "codex-implement-fanout.mjs not found — (re)install codex-orchestration@agentics" >&2; exit 1; }
   echo "$WF"
   ```

   If `$WF` is empty, tell the user to install/update the `codex-orchestration` plugin and stop.
4. **Launch the workflow** with the resolved values:

   ```
   Workflow({
     scriptPath: "<the $WF path>",
     args: { planPath: "<abs plan path>", base: "<base>", integrationBranch: "<integration>" }
   })
   ```
5. **Relay the workflow's consolidated result** (units integrated / failed, the final-verify verdict,
   and the integration branch name). Do **not** commit or push — the user reviews and merges the
   integration branch.

## Notes

- This command only *launches* the workflow; the fan-out logic, per-agent worktree isolation, and the
  verify/merge gate live in the workflow script (and follow the `calling-codex` skill for every Codex
  call).
- The workflow spawns many parallel agents and Codex sessions — appropriate for large plans, overkill
  for small ones.
