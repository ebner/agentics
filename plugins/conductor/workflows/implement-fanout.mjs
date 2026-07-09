/*
 * implement-fanout — fan-out plan implementation via a pluggable implementer backend
 * ==================================================================================
 * Fan-out sibling of the `/conductor:implement` command. Topology:
 *
 *   DECOMPOSE (1 agent)  ->  IMPLEMENT (N parallel worktree agents, cheap implementer)
 *                            ->  VERIFY/MERGE GATE (sequential, full access)  ->  FINAL VERIFY
 *
 * Backends (args.backend): 'codex' — worktree wrapper agents drive edit-only Codex per the
 * `calling-codex` skill (conductor plugin); 'claude' — worktree agents implement with their own
 * edit tools under an enumerated-git-commands-only boundary. Both return the same REPORT_SCHEMA
 * defined by the `delegation-doctrine` skill. The implementer never builds, tests, installs, or
 * touches the network — the gate (coordinator-tier, inherits the session model) verifies.
 *
 * DIVISION OF AUTHORITY:
 *   - Implementation agents: each in its OWN git worktree; commit the unit's changes to a branch
 *     `conductor/unit-<id>` (commits on dedicated branches are workflow mechanics — the user's
 *     base branch is never touched and nothing is ever pushed).
 *   - Verify/merge gate: FULL access (network + toolchain + caches) — merges each unit branch into
 *     the integration branch, runs the unit's verification, keeps green / reverts red.
 *
 * LADDER (per unit, mirrors delegation-doctrine §8):
 *   implement -> gate -> <= maxFixRounds fix rounds (codex: session resume; claude: fresh agent)
 *   -> conflict: one same-lane clean re-implementation off current integration ('-retry' branch;
 *      a conflict is not a lane failure, so it never triggers a cross-lane re-route by itself)
 *   -> re-route to the other lane if allowReroute && available ('-alt' branch, distilled history)
 *   -> failed[] with {id, spec, lastBranch, lastFailureLog, attempts} for the coordinator's rung 3.
 *   'unavailable' skips fix rounds (dead backend); 'timeout'/'blocked' produce no commit, so they
 *   skip the gate and go straight to the re-route decision.
 *
 * COST / LIMITS: N parallel implementer sessions multiply spend; OpenAI auth has concurrency
 * limits; the workflow runner caps concurrency at min(16, cores-2). Use for large, decomposable
 * plans; for small or strictly-sequential plans use the `/conductor:implement` linear path.
 *
 * PROJECT-AGNOSTIC: the gate/verify agents DISCOVER the project's build/test commands from the
 * project's CLAUDE.md / AGENTS.md / README or its build config (package.json, pom.xml, Cargo.toml,
 * go.mod, Makefile). No build tool is hardcoded.
 *
 * RUN (normally launched by `/conductor:implement --fanout`, which passes a resolved backend):
 *   Workflow({ scriptPath: <installed path>, args: {
 *     planPath: '/abs/path/to/plan.md', base: 'main', integrationBranch: 'conductor/integration',
 *     backend: 'codex'|'claude'|'auto', codexAvailable: true|false,
 *     claudeImplementerModel: 'opus'|'sonnet', codexWrapperModel: 'sonnet'|'inherit',
 *     codexEffort: 'xhigh', codexModel: '', maxFixRounds: 2, allowReroute: true } })
 */

export const meta = {
  name: 'implement-fanout',
  description: 'Fan-out plan implementation: decompose an approved plan into file-disjoint units, implement each in an isolated worktree via a pluggable cheap backend (edit-only Codex or a Claude worktree agent), then a verify/merge gate integrates each wave. Companion to the /conductor:implement command.',
  whenToUse: 'A large, approved, decomposable plan whose units touch mostly file-disjoint paths and where parallel implementation + a merge gate is worth the cost. For small or strictly-sequential plans, use the /conductor:implement linear path instead.',
  phases: [
    { title: 'Decompose', detail: 'one agent splits the plan into self-contained five-part unit specs + a dependency graph' },
    { title: 'Implement', detail: 'parallel worktree agents, one per unit, within dependency waves' },
    { title: 'Verify & merge', detail: 'sequential gate: merge each unit into the integration branch, verify, fix/re-route ladder' },
    { title: 'Final verify', detail: 'whole-integration verify against the plan' },
  ],
}

