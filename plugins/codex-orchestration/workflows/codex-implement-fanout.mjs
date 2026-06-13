/*
 * codex-implement-fanout — fan-out plan implementation via OpenAI Codex
 * =====================================================================
 * Fan-out sibling of the `codex-implement` command. Topology:
 *
 *   DECOMPOSE (1 agent)  ->  IMPLEMENT (N parallel worktree agents, edit-only Codex)
 *                            ->  VERIFY/MERGE GATE (sequential, full access)  ->  FINAL VERIFY
 *
 * Every agent that drives Codex follows the `calling-codex` skill (codex-orchestration plugin):
 * edit-only `codex exec`, network OFF, `-c 'approval_policy="never"'`, `-c 'model_reasoning_effort="xhigh"'`,
 * prompt via stdin redirect (never positional — it hangs headlessly), `--json` -> session_id,
 * `-o` capture, and the harness's own Bash sandbox disabled on the codex call (Codex's own
 * workspace-write sandbox is the boundary). Codex never builds, commits, or touches the network —
 * the Claude agents do.
 *
 * DIVISION OF AUTHORITY:
 *   - Implementation agents: each in its OWN git worktree, drive edit-only Codex then COMMIT the
 *     unit's changes to a branch `codex/unit-<id>` (Codex edits; the agent commits).
 *   - Verify/merge gate: FULL access (network + toolchain + caches) — merges each unit branch into
 *     the integration branch, builds/verifies the project's gate, keeps green / reverts red.
 *
 * KNOWN ROUGH EDGES (validate before trusting on a real plan):
 *   1. WORKTREE BASE: each impl agent rebases its worktree onto the integration branch so later waves
 *      build on merged earlier waves. Confirm the harness's `isolation:'worktree'` base behavior.
 *   2. MERGE CONFLICTS: only TRIVIAL conflicts are auto-resolved; non-disjoint units -> conflict ->
 *      that unit fails (the gate aborts the merge, never force-merges). The decomposer is told to
 *      produce FILE-DISJOINT units — that contract keeps merges cheap.
 *   3. COST / LIMITS: N parallel Codex sessions multiply spend; OpenAI auth has concurrency limits;
 *      the workflow runner caps concurrency at min(16, cores-2). Use for large, decomposable plans.
 *   4. Impl worktrees that committed are not auto-cleaned (the branch persists, which is what we
 *      need); prune stray worktrees afterward with `git worktree prune`.
 *   5. Nothing is pushed; the integration branch is separate from base; the default branch is untouched.
 *
 * PROJECT-AGNOSTIC: the gate/verify agents DISCOVER the project's build/test commands from the
 * project's CLAUDE.md / AGENTS.md / README or its build config (package.json, pom.xml, Cargo.toml,
 * go.mod, Makefile). No build tool is hardcoded.
 *
 * RUN (explicit opt-in — spawns many agents + Codex sessions):
 *   Workflow({ name: 'codex-implement-fanout',                       // if copied to .claude/workflows/
 *              args: { planPath: '/abs/path/to/plan.md', base: 'main',
 *                      integrationBranch: 'codex-fanout/integration' } })
 *   or via scriptPath to the installed plugin copy (see the plugin README).
 *   For small or strictly-sequential plans, use the `codex-implement` command instead.
 */

export const meta = {
  name: 'codex-implement-fanout',
  description: 'Fan-out plan implementation: decompose an approved plan into file-disjoint units, implement each in an isolated worktree via edit-only Codex (parallel within dependency waves), then a verify/merge gate integrates each wave. Companion to the codex-implement command.',
  whenToUse: 'A large, approved, decomposable plan whose units touch mostly file-disjoint paths and where parallel Codex implementation + a merge gate is worth the cost. For small or strictly-sequential plans, use the codex-implement command instead.',
  phases: [
    { title: 'Decompose', detail: 'one agent splits the plan into units + a dependency graph' },
    { title: 'Implement', detail: 'parallel worktree agents drive edit-only Codex, one per unit, within dependency waves' },
    { title: 'Verify & merge', detail: 'sequential gate: merge each implemented unit into the integration branch and build/verify' },
    { title: 'Final verify', detail: 'whole-integration verify against the plan' },
  ],
}

// ---------- args ----------
const PLAN_PATH = args && args.planPath
const BASE = (args && args.base) || 'main'
const INTEGRATION = (args && args.integrationBranch) || 'codex-fanout/integration'
if (!PLAN_PATH) {
  log('ERROR: pass args = { planPath: "/abs/path/to/plan.md", base?, integrationBranch? }')
  return { error: 'missing planPath' }
}

// ---------- structured-output schemas ----------
const DECOMPOSE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    units: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          description: { type: 'string' },
          files: { type: 'array', items: { type: 'string' } },
          dependsOn: { type: 'array', items: { type: 'string' } },
          tests: { type: 'string' },
        },
        required: ['id', 'title', 'description', 'files', 'dependsOn', 'tests'],
      },
    },
    fileDisjoint: { type: 'boolean' },
    notes: { type: 'string' },
  },
  required: ['units', 'fileDisjoint', 'notes'],
}

