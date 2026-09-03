# Claude Code Guidelines

This repository is a Claude Code plugin marketplace containing multiple plugins.

> **Note:** `CLAUDE.md` is a symlink to `AGENTS.md`. Edit `AGENTS.md` directly — it is the single source of truth.

## Repository Structure

```
agentics/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace manifest (lists all plugins)
├── plugins/
│   └── <plugin-name>/        # Each plugin in its own directory
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin manifest
│       ├── skills/           # Skill definitions
│       │   └── <skill-name>/
│       │       ├── SKILL.md  # Main skill file
│       │       ├── reference/ # Supporting docs loaded on demand
│       │       └── scripts/  # Executable scripts (optional)
│       ├── agents/           # Subagent definitions (optional)
│       │   └── <agent>.md
│       ├── commands/         # Slash commands (optional)
│       │   └── <command>.md
│       ├── .mcp.json         # MCP server config (optional)
│       └── README.md
└── README.md
```

## Adding a New Plugin

1. Create a new directory under `plugins/` with the plugin name (kebab-case)
2. Create `.claude-plugin/plugin.json` inside the plugin directory:
   ```json
   {
     "name": "<plugin-name>",
     "version": "1.0.0",
     "description": "<description>",
     "author": { "name": "Hannes Ebner" },
     "repository": "https://github.com/ebner/agentics",
     "license": "MIT",
     "keywords": ["relevant", "tags"]
   }
   ```
3. Create skill, command, or agent files as needed
4. Add the plugin to `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "description": "<description>",
     "version": "1.0.0"
   }
   ```

## Skill File Format

Skills are the preferred component type for new functionality. Each skill lives in its own directory under `skills/<skill-name>/` and requires a `SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name
description: >
  When to trigger this skill. Be specific about trigger phrases and contexts.
  Include both what the skill does AND when to use it.
allowed-tools:
  - WebSearch
  - WebFetch
  - Task
  - Read
  - Write
---

Instructions for Claude to follow when the skill is triggered.
```

### Progressive disclosure