// ---------- args ----------
const PLAN_PATH = args && args.planPath
const BASE = (args && args.base) || 'main'
const INTEGRATION = (args && args.integrationBranch) || 'conductor/integration'
const CLAUDE_MODEL = (args && args.claudeImplementerModel) || 'opus'
const CODEX_WRAPPER_MODEL = (args && args.codexWrapperModel) || 'sonnet'
const CODEX_EFFORT = (args && args.codexEffort) || 'xhigh'
const CODEX_MODEL = (args && args.codexModel) || ''
const MAX_FIX_ROUNDS = (args && typeof args.maxFixRounds === 'number') ? args.maxFixRounds : 2
const ALLOW_REROUTE = (args && typeof args.allowReroute === 'boolean') ? args.allowReroute : true
if (!PLAN_PATH) {
  log('ERROR: pass args = { planPath: "/abs/path/to/plan.md", base?, integrationBranch?, backend?, codexAvailable?, claudeImplementerModel?, codexWrapperModel?, codexEffort?, codexModel?, maxFixRounds?, allowReroute? }')
  return { error: 'missing planPath' }
}

// ---------- structured-output schemas ----------
const DETECT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { codexAvailable: { type: 'boolean' } },
  required: ['codexAvailable'],
}

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
          objective: { type: 'string' },
          files: { type: 'array', items: { type: 'string' } },
          interfaces: { type: 'string' },
          constraints: { type: 'string' },
          verification: { type: 'string' },
          dependsOn: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'title', 'objective', 'files', 'interfaces', 'constraints', 'verification', 'dependsOn'],
      },
    },
    fileDisjoint: { type: 'boolean' },
    notes: { type: 'string' },
  },
  required: ['units', 'fileDisjoint', 'notes'],
}

// The fan-out carrier of the delegation-doctrine report contract. 'timeout'/'unavailable' are
// wrapper-assigned; 'blocked' carries its question in gaps. implementerSaid is codex-wrapper-only
// (the gate computes claim-vs-diff for the claude lane itself).
const REPORT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    unitId: { type: 'string' },
    branch: { type: 'string' },
    status: { type: 'string', enum: ['complete', 'partial', 'blocked', 'timeout', 'unavailable'] },
    objective: { type: 'string' },
    resumeToken: { type: 'string' },
    changes: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      properties: { file: { type: 'string' }, summary: { type: 'string' } },
      required: ['file', 'summary'],
    } },
    implementerSaid: { type: 'string' },
    gaps: { type: 'array', items: { type: 'string' } },
    outOfScopeFiles: { type: 'array', items: { type: 'string' } },
  },
  required: ['unitId', 'branch', 'status', 'changes'],
}

const GATE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    unitId: { type: 'string' },
    merged: { type: 'boolean' },
    buildPassed: { type: 'boolean' },
    reason: { type: 'string' },
    failures: { type: 'array', items: { type: 'string' } },
    failureLog: { type: 'string' },
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

// ---------- backend resolution ----------
let BACKEND = (args && args.backend) || 'auto'
let CODEX_AVAILABLE = (args && typeof args.codexAvailable === 'boolean') ? args.codexAvailable : undefined
if (BACKEND === 'auto' || CODEX_AVAILABLE === undefined) {
  // Direct manual invocation: the launcher normally resolves this. Workflows cannot run bash, so
  // one trivial agent runs the doctrine §4 selection predicate.
  const det = await agent(
    [
      'Run exactly this shell test and report the result:',
      '  command -v codex >/dev/null 2>&1 && command -v jq >/dev/null 2>&1 && codex login status >/dev/null 2>&1',
      'Return codexAvailable=true only if the combined test exits 0. Do nothing else.',
    ].join('\n'),
    { schema: DETECT_SCHEMA, label: 'detect-backend', phase: 'Decompose' },
  )
  CODEX_AVAILABLE = !!(det && det.codexAvailable)
  if (BACKEND === 'auto') BACKEND = CODEX_AVAILABLE ? 'codex' : 'claude'
}
if (BACKEND === 'codex' && CODEX_AVAILABLE === false) {
  log('ERROR: backend forced to codex but codex is unavailable (install/login/jq check failed).')
  return { error: 'codex unavailable' }
}
log(`Backend: ${BACKEND} (codexAvailable=${CODEX_AVAILABLE})`)

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

