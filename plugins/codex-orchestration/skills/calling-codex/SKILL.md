---
name: calling-codex
description: >
  How to invoke OpenAI Codex from automation via the official `codex` CLI. Trigger this skill
  whenever you are about to construct a `codex exec` or `codex review` command — for plan review,
  delegated implementation, gap-fixing, or code review — or when the `codex-implement` command and
  `codex-implement-fanout` workflow run. Covers the codex-exec-vs-codex-review split, the always-on
  guardrails (effort, sandbox, approval, network, stdin, output capture, session resume), the
  edit-only orchestration pattern, and the Linux read-confinement caveat.
allowed-tools:
  - Bash
  - Read
---

# Calling Codex (official `codex` CLI)

This is the single source of truth for how to drive OpenAI Codex (GPT-5.x) from automation. The
`codex-implement` command and the `codex-implement-fanout` workflow follow it verbatim. Use the
official `codex` CLI on `PATH` — not the `openai-codex` plugin's `node …/codex-companion.mjs`
wrapper (it wraps an Experimental app-server) and not the `/codex:*` plugin slash commands (those
are for ad-hoc human use). `codex exec` and `codex review` are OpenAI's Stable automation contract.

## Prerequisites (check once)

- `codex` is installed and on `PATH`: `codex --version`.
- Authenticated: `codex login status`.
- The project is trusted: add the repo path under `~/.codex/config.toml` `[projects."…"] trust_level = "trusted"`, or the first run may block on a trust prompt.
- The configured model supports `xhigh` reasoning (the GPT-5.x-codex family and gpt-5.5 do; check `~/.codex/models_cache.json` → `supported_reasoning_levels`). If it does not, pin one that does with `-m <model>`.

## Three purposes, three invocations

1. **Diff / code review** → `codex review` (or `codex exec review`). This is the *structured* review
   pipeline — the same engine the GitHub `@codex` review bot runs. **Never** review a diff with a
   free-form `codex exec "review this"`: that drops to a generic task runner that empirically misses
   findings the structured pipeline catches (e.g. cross-file invariants like a transaction boundary
   interacting with a lazy association outside the diff).
   - **Full-changeset review (committed + uncommitted + untracked):** the target flags are mutually
     exclusive, and `--commit` is broken inside git worktrees (do not use it there). `--uncommitted`
     authoritatively covers staged + unstaged + untracked (with a per-file size cap). `--base <ref>`
     covers the branch-vs-base delta. To cover everything durably, run both `codex review --base
     origin/<base>` and `codex review --uncommitted`, then dedup the overlap. When nothing is
     committed ahead of base (`git rev-list --count origin/<base>..HEAD` == 0), `--uncommitted`
     alone is complete.
2. **Plan review** (no diff yet) → `codex exec -s read-only "<review request + the plan text embedded
   inline>"`. Codex's sandbox cannot read paths outside the workspace, so embed the plan text in the
   prompt; end the prompt with one final line `VERDICT: APPROVED` or `VERDICT: REVISE`.
3. **Task / implementation** → `codex exec -s workspace-write`. Continue an existing run with
   `codex exec resume <session-id>`.

## Guardrails — apply on every call

- **Reasoning effort, explicit every time.** Pass `-c 'model_reasoning_effort="<level>"'` on every
  call. Explicit is mandatory: the last-used effort is cached in SQLite and silently overrides
  config, and config-inherited effort can silently drop to a lower level. Use `xhigh` for
  implementation, gap-fixing, and deep plan review; `low` or `medium` only for throwaway checks.
- **Approval: `-c 'approval_policy="never"'`.** There is no `-a`/`--ask-for-approval` flag on
  `codex exec` (passing `-a never` is a parse error). `never` means "never *ask*", not "never
  *grant*": Codex runs autonomously **within** the sandbox without prompting, and — having no
  escalation path — cannot step **outside** it, so `-s` is the hard ceiling. Never pass
  `--dangerously-bypass-approvals-and-sandbox` (that removes the sandbox entirely).
- **Network OFF for implementation.** `-s workspace-write` blocks network by default — keep it that
  way; do not add `network_access=true`. Codex runs **edit-only** (see the pattern below); the
  orchestrator runs builds and dependency resolution, so Codex needs no network. Network-off is the
  OS-enforced egress control.
- **Deliver the prompt via stdin redirect** (`< promptfile`). A `codex exec` with a *positional*
  prompt and *unredirected* stdin **hangs** in a non-TTY / background context: it still reads stdin
  (the CLI prints `"Reading prompt from stdin..."` or, on newer versions, `"Reading additional
  input from stdin..."`), which never reaches EOF. Use `< file` (or `< /dev/null` if the prompt must
  be positional).
