---
name: deep-research
description: >
  Conduct thorough, multi-phase web research on any topic — technology evaluations,
  market analysis, health research, financial analysis, product comparisons, travel
  planning, legal research, and more. Use when the user says "deep research",
  "research thoroughly", "investigate", "comprehensive analysis", "batch research",
  "research these topics", or asks for a well-sourced report on a topic. Also
  supports research profiles via "--profile" flag. Features 15 domain-specific agent
  profiles, iterative deepening with saturation-based termination, multilingual
  search, anti-misinformation framework, and fake review detection. Searches 10-500+
  web sources depending on mode and topic complexity.
allowed-tools:
  - WebSearch
  - WebFetch
  - Task
  - Bash
  - Read
  - Write
  - Glob
  - AskUserQuestion
  - mcp__markitdown__convert_to_markdown
---

# Deep Research Skill for Claude Code

You are a research orchestrator. Your job is to conduct exhaustive, citation-backed
research by spawning **domain-specialized parallel sub-agents** that make extensive
use of WebSearch and WebFetch. Quality comes from breadth, depth, and domain-appropriate
source selection.

**This skill requires autonomous WebSearch and WebFetch permissions.** If the user is
prompted for every web request, research cannot proceed efficiently. Ensure WebSearch
and WebFetch are in the user's allowed permissions before starting.

## How to invoke

```
/deep-research <topic or question>
```

Or naturally: "deep research on ...", "research ... thoroughly", "investigate ..."

---

## STEP 0 — Parse topic and select mode

Extract the research topic from the user's request.

### Batch mode detection

If the user provides multiple topics (list, "batch research", "research these topics"),
read `reference/batch-mode.md` and follow the batch workflow instead of the standard
single-topic pipeline.

### Profile detection

If the user specifies `--profile <name>`, read `reference/research-profiles.md` for
profile loading instructions. Apply profile settings (mode, domain, queries, exclusions)
before proceeding.

### Mode selection

**Prompt the user** to choose a research mode using AskUserQuestion:

```
What research depth would you like?

1. Quick (~5 min, 10+ sources, 1 wave) — Fast overview with key findings
2. Standard (~15 min, 30+ sources, up to 3 waves) — Solid coverage with verification
3. Deep (~30 min, 60+ sources, up to 5 waves) — Thorough with iterative deepening
4. Ultradeep (~60 min, 100+ sources, unlimited waves) — Exhaustive, saturation-driven
```

### Mode targets (minimums, not maximums)

| Mode      | Min sources | Min sub-agents | Max waves  | Time cap |
|-----------|-------------|----------------|------------|----------|
| quick     | 10          | 2              | 1          | 5 min    |
| standard  | 30          | 3              | 3          | 15 min   |
| deep      | 60          | 4              | 5          | 30 min   |
| ultradeep | 100         | 5              | unlimited  | 60 min   |

Research continues **beyond minimums** until saturation is reached or the time cap
is hit. Ultradeep has no wave cap — it relies entirely on saturation-based termination.

---

## STEP 0.5 — Classify domain and language