// File-disjointness is the merge-gate contract: units sharing any file are merged into one
// sequential unit (dependsOn union) rather than letting the gate hit a conflict it must refuse.
function enforceDisjoint(units) {
  const out = units.map(u => ({ ...u, files: (u.files || []).slice(), dependsOn: (u.dependsOn || []).slice() }))
  let changed = true
  while (changed) {
    changed = false
    for (let i = 0; i < out.length && !changed; i++) {
      for (let j = i + 1; j < out.length && !changed; j++) {
        const a = out[i], b = out[j]
        if (a.files.some(f => b.files.includes(f))) {
          log(`Decomposition overlap: merging unit "${b.id}" into "${a.id}" (shared files: ${a.files.filter(f => b.files.includes(f)).join(', ')})`)
          a.title = `${a.title} + ${b.title}`
          a.objective = `${a.objective}\n\nADDITIONALLY (merged from overlapping unit "${b.id}"): ${b.objective}`
          a.interfaces = [a.interfaces, b.interfaces].filter(s => s && s.trim() && s.trim() !== 'none').join('\n') || 'none'
          a.constraints = [a.constraints, b.constraints].filter(s => s && s.trim()).join('\n')
          a.verification = [a.verification, b.verification].filter(s => s && s.trim()).join(' && ')
          a.files = Array.from(new Set(a.files.concat(b.files)))
          a.dependsOn = Array.from(new Set(a.dependsOn.concat(b.dependsOn)))
          out.forEach(u => { u.dependsOn = (u.dependsOn || []).map(d => (d === b.id ? a.id : d)) })
          out.splice(j, 1)
          changed = true
        }
      }
    }
  }
  out.forEach(u => { u.dependsOn = Array.from(new Set(u.dependsOn.filter(d => d !== u.id))) })
  return out
}

function firstLines(text, n) {
  return String(text || '').split('\n').slice(0, n).join('\n')
}

function distillHistory(backend, attempts, lastFailureLog) {
  const lines = attempts.map((a, i) => `attempt ${i + 1} (${a.kind}): ${a.status}${a.note ? ` — ${a.note}` : ''}`)
  return [
    `=== PRIOR ATTEMPT HISTORY (backend: ${backend} — that work was DISCARDED; re-implement from the spec on a clean base, do not try to repair it) ===`,
    ...lines,
    '--- LAST VERBATIM GATE FAILURE (ground truth, at most 200 lines) ---',
    lastFailureLog || '(none captured)',
  ].join('\n')
}

function specBlock(unit) {
  return [
    `UNIT: ${unit.id} — ${unit.title}`,
    '',
    'OBJECTIVE:',
    unit.objective,
    '',
    'FILES (closed list — touch ONLY these):',
    ...(unit.files || []).map(f => `- ${f}`),
    '',
    'INTERFACES:',
    unit.interfaces || 'none',
    '',
    'CONSTRAINTS:',
    unit.constraints,
    '- Modify only the files listed under FILES. No new dependencies without flagging them in gaps.',
    '- Do not push. Never weaken, disable, or delete an existing test to get a green result.',
    '- Implement every OBJECTIVE item completely: no TODO, no stub, no placeholder.',
    '',
    'VERIFICATION (the gate runs this — you do NOT):',
    unit.verification,
  ].join('\n')
}

function checkoutLines(branch) {
  return [
    '     git fetch --quiet || true',
    `     git checkout -B ${branch} "${INTEGRATION}" 2>/dev/null || git checkout -B ${branch} "origin/${BASE}" 2>/dev/null || git checkout -B ${branch} "${BASE}"`,
  ]
}

