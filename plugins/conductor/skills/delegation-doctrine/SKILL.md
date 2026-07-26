---
name: delegation-doctrine
description: >
  The coordinator doctrine for delegated implementation in the conductor plugin. Trigger this
  skill whenever you are about to construct an implementer handoff (a five-part unit spec), parse
  an implementer report, decide delegate-vs-keep, select an implementer backend, escalate a
  failing unit, or when the /conductor:implement command or the implement-fanout workflow runs.
  Covers the roles and role lock, the backend contract (codex and claude lanes), the spec and
  report formats, verification ownership, the escalation ladder, sizing rules, the review
  doctrine, and coordinator conduct (evidence-grounded claims, autonomy, reporting).
allowed-tools:
  - Read
  - Bash
  - Agent
---

# Delegation doctrine (conductor)

This is the single source of truth for the conductor plugin's coordinator/implementer split. The
`/conductor:implement` command and the `implement-fanout` workflow follow it; the `calling-codex`
skill covers only the codex CLI mechanics.

## 1. Why this shape

- The coordinator never touches the raw material of implementation: bulk content (whole files,
  build logs, search results) stays inside the implementer's context, and only distilled reports
  cross back. That separation is the entire cost story.
- The implementer receives only its task string. It sees no plan file and no conversation, so
  every handoff must be self-contained and the coordinator's beliefs about what the implementer
  can do must match what its prompt actually grants.
- An independent, stateless reviewer beats self-review: a writer that knows the criteria is still
  grading its own work. The reviewer gets a fresh context, the artifact, and a rubric — nothing
  else.
- Verify the premise, not just the work: a wrong decomposition propagates to every unit, so plan
  review always includes a premise check (brief B in `reference/review-rubric.md`).
- Do not over-decompose: every handoff pays a fixed setup cost. The unit floor is the
  delegation-worthiness threshold in §9.
- Escalation is first-class: cheap tier by default, stronger tier or the other backend on failure,
  the coordinator itself as the announced last resort.

## 2. Roles and role lock

Three roles:

- **Coordinator** — the main session running the command. It plans, decomposes, writes specs,
  dispatches implementers, runs every build/test/merge, parses reports, escalates, and
  consolidates.
- **Implementer** — a backend (§4) that writes code from a five-part spec and returns a structured
  report. Edit-only: it never builds, tests, installs, commits to the user's branch, or touches
  the network.
- **Reviewer** — the stateless `conductor-reviewer` agent (plan review and final review), plus
  `codex review` when the codex backend is available.

**Role lock (canonical form).** While orchestrating, the coordinator does not write or edit any
source, feature, or test code itself. Exactly two exceptions, both stated here so the rule and its
exceptions live together: (a) editing the **plan file** is orchestration, not code; (b) on
**escalation rung 3** (§8), after the available implementer lanes are exhausted, the coordinator
implements the unit directly — announcing the downgrade first. The delegate-vs-keep list in §3
governs only the decision to start orchestrating; once orchestration starts, all code edits route
to the implementer regardless of size, except rung 3.

## 3. Delegate vs keep

Delegate to an implementer:

- implementation from a frozen spec
- refactors with a defined target shape
- mechanical migrations
- bug fixes with a known reproduction
- test writing for specified behavior
- CI fixes with the failing log in hand

Keep with the coordinator (do not start orchestration for these):

- design, API design, architecture, and naming decisions
- tasks where writing the spec IS the work (unresolved ambiguity means the design is not done)
- edits below the worthiness threshold (§9): fewer than 20 estimated changed lines in at most 2
  files with no new test files
- anything requiring MCP tools, credentials, or secrets the implementer backends cannot have
- destructive or irreversible operations
- review of implementer output — never delegated to the implementer, never skipped

## 4. Backends

Every backend satisfies one contract: five-part spec in → structured report out, edit-only, no
builds/tests/installs/network, no commits to the user's branch, in-scope files only, and never
weakening or deleting an existing test to get green.

| Backend | Mechanics | Enforcement |
|---------|-----------|-------------|
| `codex` | `codex exec` per the `calling-codex` skill (edit-only sandbox, network off) | OS-enforced sandbox (Landlock/seccomp) |
| `claude` (linear) | one Agent call to `subagent_type: "conductor:conductor-implementer"` | tool allowlist — the agent has no Bash |
| `claude` (fanout) | inline worktree agent spawned by the workflow | prompt boundary (enumerated git commands only) + gate audit of the actual diff |

**Canonical launch strings** — use these exactly; other files reference, not restate, them:
`subagent_type: "conductor:conductor-implementer"` for the claude implementer and
`subagent_type: "conductor:conductor-reviewer"` for the reviewer. One Agent call per agent; when
launching more than one reviewer, put all Agent calls in the same assistant message.