Keep SKILL.md under 500 lines. For larger skills, use bundled resources:
- `reference/` — documentation loaded on demand via Read tool
- `scripts/` — executable code for deterministic tasks
- `agents/` — sub-agent templates (within the skill dir, NOT the plugin's top-level agents/)

Reference files from SKILL.md with clear guidance on when to read them. Claude only loads what's needed for the current task.

### Path references in skills

- `${CLAUDE_PLUGIN_ROOT}` is expanded ONLY in hook commands and `.mcp.json` — NOT in SKILL.md instruction text
- For file references within a skill, use paths relative to the SKILL.md location (e.g., `reference/search-strategy.md`, `domains/health/agent.md`)
- For script paths in Bash commands, use dynamic discovery since the install path is unpredictable:
  ```bash
  SCRIPT="$(find ~/.claude -path '*/<skill-name>/scripts/<script>' -print -quit 2>/dev/null)"
  ```

## Agent File Format

Agents are subagent definitions that Claude Code auto-discovers from the plugin's top-level `agents/` directory:

```markdown
---
name: agent-name
description: >
  When to use this agent. Include <example> blocks for triggering.
model: sonnet
color: green
---

Agent system prompt and instructions.
```

Only place files in the plugin's top-level `agents/` directory if they should be auto-discovered as standalone subagents. Reference templates (like domain-specific agent profiles read by a skill) belong inside the skill's directory tree, not in `agents/`.

## Command File Format

Commands are slash-command definitions:

```markdown
---
description: Short description shown in help
argument-hint: "[required-arg] [optional-arg]"
allowed-tools: ["Read", "Write", "Bash"]
---

Instructions for Claude. Use `$ARGUMENTS` for user-provided arguments.
```

## Model Compatibility

This project targets **Claude Opus 5** and **Claude Fable 5** as primary models. All
instruction content (CLAUDE.md/AGENTS.md, skills, agents, commands, and prompt strings
built by workflow scripts) must be authored against the rules in this section.

Model references in this repo are Claude Code tier aliases (`opus`, `sonnet`, `haiku`,
`inherit`), never dated API model IDs. Aliases resolve to the current generation, so they
need no per-release edit — do not introduce a pinned API model ID (`claude-opus-5`,
`claude-fable-5`) into instruction content or agent frontmatter.

### Precision — unchanged

Both models interpret instructions literally. Every rule below still applies as written:

- Use inspectable predicates (file-pattern matches, regex, explicit enum lists)
  instead of vague adjectives like "relevant", "appropriate", "as needed"
- State subagent-launch rules explicitly: which agents, one Task call per agent,
  all Task calls in the same assistant message
- Avoid `etc.`, open-ended `...`, and trailing ellipses in instruction text;
  enumerate exhaustively or reference a specific numbered section
- Replace `...` in output templates with `[repeat one entry per X]` directives —
  a literal model may reproduce `...` verbatim otherwise
- When stating an absolute rule (`always`, `never`), co-locate the concrete
  exception if one exists, rather than contradicting it in a later paragraph

### Goal over steps

Fable 5 loses output quality on over-prescriptive prompts: a fixed step sequence for work
the model can sequence itself constrains it below its own planning. This does **not**
loosen the precision rules above — the two act on different axes:

- Keep: exact predicates, closed lists, mandated output formats, named commands, caps.
- Remove: procedural micromanagement — an ordered recipe for work whose ordering is not
  load-bearing, or a prescribed tool sequence where the outcome is what matters.
- State the objective, the constraints, and what "done" is measured by. Fix the order only
  when a later step genuinely depends on an earlier one (dependency-ordered units, a
  snapshot taken before dispatch); say so where the order is fixed.

**Audit result for the existing step sequences.** The numbered sequences in this repo were reviewed
against this rule and kept, because each one's ordering is load-bearing: conductor's Stage 0–4
pipeline (a later stage consumes an earlier stage's artifact — RUN CONFIG, the approved plan, the
per-unit snapshot), the fanout worktree steps (branch checkout must precede edits, which must precede
the diff the report is built from), deep-research's STEP 0–9 (each phase consumes the previous
phase's output, and the saturation test governs the loop), and gemini-imagegen's script recipes
(deterministic CLI invocations where the argument order is the contract). Re-audit a sequence when
you touch it; do not treat these as exempt in perpetuity.

### Verbosity and deliverable length

Both models write long by default — long user-facing messages, narration between tool
calls, and long files written to disk. Lowering `effort` does not reliably shorten
visible output; instruct for it:

- Any component that produces a user-facing report forbids padding — no filler sections, no
  redundant summaries, no boilerplate — and bounds its length. Prefer a numeric target where the
  deliverable has a natural size (deep-research's per-mode word ranges); where it does not, bound
  it by content instead ("cover every unit's final state and every Must-fix finding; drop anything
  that does not change the user's next action").
- Any component that writes a file for a human to read states the same for that file.
- Lead with the outcome: the first sentence after finishing answers "what happened" or
  "what did you find", with supporting detail after it.
- Readable beats short. Keep output brief by dropping detail that does not change what the
  reader does next, never by compressing prose into fragments, invented abbreviations, or
  arrow chains.

### Verification: name the check, do not nudge

Both models verify without being asked. A bare "double-check your answer" or "re-verify
before responding" produces over-verification with no quality gain, so no prompt in this
repo carries that phrasing. What stays, and is added where a component runs long, is
verification with a named object: the command that gates a unit, the spec a result is
checked against, or a separate fresh-context reviewer. That is a harness feature rather
than a prompt nudge. An existing "check your work against X" instruction survives a
retarget; do not delete one because it mentions verification.

### Scope discipline

Opus 5 can widen a task past what was asked, and Fable 5 at higher effort can add
abstractions, helpers, or error handling nobody requested. Every component that writes code
or content on the user's behalf states the boundary:

- Deliver the requested scope; do not quietly narrow, widen, or transform it.
- Do not add features, refactors, abstractions, or error handling for conditions that
  cannot occur.
- Finish the whole task; report completion only when it is fully done, and state plainly
  what is missing when something is not.

### Delegation

Opus 5 reaches for subagents readily; Fable 5 sustains parallel subagents well. Neither
"delegate more" nor "delegate less" is the right instruction — state the criteria and a
ceiling:

- Name what qualifies for delegation and what does not (see the conductor plugin's
  `delegation-doctrine` skill §3 for this repo's worked example).
- State an explicit numeric cap on concurrent subagents wherever fan-out is possible.
- Never delegate review of a delegate's own output back to that delegate.

### Autonomy and corrections

- Opus 5 asks more often on minor decisions. Where a component runs a multi-stage pipeline,
  grant autonomy explicitly: make routine judgment calls (naming, formatting, defaults,
  choosing among equivalent approaches) without asking, and keep the confirmation gates for
  scope changes and destructive or outward-facing actions. Enumerate those gates.
- Opus 5 narrates self-corrections at length. Where a component runs long, instruct it to
  correct an earlier statement only when the error changes the user's decisions, state the
  correction in one sentence, and continue — no apology, no tally of past errors.

### Evidence-grounded claims

Fable 5 can report progress that outruns what it actually verified, especially on long
runs. Any component that reports status, coverage, or completion must derive those claims
from recorded tool output — a diff, a command's exit status, a written evidence file, a
counted registry — never from recollection. Prefer instructions that name the artifact the
claim is read from.

### Long turns and effort

- A single request on a hard task can run many minutes. Any timeout, time cap, or progress
  display in this repo must tolerate that; state the timeout next to the command it wraps.
- Give a long-running component room in its output budget: a large token ceiling costs
  nothing when unused, but a tight one truncates mid-answer.
- **Reasoning effort is not a Claude-side knob in this repo.** Claude subagents are tiered by
  `model` (the aliases above), and `effort` / `xhigh` appears here only as Codex's
  `model_reasoning_effort`, set via the conductor plugin's `codex_effort` setting. Do not add
  an `effort` argument to a Task or Agent call, and do not describe `xhigh` as a Claude setting.
  If a component needs deeper Claude reasoning, raise its `model` tier instead.
- A final summary after a long unattended run is the user's first look at the work. Instruct
  such components to re-ground the reader: outcome first, then what is needed from them,
  with terms spelled out rather than carried over from the working thread.

## Adding MCP Servers

### Bundled with a plugin

1. Create a `servers/` directory inside the plugin
2. Add the MCP server code
3. Create `.mcp.json` in the plugin root:
   ```json
   {
     "server-name": {
       "command": "node",
       "args": ["${CLAUDE_PLUGIN_ROOT}/servers/my-server.js"]
     }
   }
   ```

### MCP path notes

- Always use `${CLAUDE_PLUGIN_ROOT}` for paths in `.mcp.json` and hook commands
- Plugins are copied to a cache directory during installation — never hardcode paths

## Naming Conventions

- **Marketplace name**: `agentics`
- **Plugin names**: kebab-case (e.g., `deep-research`, `gemini-imagegen`)
- **Skill names**: kebab-case, match the directory name
- **Full skill invocation**: `/plugin-name:skill-name` or `/skill-name` if unique

## Git Commit Guidelines

- Never mention AI, Claude, or any AI assistant in commit messages
- Write commit messages as if a human authored them
- Use conventional style: short summary line, blank line, detailed description if needed
- Use `master` as the default branch name

## Versioning

- Bump the plugin version (minor) before committing changes to a plugin
- Update version in both `plugin.json` and `marketplace.json`
- When bumping, also update any version references in README files

## Documentation

- Each plugin must have its own `README.md` with installation instructions and usage
- The top-level `README.md` lists all available plugins with descriptions
- When making changes, keep both READMEs in sync

## Testing Guidelines

- Never create tautological tests that pass by definition
- Every test must be capable of failing if the code under test is broken
- Every test must include at least one positive assertion
- A tautological test is one that asserts something that is always true regardless of the code's behavior (e.g., asserting a mock returns what you told it to return, or asserting `True == True`)

### Running Tests

Each plugin with tests has its own venv. Run tests from the plugin's skill directory:

```bash
cd plugins/gemini-imagegen/skills/gemini-imagegen
.venv/bin/python -m pytest tests/ -v
```

If the venv doesn't exist yet, run any script via `run.sh` first to create it, or set it up manually:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Installation

Users install plugins with:
```bash
/plugin marketplace add ebner/agentics
/plugin install <plugin-name>@agentics
```