function implPromptCodex(unit, branch, history) {
  const modelFlag = CODEX_MODEL ? `-m '${CODEX_MODEL}' ` : ''
  return [
    `You are a CODEX WRAPPER agent for work unit "${unit.id}" (${unit.title}). You run in an isolated git worktree.`,
    'Follow the `calling-codex` skill (conductor plugin) exactly — you delegate ALL code edits to edit-only Codex; you do NOT write feature code yourself.',
    '',
    'The unit spec below is SELF-CONTAINED — embed it in the Codex handoff verbatim (Codex cannot read the plan).',
    specBlock(unit),
    history ? `\n${history}\n` : '',
    'Steps:',
    '1. Base your worktree on the integration branch so you build on earlier waves:',
    ...checkoutLines(branch),
    '2. Write a Codex handoff prompt FILE containing the unit spec above plus this report suffix:',
    '   "End your reply with the structured report, in exactly this format:',
    '    STATUS: <complete|partial|blocked> / OBJECTIVE: <one line> / CHANGES: one line per touched file / GAPS: one line per gap or the single word none"',
    '3. Run Codex EDIT-ONLY, network off, prompt via STDIN REDIRECT, per the calling-codex skill (disable the harness Bash sandbox on this call). Use mktemp — avoid predictable /tmp paths:',
    '     handoff=$(mktemp); out=$(mktemp); jsonl=$(mktemp)   # write the handoff prompt into "$handoff"',
    `     timeout 1200 codex exec -s workspace-write ${modelFlag}-c 'approval_policy="never"' -c 'model_reasoning_effort="${CODEX_EFFORT}"' \\`,
    '       --json -o "$out" < "$handoff" > "$jsonl"',
    '   Capture resumeToken: jq -r \'select(.type=="thread.started").session_id\' "$jsonl" | head -1',
    '4. Map the outcome to status:',
    '   - exit 124 -> status "timeout": do NOT commit; leave the worktree as-is and report.',
    '   - non-zero exit with stderr matching auth/login/quota/rate-limit -> status "unavailable": do NOT commit.',
    '   - non-zero exit with no edits (git status --porcelain empty) or empty "$out" -> status "unavailable".',
    '   - Codex report says blocked -> status "blocked": do NOT commit; put its question into gaps.',
    '   - otherwise -> status per Codex\'s own STATUS line ("complete" or "partial").',
    '5. Only for "complete"/"partial": build the changes array from `git status --porcelain` (one entry per touched file — never from memory), list files outside the FILES list as outOfScopeFiles, then commit:',
    `     git add -A && git commit -m "unit ${unit.id}: ${unit.title}"`,
    '6. Set implementerSaid to a one-line summary of Codex\'s final message, noting any disagreement between its claims and the actual diff. Copy Codex\'s GAPS lines into gaps.',
    '',
    `Return the structured report with branch = "${branch}". Do NOT build or run tests (that is the gate's job). Do NOT push.`,
  ].join('\n')
}

function implPromptClaude(unit, branch, history) {
  return [
    `You are the IMPLEMENTER for work unit "${unit.id}" (${unit.title}). You run in an isolated git worktree and write the code YOURSELF with your edit tools.`,
    '',
    'ROLE BOUNDARY — you implement, the gate verifies:',
    '- The ONLY commands you may run are the git commands printed in steps 1, 3 and 4 below. A command that is not one of those is forbidden.',
    '- Never run a build, test, lint, install, package-manager, or network command. The gate runs the verification command.',
    '',
    specBlock(unit),
    history ? `\n${history}\n` : '',
    'Steps:',
    '1. Check out the unit branch:',
    ...checkoutLines(branch),
    '2. Read every file named under FILES (and any file INTERFACES references), then implement the OBJECTIVE completely. Edit only the FILES list. If the spec is ambiguous or you are blocked, stop, do NOT commit, and return status "blocked" with exactly one precise question in gaps.',
    '3. Run `git status --porcelain` and `git diff --stat`; build the changes array from that output (one entry per touched file — never from memory). List files outside the FILES list as outOfScopeFiles.',
    `4. git add -A && git commit -m "unit ${unit.id}: ${unit.title}"`,
    '',
    `Return the structured report with branch = "${branch}" and resumeToken = "". Status "complete" only if every OBJECTIVE item is implemented; otherwise "partial" with one gaps entry per missing item. Do NOT push.`,
  ].join('\n')
}

