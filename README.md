# Agentics — Claude Code Plugin Marketplace

A collection of advanced Claude Code plugins for research, content generation, and more.

## Installation

```bash
# Add this marketplace to Claude Code:
/plugin marketplace add ebner/agentics

# Install individual plugins:
/plugin install deep-research@agentics
/plugin install gemini-imagegen@agentics
/plugin install conductor@agentics
```

## Security and cost

These plugins run with the same permissions as your Claude Code session. Know what each one does
before you install it:

- **deep-research** fetches and reads web pages and runs many research subagents in parallel. A
  deep run can use a large share of your plan's usage or a significant amount of API spend.
- **gemini-imagegen** calls the Google Gemini API, which is billed per image by Google, using the
  `GEMINI_API_KEY` from your environment. The key is never written to disk. On first use it
  creates a Python virtual environment inside the plugin directory and installs the pinned packages
  from `requirements.txt` from PyPI.
- **conductor** runs your project's build and test commands, creates git branches and worktrees,
  and (when installed) runs the OpenAI Codex CLI, which bills against your OpenAI account. Codex
  runs in its sandbox with writes confined to the project and network off. conductor never
  commits to your branch or pushes. The plugin's README describes its safety model in detail.
  Fan-out mode starts many agents in parallel.

Report a security problem through this repository's private vulnerability reporting (the
**Security** tab), not through a public issue.

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

Image generation and editing using Google's Gemini API (Nano Banana 2.1). Supports text-to-image,
image editing, SVG vector generation, multi-image composition, multi-turn
refinement, and automatic transparency conversion. Includes prompt sidecar
metadata files for reproducibility. Nano Banana Pro support adds
identity-preserving style transfer and face-consistent composition.

### conductor

Plan big, execute small — a coordinator/orchestrator for delegated implementation. The
coordinating model plans (from an approved plan file or a raw task description), reviews, and
runs every build/test/merge; a cheaper pluggable implementer — the OpenAI Codex CLI (edit-only,
network-off) or a Claude subagent (edit tools only) — writes all the code. One command
(`/conductor:implement`) with a linear default and a `--fanout` mode (decompose into
file-disjoint units → parallel worktree implementers → verify/merge gate). Backend-agnostic
five-part spec + structured report contract, a cross-backend escalation ladder, cross-model
review on both ends, a project-agnostic build/test gate discovered from the target project's
own config, and an append-only run ledger that lets an interrupted run continue with `--resume`.
Replaces the former codex-orchestration plugin.

## License

MIT