- **Capture the result — the mechanism differs by subcommand.** `codex exec` supports `-o <file>` (it
  writes the final message). `codex review` has **no** `-o`/`--output` flag — passing it exits with a
  usage error (`Usage: codex review …`) — so capture its review by **redirecting stdout** to a file
  (`… < /dev/null > "$out" 2>&1`). For `codex exec`, do not parse `--output-schema` output as the
  result — intermediate messages also conform to the schema, and it is unreliable on `resume`; mandate
  a `VERDICT:` line instead. Use `--json` (event stream) to read the `session_id` from the
  `thread.started` event.
- **Resume with an explicit captured `session_id`, not `--last`** (concurrent worktrees race on
  `--last`).
- **Sandbox nesting.** Codex enforces its own sandbox via Landlock/seccomp. If the calling harness
  also sandboxes shell commands, the two can conflict and Codex's sandbox fails to initialize — run
  the `codex` Bash call with the harness's own sandbox disabled (in Claude Code: Bash
  `dangerouslyDisableSandbox: true`). This removes only the *outer* layer; Codex's `-s` sandbox still
  confines it. The user's permission mode must allow this.

## Reference command lines

```bash
# Use mktemp for every capture file — avoid predictable /tmp paths.

# Plan review (read-only; write the review brief + plan into "$prompt"):
prompt=$(mktemp); out=$(mktemp)
codex exec -s read-only -c 'approval_policy="never"' -c 'model_reasoning_effort="xhigh"' \
  -o "$out" < "$prompt"

# Implementation (edit-only; network off; capture session id; write the handoff into "$handoff"):
handoff=$(mktemp); out=$(mktemp); jsonl=$(mktemp)
codex exec -s workspace-write -c 'approval_policy="never"' -c 'model_reasoning_effort="xhigh"' \
  --json -o "$out" < "$handoff" > "$jsonl"
SESSION_ID=$(jq -r 'select(.type=="thread.started").session_id' "$jsonl" | head -1)

# Gap-fix (resume the same session; write gaps + verbatim failures into "$fix"):
fix=$(mktemp)
codex exec resume "$SESSION_ID" -s workspace-write -c 'approval_policy="never"' \
  -c 'model_reasoning_effort="xhigh"' -o "$(mktemp)" - < "$fix"

# Structured diff review (full changeset) — codex review has NO -o flag; capture via stdout redirect:
unc=$(mktemp); base_out=$(mktemp)
codex review --uncommitted -c 'approval_policy="never"' -c 'model_reasoning_effort="xhigh"' < /dev/null > "$unc" 2>&1
codex review --base origin/<base> -c 'approval_policy="never"' -c 'model_reasoning_effort="xhigh"' < /dev/null > "$base_out" 2>&1
```

Run a long implementation or review in the background (in Claude Code, Bash `run_in_background: true`)
and read its captured output on completion — the `-o` file for `codex exec`, or the redirected-stdout
file for `codex review`. The CLI has no script-level `--background` flag and no `status`/`--wait` to
poll.

## Edit-only orchestration pattern

Codex only **edits** code. It does not build, install, test, commit, or touch the network — the
**orchestrator** (the calling agent, which has full access) does all of that. This keeps Codex
network-free and minimizes its footprint:

- The orchestrator discovers the project's verification gate from the project's `CLAUDE.md` /
  `AGENTS.md` / `README`, or from its build config (`package.json` scripts, `pom.xml`, `Cargo.toml`,
  `go.mod`, `Makefile`), and runs typecheck / build / lint / test itself.
- For a multi-step plan, the orchestrator runs a **per-phase loop**: Codex implements one phase
  (offline, via `codex exec resume` to carry context across phases), then the orchestrator
  builds/verifies that phase and feeds any failure back to Codex before the next phase. **The failure
  handback must be the full verbatim output** — the exact commands, their stderr, errors with
  `file:line`, failing-test assertion diffs, and stack traces (root errors first, capped, never a
  summary). Codex did not run the build, so this is its only view of the failure; it then reads the
  cited files and fixes.
- Codex's handoff prompt must forbid: commits, pushes, dependency additions without flagging, builds
  / tests / installs / network commands, and edits outside the named in-scope files. It must honor
  the target project's own conventions as documented in that project's `CLAUDE.md` / `AGENTS.md`.

## Sandbox / safety model

- **Writes** (workspace-only) and **network** (off) are OS-enforced (Landlock/seccomp on Linux).
- **Read-confinement to the project is NOT enforced on Linux** in current Codex versions (a raw
  shell read of a file under `$HOME` is not kernel-blocked). The protection model is therefore
  **network-off + write-confine + edit-only**: with no egress and no task-reason to read outside the
  project, anything Codex reads cannot leave except in its reply to the orchestrator. Do not treat
  read-confinement as a security boundary on Linux.
- The only mode that removes confinement is `--dangerously-bypass-approvals-and-sandbox`. Never use
  it from automation.