function gatePrompt(unit, impl) {
  return [
    `You are the VERIFY/MERGE GATE for unit "${unit.id}" on branch "${impl.branch}". You have FULL access (network + toolchain + caches).`,
    `Integrate this unit into the integration branch "${INTEGRATION}", then verify. Keep it only if green.`,
    '',
    'Steps:',
    '1. Ensure the integration branch exists and is checked out:',
    `     git rev-parse --verify "${INTEGRATION}" >/dev/null 2>&1 || git branch "${INTEGRATION}" "origin/${BASE}" 2>/dev/null || git branch "${INTEGRATION}" "${BASE}"`,
    `     git checkout "${INTEGRATION}"`,
    `2. Merge the unit branch:  git merge --no-ff --no-edit "${impl.branch}"`,
    '   - On conflict: resolve ONLY if trivial and obviously correct. Otherwise: git merge --abort, return merged:false, reason:"conflict", and STOP — never force-merge. On a conflict leave failureLog empty.',
    `3. Audit scope from the ACTUAL diff of the merge (git diff HEAD~1..HEAD --name-only): any file outside this unit's FILES list (${(unit.files || []).join(', ')}) is a scope violation — report it in failures.`,
    `4. Run the project's FAST gate. DISCOVER the commands from the project's CLAUDE.md / AGENTS.md / README or its build config (package.json scripts, pom.xml, Cargo.toml, go.mod, Makefile): typecheck / build / lint as the project defines them, then this unit's verification command(s): ${unit.verification}`,
    '5. If green -> keep the merge (merged:true, buildPassed:true). If red -> undo it (git reset --hard HEAD~1) so the integration branch stays buildable; return merged:false.',
    '   On a red BUILD (not a conflict), put the FULL VERBATIM failing output into failureLog — the exact commands, their stderr, errors with file:line, failing-test names + assertion diffs, and stack traces (root errors first; cap ~200 lines; do NOT summarize). A fix agent feeds this straight back to the implementer, which never ran the build.',
    '   (The heavy/slow suite runs once in the Final verify phase, not per unit.)',
    'Return the structured result. Do NOT push.',
  ].join('\n')
}

function fixPromptCodex(unit, impl, failureLog, round) {
  const branch = `${impl.branch}-r${round}`
  return [
    `You are a CODEX-WRAPPER FIX agent for work unit "${unit.id}" (gate round ${round}). You run in an isolated git worktree.`,
    'Follow the `calling-codex` skill — you delegate ALL edits to edit-only Codex; you do NOT write feature code yourself.',
    'The gate merged this unit and the project verification FAILED. Hand the verbatim failing output (at the end) to Codex unchanged; do not summarize it.',
    '',
    'Steps:',
    '1. Get a fresh fix branch on the unit\'s code (avoids "already checked out" conflicts):',
    '     git fetch --quiet || true',
    `     git checkout -B ${branch} "${impl.branch}"`,
    '2. Write the failing output below, plus "fix ONLY these failures; stay in the unit\'s FILES list; do NOT build/test/commit/install or use the network", into a prompt file. Then resume the unit\'s Codex session — NOTE: `codex exec resume` takes NO -s flag; pass the sandbox as a config override, per the calling-codex skill:',
    `     timeout 1200 codex exec resume "${impl.resumeToken || ''}" -c 'sandbox_mode="workspace-write"' -c 'approval_policy="never"' -c 'model_reasoning_effort="${CODEX_EFFORT}"' -o "$(mktemp)" - < "$FIXPROMPT"`,
    `   If the resumeToken is empty, or the previous attempt timed out, do NOT resume — run a fresh exec instead, embedding the unit spec below plus the failures in the prompt file:`,
    `     timeout 1200 codex exec -s workspace-write -c 'approval_policy="never"' -c 'model_reasoning_effort="${CODEX_EFFORT}"' --json -o "$(mktemp)" < "$FIXPROMPT" > "$(mktemp)"`,
    specBlock(unit),
    '   Map exit 124 -> status "timeout" (do NOT commit); auth/quota stderr -> "unavailable" (do NOT commit).',
    `3. On "complete"/"partial": rebuild the changes array from \`git status --porcelain\`, then commit:  git add -A && git commit -m "unit ${unit.id} fix r${round}"`,
    '',
    `Return the structured report with branch = "${branch}" and the resumeToken you used or captured. Do NOT build, test, or push.`,
    '',
    '--- VERBATIM GATE FAILURE OUTPUT ---',
    failureLog || '(none captured)',
  ].join('\n')
}

