# Spec and report templates (conductor)

Verbatim templates for every implementer handoff and report. The coordinator fills the
placeholders; the structure is fixed. Backend-agnostic except where a section says otherwise.

## 1. The five-part spec

```
UNIT: <unit id> — <unit title>

OBJECTIVE:
<What to build, standalone — complete enough that a reader with no other context can implement
it. State the acceptance criteria in checkable terms.>

FILES (closed list — touch ONLY these):
- <file path> — <create|modify>
[repeat one line per in-scope file]

INTERFACES:
<The signatures, types, and contracts this unit exposes or consumes — verbatim where the plan
fixes them, so units implemented in parallel agree. Write "none" if the unit is self-contained.>

CONSTRAINTS:
- Follow the project's documented conventions: <the conventions recorded in Stage 0, quoted or
  summarized concretely — naming, error types, i18n, lint rules>
- Reuse these existing utilities instead of writing new ones: <utilities the plan names, with
  paths; or "none named">
- Modify only the files listed under FILES. No new dependencies without flagging them in GAPS.
- Do not commit, push, build, test, lint, install, or use the network. The coordinator verifies.
- Never weaken, disable, or delete an existing test to get a green result.
- Implement every OBJECTIVE item completely: no TODO, no stub, no placeholder.
- Build the OBJECTIVE at the scope it states: no extra features, refactors, or abstractions, and no
  error handling or fallbacks for conditions that cannot occur. A bug fix needs no surrounding
  cleanup; a single call site needs no helper. Match the surrounding code's idiom and comment density.
- If you think the OBJECTIVE is wrong or a better approach exists, implement it as specified and say
  so in one GAPS line. Settle routine choices (a local name, a formatting detail, one of two
  equivalent constructs) yourself — `blocked` is for a genuine requirement ambiguity only.

VERIFICATION (the coordinator runs this — you do NOT):
<the exact command(s) that will gate this unit>
```

## 2. Codex report suffix

Appended only to **codex** handoffs (the claude implementer agent already carries the report
contract in its system prompt). Do not use `--output-schema` to capture this — mandate the text
format and read it from the `-o` file, per the `calling-codex` skill.

```
End your reply with the structured report, in exactly this format:

STATUS: <complete|partial|blocked>
OBJECTIVE: <the unit objective restated in one line>
CHANGES:
- <file path> — <one-line summary of what changed>
[repeat one line per touched file]
GAPS:
- <gap, deviation, or open question>
[repeat one line per gap, or write the single word: none]
```

## 3. The structured report

What every implementer returns (claude: as the end of its final message; codex: via the suffix in
§2; fanout: as the JSON fields of REPORT_SCHEMA carrying the same content).

```
STATUS: <complete|partial|blocked>
OBJECTIVE: <the unit objective restated in one line>
CHANGES:
- <file path> — <one-line summary of what changed>
[repeat one line per touched file]
GAPS:
- <gap, deviation, or open question>
[repeat one line per gap, or write the single word: none]
```

Notes:
- `timeout` and `unavailable` are assigned by the coordinator or wrapper on infrastructure
  failure — an implementer never declares them (doctrine §4).
- There is deliberately no VERIFIED field: implementers are edit-only and cannot run
  verification; the coordinator owns it (doctrine §7).
- When a wrapper assembles the report for codex, it adds one line —
  `IMPLEMENTER-SAID: <one-line summary of codex's final message, noting any disagreement with the
  actual diff>` — and builds CHANGES from `git status --porcelain`, not from the final message.

## 4. Fix-round handoff

```
UNIT: <unit id> — fix round <n> of 2

The coordinator ran the verification gate and it FAILED. Fix ONLY these failures. Stay within the
unit's FILES list. Read every file the errors cite before editing. Do not commit, push, build,
test, install, or use the network. Never weaken, disable, or delete an existing test to get green.

OPEN GAPS FROM YOUR REPORT (if any):
<the GAPS lines being addressed, or "none">

--- VERBATIM GATE FAILURE OUTPUT (root errors first; not summarized) ---
<the exact command(s) run, their stderr, compiler/type errors with file:line, failing test names
with assertion diffs, and stack traces — capped in volume but never paraphrased>
```

Delivery per backend (doctrine §4): codex → `codex exec resume <session_id>` with this text as the
prompt file; claude → a fresh `conductor:conductor-implementer` launch whose task is the original
five-part spec + the prior report's CHANGES + this fix-round block.

## 5. Escalation handoff (rung 2 — the other lane)

```
UNIT: <unit id> — re-route to <backend> after the <other backend> lane was exhausted.

<the full five-part spec, verbatim from §1>

=== PRIOR ATTEMPT HISTORY (that work was DISCARDED; re-implement from the spec on a clean base —
do not try to repair it) ===
attempt 1 (implement): <one-line outcome> — <first 3 lines of that failure log>
[repeat one line per prior attempt]
--- LAST VERBATIM GATE FAILURE (ground truth; at most 200 lines) ---
<the final failure log, verbatim>
```

Before dispatching rung 2 in linear mode, the coordinator restores every file the failed lane
touched from the unit's pre-dispatch snapshot; in fanout mode the workflow starts a fresh `-alt`
branch off the integration branch (doctrine §8).
