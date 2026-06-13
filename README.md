# Agentics — Claude Code Plugin Marketplace

A collection of advanced Claude Code plugins for research, content generation, and more.

## Installation

```bash
# Add this marketplace to Claude Code:
/plugin marketplace add ebner/agentics

# Install individual plugins:
/plugin install deep-research@agentics
/plugin install gemini-imagegen@agentics
/plugin install codex-orchestration@agentics
```

## Plugins

### deep-research

Multi-phase web research with 15 domain-specific agent profiles covering health,
finance, legal, technology, consumer products, travel, entertainment, sports,
cooking, science, education, career, parenting, pets, and general topics.
Features interactive research plan preview, iterative follow-up refinement,
batch research across multiple topics, reusable research profiles, saturation-based
termination, multilingual search, anti-misinformation framework with domain-specific
REJECT lists, and fake review detection. Produces citation-backed markdown reports
with source credibility assessment.

### gemini-imagegen

Image generation and editing using Google's Gemini API. Supports text-to-image,
image editing, SVG vector generation, multi-image composition, multi-turn
refinement, and automatic transparency conversion. Includes prompt sidecar
metadata files for reproducibility.

### codex-orchestration

Hand an already-approved implementation plan to OpenAI Codex for implementation via the official
`codex` CLI. Provides the `/codex-orchestration:codex-implement` command (linear handoff: cross-model
plan review → per-phase implement/verify/fix → close-out), the `codex-implement-fanout` workflow
(parallel fan-out: decompose → isolated worktree implementers → verify/merge gate), and the
`calling-codex` skill (the shared edit-only, network-off Codex-invocation convention). Codex writes the
code edit-only and offline; the orchestrator owns every build, test, and merge. Project-agnostic — the
build/test gate is discovered from the target project's own config.

## License

MIT