const IMPL_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    unitId: { type: 'string' },
    branch: { type: 'string' },
    status: { type: 'string', enum: ['done', 'failed'] },
    sessionId: { type: 'string' },
    touchedFiles: { type: 'array', items: { type: 'string' } },
    outOfScopeFiles: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['unitId', 'branch', 'status', 'summary'],
}

const GATE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    unitId: { type: 'string' },
    merged: { type: 'boolean' },
    buildPassed: { type: 'boolean' },
    reason: { type: 'string' },
    failures: { type: 'array', items: { type: 'string' } },
  },
  required: ['unitId', 'merged', 'reason'],
}

const FINAL_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    integrationBranch: { type: 'string' },
    gatePassed: { type: 'boolean' },
    fullyImplemented: { type: 'array', items: { type: 'string' } },
    outstanding: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['gatePassed', 'notes'],
}

// ---------- helpers (plain JS) ----------
// Topological layering: units with all deps already satisfied form the next wave.
function topoWaves(units) {
  const ids = new Set(units.map(u => u.id))
  const done = new Set()
  const waves = []
  let remaining = units.slice()
  while (remaining.length) {
    const ready = remaining.filter(u => (u.dependsOn || []).every(d => done.has(d) || !ids.has(d)))
    if (!ready.length) {
      log(`WARNING: unresolved dependency cycle among ${remaining.map(u => u.id).join(', ')} — running them together`)
      waves.push(remaining)
      remaining.forEach(u => done.add(u.id))
      break
    }
    waves.push(ready)
    ready.forEach(u => done.add(u.id))
    remaining = remaining.filter(u => !done.has(u.id))
  }
  return waves
}

function implPrompt(unit) {
  return [
    `You are an IMPLEMENTATION agent for work unit "${unit.id}" (${unit.title}). You run in an isolated git worktree.`,
    `Follow the \`calling-codex\` skill (codex-orchestration plugin) exactly — you delegate ALL code edits to edit-only Codex; you do NOT write feature code yourself.`,
    ``,
    `Unit spec:`,
    `- Description: ${unit.description}`,
    `- In-scope files (touch ONLY these): ${(unit.files || []).join(', ')}`,
    `- Tests for this unit: ${unit.tests}`,
    `- The full approved plan is at ${PLAN_PATH} — read it for context (you can read it; Codex cannot).`,
    ``,
    `Steps:`,
    `1. Base your worktree on the integration branch so you build on earlier waves:`,
    `     git fetch --quiet || true`,
    `     git checkout -B codex/unit-${unit.id} "${INTEGRATION}" 2>/dev/null || git checkout -B codex/unit-${unit.id} "origin/${BASE}" 2>/dev/null || git checkout -B codex/unit-${unit.id} "${BASE}"`,
    `2. Write a Codex handoff prompt FILE for THIS unit (GPT-5.x blocks: <task> with the unit's files/criteria/tests,`,
    `   the relevant plan excerpt, <grounding_rules> [follow the project's documented conventions in its CLAUDE.md/AGENTS.md],`,
    `   <action_safety> [in-scope files only; NO commit/push; NO builds/tests/installs/network — the gate verifies], <completeness_contract>).`,
    `3. Run Codex EDIT-ONLY, network off, prompt via STDIN REDIRECT, per the calling-codex skill (disable the harness Bash sandbox on this call):`,
    `     codex exec -s workspace-write -c 'approval_policy="never"' -c 'model_reasoning_effort="xhigh"' \\`,
    `       --json -o /tmp/impl-${unit.id}.out < /tmp/impl-${unit.id}.handoff > /tmp/impl-${unit.id}.jsonl`,
    `   Capture sessionId: jq -r 'select(.type=="thread.started").session_id' /tmp/impl-${unit.id}.jsonl | head -1`,
    `   Non-zero exit / empty -o -> status:"failed".`,
    `4. Commit the unit's changes (Codex never commits — you do):`,
    `     git add -A && git commit -m "codex unit ${unit.id}: ${unit.title}"`,
    `5. Verify Codex stayed in scope; list any files touched outside ${(unit.files || []).join(', ')} as outOfScopeFiles.`,
    ``,
    `Return the structured result. Do NOT build or run tests (that is the gate's job). Do NOT push.`,
  ].join('\n')
}

function gatePrompt(unit, impl) {
  return [
    `You are the VERIFY/MERGE GATE for unit "${unit.id}" on branch "${impl.branch}". You have FULL access (network + toolchain + caches).`,
    `Integrate this unit into the integration branch "${INTEGRATION}", then build/verify. Keep it only if green.`,
    ``,
    `Steps:`,
    `1. Ensure the integration branch exists and is checked out:`,
    `     git rev-parse --verify "${INTEGRATION}" >/dev/null 2>&1 || git branch "${INTEGRATION}" "origin/${BASE}" 2>/dev/null || git branch "${INTEGRATION}" "${BASE}"`,
    `     git checkout "${INTEGRATION}"`,
    `2. Merge the unit branch:  git merge --no-ff --no-edit "${impl.branch}"`,
    `   - On conflict: resolve ONLY if trivial and obviously correct. Otherwise: git merge --abort, return merged:false, reason:"conflict", and STOP — never force-merge.`,
    `3. Build/verify the project's FAST gate. DISCOVER the commands from the project's CLAUDE.md / AGENTS.md / README or its build config (package.json scripts, pom.xml, Cargo.toml, go.mod, Makefile): typecheck / build / lint as the project defines them, then this unit's tests (${unit.tests}). You may use network + toolchain.`,
    `4. If green -> keep the merge (merged:true, buildPassed:true). If red -> undo it (git reset --hard HEAD~1) so the integration branch stays buildable; return merged:false with the failures.`,
    `   (The heavy/slow suite runs once in the Final verify phase, not per unit.)`,
    `Return the structured result. Do NOT push.`,
  ].join('\n')
}