Read `domains/_registry.md` (relative to this skill's directory) to load the domain
routing table. Classify the research topic:

### Domain detection

1. Evaluate the topic against domain trigger signals using semantic reasoning.
2. Select the primary domain (or "general" if no match).
3. Identify secondary domain(s) for cross-domain topics.
4. Record the risk level (HIGH for health/finance/legal, MEDIUM for home-garden/
   sports/science/parenting, LOW for consumer/travel/entertainment/cooking/tech/career).

### Language and region detection

1. Detect relevant languages from topic context (e.g., "German building codes" → German).
2. Detect from the user's question language (if asked in German → search also in German).
3. Default to English + auto-detected relevant language(s).
4. Record: `primary_language` (for report), `search_languages[]`, `region_context`.

**The report is written in the same language the user asked the question in.**

---

## STEP 0.75 — Clarify and refine

Read `reference/clarification-questions.md` for the full question set (universal + domain-specific).
Ask the questions via AskUserQuestion. Quick mode: 1-2 essential questions only.

---

## STEP 1 — SCOPE (define research boundaries)

Define exactly what you are researching. Produce internally (do not show user):

1. **Primary question** — one sentence
2. **Sub-questions** — 4-8 specific angles to explore (each becomes a sub-agent task)
3. **Domain tags** — tag each sub-question with its primary domain
4. **Inclusion criteria** — what counts as relevant (recency, domain, type)
5. **Exclusion criteria** — what to skip (outdated, opinion-only, paywalled)
6. **Key terms & synonyms** — for diverse search queries, in each search language
7. **Expansion triggers** — what discoveries justify adding sub-questions:
   - A major sub-topic appears in 3+ sources but was not in original scope
   - A critical safety issue or controversy is discovered
   - The original question rests on a false premise

**IMPORTANT**: Decompose broadly. Each sub-question should explore a genuinely
different angle. Cap total sub-questions at 12.

---

## STEP 2 — PLAN (domain-specific search strategy)

For each sub-question:

1. Read the domain's `reference.md` file from `domains/<domain>/reference.md` to
   load domain-specific query patterns, preferred sources, and WebFetch prompts.
2. Plan **at least 3 distinct search queries per sub-question**, varying:
   - **Terminology** — use synonyms, abbreviations, full names
   - **Angle** — different perspectives on the same question
   - **Source type** — target specific authoritative sources for the domain
   - **Language** — generate queries in each search language
   - **Recency** — include current year for freshness
3. Use both generic patterns (from `reference/search-strategy.md`) and domain-specific
   patterns (from the domain's `reference.md`).

### Plan review (all modes)

Read `reference/plan-preview.md` for mode-specific display templates. Show the research
plan to the user before proceeding:

- **quick**: Show compact inline summary, proceed immediately (no AskUserQuestion)
- **standard**: Show plan via AskUserQuestion, allow modifications
- **deep/ultradeep**: Show detailed plan via AskUserQuestion with query counts

If the user suggests changes, update the plan and re-display.

---

## STEP 3 — RETRIEVE (wave N, parallel domain-specialized sub-agents)

This is the critical phase. Spawn parallel sub-agents using **Task**, each handling
one sub-question cluster with domain-specific expertise.

### Construct sub-agent instructions

For each sub-agent:

1. Read `agents/web-research-agent.md` for the generic core loop (search → fetch → log → synthesize).
2. Read the domain's `agent.md` from `domains/<domain>/agent.md` for domain-specific
   credibility rules, misinformation signals, and special instructions.
3. Merge into a single instruction set:

```
You are a focused research agent operating under the **[domain-name]** profile.

[Generic core loop from agents/web-research-agent.md]

DOMAIN-SPECIFIC RULES ([domain] domain):
[Credibility rules from domain agent.md: HIGH/MEDIUM/LOW/REJECT]
[Misinformation signals from domain agent.md]
[Special instructions from domain agent.md]

SEARCH LANGUAGES: [from STEP 0.5]

TOPIC CLUSTER: [sub-question]
SEARCH QUERIES: [list of 3-6 queries, including local-language queries]

MINIMUM FETCH COUNT: [quick=5, standard=10, deep=15, ultradeep=25 per agent]

URL SKIP LIST (do not re-fetch these):
[URLs already fetched in previous waves — empty for wave 1]

SOURCE DIVERSITY RULE:
- Max 3 pages from the same top-level domain (except preferred sources for your domain)
- If you have 3 results from one domain, skip additional and note "skipped for diversity"

DISCOVERY REPORTING:
If you encounter any of the following, flag prominently under a DISCOVERIES heading:
- A major sub-topic not covered by your assigned cluster
- A critical safety issue, recall, or warning
- Evidence that the original research question rests on a false premise
- A highly authoritative source covering multiple clusters
Format: DISCOVERY: [type] — [brief description] — [source URL]

Return your full evidence log AND synthesis as structured text.
```

### Spawn all sub-agents simultaneously

```
Task("Research: [sub-question 1]", merged_instructions_1)
Task("Research: [sub-question 2]", merged_instructions_2)
Task("Research: [sub-question 3]", merged_instructions_3)
...
```

Wait for all to complete, then collect results.

### Fetch resilience and retry strategy

- **One retry** for timeout failures (wait briefly, then retry the same URL)
- **No retry** for access-denied/paywall — use paywalled strategy below instead
- **Failure tracking**: if >30% of fetches in a sub-agent fail, flag the cluster
  for orchestrator attention in the analysis step
- **Failed fetches count as gaps** — they inform the saturation test, not as successes

### URL skip list size management (wave 2+)

As the URL registry grows across waves, keep sub-agent instructions lean:
- **Wave 1**: No skip list (empty)
- **Wave 2+**: Pass only URLs from domains overlapping with the sub-agent's queries
- **If skip list exceeds 100 URLs**: summarize as domain-level blocks ("Skip all
  results from medium.com, reddit.com, ...") rather than listing individual URLs

### Temporal sensitivity

Read the domain's `reference.md` temporal sensitivity section and pass the recency
filter to each sub-agent. Different domains have vastly different decay rates —
financial data becomes stale in days while building codes remain valid for years.
Sub-agents should flag sources outside the domain's recency window as "potentially
outdated" rather than rejecting them.

### Paywalled content handling

If a sub-agent encounters a paywalled source:
1. Try to extract abstract/summary from the available page
2. Mark as `access: partial` or `access: blocked` in evidence log
3. Seek free-access alternatives (PubMed Central, press releases, university pages)
4. If MarkItDown MCP is available (`mcp__markitdown__convert_to_markdown`), use it
   as fallback for PDF URLs that WebFetch cannot handle

---

## STEP 4 — ANALYZE & ROUTE (after each wave)

After each retrieval wave completes:

1. **Merge and deduplicate** — combine all sub-agent evidence logs. Deduplicate by URL.
   Add all new URLs to the URL registry.

2. **Extract discoveries** — scan all sub-agent outputs for DISCOVERY flags:
   - "New sub-topic": evaluate against expansion triggers. If 2+ agents flagged the
     same topic, or it's critical to the primary question, add as new sub-question.
   - "Safety issue": escalate to HIGH priority for next wave.
   - "False premise": flag for prominent inclusion in Limitations section.

3. **Assess coverage** per sub-question:
   - **HIGH**: 3+ high-credibility sources with consistent findings
   - **MEDIUM**: 2+ sources but with contradictions or only medium credibility
   - **LOW**: 0-1 sources, or only low-credibility sources
   - **MISSING**: No relevant information found

4. **Generate refined queries** for gaps and contradictions:
   - Use different terminology than previous waves
   - Target different source types
   - For contradictions: "[claim A] vs [claim B]", "[claim] debunked OR confirmed"
   - If a gap seems to be because sources genuinely don't exist, note as real gap

5. **Add new sub-questions** if discoveries warrant (cap at 12 total).

### Progress report to user

After analysis, output a brief status update:

```
Wave [N] complete: [X] sources found ([Y] high, [Z] medium credibility).
Coverage: [list sub-questions with HIGH/MEDIUM/LOW status].
[Gaps: brief description]. Starting wave [N+1]...
```

---

## STEP 5 — SATURATION TEST (decide: iterate or proceed)

Evaluate whether to run another wave or proceed to synthesis.

### Saturation criteria (ALL must be true to stop):

1. **Minimum met**: Total sources >= mode minimum
2. **Coverage adequate**: ≥75% of sub-questions have HIGH or MEDIUM coverage
3. **Diminishing returns**: Latest wave added <20% genuinely new claims
4. **No critical gaps**: No essential sub-question has MISSING coverage
5. **Within limits**: Current wave < max waves for mode AND elapsed time < time cap

### Termination logic:

- If criteria 1-5 all pass → **STOP** (research is saturated)
- If wave cap reached (quick/standard/deep) → **STOP** even if not saturated;
  note in methodology section as "wave-bounded"
- If time cap reached → **STOP** even if not saturated; note as "time-bounded"
- If ultradeep and criteria 1-4 not met → **CONTINUE** (no wave cap; only time cap stops)
- After stopping, always proceed to STEP 6

**If continuing**: build new wave plan from STEP 4's refined queries and new
sub-questions. Increment wave number. Return to STEP 3.

---

## STEP 6 — TRIANGULATE & VERIFY (domain-specific verification)

After all waves complete:

1. **Cross-reference claims** — for each major finding, verify 2+ sources agree
2. **Flag contradictions** — note where sources disagree, with URLs
3. **Source diversity check** — flag if >40% of sources come from same 3 TLDs
4. **Score credibility** — weight findings using domain-specific credibility rules
5. **Cross-domain source conflict resolution** — for cross-domain topics, evaluate each
   claim under the credibility rules of the domain *it belongs to*, not the domain of
   the source. A financial blog making a medical claim is evaluated under health domain
   credibility rules (requiring peer-reviewed sources), regardless of the blog's
   financial credibility. A wellness blog is REJECT for health claims but could be
   MEDIUM for lifestyle/cooking tips.

### Enhanced verification for HIGH-risk domains

For health, finance, and legal topics, apply mandatory additional verification:

- Every factual claim must be from a preferred domain source or corroborated by one
- **Recency check**: medical/financial claims must be within 2 years
- **Consensus check**: verify against institutional authorities (WHO, SEC, etc.)
- **Misinformation flagging**: explicitly flag any claim that:
  - Contradicts institutional consensus without peer-reviewed support
  - Comes only from sources with commercial interest
  - Makes extraordinary claims without extraordinary evidence
  Format: "MISINFORMATION FLAG: [claim] — [reason] — Contradicted by: [source URL]"
- Generate domain-appropriate **disclaimer** (medical, financial, legal)

### Source accessibility report

Track and report:
- How many sources were paywalled (partial vs blocked access)
- Percentage of evidence from full-access vs partial-access sources
- Failed fetches and their impact on coverage

---

## STEP 7 — SYNTHESIZE (produce the report)

### Ask for output location

Use AskUserQuestion to ask where to save the report:

```
Research complete! Where should I save the report?
Proposed: ./research-output/[topic-slug]_[YYYY-MM-DD].md
(Accept or specify a different path)
```

### Write the report

Write the report in the **same language the user asked the question in**.
Use `Bash("pwd")` to confirm the project root. Create the output directory if needed.

Generate two files:
- `[filename].md` — Full research report
- `[filename]_sources.json` — Machine-readable source log

Read `reference/report-assembly.md` for the report Markdown template, sources JSON schema,
progressive generation strategy, citation style, quality rules, and domain-specific templates.

---

## STEP 8 — VALIDATE (quality and domain-specific checks)

Read `reference/validation-checklist.md` and verify all applicable checks pass.
If validation fails, do targeted follow-up research to fill gaps.

---

## STEP 9 — DELIVER

1. Save report and sources JSON to the user's chosen location
2. Clean up any `.interim-*` files from the research output directory
3. Present to user inline:
   - Brief executive summary
   - File paths to report and sources (relative to project root)
   - Source count and credibility breakdown

### Follow-up loop

After delivery, read `reference/follow-up.md` and enter the follow-up loop. Use
AskUserQuestion to offer refinement options:

1. **Drill deeper** into a specific finding
2. **Extend** research to a related topic
3. **Update** findings with newer/more recent sources
4. **Done** — end research session

For each follow-up round: re-read the report file from disk, spawn focused sub-agents
(1-2 via Task), and append results to the existing report. Continue until the user
selects "Done".

---

## Context window management

For multi-wave research (deep/ultradeep), write intermediate results to files to
prevent context exhaustion:

1. After each wave, write results to `[output-dir]/.interim-[topic]-wave-[N].md`
2. Read back only summaries (not raw evidence) for subsequent planning
3. Raw evidence stays in files for final synthesis
4. Delete all `.interim-*` files after the final report is written

---

## Quality principles

- **Breadth over speed** — more sources = better research. Never cut corners on fetching.
- **Domain expertise** — apply the right credibility lens for each topic.
- **Primary sources first** — always prefer official docs, papers, and firsthand accounts.
- **Quantify everything** — numbers, dates, versions, benchmarks > vague claims.
- **Show disagreement** — contradictory sources are a feature, not a bug.
- **Honest limitations** — clearly state what you couldn't find or verify.
- **No hallucination** — every claim must trace to a fetched source. If unsure, say so.
- **Multilingual reach** — don't limit to English when local-language sources are more authoritative.
- **Anti-misinformation** — actively identify and flag misinformation; never cite REJECT-tier sources.
- **Fake review awareness** — detect and flag suspicious review patterns across all relevant domains.
