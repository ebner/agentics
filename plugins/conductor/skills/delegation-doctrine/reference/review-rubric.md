# Review rubric and brief templates (conductor)

Every review the conductor runs — plan review and final changeset review — uses a brief built from
these templates. The reviewer is the stateless `conductor-reviewer` agent (or `codex exec` /
`codex review` for the cross-model half). Briefs supply criteria + a no-fire list; the rubric
principles below govern how the criteria are written.

## 1. Rubric principles

1. **Every criterion is independently checkable.** The rubric must be more specific than the task.
   "Check the plan covers error handling" lets a reviewer skim; "open the plan, find the section
   covering failures of the X call, and confirm it names the retry/fallback behavior" forces
   evidence.
2. **"Satisfied" is earned with concrete evidence** — a `file:line` reference, a quoted passage,
   or the output of a command the reviewer ran. Unverifiable claims are marked UNVERIFIABLE, never
   passed.
3. **Describe the goal, not the steps.** A criterion that prescribes one specific command fails
   silently when that command is unavailable; define what counts as proof and let the reviewer
   find it.
4. **Anticipate the writer's shortcuts.** Include criteria for the known evasions: weakened or
   deleted tests, stubs presented as complete, silently narrowed scope, hardcoded fixtures.
5. **Mandate the feedback format.** The reviewer's output is the fix loop's only signal: one-line
   scoreboard, then exactly one bullet per failed criterion (what is wrong + what to do), then the
   VERDICT line.
6. **Give an explicit no-fire list.** Without one the reviewer thrashes on style nits and
   pre-existing issues. Standard no-fire items: style already accepted by the project's lint
   configuration; failures that pre-exist the change and are listed in the brief; suggestions to
   expand scope beyond the plan.

## 2. Plan-review brief A — completeness

Used by: the codex read-only plan review (always, when codex is available), or the first
`conductor-reviewer` when codex is unavailable. Adversarial stance.

```
Review this implementation plan adversarially. The plan text is embedded below in full.

Criteria:
1. Completeness — every stated requirement maps to a plan unit; nothing an implementer must guess.
2. Feasibility — the approach works against this codebase as it actually is (verify claims about
   existing code with file:line evidence).
3. Edge cases — failure paths, empty/invalid inputs, and concurrency concerns the plan's changes
   plausibly touch are addressed or explicitly deferred.
4. Test gaps — each unit's verification commands actually exercise its acceptance criteria.
5. Convention alignment — the plan honors the project's documented conventions (CLAUDE.md /
   AGENTS.md).
6. Reuse — the plan uses existing utilities where they exist instead of introducing new code
   (name the existing utility if you find one).

No-fire list: style preferences not encoded in the project's lint configuration; pre-existing
issues in files the plan does not touch; scope expansion beyond the stated requirements.

Output: one-line scoreboard; one bullet per failed criterion (what is wrong + what to do); final
line exactly `VERDICT: APPROVED` or `VERDICT: REVISE`.
```

## 3. Plan-review brief B — premise and decomposition

Used by: the `conductor-reviewer` on every plan review (both codex-available and codex-absent
paths) — the premise check must always run, because a wrong decomposition propagates to every
unit.

```
Review this implementation plan's PREMISE and DECOMPOSITION adversarially. The plan text is
embedded below in full. Do not re-review completeness — another reviewer covers it.

Criteria:
1. Premise — is this the right approach at all? Check the plan's key assumptions against the
   actual codebase (file:line evidence) and flag any assumption that does not hold.
2. Problem-fit — does the plan solve the stated problem, or a plausible adjacent one?
3. Decomposition — are the units genuinely separable as claimed? Verify the FILES lists do not
   hide a shared dependency that forces an ordering the plan does not declare.
4. Dependency graph — are the declared dependsOn relations correct and complete?
5. Unit sizing — no unit below the worthiness floor (under 20 changed lines in at most 2 files
   with no new test files); flag undersized units for merging.

No-fire list: completeness gaps (brief A's ground); style; scope expansion.

Output: one-line scoreboard; one bullet per failed criterion; final line exactly
`VERDICT: APPROVED` or `VERDICT: REVISE`.
```

## 4. Final-review brief

Used by: the `conductor-reviewer` in Stage 4 close-out (alongside `codex review` when available).
Built per run: derive one criterion from each acceptance criterion in the plan, then append the
standard shortcut criteria.

```
Review the implemented changeset against the approved plan. The changeset is the uncommitted
changes plus commits ahead of <base> (inspect via git diff / git log / git show). The plan's
acceptance criteria follow.

Criteria:
<one numbered criterion per plan acceptance criterion, each phrased so it is checkable with
file:line or command-output evidence>
[repeat one criterion per acceptance criterion]
N+1. No weakened, disabled, or deleted tests anywhere in the diff.
N+2. No TODO/stub/placeholder presented as a completed item.
N+3. No silent scope narrowing — everything the plan promises is present or explicitly reported
     as outstanding.
N+4. Verification evidence — the verification commands listed in the brief pass when you run
     them (run only the commands this brief lists).

No-fire list: style already accepted by the project's lint configuration; failures that pre-exist
the change (listed here: <pre-existing failures or "none">); improvement ideas beyond the plan's
scope.

Output: one-line scoreboard; one bullet per failed criterion; final line exactly
`VERDICT: APPROVED` or `VERDICT: REVISE`.
```

## 5. Codex plan-review invocation note

Codex's sandbox cannot read paths outside the workspace, so the brief and the full plan text are
embedded in the prompt file, run read-only per the `calling-codex` skill, and the verdict is read
from the `-o` capture file. The prompt must end with the same final-line instruction:
"End your reply with exactly one line: `VERDICT: APPROVED` or `VERDICT: REVISE`."