function finalPrompt() {
  return [
    `You are the FINAL VERIFIER. Check out the integration branch "${INTEGRATION}" and run the project's FULL gate (full access):`,
    `DISCOVER the commands from the project's CLAUDE.md / AGENTS.md / README or build config — typecheck, build, lint, the full test suite, and any integration / end-to-end suite the project defines.`,
    `Then compare the integrated result against the approved plan at ${PLAN_PATH}: which plan items are fully implemented, which remain outstanding.`,
    `Do NOT commit or push. Return the structured result.`,
  ].join('\n')
}

// ---------- 1. Decompose ----------
phase('Decompose')
const decomp = await agent(
  [
    `You are the DECOMPOSER. Read the approved implementation plan at ${PLAN_PATH}.`,
    `Split it into independent work UNITS suitable for parallel implementation. REQUIREMENTS:`,
    `- Each unit must be as FILE-DISJOINT from the others as possible (overlapping files cause merge conflicts the gate cannot auto-resolve).`,
    `- Give each unit a stable id (kebab-case), title, description, the exact set of files it will create/modify, its tests, and dependsOn (ids of units whose code it builds on).`,
    `- Set fileDisjoint=true only if no two units share a file; otherwise false, and explain the overlaps in notes.`,
    `- Respect the plan's own phases: a phase that builds on a prior phase becomes a unit that dependsOn it.`,
    `Return the structured decomposition. Do not implement anything.`,
  ].join('\n'),
  { schema: DECOMPOSE_SCHEMA, label: 'decompose', phase: 'Decompose' },
)

const units = (decomp && decomp.units) || []
if (!units.length) {
  log('Decomposition produced no units — aborting.')
  return { error: 'empty decomposition', decomp }
}
if (decomp.fileDisjoint === false) {
  log(`WARNING: units are NOT file-disjoint — expect merge conflicts the gate will fail rather than force. ${decomp.notes || ''}`)
}
const waves = topoWaves(units)
log(`Decomposed into ${units.length} unit(s) across ${waves.length} dependency wave(s).`)

// ---------- 2 + 3. Per wave: implement (parallel) -> verify/merge (sequential gate) ----------
const integrated = []
const failedUnits = []
for (let w = 0; w < waves.length; w++) {
  const wave = waves[w]
  log(`Wave ${w + 1}/${waves.length}: ${wave.map(u => u.id).join(', ')}`)

  // Implement — parallel, each unit isolated in its own worktree, edit-only Codex.
  phase('Implement')
  const impls = (await parallel(wave.map(unit => () =>
    agent(implPrompt(unit), { isolation: 'worktree', schema: IMPL_SCHEMA, label: `impl:${unit.id}`, phase: 'Implement' }),
  ))).filter(Boolean)

  // Verify & merge — sequential gate in dependency order (merges are stateful on the integration branch).
  phase('Verify & merge')
  for (const unit of wave) {
    const impl = impls.find(i => i && i.unitId === unit.id)
    if (!impl || impl.status !== 'done') {
      failedUnits.push(unit.id)
      log(`  ${unit.id}: implementation failed/missing — skipped`)
      continue
    }
    if (impl.outOfScopeFiles && impl.outOfScopeFiles.length) {
      log(`  ${unit.id}: Codex touched out-of-scope files: ${impl.outOfScopeFiles.join(', ')}`)
    }
    const gate = await agent(gatePrompt(unit, impl), { schema: GATE_SCHEMA, label: `gate:${unit.id}`, phase: 'Verify & merge' })
    if (gate && gate.merged) {
      integrated.push(unit.id)
      log(`  ${unit.id}: verified + merged`)
    } else {
      failedUnits.push(unit.id)
      log(`  ${unit.id}: gate failed — ${(gate && gate.reason) || 'unknown'}`)
    }
  }
}

// ---------- 4. Final verify ----------
phase('Final verify')
const final = await agent(finalPrompt(), { schema: FINAL_SCHEMA, label: 'final-verify', phase: 'Final verify' })

log(`Integrated ${integrated.length}/${units.length} unit(s); ${failedUnits.length} failed. Final gate: ${final && final.gatePassed ? 'PASS' : 'FAIL'}.`)
return {
  units: units.length,
  waves: waves.length,
  integrationBranch: INTEGRATION,
  integrated,
  failed: failedUnits,
  final,
}
