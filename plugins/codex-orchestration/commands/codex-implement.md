---
description: Hand an approved implementation plan to OpenAI Codex (edit-only) for implementation, with cross-model plan review and a per-phase verify/fix loop
argument-hint: "[path/to/plan.md]"
allowed-tools: ["Read", "Write", "Bash", "Agent", "AskUserQuestion", "Skill"]
---

# Codex Implement

Hand an **already-approved** implementation plan to **Codex** for implementation, with cross-model
review on both ends. The orchestrating model orchestrates and reviews; **Codex writes all the code**.

The flow, driven **phase by phase** for multi-step plans: review the plan (orchestrator **and** Codex)
→ for each phase, Codex implements (offline, edit-only) and the orchestrator builds/verifies and feeds
back any fixes → then a simplification pass + final review (orchestrator **and** Codex). **Codex edits;
the orchestrator runs every build/test (Codex has no network and never builds).**

> **Prerequisite:** a plan must already exist and be approved (produced by plan mode or a planning
> command). This command does not plan; it executes an approved plan via Codex. Run it as your next
> message after approving the plan — approving only unlocks edit tools; this command's role-lock
> redirects implementation to Codex.
>
> **Codex invocation:** every `codex` call in this command follows the **`calling-codex` skill** in
> this plugin — official CLI only, always `-c 'model_reasoning_effort="xhigh"'` and
> `-c 'approval_policy="never"'`, network off, prompt via stdin redirect, `-o` capture, `--json`
> session id, background long runs, disable the harness's own Bash sandbox on write-capable calls.
> Load that skill before the first Codex call; the lines here restate only the shape.

## Usage

```
/codex-orchestration:codex-implement [path/to/plan.md]
```

`$ARGUMENTS` (optional) is the plan-file path. If omitted, the command resolves the current session's
plan.

## Pipeline overview

| Stage | What runs | Who | Bound |
|-------|-----------|-----|-------|
| 0 | Preconditions, plan resolution, project-gate discovery, role lock | orchestrator | — |
| 1 | Dual plan review (orchestrator architect + Codex), revise loop | orchestrator + Codex | ≤ 3 rounds |
| 2 | Per-phase loop: Codex implements a phase (offline, edit-only) → orchestrator builds/verifies → fix loop → next phase | Codex edits; **orchestrator builds/verifies** | ≤ 2 fix rounds / phase |
| 3 | Close-out: re-verify + simplify + final dual review + consolidate | orchestrator + Codex | — |

Run autonomously end-to-end. Do not ask "should I continue?" between stages — stop only at the
genuine forks called out below. **Codex is edit-only (network off, no builds); the orchestrator runs
every build/test. Never auto-commit or push.**

## Stage 0 — Preconditions, plan, project gate, role lock

1. **Codex available?** Run `codex login status` (and `codex --version`). If `codex` is missing or not
   logged in, stop and tell the user to install it / run `codex login`. Do not fabricate a fallback or
   use the `openai-codex` plugin's companion script.
2. **Resolve the plan**, in this order: `$ARGUMENTS` path → the current session's plan file → a plan
   created earlier in this conversation → otherwise ask the user with `AskUserQuestion`. Read it in
   full.
3. **Discover the project's verification gate and conventions** (do NOT assume any specific stack):
   - **Gate commands** — read the project's `CLAUDE.md` / `AGENTS.md` / `README`, then its build
     config (`package.json` scripts, `pom.xml`, `Cargo.toml`, `go.mod`, `Makefile`) to determine how
     to typecheck, build, lint, and test. Record the fast checks (typecheck/build/lint + targeted
     tests) separately from the heavy/slow suite (full test run, integration, end-to-end).
   - **Base branch** — `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'`;
     fall back to `main` if unset.
   - **Project conventions** — note the conventions the project documents in its `CLAUDE.md` /
     `AGENTS.md` (identifier generation, error types, localization/i18n, framework-specific nesting or
     lint rules) so the Codex handoff can require them.
4. **Role lock.** For the rest of this command you are the **ORCHESTRATOR**: do not write or edit any
   source, feature, or test code yourself. Every code edit is delegated to Codex via `codex exec`.
   Your job is to construct prompts, review, verify, and consolidate. (Editing the *plan file* in
   Stage 1 is allowed — that is orchestration, not code.)

## Stage 1 — Dual plan review (≤ 3 rounds)

Run both reviewers, then decide.

**Codex (read-only, structured-as-VERDICT).** Codex's sandbox cannot read paths outside the
workspace, so embed the plan in the prompt. Write a prompt file containing an adversarial plan-review
brief (completeness, feasibility, missing edge cases, test gaps, alignment with the project's
documented conventions, reuse of existing utilities, risks), then the full plan text, then a final
instruction: "End your reply with exactly one line: `VERDICT: APPROVED` or `VERDICT: REVISE`." Run it
read-only per the `calling-codex` skill and read the verdict from the `-o` file (non-zero exit → report
and stop).

