# Run ledger (conductor)

The ledger is the durable record of one `/conductor:implement` run. It exists for two reasons: a
run must survive losing the coordinator's context (a compaction mid-run, or a crashed or closed
session), and every status the coordinator reports must be read from an artifact (doctrine §11).
The conversation is not a record; the ledger is.

## 1. Location and layout

```bash
LEDGER_ROOT="$(git rev-parse --path-format=absolute --git-common-dir)/conductor/runs"
RUN_ID="$(date -u +%Y%m%d-%H%M%S)-<branch-slug>"   # branch name slugified, / -> -
RUN_DIR="$LEDGER_ROOT/$RUN_ID"; mkdir -p "$RUN_DIR/artifacts"
```

It lives inside the git directory, so it is never tracked, never shows in `git status`, needs no
`.gitignore` entry, and is shared by every worktree of the repository.

```text
<RUN_DIR>/
  run.md        # written at Stage 0 step 8; later additions are appended, never rewritten
  log.jsonl     # append-only event log (§2)
  artifacts/    # verbatim captures, named <unit>-<attempt>.<kind> or stage<N>-<name>.<kind>
```

`run.md` holds the run id, the entry mode (plan or raw-task), the full RUN CONFIG block (which
includes the execution mode, linear or fan-out, and the base and integration branches), the Stage
0.7 baseline (full `HEAD` SHA, branch, `git status --porcelain` lines), and either the absolute
plan path (plan mode) or the user's task description verbatim (raw-task mode). Two later appends:
the plan path, once Stage 1 has written the plan (raw-task mode only), and, in linear mode, the
derived unit list (id, FILES, verification command, dependencies) under a `## Units` heading at
Stage 3 entry. A fan-out run's unit list is in the saved workflow result instead.

Artifacts are copied verbatim, never summarized: codex `-o` and `--json` captures, each gate run's
full output, each reviewer's full output, the independent plan proposal, and the fan-out
workflow's result. Codex's `workspace-write` sandbox treats `.git` as read-only (verified on
codex-cli 0.162.1), so keep codex's `-o` target a `mktemp` file and copy it into `artifacts/` after
the call returns. The `--json` stream is redirected by the calling shell, which runs outside the
sandbox, so it may go straight into `artifacts/`.

## 2. Events

One JSON object per line, appended with `>>`. Every line has `t` (UTC ISO-8601) and `ev`. A line is
never edited or deleted: a correction is a new line, and the latest line for a key wins.

| `ev` | Append when | Fields |
|------|-------------|--------|
| `stage` | a stage is entered or reaches an outcome | `stage` (0–4), `outcome`: `entered` \| `plan-approved` \| `user-approved` \| `resumed` \| `abandoned` \| `done` |
| `review` | a reviewer returns (Stage 2 or 4) | `stage`, `round`, `reviewer` (`codex` \| `conductor-reviewer` \| `project`), `verdict` (`APPROVED` \| `REVISE` \| `none`), `file` |
| `snapshot` | at 3a, before U's first dispatch | `unit`, `stash` (the `git stash create` SHA, or `""`), `head` (full SHA), `porcelain` (artifact path) |
| `dispatch` | **before** every implementation attempt: 3b, 3e, 3f (rung 3 included), and the Stage 4 fix round | `unit` (or `close-out`), `attempt` (1, 2, 3 in order across all rungs for that unit), `rung` (1–3), `lane` (`codex` \| `claude` \| `coordinator`), `step` (`implement` \| `fix-1` \| `fix-2`) |
| `report` | the attempt ends: an implementer returns, a status is assigned, or the coordinator finishes its rung-3 edits | `unit`, `attempt`, `status` (`complete` \| `partial` \| `blocked` \| `timeout` \| `unavailable`), `session` (codex session id or `""`), `file` |
| `gate` | after every gate run, Stage 3 and Stage 4 | `unit` (or `close-out`), `cmd`, `exit`, `file` |
| `unit` | U reaches its final state | `unit`, `state` (`fully-implemented` \| `compromise` \| `skipped` \| `rung3`), `note` (one line) |
| `fanout` | the Workflow tool returns a run id, and when the workflow finishes | `run_id`, `state` (`launched` \| `finished`), `file` (the saved workflow result, on `finished`) |

