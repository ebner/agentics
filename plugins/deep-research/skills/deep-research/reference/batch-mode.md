# Batch Research Mode

## Purpose
Research multiple related topics in a single session, producing individual reports
per topic plus a cross-topic synthesis.

## Detection
Batch mode is triggered when:
- User provides a list of topics (numbered, bulleted, or comma-separated)
- User says "batch research", "research these topics", "compare research on..."
- User provides multiple topics in a single `/deep-research` invocation

## Workflow

### 1. Parse topics
Extract individual topics from the user's input. Present the list back to the user
for confirmation via AskUserQuestion:
```
I detected [N] topics for batch research:
1. [topic 1]
2. [topic 2]
[repeat one numbered line per detected topic]

Mode for each: [auto-detect or user-specified]
Proceed? (Confirm, modify topics, or suggest changes)
```

### 2. Run each topic sequentially
For each topic, run the full single-topic pipeline (STEP 0.5 through STEP 9):
- Each topic gets its own domain classification, sub-questions, and sub-agents
- Each topic produces its own report file and sources JSON
- Maintain a **global URL registry** across topics for deduplication
- Between topics, output a brief status: "Topic [N]/[total] complete: [topic]. Starting topic [N+1]."

### 3. Global URL registry
Track all URLs fetched across all topics. When starting a new topic:
- Pass already-fetched URLs into the URL skip list for sub-agents
- If the same URL is relevant to multiple topics, note the cross-reference but don't re-fetch
- This saves time and tokens while ensuring consistent findings

### 4. Cross-topic synthesis
After all individual topics are complete:
1. Read back all individual report files
2. Produce a `batch-synthesis_[date].md` in the same output directory containing:

```markdown
# Batch Research Synthesis

> **Topics**: [N] | **Total sources**: [sum] | **Date**: [YYYY-MM-DD]

## Topics Researched
1. [topic 1] — [report path]
2. [topic 2] — [report path]
[repeat one numbered line per researched topic]

## Cross-cutting Themes
[Themes that appear across multiple topics, with references to specific reports]

## Shared Sources
[Sources cited in 2+ reports, indicating authoritative cross-topic references]

## Contradictions Between Topics
[Findings that contradict each other across topics, with analysis]

## Comparative Summary
[Side-by-side comparison of key findings per topic]

## Recommendations
[Holistic recommendations informed by the full set of research]
```

### 5. Delivery
Present to the user:
- Path to each individual report
- Path to the synthesis report
- Total source count across all topics
- Key cross-cutting themes (1-2 sentences)
- Offer the standard follow-up prompt for the batch as a whole

## No artificial caps
There is no limit on the number of topics — the user decides scope. Each topic runs
through its own sub-agents (via Task), so context is managed per-topic.

## Mode handling
- If no mode is specified, use the same mode for all topics
- Users can specify different modes per topic: "quick: topic A, deep: topic B"
- Default to standard mode if unspecified