function fixPromptClaude(unit, impl, failureLog, round) {
  const branch = `${impl.branch}-r${round}`
  return [
    `You are the FIX IMPLEMENTER for unit "${unit.id}", round ${round}. You run in an isolated git worktree and write the code YOURSELF with your edit tools.`,
    'The gate merged this unit and the project verification FAILED; the verbatim output is at the end.',
    '',
    'ROLE BOUNDARY — same as implementation:',
    '- The ONLY commands you may run are the git commands printed in steps 1, 3 and 4 below.',
    '- Never run a build, test, lint, install, package-manager, or network command.',
    '',
    'The unit spec (unchanged):',
    specBlock(unit),
    '',
    'Steps:',
    '1. git fetch --quiet || true',
    `     git checkout -B ${branch} "${impl.branch}"`,
    '2. Read the failure output, open every cited file, and fix ONLY these failures. Stay within the FILES list.',
    '3. Rebuild the changes array from `git status --porcelain` and `git diff --stat`.',
    `4. git add -A && git commit -m "unit ${unit.id} fix r${round}"`,
    '',
    `Return the structured report with branch = "${branch}" and resumeToken = "".`,
    '',
    '--- VERBATIM GATE FAILURE OUTPUT ---',
    failureLog || '(none captured)',
  ].join('\n')
}

function finalPrompt() {
  return [
    `You are the FINAL VERIFIER. Check out the integration branch "${INTEGRATION}" and run the project's FULL gate (full access):`,
    'DISCOVER the commands from the project\'s CLAUDE.md / AGENTS.md / README or build config — typecheck, build, lint, the full test suite, and any integration / end-to-end suite the project defines.',
    `Then compare the integrated result against the approved plan at ${PLAN_PATH}: which plan items are fully implemented, which remain outstanding.`,
    'Do NOT commit or push. Return the structured result.',
  ].join('\n')
}

// ---------- backend dispatch ----------
const wrapperModel = CODEX_WRAPPER_MODEL === 'inherit' ? undefined : CODEX_WRAPPER_MODEL
const claudeFixModel = round => ((CLAUDE_MODEL === 'sonnet' && round >= 2) ? 'opus' : CLAUDE_MODEL)

function runImpl(unit, backend, suffix, history, phaseName) {
  const branch = `conductor/unit-${unit.id}${suffix || ''}`
  const opts = { isolation: 'worktree', schema: REPORT_SCHEMA, label: `impl:${unit.id}${suffix || ''}`, phase: phaseName }
  return backend === 'codex'
    ? agent(implPromptCodex(unit, branch, history), wrapperModel ? { ...opts, model: wrapperModel } : opts)
    : agent(implPromptClaude(unit, branch, history), { ...opts, model: CLAUDE_MODEL })
}

function runFix(unit, state, failureLog, round, backend) {
  const opts = { isolation: 'worktree', schema: REPORT_SCHEMA, label: `fix:${unit.id}#${round}`, phase: 'Verify & merge' }
  return backend === 'codex'
    ? agent(fixPromptCodex(unit, state, failureLog, round), wrapperModel ? { ...opts, model: wrapperModel } : opts)
    : agent(fixPromptClaude(unit, state, failureLog, round), { ...opts, model: claudeFixModel(round) })
}

