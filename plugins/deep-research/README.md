# Deep Research Skill for Claude Code

A Claude Code skill that replicates Claude.ai's Research mode behavior — conducting
exhaustive, multi-phase web research with parallel sub-agents, fetching and analyzing
50-200+ web sources, and producing citation-backed reports.

## Why this exists

Claude.ai's Research mode conducts hundreds of web searches and fetches across
parallel agents. Claude Code's built-in WebSearch/WebFetch are single-shot tools.
This skill bridges the gap by orchestrating Claude Code's tools into a systematic
research pipeline.

## What it does

```
You (in Claude Code):  /deep-research Comparing Java virtual threads vs Kotlin coroutines

Claude Code:
  → Decomposes into 6 sub-questions
  → Spawns 3-5 parallel sub-agents (via Task tool)
  → Each agent runs 5-15 WebSearch queries
  → Each agent fetches 10-25 web pages via WebFetch
  → Results are triangulated and cross-verified
  → Contradictions and gaps are identified
  → Follow-up searches fill gaps
  → Structured report written to ./research-output/ in your project
  → Sources JSON saved alongside report
```

## Installation

```bash
# Add the agentics marketplace:
/plugin marketplace add ebner/agentics

# Install the deep-research plugin:
/plugin install deep-research@agentics
```

Reports are saved to `./research-output/` (or your chosen location) in whichever
project directory you start Claude Code from.

### Prerequisites

- **Claude Code** with WebSearch enabled (requires Anthropic first-party API;
  WebSearch is not available on Bedrock/Vertex)
- No additional dependencies for the default path — the skill uses only Claude Code's
  built-in tools