**Selection predicate** (run exactly once per command run):

```bash
command -v codex >/dev/null 2>&1 && command -v jq >/dev/null 2>&1 && codex login status >/dev/null 2>&1
```

All three succeed → codex is available. `--backend`/settings force a lane; `auto` picks codex when
available, else claude. A forced `--backend` still runs the predicate solely to record
`codexAvailable` for escalation rung 2. Repo trust (`~/.codex/config.toml`) and an xhigh-capable
codex model are documented prerequisites, not probed — a violation surfaces as `unavailable` or
`timeout` per the mapping below.

**Failure → STATUS mapping** (the coordinator or wrapper assigns infrastructure statuses; the
implementer itself only declares `complete`, `partial`, or `blocked`):

| Signal | STATUS |
|--------|--------|
| codex missing / not logged in / jq missing when the lane is forced | `unavailable` |
| `codex exec` non-zero exit with no edits, or stderr matching auth/quota/rate-limit | `unavailable` |
| claude agent spawn error, or no parseable report after one re-ask | `unavailable` |
| exit 124 from the `timeout 1200` wrapper | `timeout` |
| `codex exec` non-zero exit but edits exist | `partial` |
| report present with non-empty GAPS | `partial` |
| report says blocked with a question | `blocked` |

Ladder handling: `unavailable` → skip fix rounds, re-route immediately (§8). `timeout` → roll the
edits back, count one attempt, next attempt is a fresh exec (never resume a timed-out codex
session). `blocked` → answer the question via a fix-round handoff, or `AskUserQuestion` if it is a
genuine requirement fork; in fanout mode the question rides the distilled history (§8).

**Resume semantics per backend and mode:**

| Backend / mode | Fix-round mechanism |
|----------------|---------------------|
| codex (linear and fanout) | `codex exec resume <captured session_id>` per `calling-codex` (resume takes no `-s` flag; sandbox via `-c 'sandbox_mode="workspace-write"'`) |
| claude (linear and fanout) | a **fresh** implementer launch with the spec + the prior report's CHANGES + the verbatim failures — subagents are one-shot; fanout fix agents additionally check out the unit's branch |

## 5. The five-part spec

The handoff unit. Rules:

- **Self-contained.** The implementer sees only this text. Everything it needs — context,
  interfaces, conventions — is in the spec, never "see the plan".
- **FILES is a closed list.** The implementer may touch only these files; anything else is a spec
  violation.
- **VERIFICATION names the exact command(s) the coordinator will run.** The implementer must not
  run them — the section exists so the implementer knows what "done" will be measured by.
- If you cannot finish writing any of the five parts, the decision isn't made yet: fix the plan
  first (a role-lock exception per §2), or `AskUserQuestion` if the gap is a genuine requirement
  ambiguity.

Read `reference/spec-and-report.md` for the verbatim templates before constructing the first
handoff of a run.

## 6. The structured report

Fields: STATUS / OBJECTIVE / CHANGES / GAPS (template in `reference/spec-and-report.md`).
IMPLEMENTER-SAID is added by whoever assembles a report on the implementer's behalf (the codex
paths) and flags disagreement between the implementer's claim and the actual diff.

**Reports are claims, not evidence.** The coordinator (or the fanout wrapper/gate) rebuilds
CHANGES authoritatively from `git status --porcelain` against the unit's pre-dispatch snapshot —
never from the implementer's memory. "The implementer said it works" is forbidden as evidence.
Out-of-scope edits are rolled back (tracked files restored from the snapshot, new untracked files
deleted) and the round counts as failed.

## 7. Verification ownership and verbatim handback

The coordinator — not the implementer — runs the build/verify: it has network, toolchain, and
caches; the implementer has none. When a gate fails, the failure handback must be the full
verbatim output: the exact command(s) run, their stderr, compiler/type errors with `file:line`,
failing test names with assertion diffs, and stack traces (root errors first; cap the volume but
do **not** summarize or paraphrase). The implementer did not run the build, so this handback is
its only view of the failure; also tell it to read the cited files.

## 8. Escalation ladder

Per unit, with explicit caps:

| Rung | Who | Bound |
|------|-----|-------|
| 1 | primary lane | 1 implementation pass + at most 2 fix rounds |
| 2 | the other lane, if available | fresh spec + distilled failure history, clean re-implementation, 1 pass + at most 2 fix rounds |
| 3 | the coordinator itself | announced downgrade; if its own attempt fails the fast gate twice → `AskUserQuestion` (skip unit / halt) |