// Gate + bounded fix loop for one lane attempt. Returns { merged, state, attempts, lastGate }.
async function gateWithFixes(unit, impl, backend) {
  const attempts = []
  let state = impl
  if (!state) state = { unitId: unit.id, branch: '', status: 'unavailable', changes: [], gaps: ['agent returned no result'] }
  attempts.push({ kind: 'implement', status: state.status, note: (state.gaps && state.gaps[0]) || '' })
  // No commit exists for these statuses -> nothing to gate; the ladder decides what happens next.
  if (state.status !== 'complete' && state.status !== 'partial') {
    return { merged: false, state, attempts, lastGate: null }
  }
  if (state.outOfScopeFiles && state.outOfScopeFiles.length) {
    log(`  ${unit.id}: implementer touched out-of-scope files: ${state.outOfScopeFiles.join(', ')}`)
  }
  let gate = await agent(gatePrompt(unit, state), { schema: GATE_SCHEMA, label: `gate:${unit.id}`, phase: 'Verify & merge' })
  let round = 0
  while (gate && !gate.merged && gate.failureLog && round < MAX_FIX_ROUNDS) {
    round++
    log(`  ${unit.id}: gate failed (round ${round}) — handing verbatim failures back to the ${backend} lane`)
    let fixed = await runFix(unit, state, gate.failureLog, round, backend)
    if (!fixed) fixed = { unitId: unit.id, branch: state.branch, status: 'unavailable', changes: [], gaps: ['fix agent returned no result'] }
    attempts.push({ kind: `fix-r${round}`, status: fixed.status, note: firstLines(gate.failureLog, 3) })
    if (fixed.status !== 'complete' && fixed.status !== 'partial') { state = fixed; break }
    state = fixed
    gate = await agent(gatePrompt(unit, state), { schema: GATE_SCHEMA, label: `gate:${unit.id}#${round}`, phase: 'Verify & merge' })
  }
  return { merged: !!(gate && gate.merged), state, attempts, lastGate: gate }
}

// ---------- 1. Decompose ----------
phase('Decompose')
const decomp = await agent(
  [
    `You are the DECOMPOSER. Read the approved implementation plan at ${PLAN_PATH}.`,
    'Split it into independent work UNITS suitable for parallel implementation. REQUIREMENTS:',
    '- Each unit must be FILE-DISJOINT from the others (overlapping files cause merge conflicts the gate cannot auto-resolve; overlapping units will be merged into one).',
    '- For each unit author a SELF-CONTAINED five-part spec — the implementer will NOT see the plan:',
    '  objective (what to build, standalone, with checkable acceptance criteria), files (the exact create/modify list),',
    '  interfaces (the signatures/types/contracts this unit exposes or consumes — verbatim where the plan fixes them, so dependent units implemented in parallel agree; "none" if self-contained),',
    '  constraints (the project conventions that apply, stated concretely), verification (the exact command(s) the gate runs for this unit).',
    '- Give each unit a stable kebab-case id, a title, and dependsOn (ids of units whose code it builds on).',
    '- Set fileDisjoint=true only if no two units share a file; otherwise false, and explain the overlaps in notes.',
    "- Respect the plan's own phases: a phase that builds on a prior phase becomes a unit that dependsOn it.",
    '- No unit below the worthiness floor (under 20 estimated changed lines in at most 2 files with no new test files) — merge undersized units into an adjacent unit.',
    'Return the structured decomposition. Do not implement anything.',
  ].join('\n'),
  { schema: DECOMPOSE_SCHEMA, label: 'decompose', phase: 'Decompose' },
)

let units = (decomp && decomp.units) || []
if (!units.length) {
  log('Decomposition produced no units — aborting.')
  return { error: 'empty decomposition', decomp }
}
if (decomp.fileDisjoint === false) {
  log(`Decomposer reported overlapping units — enforcing disjointness by merging. ${decomp.notes || ''}`)
}
units = enforceDisjoint(units)
const waves = topoWaves(units)
log(`Decomposed into ${units.length} unit(s) across ${waves.length} dependency wave(s).`)