Append `stage 0 abandoned` in raw-task mode when the user picks *Cancel* or *Implement directly* at
the worthiness gate, and `stage 2 abandoned` when the user picks *Cancel* at the raw-task approval
pause. (In plan mode the worthiness gate runs before the ledger exists.) Every other stop leaves
the run resumable.

An attempt is **in flight** when it has a `dispatch` line and no `report` line with the same `unit`
and `attempt`. That is why `dispatch` is appended before launch, not after.

When `fanout finished` arrives, save the workflow result to `artifacts/` and append one `unit` line
per unit: `fully-implemented` for each integrated unit. Each `failed[]` unit then goes to rung 3 and
gets its own `dispatch`, `report`, `gate`, and `unit` lines like a linear unit.

## 3. Reading the ledger mid-run

When the conversation has been compacted during a run, re-read `run.md` and `log.jsonl` before the
next action. The ledger outranks recollection: if they disagree, the ledger is right.

The Stage 4 report takes each unit's final state from the `unit` lines, its attempt count from the
`dispatch` lines (for fan-out units, from the saved workflow result), and every gate result from the
`gate` lines, not from memory.

## 4. Resume (`--resume [run-id]`)

`--resume` continues a run that a new session can no longer see. It replaces Stage 0 steps 3–8.
Steps 1–2 still run, but the RUN CONFIG recorded in `run.md` wins over the settings file: only
`codexAvailable` is taken from the fresh step-2 check. A recorded codex lane that now fails that
check counts as `unavailable` (doctrine §4).

1. **Locate.** Without a run id, use the most recent run directory whose `log.jsonl` has neither a
   `done` nor an `abandoned` line; if there is none, stop and list the directories under
   `$LEDGER_ROOT`. With a run id, use `$LEDGER_ROOT/<run-id>`; if its log has a `done` or
   `abandoned` line, stop and say the run is already closed.
2. **Re-adopt.** Read `run.md` and `log.jsonl` in full. Load the `calling-codex` skill when the
   codex lane is in use. Take the RUN CONFIG from `run.md` and re-enter the role lock (doctrine
   §2). Append `stage` with `outcome: resumed`.
3. **Check the tree.** The current branch must match the branch recorded in `run.md`. For a
   fan-out run with a `stage 3 entered` line, that is the integration branch. If it does not
   match, this is a §Forks stop.
4. **Find the position.** Take the first case that matches, then continue the normal pipeline from
   there:
   - A `stage 4 entered` line: restart Stage 4 at step 1. If a `close-out` `dispatch` line exists,
     the close-out fix round has been used; do not dispatch another.
   - A fan-out run with `fanout launched` and no `finished`: in the session that launched it, call
     `Workflow({ scriptPath, resumeFromRunId: <run_id> })`, and completed agent calls are replayed
     from cache. From any other session, this is a §Forks stop.
   - A fan-out run with `fanout finished`: continue with the `failed[]` units at rung 3 as linear
     units (the cases below), then Stage 4.
   - Raw-task mode with no plan path in `run.md`: restart at Stage 1 with the recorded task
     description.
   - No `stage 3 entered` line: if a `plan-approved` line exists and, in raw-task mode, a
     `user-approved` line also exists, go to Stage 3. Otherwise resume Stage 2 with fresh reviewers
     at round (highest recorded `round` + 1), keeping the 3-round cap.
   - Stage 3 of a linear run, or a rung-3 unit after fan-out: skip every unit that has a `unit`
     line. If every unit has one, do the whole-changeset pass and go to Stage 4. Otherwise, for the
     first unit U without one:
     - **An attempt in flight.** If it is a codex-lane attempt and `pgrep -af 'codex exec'` lists a
       process, this is a §Forks stop. Otherwise treat the attempt as `timeout` (doctrine §4):
       restore the files it touched from U's `snapshot`, append its `report` line with `status:
       timeout`, and make the next attempt fresh.
     - **The last report is `timeout`, `unavailable`, or `blocked`.** Apply doctrine §4's ladder
       handling for that status.
     - **Otherwise** run 3d now. The gate result decides the next step: a pass gives U its `unit`
       line, and a failure continues the ladder.
     Rung and fix-round counts come from U's `dispatch` lines. A resumed run gets no extra
     attempts.

## 5. Retention

Run directories are never deleted by the command. They are small, and the user may delete
`$LEDGER_ROOT` or any run directory at any time when no run is active.