Rung 2 never repairs the failed diff: linear mode restores every file the failed lane touched from
the unit's pre-dispatch snapshot first; fanout mode re-implements on a fresh `-alt` branch off the
integration branch. If the claude lane runs sonnet, fix round 2 of rung 1 re-launches with
`model: "opus"` before any cross-lane re-route. The distilled failure history format is in
`reference/spec-and-report.md`; rung 3's announcement is built from the actual attempt record:

```
Escalation notice: implementer lanes exhausted for unit <id>
(<lane>: <outcome per attempt> [repeat per lane tried]);
per the role-lock exception I am implementing <id> directly.
```

## 9. Sizing and decomposition

- **Unit floor = the worthiness threshold**: a unit estimated under 20 changed lines in at most 2
  files with no new test files is too small to delegate on its own — merge it into an adjacent
  unit. Rationale: each handoff pays a fixed setup cost, so brief granularity has an optimum.
- **Fanout requires file-disjoint units.** Overlapping units cause merge conflicts the gate will
  not force-merge; the workflow merges overlapping units into one sequential unit before waving.
- Linear units need not be file-disjoint, but each still needs its own FILES list and verification
  command(s).
- **Unit ceiling = 20 per plan, and at most 12 units in any one dependency wave.** The floor above
  stops over-decomposition of small work; this ceiling stops the opposite failure, where a large plan
  fans out to dozens of concurrent implementer sessions. Each session is a separate paid context that
  re-reads its files and re-establishes its own understanding, so a wave's cost and its conflict
  surface both grow with its width, while the verify/merge gate stays serial per wave. Exceeding
  either number means the decomposition is too fine: merge adjacent units in the same files, or split
  the plan into runs. The workflow runner also caps live agents at `min(16, cores - 2)`, but that is a
  machine-level backstop that queues the overflow — it is not a substitute for deciding the unit count
  at plan time, and a plan that relies on it will simply run its extra units later, not cheaper.

## 10. Review doctrine

- The reviewer is stateless and independent: a fresh `conductor-reviewer` context per review,
  never the implementer reviewing its own work.
- Cross-model review whenever the codex backend is available (codex reviews what claude-side
  agents wrote and vice versa); when it is not, the stateless different-context reviewer is the
  stated fallback.
- Every brief supplies checkable criteria, an explicit no-fire list, and the mandated output
  format. Read `reference/review-rubric.md` for the rubric principles and the brief templates
  before launching the first reviewer of a run.
- Briefs filter by **scope, not severity**: the no-fire list names ground the reviewer does not own,
  and the reviewer reports everything else with a severity and a confidence label. A brief that asks
  for only high-severity or high-confidence findings gets a reviewer that investigates just as hard
  and then withholds real defects — recall drops with no visible signal. Ranking happens downstream
  in the coordinator, never in the reviewer: at Stage 2 Decide for plan reviews, at Stage 4 step 5 for
  the final review (rubric principle 7).
- **The verdict is a pure function of the severity labels**, and every brief restates the rule because
  cross-model reviewers see only the brief (rubric principle 8): REVISE if any reported finding is
  `severity: high` or `medium` through any channel, APPROVED only when every reported finding is
  `severity: low`. Downstream gates therefore read the VERDICT line and the labels — never the finding
  count, and never which channel a finding arrived through. Findings from sources whose format the
  conductor does not control (`codex review`, the project's own review command) are labeled by the
  coordinator before ranking, not discarded for lacking a label.

## 11. Coordinator conduct

The coordinator runs long, largely unattended, and its output is the user's only view of the run.
Four rules follow from that:

- **Claims come from artifacts, never recollection.** Every status the coordinator reports — a unit's
  outcome, a gate result, a CHANGES list, a source count — is read from a recorded artifact: the
  per-unit diff against its 3a snapshot, a command's exit status and captured output, the plan file.
  §6 states this for implementer reports; it applies equally to what the coordinator tells the user.
  Where a claim cannot be traced to an artifact, report it as unverified rather than asserting it.
- **Decide routine matters; stop only at the enumerated forks.** The command's §Forks list is the
  complete set of stopping points. Naming, formatting, which of two equivalent spec phrasings to use,
  and how to word a constraint are the coordinator's own calls — make them and move on. Do not add a
  confirmation step the fork list does not name.
- **Correct only what changes the user's decisions.** On a long run the coordinator will revise its
  own earlier reading of a failure or a plan item. State the correction in one sentence and continue;
  no apology, no re-derivation of how the earlier reading arose, no running tally of past mistakes.
  A revised belief that changes nothing for the user needs no announcement at all.
- **The close-out report re-grounds the reader.** By Stage 4 the user has not been watching for many
  minutes and does not share the working vocabulary the run built up. Lead with the outcome, then
  what is needed from them. Spell out unit ids, file paths, and gate names rather than carrying over
  shorthand. Keep it short by dropping detail that does not change the user's next action — not by
  compressing prose into fragments or arrow chains.