// ---------- 2 + 3. Per wave: implement (parallel) -> verify/merge ladder (sequential) ----------
const integrated = []
const failed = []
for (let w = 0; w < waves.length; w++) {
  const wave = waves[w]
  log(`Wave ${w + 1}/${waves.length}: ${wave.map(u => u.id).join(', ')}`)

  // Implementation is parallel within the wave; the gate ladder is sequential (merges are
  // stateful on the integration branch), so runLadder re-runs the implement step itself only
  // for conflict-retry / re-route. To keep first-pass parallelism, prefetch rung-1 impls here.
  phase('Implement')
  const firstImpls = await parallel(wave.map(unit => () => runImpl(unit, BACKEND, '', '', 'Implement')))

  phase('Verify & merge')
  for (let i = 0; i < wave.length; i++) {
    const unit = wave[i]
    const record = { attempts: [], lastFailureLog: '', lastBranch: '' }
    let res = await gateWithFixes(unit, firstImpls[i], BACKEND)
    record.attempts.push(...res.attempts.map(a => ({ ...a, lane: BACKEND })))
    record.lastFailureLog = (res.lastGate && res.lastGate.failureLog) || ''
    record.lastBranch = (res.state && res.state.branch) || ''
    let merged = res.merged

    if (!merged) {
      const wasConflict = !!(res.lastGate && !res.lastGate.merged && !res.lastGate.failureLog)
      if (wasConflict) {
        log(`  ${unit.id}: merge conflict — one same-lane clean re-implementation off current integration`)
        const retryImpl = await runImpl(unit, BACKEND, '-retry', '', 'Verify & merge')
        res = await gateWithFixes(unit, retryImpl, BACKEND)
        record.attempts.push(...res.attempts.map(a => ({ ...a, lane: `${BACKEND}-retry` })))
        record.lastFailureLog = (res.lastGate && res.lastGate.failureLog) || record.lastFailureLog
        record.lastBranch = (res.state && res.state.branch) || record.lastBranch
        merged = res.merged
      }
    }

    if (!merged) {
      const other = BACKEND === 'codex' ? 'claude' : 'codex'
      const otherAvailable = other === 'claude' ? true : !!CODEX_AVAILABLE
      if (ALLOW_REROUTE && otherAvailable) {
        log(`  ${unit.id}: re-routing to the ${other} lane`)
        const history = distillHistory(BACKEND, record.attempts, record.lastFailureLog)
        const altImpl = await runImpl(unit, other, '-alt', history, 'Verify & merge')
        res = await gateWithFixes(unit, altImpl, other)
        record.attempts.push(...res.attempts.map(a => ({ ...a, lane: other })))
        record.lastFailureLog = (res.lastGate && res.lastGate.failureLog) || record.lastFailureLog
        record.lastBranch = (res.state && res.state.branch) || record.lastBranch
        merged = res.merged
      }
    }

    if (merged) {
      integrated.push(unit.id)
      log(`  ${unit.id}: verified + merged (${record.attempts.length} attempt(s))`)
    } else {
      failed.push({ id: unit.id, spec: unit, lastBranch: record.lastBranch, lastFailureLog: record.lastFailureLog, attempts: record.attempts })
      log(`  ${unit.id}: exhausted after ${record.attempts.length} attempt(s) — handing to the coordinator (rung 3)`)
    }
  }
}

// ---------- 4. Final verify ----------
phase('Final verify')
const final = await agent(finalPrompt(), { schema: FINAL_SCHEMA, label: 'final-verify', phase: 'Final verify' })

log(`Integrated ${integrated.length}/${units.length} unit(s); ${failed.length} failed. Final gate: ${final && final.gatePassed ? 'PASS' : 'FAIL'}.`)
return {
  backend: BACKEND,
  units: units.length,
  waves: waves.length,
  integrationBranch: INTEGRATION,
  integrated,
  failed,
  final,
}