- Optional: `markitdown-mcp` for PDF/YouTube content extraction
- Optional: `FIRECRAWL_API_KEY` (a [Firecrawl](https://firecrawl.dev) account) — enables a
  hosted-scrape fallback for JS-rendered or bot-blocked pages that WebFetch cannot retrieve.
  **Off by default**; when unset, fetching behaves exactly as before. Uses `curl` and
  `python3` (only to parse the API response), both standard on macOS/Linux.

### Permissions setup (important)

This skill makes **60-500+ web requests per session** via sub-agents. If permissions
aren't pre-approved, you'll be prompted for every single request — making research
impractical. Configure these permissions before your first run:

**Add to your project's `.claude/settings.json`:**

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "mcp__markitdown__convert_to_markdown"
    ]
  }
}
```

Or grant permissions interactively during your first session by selecting
"Always allow" when prompted for WebSearch and WebFetch.

> **Note:** Claude Code permissions are project-scoped or global — there is no
> per-plugin permission mechanism. Allowing WebSearch in `.claude/settings.json`
> allows it for all skills and conversations in that project, not just this skill.
> If you want to limit the scope, use project-level settings (`.claude/settings.json`
> in your project root) rather than global settings (`~/.claude/settings.json`).

**What each permission does:**

| Permission | Why needed | Requests per session |
|---|---|---|
| `WebSearch` | Search queries across all sub-agents | 10–100+ |
| `WebFetch` | Fetch and analyze web pages | 10–200+ |
| `mcp__markitdown__convert_to_markdown` | PDF/YouTube fallback (optional) | 0–10 |
| `Bash(curl:*)` | Firecrawl scrape fallback — only if `FIRECRAWL_API_KEY` is set | 0–10 |

The other tools the skill uses (`Task`, `Read`, `Write`, `Bash`, `Glob`,
`AskUserQuestion`) are typically auto-approved by Claude Code and don't need
explicit permission configuration. If you enable the Firecrawl fallback, also allow its
scrape call by adding `"Bash(curl:*)"` to the allow list (or approve it once interactively).

## Usage

### Basic (standard mode — 20-30 searches, 30-60 fetches)
```
/deep-research Java virtual threads vs Kotlin coroutines for high-throughput services
```

### Quick mode (10-15 searches — fast overview)
```
/deep-research quick: is GraalVM native image production-ready in 2025?
```

### Deep mode (40-60 searches — thorough analysis)
```
/deep-research in deep mode: evaluate Micronaut vs Quarkus vs Spring Boot for new microservices
```

### Ultradeep mode (60-100+ searches — exhaustive investigation)
```
/deep-research in ultradeep mode: state of the art in Java garbage collectors 2025
```

### Natural language (Claude auto-detects the skill)
```
Research thoroughly: what are the tradeoffs of event sourcing vs CRUD for our order service?
```

### Batch research (multiple related topics)
```
/deep-research batch:
- Java virtual threads performance characteristics
- Kotlin coroutines performance characteristics
- Go goroutines performance characteristics
```

### With a research profile
```
/deep-research --profile security-audit: evaluate our JWT implementation
```

## Research modes

| Mode      | Searches | Pages fetched | Sub-agents | Duration  | Best for                        |
|-----------|----------|--------------|------------|-----------|----------------------------------|
| quick     | 10-15    | 10-20        | 2          | 2-5 min   | Quick fact-check, overview       |
| standard  | 20-30    | 30-60        | 3          | 5-15 min  | Most research questions          |
| deep      | 40-60    | 60-120       | 4-5        | 15-30 min | Architecture decisions, evals    |
| ultradeep | 60-100   | 100-200      | 6-8        | 30-60 min | Comprehensive reports, RFCs      |

## Output

Reports are saved to `./research-output/` in your project directory (where Claude Code
was started). This keeps research artifacts alongside your codebase — visible in the
file tree, easy to commit or `.gitignore`.

Each research run produces two files:

1. **`research-output/[topic]_[date].md`** — Full markdown report with:
   - Executive summary (≤ 250 words)
   - Detailed findings organized by theme
   - Inline citations [1], [2], etc.
   - Limitations and caveats
   - Recommendations (when applicable)
   - Full numbered reference list with URLs

2. **`research-output/[topic]_[date]_sources.json`** — Machine-readable source log:
   - Every URL fetched, with credibility score
   - Key claims extracted from each source
   - Metadata (search count, fetch count, agent count)

## Customization

### Adjusting search volume

Edit `SKILL.md` and change the targets in the mode table. For example, to make
standard mode more aggressive:

```
| standard   | 30-50    | 50-100  | 4          | 10-20 min  |
```

### Tuning model cost (token optimization)

The parallel worker sub-agents run on **Sonnet** by default, while the orchestrator stays
on your session model. Mechanical retrieval (search → fetch → extract → log) doesn't need a
frontier model, so this tiering is the biggest cost lever and has no impact on research
quality — the quality-critical scoping, triangulation, and synthesis all run in the
orchestrator. Workers also write their full evidence to interim files and return only a
compact summary, which keeps the orchestrator's context (and token use) flat across waves.

To change the worker tier, edit the model-tiering instruction in `SKILL.md` STEP 3:
`haiku` for the cheapest runs (fine for low-risk domains), or `opus` for maximum worker
depth. The orchestrator tier is never lowered.

### Adding domain-specific search patterns

Edit `reference/search-strategy.md` to add patterns for your domain. For example,
for JVM-focused research, you could add:

```
### Pattern: JVM ecosystem
"[topic] JEP"                     → JDK Enhancement Proposals
"[topic] site:openjdk.org"        → OpenJDK official
"[topic] site:inside.java"        → Inside Java blog
"[topic] JMH benchmark"           → microbenchmarks
"[topic] GC tuning"               → garbage collection
```

### Changing output location

Edit the output path in SKILL.md Step 5. Default is `./research-output/` relative
to the project root. You might prefer `./docs/research/` to keep it with other docs.

### Restricting to specific source types

Add to SKILL.md's exclusion criteria in Step 1:
```
- Exclude: marketing content, vendor comparison pages, SEO content farms
- Prefer: engineering blogs, official documentation, peer-reviewed content
```

## Architecture

```
deep-research/
├── skills/deep-research/
│   ├── SKILL.md                       # Main skill (orchestrator)
│   ├── agents/
│   │   └── web-research-agent.md      # Sub-agent template for parallel retrieval
│   ├── reference/
│   │   ├── search-strategy.md         # Query generation patterns
│   │   ├── report-assembly.md         # Report structure, templates, and quality gates
│   │   ├── clarification-questions.md # Domain-specific question sets
│   │   ├── validation-checklist.md    # Report validation criteria
│   │   ├── plan-preview.md           # Research plan display templates
│   │   ├── follow-up.md             # Iterative refinement workflow
│   │   ├── batch-mode.md            # Multi-topic batch research
│   │   └── research-profiles.md     # User-defined research presets
│   └── domains/
│       ├── _registry.md               # Domain routing table (15 domains)
│       ├── health/                    # agent.md + reference.md per domain
│       ├── finance/
│       ├── legal/
│       ├── medical-pharma/
│       └── ... (15 domains total)
├── .claude-plugin/plugin.json         # Plugin manifest
└── README.md
```

## How it compares to commercial deep research services

> Pricing and features last verified March 2026. AI services evolve rapidly —
> check provider websites for current details before making purchasing decisions.

### Services compared

| Service | Provider | Launched |
|---|---|---|
| **This skill** | Open-source plugin for Claude Code | 2025 |
| **[OpenAI Deep Research](https://openai.com/index/introducing-deep-research/)** | OpenAI (ChatGPT) | Feb 2025 |
| **[Gemini Deep Research](https://blog.google/products/gemini/google-gemini-deep-research/)** | Google | Dec 2024 |
| **[Perplexity Deep Research](https://www.perplexity.ai/hub/faq/what-is-deep-research)** | Perplexity AI | Feb 2025 |
| **[Claude.ai Research](https://support.claude.com/en/articles/11088861-using-research-on-claude)** | Anthropic | Mar 2025 |
| **[Grok DeepSearch](https://supergrok.online/)** | xAI | 2025 |
| **[Copilot Deep Research](https://support.microsoft.com/en-us/topic/deep-research-in-microsoft-copilot-d958a5d3-4758-493e-a381-63f0815a97bd)** | Microsoft | Mar 2025 |

### Feature comparison

| Capability | This skill | OpenAI | Gemini | Perplexity | Claude.ai | Grok | MS Copilot |
|---|---|---|---|---|---|---|---|
| Parallel sub-agents | ✅ 2–8 | ✅ | ✅ | ✅ | ✅ | ✅ Heavy | ✅ Researcher |
| Searches per session | 10–100+ | Hundreds | 100+ | Dozens | Dozens | Varies | Not disclosed |
| Typical duration | 2–60 min | 5–30 min | 5–15 min | 2–4 min | Minutes | Varies | 5–10 min |
| Output format | Markdown + JSON | Document viewer | Report + Docs | Report + PDF | In-chat | In-chat | Report |
| Citations | ✅ Numbered | ✅ Inline + sidebar | ✅ Works Cited | ✅ Inline links | ✅ Linked | ✅ | ✅ |
| Structured report with ToC | ✅ | ✅ Navigable | ✅ Auto-generated | ✅ | ❌ | ❌ | ✅ |
| Key takeaways per section | ✅ Bold | ❌ | ❌ | ✅ Bold facts | ❌ | ❌ | ❌ |
| Comparison tables | ✅ Weighted scoring | ✅ | ✅ Feature matrices | ✅ Auto-generated | ❌ | ❌ | ✅ |
| Evidence quality hierarchy | ✅ Pyramid | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Domain-specific report structure | ✅ 15 domains | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Generic |
| Credibility scoring | ✅ Per-source | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Contradiction detection | ✅ | Partial | ❌ | ❌ | ❌ | ❌ | ❌ |
| Machine-readable sources | ✅ JSON | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Reads local files | ✅ | ✅ Uploads | ❌ | ❌ | ❌ | ❌ | ❌ |
| Customizable depth | ✅ 4 modes + profiles | ❌ | ❌ | ❌ | ❌ | 4 modes | 2 modes |
| Editable/forkable | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Research plan preview | ✅ All modes | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Follow-up refinement | ✅ File-based | ✅ Chat | ❌ | ✅ Chat | ✅ Chat | ✅ Chat | ❌ |
| Batch research | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Research profiles | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Interactive charts/visuals | ❌ | ✅ Code execution | ✅ Ultra ($250/mo) | ✅ Timelines | ❌ | ❌ | ✅ Python |
| Export formats | Markdown, JSON | Markdown, Word, PDF | Docs, Sheets, PDF, Audio | PDF, Pages | ❌ | ❌ | Word, Excel |
| Google Docs export | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| M365 integration | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Internal docs search | ❌ | ✅ Connected apps | Google Workspace | ❌ | Google Workspace | ❌ | M365 + connectors |
| Real-time social data | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ X/Twitter | ❌ |
| Runs in terminal | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Deep research API | N/A | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |

### Pricing comparison

| Service | Free tier | Entry plan | Power plan | Deep research limits | API pricing (per M tokens) |
|---|---|---|---|---|---|
| **This skill** | — | Claude Code¹ | — | Unlimited² | Uses your Claude API quota |
| **OpenAI** | 5 lightweight/mo | Plus $20/mo | Pro $200/mo | 5 / 25 / 250 per mo | o3-DR: $10 in, $40 out |
| **Gemini** | ❌ | AI Pro $19.99/mo | AI Ultra (higher) | Soft daily cap | — |
| **Perplexity** | Limited daily | Pro $20/mo | Max $200/mo | ~20/mo (Pro) / unlimited (Max) | Sonar DR: $2 in, $8 out |
| **Claude.ai** | Limited | Pro $20/mo | Max $100–200/mo | Shares regular msg limits | Standard Claude API |
| **Grok** | 10 prompts/2h | SuperGrok $30/mo | Heavy $300/mo | Varies by tier | Grok 4: $3 in, $15 out |
| **MS Copilot** | ❌ | M365 Premium $19.99/mo | Enterprise $30/user/mo | 25 Researcher queries/mo | — |

¹ Claude Code included with Pro ($20/mo), Max ($100–200/mo), or Team ($25–30/user/mo).
² No per-query limit; each run consumes API tokens. A standard-mode session typically costs $2–10 in tokens.

### Strengths and limitations at a glance

**This skill** — Best for developers who want research artifacts alongside code,
machine-readable output, full customization, and no per-query caps. Features
interactive plan preview in all modes, iterative follow-up refinement, batch
research across multiple topics, and reusable research profiles. Tradeoff:
requires Claude Code setup and API key; no GUI; depends on WebSearch availability
(Anthropic first-party API only, not Bedrock/Vertex).

**OpenAI Deep Research** — Deepest single-query analytical depth; document viewer
with navigable ToC and citation sidebar; can execute code and analyze images/PDFs
during research; exports to Markdown, Word, PDF. Now also has plan preview and
connected apps (MCP). Tradeoff: tight query limits on non-Pro plans; $200/mo for
serious usage.

**Google Gemini** — Interactive research plan before execution; native Google Docs
export; visual reports with charts and interactive simulations (Ultra tier, $250/mo);
audio overview (podcast-style summary); Google Workspace integration. Tradeoff:
opaque daily caps; visual features require expensive Ultra tier.

**Perplexity** — Fastest (2–4 min); most accessible free tier; good API.
Tradeoff: limits were cut without notice in 2026 (Pro went from 50 to 20/mo);
less analytical depth than OpenAI or Grok.

**Claude.ai Research** — Seamless if you're already in Claude; can search
connected Google Workspace; massive context window (1M tokens) for analyzing
large documents alongside research. Tradeoff: shares regular message limits
(research burns through them faster); no dedicated research API.

**Grok DeepSearch** — Unique real-time X/Twitter data access; highest benchmark
scores in Heavy mode; free tier for students. Tradeoff: $300/mo for Heavy;
reliability complaints; content moderation controversies.

**Microsoft Copilot** — Best for M365-centric teams; Researcher agent can pull
from Salesforce, ServiceNow, Confluence connectors; Analyst agent runs Python
on your data. Tradeoff: 25 queries/mo cap; full access requires enterprise
licensing; occasional factual errors noted in reviews.

### When to use what

Choose based on your primary need:

| If you need… | Use |
|---|---|
| Research output as project files (Markdown + JSON) | **This skill** |
| Source credibility scoring and contradiction detection | **This skill** |
| Research that reads your local codebase | **This skill** |
| Unlimited runs with no per-query cap | **This skill** |
| Maximum analytical depth on a single hard question | **OpenAI Deep Research** (Pro) |
| Interactive research plan you can edit before execution | **This skill** or **Google Gemini** |
| Iterative follow-up to drill deeper into findings | **This skill** |
| Research multiple related topics with cross-synthesis | **This skill** (batch mode) |
| Reusable research configurations for recurring tasks | **This skill** (profiles) |
| Research exported to Google Docs | **Google Gemini** |
| Fastest results (under 4 minutes) | **Perplexity** |
| Free deep research with no subscription | **Perplexity** (limited) |
| Programmatic deep research via API | **OpenAI** or **Perplexity** API |
| Research over your Google Workspace (Gmail, Docs) | **Claude.ai** or **Gemini** |
| Real-time social media / X data | **Grok** |
| Highest raw benchmark performance | **Grok Heavy** ($300/mo) |
| Research embedded in Word / Excel / M365 | **Microsoft Copilot** |
| Enterprise data connectors (Salesforce, ServiceNow) | **Microsoft Copilot** |
| Research + data analysis with Python execution | **MS Copilot Analyst** or **OpenAI** |
| Full control — edit search patterns, modes, output | **This skill** |

### Cost comparison for 50 research sessions/month

| Service | Plan needed | Monthly cost | Notes |
|---|---|---|---|
| **This skill** | Claude Pro | ~$20 + ~$150–500 API³ | No query cap; cost scales with depth |
| **OpenAI** | Pro | $200 | 250 queries included |
| **Gemini** | AI Pro | $19.99 | Soft daily limits may throttle |
| **Perplexity** | Max | $200 | Unlimited on Max; Pro caps at 20/mo |
| **Claude.ai** | Max 5x | $100 | Burns regular limits; may not reach 50 |
| **Grok** | SuperGrok | $30 | Heavy mode requires $300/mo |
| **MS Copilot** | Enterprise | $30/user/mo | Only 25 Researcher queries; insufficient |

³ API cost estimate assumes standard mode. Worker sub-agents run on Sonnet by default
while the orchestrator keeps your session model, which holds cost down without affecting
quality; running the orchestrator on Opus or using ultradeep mode increases cost
significantly. Quick mode runs are ~$1–3 each.

## Troubleshooting

**"WebSearch tool not available"**
→ You're likely on Bedrock or Vertex. WebSearch requires Anthropic's first-party API.

**Sub-agents not spawning in parallel**
→ Make sure you're on a recent Claude Code version that supports the Task tool.
   Run `claude --version` to check.

**Reports are thin / too few sources**
→ Try a higher mode: `/deep-research in deep mode: ...`
→ Check that WebFetch is actually fetching (some sites block bots).

**Skill not triggering automatically**
→ Use the explicit slash command: `/deep-research <topic>`
→ Or say: "Use the deep-research skill to investigate ..."

## License

MIT — modify freely for your workflow.
