# Claude Code Guidelines

This repository is a Claude Code plugin marketplace containing multiple plugins.

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

## Installation

Users install plugins with:
```bash
/plugin marketplace add ebner/agentics
/plugin install <plugin-name>@agentics
```
