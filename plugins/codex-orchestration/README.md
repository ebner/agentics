# codex-orchestration

Hand an **already-approved** implementation plan to **OpenAI Codex** for implementation via the
official `codex` CLI, with cross-model review on both ends. The orchestrating model orchestrates and
reviews; **Codex writes all the code, edit-only and offline.**

Components, one shared convention:

| Component | What it is |
|-----------|------------|
| `/codex-orchestration:codex-implement` | **Command** — linear handoff: plan review (orchestrator + Codex) → per-phase implement / verify / fix → close-out. |
| `/codex-orchestration:codex-implement-fanout` | **Command** — launcher for the fan-out workflow: resolves the plan, discovers the workflow script, and runs it (auto-registered; no `ultracode`/path needed). |
| `codex-implement-fanout` | **Workflow** — the fan-out engine the launcher runs: decompose → parallel worktree implementers (edit-only Codex) → verify/merge gate → final verify. |
| `calling-codex` | **Skill** — the shared Codex-invocation convention (edit-only, network-off, sandbox, flags). Loaded by the commands and the workflow. |

## Prerequisites

- The OpenAI `codex` CLI installed and authenticated: `codex --version`, `codex login status`.
- The current repo marked trusted in `~/.codex/config.toml` (else the first run may block on a trust prompt).
- A Codex model that supports `xhigh` reasoning (the GPT-5.x-codex family and gpt-5.5 do).
- **A plan already produced and approved** (via plan mode or a planning command). These tools
  *implement* an approved plan; they do not plan.

The `calling-codex` skill documents all of this in detail; both the command and the workflow follow it.

## Install

```bash
/plugin marketplace add ebner/agentics
/plugin install codex-orchestration@agentics
```

## Usage — the command (whole plan, sequential)

```
/codex-orchestration:codex-implement [path/to/plan.md]
```

Run it as your **next message after approving the plan** (approving only unlocks edit tools; the
command's role-lock redirects implementation to Codex). It walks **every** phase of the plan with a
per-phase implement → verify → fix loop, discovers your project's build/test gate automatically (from
`CLAUDE.md` / `AGENTS.md` / `README` or your build config), and closes out with a simplification pass +
a final dual review. No opt-in needed — it is a normal slash command. Codex never builds or touches the
network; the orchestrator runs every build/test.

## Usage — the fan-out workflow (decomposable plans, parallel)

**Easiest — the launcher command** (auto-registered on install; no `ultracode`, no path juggling):

```
/codex-orchestration:codex-implement-fanout [path/to/plan.md] [--base <branch>] [--integration <branch>]
```

It resolves the plan, discovers the installed workflow script, and launches it — and **invoking it is
itself the Workflow opt-in**. You supply only the plan path; the workflow's decompose step derives the
units and dependency waves itself. (Spawns many parallel agents + Codex sessions — meant for large,
decomposable plans.)

**Manual alternatives**, if you prefer to drive the Workflow tool yourself (plugin workflows are not
auto-registered as named workflows — name resolution only reads the project's `.claude/workflows/` +
built-ins):

```bash
# A) By scriptPath, from the installed plugin (dynamic-discover the cache path):
WF=$(find ~/.claude -path '*/codex-orchestration/workflows/codex-implement-fanout.mjs' -print -quit)
# → Workflow({ scriptPath: WF, args: { planPath: '/abs/path/to/plan.md', base: 'main' } })

# B) As a named workflow, after copying it into your project:
cp "$WF" .claude/workflows/codex-implement-fanout.mjs
# → Workflow({ name: 'codex-implement-fanout', args: { planPath: '/abs/path/to/plan.md', base: 'main' } })

# C) Via the ultracode keyword (opt-in), letting the model decompose + launch:
#    "ultracode — implement the approved plan at /abs/path/to/plan.md by fanning out via Codex"
```

`args`: `planPath` (required, absolute), `base` (default `main`), `integrationBranch`
(default `codex-fanout/integration`). The workflow decomposes the plan into file-disjoint units,
implements each in its own git worktree via edit-only Codex (parallel within a dependency wave), and a
sequential gate merges + verifies each unit into the integration branch. Nothing is pushed; the
integration branch is separate from your base branch.