**Orchestrator (independent architect).** Launch one `Plan` agent (`subagent_type: "Plan"`) with an
adversarial completeness brief over the same plan: gaps, infeasibility, missing edge cases, untested
paths, convention misalignment, and whether existing utilities should be reused instead of new code.

**Decide.**
- Both clear (Codex `APPROVED`, architect finds nothing material) → Stage 2.
- Otherwise edit the plan file to address substantive findings, then re-review (Codex may `resume` with
  a "what changed" note, or run fresh). Cap 3 rounds.
- **Genuine fork → stop + `AskUserQuestion`:** an ambiguous requirement the reviewers surface, or a
  persistent `VERDICT: REVISE` after round 3. Mechanical completeness gaps are auto-resolved without
  asking.

## Stage 2 — Implement + verify, phase by phase

Codex is **edit-only**: it writes code but never builds, installs, or touches the network. The
orchestrator (full access) runs every build/verify between Codex's edit-steps. Walk the plan's phases
in order; a small or single-phase plan collapses to one iteration.

For each phase **P** of the plan:

### 2a. Codex implements P (offline, edit-only)

Build a handoff prompt for *this phase* using the GPT-5.x block structure (per the `calling-codex`
skill):
- `<task>` — implement phase **P** (quote P's files, acceptance criteria, and the tests that define
  "done").
- Plan context — on phase 1 embed the full plan; later phases rely on the resumed session's memory.
- `<grounding_rules>` — follow the project's documented conventions; reuse the utilities the plan
  names; read before writing.
- `<action_safety>` — modify only in-scope files; no new dependencies without flagging; do not
  commit/push; do not run builds, tests, installs, or any network command (the orchestrator verifies);
  honor the project conventions captured in Stage 0.
- `<completeness_contract>` — implement every item of phase P; no TODO/stub/placeholder.

Run it edit-only, network off, in the background, prompt via stdin redirect, per the `calling-codex`
skill. On phase 1 capture the `session_id` from the `--json` stream; on later phases resume that
session. Present Codex's final message + touched files. Non-zero exit / empty output → surface and
stop.

### 2b. Orchestrator verifies P (full access)

You — not Codex — run the build/verify for phase P (you have network + toolchain + cache access; Codex
does not). Read the changed code + `git diff`, then run the **fast** gate discovered in Stage 0
(typecheck / build / lint + P's targeted tests). The heavy/slow suite runs once at the end in Stage 3.
Record P against the plan: Fully Implemented / Compromises / Outstanding.

### 2c. Fix loop for P (≤ 2 rounds)

If P's verify fails or P has outstanding items, resume Codex (edit-only) with the gaps + the **full
verbatim failing output** — the exact command(s) run, their stderr, compiler/type errors with
`file:line`, failing test names with assertion diffs, and stack traces (root errors first; cap the
volume but do **not** summarize or paraphrase). Codex did not run the build, so this prompt is its only
view of the failure; also tell it to read the cited files. Re-run 2b. Cap 2 fix rounds per phase; if P
still fails, stop and surface the residual (genuine fork). On success, advance to P+1.

After the last phase, do a whole-changeset pass against the plan (Fully Implemented / Compromises /
Outstanding), annotate any accepted compromises into the plan file, then go to Stage 3.

## Stage 3 — Close-out (re-verify + simplify + final dual review)

If the project has a dedicated post-implementation pipeline (a `/plan-follow-up`-style command that
re-verifies, simplifies, runs a dual review, and consolidates), delegate to it and stop. Otherwise run
the close-out directly:

1. **Re-verify** the whole changeset against the plan with the project's full gate, including the
   heavy/slow suite (full tests, integration, end-to-end) discovered in Stage 0.
2. **Simplify** — run a behavior-preserving simplification pass if one is available (the built-in
   `simplify` skill, or the project's simplify command).
3. **Final dual review** — a structured `codex review` over the full changeset (the `--base` +
   `--uncommitted` recipe in the `calling-codex` skill) PLUS the project's own review command if it
   has one. Capture both verbatim.
4. **Consolidate** findings into Must-fix / Should-fix / Optional with cross-reviewer attribution, and
   end with a pre-PR recommendation.

Do not auto-commit or push — the user reviews the recommendation and commits.

## Failure & fork handling (summary)

- Codex missing / logged out → stop, point to `codex login`.
- Non-zero `codex exec` exit, or empty output → surface, do not fabricate.
- Plan-review unresolved after 3 rounds, or an ambiguous requirement → stop + `AskUserQuestion`.
- Per-phase gap-fix unresolved after 2 rounds → stop + surface the residual list.
- Missing/empty plan → `AskUserQuestion` for the path.
- Every Codex prompt forbids commits, dependency additions without flagging, out-of-scope edits, and
  running builds/tests/installs/network (Codex is edit-only; the orchestrator verifies).
