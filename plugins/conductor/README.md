# conductor

Plan big, execute small. The **coordinating model** (your main session) plans, decomposes,
reviews, and runs every build/test/merge; a **cheaper pluggable implementer** — the OpenAI Codex
CLI (edit-only, network-off) or a Claude subagent (edit tools only) — writes all the code. The
goal: spend the big model's tokens on judgment (specs, verification, review) and the cheap tier's
tokens on volume (code), without giving up output quality.

Components:

| Component | What it is |
|-----------|------------|
| `/conductor:implement` | **Command** — the coordinator script: plan or accept a plan → dual plan review → per-unit spec/implement/verify/fix (linear), or `--fanout` → close-out with cross-model review. Every run keeps a ledger and can be continued with `--resume`. |
| `conductor-implementer` | **Agent** — the claude-lane implementer (opus by default; no Bash — edit-only is structurally enforced). Launched only by the command. |
| `conductor-reviewer` | **Agent** — stateless evidence-forcing reviewer (inherits your session's model — review stays on the big tier). Launched only by the command. |
| `delegation-doctrine` | **Skill** — the coordinator doctrine: roles, five-part spec + report contract, escalation ladder, review rubric (with `reference/` templates). |
| `calling-codex` | **Skill** — the codex CLI invocation convention (edit-only, network-off, sandbox, flags, session resume). |
| `implement-fanout` | **Workflow** — parallel fan-out: decompose into file-disjoint units → isolated worktree implementers → verify/merge gate → final verify. |

## Replaces codex-orchestration

This plugin replaces `codex-orchestration`. Uninstall that plugin and migrate invocations:

- `/codex-orchestration:codex-implement [plan]` → `/conductor:implement [plan]`
- `/codex-orchestration:codex-implement-fanout [plan]` → `/conductor:implement [plan] --fanout`

What changed: the implementer is now pluggable (codex **or** a Claude subagent — codex is no
longer a hard requirement), the command can also plan from a raw task description (with a
mandatory approval pause), every handoff uses a backend-agnostic five-part spec + structured
report, a cross-backend escalation ladder replaces dead-end failures, and the fan-out gained a
close-out review stage. The hard-won codex guardrails carry over unchanged — plus a fix: `codex
exec resume` takes no `-s` flag, so resume calls now pass the sandbox via
`-c 'sandbox_mode="workspace-write"'`.

## Prerequisites

- **Claude lane: nothing extra.** It works out of the box; the implementer is a Claude subagent.
- **Codex lane (optional, auto-detected):** the OpenAI `codex` CLI installed and authenticated
  (`codex --version`, `codex login status`), `jq` on PATH, the repo trusted in
  `~/.codex/config.toml`, and a codex model supporting `xhigh` reasoning (the GPT-5.x-codex
  family and gpt-5.5 do).

## Install

```bash
/plugin marketplace add ebner/agentics
/plugin install conductor@agentics
```

## Usage

```
/conductor:implement [path/to/plan.md | task description] [--fanout] [--backend codex|claude]
                     [--base <branch>] [--integration <branch>] [--implementer-model opus|sonnet]
/conductor:implement --resume [run-id]
```

Two entry modes:

- **Plan mode** — pass an approved plan file (or run it as your next message after approving a
  plan in plan mode; it resolves the session's plan automatically). The command reviews the plan
  (cross-model when codex is available), then implements it unit by unit.
- **Raw-task mode** — pass a task description. The coordinator explores the codebase, drafts a
  plan, reviews it, and **pauses for your approval** before implementing anything. When codex is
  available and the task changes a public interface, a persistent schema, or the dependencies,
  or has two plausible approaches, codex first writes its own plan without seeing the
  coordinator's. The coordinator compares the two after drafting and records each divergence it
  adopted or rejected in the plan.

A delegation-worthiness gate declines orchestration for tiny tasks (under 20 changed lines in at
most 2 files) where the overhead exceeds the savings — you choose direct implementation instead.

### Backend selection and escalation

| Situation | What happens |
|-----------|--------------|
| `--backend` omitted (auto) | codex lane if `codex` + `jq` installed and logged in, else claude lane — announced with the reason |
| unit fails its gate | ≤ 2 fix rounds on the same lane (codex: session resume; claude: fresh agent with verbatim failures) |
| lane exhausted | re-route to the other lane: fresh spec + distilled failure history, clean re-implementation |
| both lanes exhausted | the coordinator implements that unit itself — announced explicitly |

Model tiers: implementation runs on the cheap tier (codex at your configured model, or a Claude
opus/sonnet subagent); plan review and final review stay on the strong tier (codex `xhigh` +
a reviewer inheriting your session's model). The coordinator never writes code outside the
announced last-resort rung.

### Settings file (optional)

Create `.claude/conductor.local.md` in the target project (add it to `.gitignore`):

```markdown
---
backend: auto                    # codex | claude | auto
claude_implementer_model: opus   # opus | sonnet
codex_effort: xhigh              # implementation/fix calls only; reviews always run xhigh
codex_model: ""                  # empty = your configured codex default
independent_plan: auto           # auto | always | never — codex's independent plan in raw-task mode
fast_gate: ""                    # override gate discovery, e.g. "npm run typecheck && npm test -- --changed"
heavy_gate: ""                   # e.g. "npm test && npm run e2e"
---
```

Precedence: command flags > settings keys > defaults.

## Fan-out (`--fanout`)

For large, decomposable plans. Invoking the flag is itself the multi-agent opt-in (spawns many
parallel agents and implementer sessions — meant for plans with genuinely independent units).

- **Dynamic decomposition.** A coordinator-tier agent splits the plan into file-disjoint units,
  each carrying a self-contained five-part spec, layered into dependency waves. Overlapping units
  are merged into one sequential unit rather than risking merge conflicts.
- **One worktree per implementer.** Each unit's agent runs with `isolation: 'worktree'` and
  commits to its own branch `conductor/unit-<id>` — parallel agents never collide on files or the
  git index.
- **Sequential verify/merge gate.** A coordinator-tier gate merges each unit branch into the
  integration branch (`git merge --no-ff`), audits scope from the actual diff, and runs the
  unit's verification. Red build → verbatim failure log → the unit's fix ladder (≤ 2 rounds, then
  re-route to the other backend). Non-trivial conflicts are never force-merged — the unit gets
  one clean re-implementation off the updated integration branch instead.
- **Where the result lands.** The merged, verified result is on the integration branch (default
  `conductor/integration`). Nothing is pushed and nothing touches your base branch — the final
  merge is yours to review. Units that exhaust the ladder come back to the coordinator with their
  spec and last failure log (the announced last-resort rung), and close-out review runs against
  the integration branch.

## Run ledger and `--resume`

Every run writes an append-only ledger to `.git/conductor/runs/<run-id>/` (inside the git
directory, so it is never tracked and needs no `.gitignore` entry). It holds the run
configuration, one log line per dispatch, report, gate run, and review, and verbatim copies of
codex output, gate output, and reviewer output. The coordinator reads it after a context
compaction, the close-out report takes unit outcomes from it, and you can audit any claim in the
report against it.

If a session dies mid-run, continue it from a new session:

```
/conductor:implement --resume              # the most recent unfinished run
/conductor:implement --resume <run-id>     # a specific run
```

Units already finished are skipped. An attempt that was in flight is rolled back to its snapshot
and retried fresh, counting as one attempt. A fan-out run can only be resumed from the session
that launched it; from another session you choose between re-running the fan-out and stopping.
Delete `.git/conductor/runs/` whenever no run is active.

## Safety model (summary; full detail in the `calling-codex` skill)

Codex runs **edit-only**: writes confined to the workspace and network **off**, both OS-enforced
(Landlock/seccomp on Linux). It never builds, installs, commits, or escalates
(`approval_policy=never` keeps the sandbox as a hard ceiling). The claude-lane implementer has
the same posture enforced by its tool allowlist: no Bash in linear mode; enumerated git commands
only in fan-out worktrees, audited by the gate. The coordinator — with full access — owns all
builds, tests, network, and merges, and never auto-commits or pushes to your branch. Note:
read-confinement to the project is **not** kernel-enforced on Linux in current Codex versions;
the protection is network-off + write-confine + edit-only. Never run Codex with
`--dangerously-bypass-approvals-and-sandbox`.

## Examples

### 1. Implement an approved plan (linear — the common case)

Plan in plan mode and approve it, then make your **next** message:

```
/conductor:implement
```

It resolves the current session's plan automatically; or pass a path explicitly:

```
/conductor:implement docs/plans/add-rate-limiter.md
```

### 2. Start from a task description

```
/conductor:implement Add per-tenant data isolation to the API: tenant column on resource tables,
JWT middleware, repository-layer scoping, migrations, and integration tests.
```

The coordinator plans, reviews the plan, pauses for your approval, then implements.

### 3. Fan out a large plan

```
/conductor:implement ~/.claude/plans/tenant-isolation.md --fanout
```

Decompose → parallel worktree implementers → merge gate → close-out review on
`conductor/integration`. Override defaults with `--base <branch>`, `--integration <branch>`, or
`--backend codex|claude`.

## Dev tests

`tests/mock-codex` is a PATH stub that enforces the calling-codex guardrail flags (exits 2 on any
violation) and simulates failure modes (`MOCK_CODEX_FAIL`, `MOCK_CODEX_MODE`);
`tests/make-toy-repo.sh` builds a scratch repo with a 2-unit plan and a deterministic red-gate
scenario. See the headers of both scripts.