### How parallelism and auto-merge work

The workflow guarantees per-agent isolation and automatic integration:

- **One worktree per implementing agent.** Each unit's implementation agent runs with
  `isolation: 'worktree'`, so parallel agents within a dependency wave edit in **separate git
  worktrees** — they never collide on files or the git index.
- **Each agent commits to its own branch.** Inside its worktree the agent bases off the integration
  branch, drives edit-only Codex, then commits the unit's changes to `codex/unit-<id>`. Branches are
  repo-global, so the gate sees them even after a worktree is cleaned.
- **Automatic merge + per-unit fix loop.** When a wave's agents finish, the sequential verify/merge
  gate **merges each unit branch into the integration branch** (`git merge --no-ff`) and runs the
  project's build/verify. On a **red build** it captures the verbatim failing output, **resumes that
  unit's Codex session with it, re-commits on a fresh fix branch, and re-gates (≤ 2 fix rounds)** before
  giving up on the unit. It keeps a merge only when green, reverts on red, and aborts on a non-trivial
  conflict (conflicts are not auto-fixed; never force-merges). The next wave bases off the updated
  integration branch.
- **Where the result lands.** The merged, verified result is on `integrationBranch` (default
  `codex-fanout/integration`); set `args.integrationBranch` to your feature branch to integrate there
  directly. Nothing is pushed and nothing is merged to your base branch — that final merge is yours to
  review. The harness auto-cleans the per-agent worktrees at workflow end; run `git worktree prune` if
  any persist.

## When to use which

- **Sequential, small, or strict dependency-chain plan → the command.** Simpler, and a chain can't be
  parallelized anyway.
- **Large, decomposable, mostly file-disjoint plan → the workflow.** Fan-out parallelizes only the
  *independent* units within a dependency wave and sequences the rest, so it pays off when the plan has
  genuinely independent work; a strict chain gains little over the command.

## Safety model (summary; full detail in the `calling-codex` skill)

Codex runs **edit-only**: writes confined to the workspace and network **off**, both OS-enforced
(Landlock/seccomp on Linux). It never builds, installs, commits, or escalates (`approval_policy=never`
keeps the sandbox as a hard ceiling). The orchestrator — the calling agent, with full access — owns all
builds, tests, network, and merges. Note: read-confinement to the project is **not** kernel-enforced on
Linux in current Codex versions; the protection is network-off + write-confine + edit-only (no egress,
no task-reason to read outside the project). Never run Codex with
`--dangerously-bypass-approvals-and-sandbox`.

## Examples

### 1. Implement an approved plan (sequential — the common case)

Plan in plan mode (or a planning command) and approve it, then make your **next** message:

```
/codex-orchestration:codex-implement
```

It resolves the current session's plan automatically; or pass a path explicitly:

```
/codex-orchestration:codex-implement docs/plans/add-rate-limiter.md
```

Codex reviews the plan, implements each phase edit-only, the orchestrator builds/verifies between
phases, and it ends with a consolidated pre-PR report. Nothing is committed.

### 2. Fan out a large plan — the launcher command (easiest)

```
/codex-orchestration:codex-implement-fanout /abs/path/to/plan.md
```

That's it — the command resolves the plan, discovers the installed workflow script, and launches the
fan-out (no `ultracode`, no path juggling). Override defaults with `--base <branch>` or
`--integration <branch>`. To drive the Workflow tool manually instead (scriptPath,
copy-to-`.claude/workflows/`, or the `ultracode` keyword), see *Usage — the fan-out workflow* above.

### 3. What the fan-out produces

For a plan with units A and B (independent) and C (depends on A):

- **Wave 1** — agents for A and B run in parallel, each in its own worktree, committing `codex/unit-a`
  and `codex/unit-b`; the gate merges both into `codex-fanout/integration` and verifies each.
- **Wave 2** — the agent for C bases off the updated integration branch, commits `codex/unit-c`; the
  gate merges and verifies it.
- **Final verify** runs the project's full gate against the plan.

Result: `codex-fanout/integration` holds all merged, verified units; nothing is pushed — you review and
merge it to your base branch.
