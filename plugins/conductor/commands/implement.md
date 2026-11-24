---
description: Orchestrate implementation of a plan or task — the coordinator plans/reviews/verifies, a cheaper implementer (Codex CLI or a Claude subagent) writes all the code
argument-hint: "[plan.md path | task description] [--fanout] [--backend codex|claude] [--base <branch>] [--integration <branch>] [--implementer-model opus|sonnet] [--resume [run-id]]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Agent", "AskUserQuestion", "Skill", "Workflow"]
---

# Conductor: Implement

Plan big, execute small. You — the COORDINATOR — plan, decompose, review, and run every
build/test/merge; a cheaper implementer backend (OpenAI Codex edit-only, or a Claude subagent)
writes all the code. Entry is either an approved plan file or a raw task description (then you
plan first and pause for the user's approval of the plan).

> **Doctrine:** every delegation follows the **`delegation-doctrine` skill** (roles, spec/report
> contract, escalation ladder, review doctrine). Load it before Stage 0 step 4. Every `codex` call
> follows the **`calling-codex` skill**; load it before the first codex call (only if the codex
> lane is selected).
>
> **Autonomy:** run end-to-end. Do not ask "should I continue?" between stages — **§Forks is the
> complete list of stopping points**, so a decision not named there is yours to make: how to word a
> spec, which of two equivalent phrasings to use, a naming or formatting choice, how to distribute
> acceptance criteria across units. Make it and keep going; do not close a stage by offering the user
> a next step the stage already covers. **Never auto-commit or push** —
> this applies to the user's branch and base; in fanout mode the workflow's unit-branch commits and
> integration-branch merges are orchestration mechanics on dedicated branches (base untouched,
> nothing ever pushed; gate agents act as coordinator-tier delegates).
>
> **Conduct:** doctrine §11 governs how you report — every status claim is read from an artifact
> (the run ledger, a diff, an exit status, the plan file) and never from recollection; corrections
> are one sentence and only when they change the user's decisions; the Stage 4 report re-grounds a
> user who has not been watching.
>
> **Run ledger:** every run keeps an append-only ledger per the doctrine's `reference/run-ledger.md`
> (location, events, resume). Append each event at the point that file's §2 names. After a context
> compaction mid-run, re-read the ledger before your next action.

## Usage

```
/conductor:implement [path/to/plan.md | task description] [--fanout] [--backend codex|claude]
                     [--base <branch>] [--integration <branch>] [--implementer-model opus|sonnet]
/conductor:implement --resume [run-id]
```

`--resume` continues an interrupted run from its ledger: after Stage 0 steps 1–2, load the
`delegation-doctrine` skill, read its `reference/run-ledger.md`, and follow its §4 instead of
Stage 0 steps 3–8.

## Pipeline overview

| Stage | What runs | Who | Bound |
|-------|-----------|-----|-------|
| 0 | Settings, backend selection, entry resolution, worthiness gate, gate discovery, role lock, baseline | coordinator | — |
| 1 | (raw-task mode only) explore + independent proposal when triggered + draft the plan | coordinator; codex for the proposal | 1 proposal |
| 2 | Plan review + revise; raw-task mode ends with a user approval pause | reviewers per Stage 2 | ≤ 3 rounds |
| 3 | Per-unit spec → implement → verify → fix (linear), or `--fanout` workflow | implementer edits; **coordinator verifies** | ≤ 2 fix rounds per lane, ≤ 2 lanes, then coordinator |
| 4 | Close-out: heavy gate, simplification list, final review, 1 fix round, consolidate | coordinator + reviewers | 1 close-out fix round |

## Stage 0 — Preconditions & routing

1. **Settings.** If `.claude/conductor.local.md` exists, read its YAML frontmatter. Keys (all
   optional): `backend: auto|codex|claude` (default `auto`), `claude_implementer_model:
   opus|sonnet` (default `opus`), `codex_effort` (default `xhigh`; implementation and fix calls
   only), `codex_model` (default empty = the user's configured codex model), `fast_gate`,
   `heavy_gate` (shell commands overriding step 5's discovery), `independent_plan:
   auto|always|never` (default `auto`; Stage 1). Precedence, in order: command flag > settings
   key > default. The RUN CONFIG block (backend, codexAvailable, lane models, gate commands, base
   branch, baseline, independent_plan, execution mode linear or fan-out, and for fan-out the
   `--base` and `--integration` branches resolved per the fan-out branch's step 1) is finalized
   after step 7; later stages reference it.
2. **Backend selection** (run the detection exactly once):
   - Forced `--backend codex` (flag or settings): run `codex --version`, `codex login status`,
     and `command -v jq`. Any failure → `AskUserQuestion` (switch to the claude lane / stop so
     the user can fix codex — name the failing check and the fix). Never fall back silently.
   - Forced `--backend claude`: run the same three checks anyway, solely to record
     `codexAvailable` for escalation rung 2.
   - Auto: all three checks pass → codex lane; otherwise claude lane. Announce the selected lane
     and why, quoting the failing check if any.
   - Repo trust (`~/.codex/config.toml`) and an xhigh-capable codex model are documented
     prerequisites, not probed — violations surface as `unavailable`/`timeout` per the doctrine's
     failure mapping.
   - The claude lane's implementer is `conductor:conductor-implementer` (launch strings per
     doctrine §4), launched with `model: "sonnet"` only when `claude_implementer_model: sonnet`
     is configured; otherwise its frontmatter default (opus) applies.
3. **Entry resolution.** Strip the flags from `$ARGUMENTS`; then:
   - the remainder resolves to an existing regular file → **plan mode**: read it in full;
   - the remainder matches `\.(md|txt)$` or contains `/` but no such file exists →
     `AskUserQuestion` (fix the path / treat the text as a task description);
   - the remainder is non-empty text → **raw-task mode**;
   - the remainder is empty → resolve in this order: the current session's plan file → a plan
     created earlier in this conversation → otherwise `AskUserQuestion`.
4. **Delegation-worthiness gate** (plan mode: now; raw-task mode: immediately after Stage 1,
   before Stage 2's review rounds). If the plan names ≤ 2 files AND the summed estimated changed
   lines is < 20 AND no new test files are required — OR the task requires MCP tools,
   credentials, or secrets the implementer backends cannot have — then `AskUserQuestion`:
   *Implement directly in this session* (role lock disengages; in raw-task mode this means
   implementing the just-written plan yourself) / *Orchestrate anyway* / *Cancel*.
5. **Discover the project's verification gate and conventions** (do NOT assume any specific stack):
   - **Gate commands** — read the project's `CLAUDE.md` / `AGENTS.md` / `README`, then its build
     config (`package.json` scripts, `pom.xml`, `Cargo.toml`, `go.mod`, `Makefile`) to determine
     how to typecheck, build, lint, and test. Record the fast checks (typecheck/build/lint +
     targeted tests) separately from the heavy/slow suite (full test run, integration,
     end-to-end). Settings `fast_gate`/`heavy_gate` override discovery when present.
   - **Base branch** — `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'`;
     if unset: `master` if `git rev-parse --verify master` succeeds, else `main`, else the current
     branch — announce the choice.
   - **Project conventions** — note the conventions the project documents in its `CLAUDE.md` /
     `AGENTS.md` (identifier generation, error types, localization/i18n, framework-specific
     nesting or lint rules) so every spec's CONSTRAINTS can require them.
6. **Role lock.** For the rest of this command you are the **COORDINATOR**: do not write or edit
   any source, feature, or test code yourself. Every code edit is delegated to the implementer
   backend. Your job is to construct specs, dispatch, review, verify, and consolidate. Exactly two
   exceptions, stated here so the rule and its exceptions live together: (a) editing the *plan
   file* is orchestration, not code; (b) escalation rung 3 in Stage 3f — after the available
   implementer lanes are exhausted — is the only case where you implement directly, and you must
   state the downgrade first. The delegate-vs-keep list in doctrine §3 governs only the entry
   decision (step 4); once orchestration starts, all code edits route to the implementer
   regardless of size, except rung 3.
7. **Working-tree baseline.** Record `git status --porcelain`. If non-empty → `AskUserQuestion`
   (proceed — rollbacks become best-effort, scoped to files this run touches — or stop so the
   user can commit/stash first). The baseline scopes all later rollbacks and per-unit deltas.
8. **Open the run ledger.** Create the run directory and write `run.md` per
   `reference/run-ledger.md` §1, then append `stage` 0 `entered`. Announce the run id once, so the
   user can pass it to `--resume`.

## Stage 1 — Plan (raw-task mode only)

Explore the codebase first: the project's conventions, the code the task touches, and existing
utilities that should be reused instead of new code.

**Independent proposal — decide.** A second model can propose its own plan without seeing yours,
so where the two diverge, the divergence is not anchored to your draft. It runs when codex is
available and either `independent_plan: always` is set, or `independent_plan: auto` is set and
both of these hold:
- your exploration estimates the task above the worthiness floor (doctrine §9);
- the change will do at least one of these: alter a public interface (an exported API, CLI flags,
  an HTTP endpoint, or a file format or wire protocol other code consumes), change a persistent
  schema or include a data migration, add a runtime dependency, or choose between two approaches
  you can name that would change different sets of files.

Otherwise skip it and say why in one line (codex unavailable, `never`, or no trigger matched).
When it runs, launch the read-only codex call with the independent-proposal brief from the
doctrine's `reference/review-rubric.md` §6 in the background now, and draft while it runs.

**Draft.** Write the plan to `~/.claude/plans/<branch-slug>.md` (branch name slugified, `/` → `-`;
add a `-<topic-slug>` suffix if that file exists for an unrelated plan). Required structure:
numbered units, each with Files / acceptance criteria / verification command(s) / dependencies.
Stay inside doctrine §9's sizing band: no unit below the worthiness floor (merge undersized units),
and no more than 20 units in the plan or 12 in any one dependency wave (merge adjacent same-file
units, or split the work into separate runs). Append the plan path to the ledger's `run.md`.

**Independent proposal — compare.** The order is fixed: read the proposal only after your plan
file is written, or the comparison is anchored after all. Copy the proposal into the ledger's
`artifacts/`. For each material divergence (a different overall approach, a unit or risk your plan
lacks, or a different FILES set for the same unit), adopt it into the plan or reject it, and record
it under `## Independent proposal — divergences` as one line: what differed, adopted or rejected,
and why. A codex failure here is not a stop: note it in one line and continue without the proposal.

Do not pause for approval yet — Stage 2 reviews first, then pauses.

## Stage 2 — Plan review (≤ 3 rounds)

Reviewer briefs live in the doctrine's `reference/review-rubric.md`; read that file before
launching the first reviewer. Briefs follow doctrine §10's no-history rule: a fresh reviewer in a
later round gets the revised plan, never the previous round's findings or verdicts, and the plan
text embedded in any brief omits the `## Independent proposal — divergences` section. Save each
reviewer's full output to the ledger's `artifacts/` and append its `review` line. Append `stage` 2
`plan-approved` when every reviewer approves, and `user-approved` when the user approves at the
raw-task pause.

- **Codex available** → run both, in parallel where possible:
  1. **Codex plan review (read-only).** Codex's sandbox cannot read paths outside the workspace,
     so embed the plan in the prompt: write a prompt file containing brief A (completeness) plus
     the full plan text, ending with "End your reply with exactly one line: `VERDICT: APPROVED`
     or `VERDICT: REVISE`." Run it read-only per the `calling-codex` skill and read the verdict
     from the `-o` file (non-zero exit → report and stop).
  2. **One `conductor:conductor-reviewer` agent with brief B** (premise & decomposition — the
     codex brief covers completeness, so the premise check runs on every path).
- **Codex unavailable** → launch two `conductor:conductor-reviewer` agents, one with brief A and
  one with brief B. One Agent call per reviewer, both Agent calls in the same assistant message.
- **Decide.** Reviewers report every finding with a severity and a confidence label, and compute
  their own VERDICT from those labels alone — REVISE if any reported finding is `severity: high` or
  `medium` through any channel, APPROVED only when every reported finding is `severity: low` (rubric
  principles 7 and 8). **Decide on the VERDICT line, never on the finding count**, which is expected
  to exceed the number of things worth acting on. The two cases below are mutually exclusive and
  cover every outcome, so there is no path where a finding both blocks and does not block:
  - **Every reviewer returned `VERDICT: APPROVED`** (codex included where applicable) → Stage 3. By
    the verdict rule this means nothing above `severity: low` was reported, so carry those low
    findings into the plan file as notes and run no further review round.
  - **Any reviewer returned `VERDICT: REVISE`** → edit the plan file to address every `severity: high`
    and `severity: medium` finding that reviewer reported, counting `ADDITIONAL:` bullets exactly like
    VIOLATED criteria at the same severity. Then re-review (codex may `resume` with a "what changed"
    note, or run fresh). Cap 3 rounds. Mechanical completeness gaps are auto-resolved without asking.
  - **Genuine fork → stop + `AskUserQuestion`:** an ambiguous requirement a reviewer surfaces, or any
    reviewer still at `VERDICT: REVISE` when round 3 ends.
- **Raw-task mode only — mandatory approval pause** after review passes: `AskUserQuestion`
  presenting the plan summary — *Approve* / *Revise* (free-text feedback → apply → one more
  review round → re-ask) / *Cancel*. Plan mode skips this pause (the plan was already approved;
  reviews only auto-fix mechanical gaps).

## Stage 3 — Implement (linear default)

First, **derive the unit list**: if the plan is already structured into numbered units/phases
with files and acceptance criteria, use them; otherwise decompose the plan into units (Files /
acceptance criteria / verification command(s) / dependencies — the Stage 1 shape) and annotate
the unit list into the plan file (an orchestration act, allowed under the role lock; a small plan
collapses to one unit). Append the unit list to the ledger's `run.md` and append `stage` 3
`entered`.

Ledger points in the per-unit loop: `snapshot` at 3a; `dispatch` immediately **before** every
attempt in 3b, 3e, and 3f, rung 3 included; `report` at 3c, for an assigned `timeout` or
`unavailable`, and when your own rung-3 edits are done; `gate`
after every 3d run, with the full gate output saved under `artifacts/`; `unit` when U reaches its
final state.

Then, for each unit **U** in dependency order:

### 3a. Snapshot + spec

Record U's pre-dispatch snapshot: `git stash create` (keep the SHA; it may be empty on a clean
tree) and `git status --porcelain`. Then build U's five-part spec from the doctrine's
`reference/spec-and-report.md` template — fully self-contained (the implementer never sees the
plan; every spec stands alone, including context earlier units would otherwise provide). If you
cannot finish writing any of the five parts, the decision isn't made yet: fix the plan first, or
`AskUserQuestion` for a genuine requirement ambiguity.

### 3b. Dispatch

- **codex lane:** a fresh `codex exec` per unit — edit-only, network off, background, prompt via
  stdin redirect, `timeout 1200` prefix, `--json` session_id captured (needed only for fix
  rounds), effort per RUN CONFIG — all per the `calling-codex` skill. Append the codex report
  suffix from `reference/spec-and-report.md` to the handoff.
- **claude lane:** one Agent call, `subagent_type: "conductor:conductor-implementer"`, `model`
  per RUN CONFIG (omit for opus), the spec as the entire task text.

### 3c. Report intake

Parse the structured report. Rebuild CHANGES authoritatively from the per-unit delta —
`git status --porcelain` diffed against U's 3a snapshot — so earlier units' uncommitted edits
never pollute the scope check; the implementer's own list is a claim. A claim-vs-diff mismatch is
flagged as IMPLEMENTER-SAID in U's record. Edits outside the spec's FILES list: restore those
files from the snapshot (delete new untracked ones) and count the round as failed.
`STATUS: blocked` with a question → answer it via a fix-round handoff, or `AskUserQuestion` if it
is a genuine requirement fork.

### 3d. Coordinator verifies

You — not the implementer — run the build/verify (you have network + toolchain + caches; the
implementer does not). Read the changed code and the diff, then run the **fast** gate from RUN
CONFIG plus U's verification command(s). The heavy/slow suite runs once in Stage 4. Record U:
Fully Implemented / Compromises / Outstanding.

### 3e. Fix loop (≤ 2 rounds per lane)

If U's verify fails or U has outstanding items, hand back the gaps + the **full verbatim failing
output** — the exact command(s) run, their stderr, compiler/type errors with `file:line`, failing
test names with assertion diffs, and stack traces (root errors first; cap the volume but do
**not** summarize or paraphrase). The implementer did not run the build, so this handback is its
only view of the failure; also tell it to read the cited files. Delivery per doctrine §4: codex →
`codex exec resume <session-id>` (no `-s` on resume — sandbox via config override, per
`calling-codex`); claude → a fresh `conductor:conductor-implementer` launch with the spec + the
prior report's CHANGES + the fix-round block. If the claude lane runs sonnet, fix round 2
launches with `model: "opus"`. Re-run 3d after each round. Cap 2 fix rounds, then 3f.

### 3f. Escalation ladder

Follow doctrine §8: rung 2 re-routes to the other lane (if `codexAvailable`/claude permits) with
a fresh spec + distilled failure history, after restoring every file the failed lane touched from
U's 3a snapshot; rung 3 is you, announced with the escalation notice built from the actual
attempt record. `STATUS: unavailable` skips fix rounds → immediate re-route. `STATUS: timeout` →
roll back, count one attempt, next attempt fresh (never resume a timed-out session). If your own
rung-3 attempt fails the fast gate twice → `AskUserQuestion` (skip unit U / halt the run).

After the last unit: do a whole-changeset pass against the plan (Fully Implemented / Compromises /
Outstanding), annotate any accepted compromises into the plan file, then go to Stage 4.

## Stage 3 — fan-out branch (`--fanout`)

Runs instead of the linear loop, after Stage 2. Spawns many parallel agents — invoking
`--fanout` is itself the opt-in.

1. Resolve `--base` (default: the Stage 0 base branch) and `--integration` (default
   `conductor/integration`).
2. Discover the installed workflow script:
   ```bash
   WF=$(find ~/.claude -path '*conductor/workflows/implement-fanout.mjs' -print -quit)
   ```
   Empty → stop and tell the user to install/update `conductor@agentics`.
3. Launch it: `Workflow({ scriptPath: WF, args: { planPath, base, integrationBranch, backend,
   codexAvailable, claudeImplementerModel, codexEffort, codexModel } })` — backend already
   resolved by Stage 0 (never pass `auto` from here). Append `stage` 3 `entered` before the
   call, and `fanout` with the returned run id and `state: launched` after it. When the completion
   notification arrives, record `fanout finished` and the per-unit lines per
   `reference/run-ledger.md` §2.
4. Relay the consolidated result verbatim (units, waves, integrated, failed, final gate). For
   each `failed[]` unit, apply rung 3 per doctrine §8 (it arrives with its spec and last verbatim
   failure log).
5. Then Stage 4 runs against the integration branch — explicit precondition: `git checkout
   <integration>` and a clean-tree check first. Close-out fixes remain uncommitted on the
   integration branch for the user's review.

## Stage 4 — Close-out

If the project has a dedicated post-implementation pipeline (a `/plan-follow-up`-style command
that re-verifies, simplifies, runs a dual review, and consolidates), append `stage` 4 `done`,
delegate to it, and stop.
Otherwise append `stage` 4 `entered` and run the steps below. Ledger points: a `gate` line with
unit `close-out` after every gate run, a `review` line (stage 4) per reviewer with its full output
saved, and `dispatch` / `report` lines with unit `close-out` around the step 4 fix round.

1. **Re-verify** the whole changeset against the plan with the project's full gate, including the
   heavy/slow suite (full tests, integration, end-to-end) from RUN CONFIG.
2. **Simplification list** — read the full diff yourself and produce a list of
   behavior-preserving simplification items (read-only; do NOT invoke the built-in `simplify`
   skill — it auto-applies edits, which would violate the role lock).
3. **Final review** —
   - codex available: a structured `codex review` over the full changeset (the `--base` +
     `--uncommitted` recipe in the `calling-codex` skill) PLUS one
     `conductor:conductor-reviewer` agent with the final-review brief from
     `reference/review-rubric.md`.
   - codex unavailable: the `conductor:conductor-reviewer` agent alone, with the stated caveat:
     "cross-model review is unavailable; a stateless different-context reviewer is the fallback."
   - Plus the project's own review command if it has one. Capture all outputs verbatim.
4. **Close-out fix round (cap 1).**

   First **normalize every finding to a severity label**, because only `conductor-reviewer` emits
   them: `codex review` and the project's own review command have output formats this command does
   not control. For each of their findings, assign `severity: high|medium|low` yourself using the
   same bar the reviewer applies (high = wrong behavior, a failing or weakened test, a security or
   data-loss risk, or a promised plan item missing; medium = a real defect with a bounded blast
   radius; low = everything else that is still worth recording), and mark it `severity: <label>
   (assigned)` so the report shows the label was yours. A finding from these sources is never dropped
   for lacking a label.

   Then route **by severity label only, never by channel or source** — a `severity: high` finding
   reported under `ADDITIONAL:`, or one you labeled from `codex review`, is Must-fix exactly like a
   VIOLATED criterion at that severity:
   - **Must-fix → dispatched:** every `severity: high` finding from any reviewer and any channel.
   - **`severity: medium`:** dispatch it in this round if it blocks a PR — it changes behavior the
     plan promised, or a reviewer marked it `confidence: high`; otherwise it lands in step 5's
     Should-fix.
   - **`severity: low`:** never dispatched; lands in step 5's Should-fix or Optional.

   Combine the dispatched findings with the accepted simplification items into one spec, send it to
   the primary implementer lane (3b/3c/3d semantics), then re-run the fast gate. Anything still open
   goes into the report.
5. **Consolidate** findings into Must-fix / Should-fix / Optional with cross-reviewer
   attribution, and end with a pre-PR recommendation. Rank by the severity labels from step 4 —
   including the ones you assigned there — rather than re-litigating whether a finding was worth
   raising: `high` → Must-fix, `medium` → Must-fix if it was dispatched in step 4 and Should-fix
   otherwise, `low` → Should-fix or Optional. A finding that step 4 dispatched and the fix round
   resolved is reported as fixed, not dropped from the list.

   Take each unit's final state and attempt count, and every gate result, from the ledger's
   `log.jsonl` (`reference/run-ledger.md` §3). Name the run id and the ledger path once, so the
   user can audit any claim against the verbatim artifacts. Append `stage` 4 `done` after writing
   the report.

   **Write this report for someone who stopped watching.** It is their first look at the run: open
   with the outcome in one or two sentences (what was built, whether the gate is green, what is
   outstanding), then what you need from them, then the ranked findings. Spell out unit ids, file
   paths, and gate command names instead of carrying over run shorthand. Cover every unit's final
   state and every Must-fix finding; drop anything that does not change the user's next action — no
   per-unit narration of attempts that eventually passed, no restating the plan, no recap of tool
   calls they can read in the diff. Keep the prose in full sentences: brevity comes from omitting
   detail, not from compressing what remains into fragments or arrow chains.

Do not auto-commit or push — the user reviews the recommendation and commits.

## §Forks — failure & fork handling (complete list)

- Missing/empty plan or task → `AskUserQuestion` (Stage 0.3).
- Path-like argument that doesn't exist → `AskUserQuestion` (fix path / treat as task).
- Worthiness gate trips → `AskUserQuestion` (direct / orchestrate / cancel).
- Forced codex backend unavailable → `AskUserQuestion` (switch lane / stop).
- Dirty working tree at Stage 0.7 → `AskUserQuestion` (proceed best-effort / stop).
- Plan review unresolved after 3 rounds, or an ambiguous requirement → `AskUserQuestion`.
- Raw-task mode plan approval → `AskUserQuestion` (mandatory pause).
- Implementer `blocked` on a genuine requirement fork → `AskUserQuestion`.
- Rung-3 coordinator attempt fails the fast gate twice → `AskUserQuestion` (skip unit / halt).
- `--resume` and the current branch differs from the branch the ledger recorded →
  `AskUserQuestion` (check out the recorded branch / stop).
- `--resume` finds an in-flight attempt and `pgrep -af 'codex exec'` lists a process →
  `AskUserQuestion` (wait for it to exit, at most the 1200-second cap / kill it and roll back).
- `--resume` of a fan-out run from a session other than the one that launched it →
  `AskUserQuestion` (re-run the fan-out on a fresh integration branch / stop, leaving the current
  integration branch for manual inspection).
- Non-zero codex exit or empty output → surface it and follow the doctrine failure mapping; never
  fabricate results.
- Every implementer handoff forbids: commits, pushes, dependency additions without flagging,
  edits outside the FILES list, and running builds / tests / installs / network commands (the
  coordinator verifies).
