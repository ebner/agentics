# Follow-up Refinement Reference

## Purpose

After delivering a research report, offer the user options to iterate on the findings
without starting a full new research session. This keeps follow-up rounds fast and
focused by reusing existing context.

## Follow-up prompt

After STEP 9 delivery, use AskUserQuestion:

```
Research delivered. You can:
1. Drill deeper into a specific finding
2. Extend research to a related topic
3. Update findings with newer/more recent sources
4. Done (end research session)

What would you like to explore further?
```

## Option 1: Drill deeper

The user wants more detail on a specific finding or section of the report.

Workflow:
1. Ask the user which finding/section to drill into
2. Re-read the existing report file and sources JSON from disk
3. Identify the relevant sub-question(s) and existing sources
4. Spawn 1-2 focused sub-agents via Task. When spawning more than one, use one Task call per sub-agent and place all Task calls in the same assistant message so they run in parallel. Each sub-agent receives:
   - The specific finding as the research focus
   - Existing sources as context (avoid re-fetching)
   - Narrower, more specific queries targeting depth
5. Append results as a new "## Follow-up: [topic]" section in the existing report
6. Update the sources JSON with any new sources
7. Return to the follow-up prompt

## Option 2: Extend research

The user wants to explore a related but new angle not covered in the report.

Workflow:
1. Ask the user what related topic to explore
2. Re-read the existing report to understand context
3. Create 1-3 new sub-questions for the extension topic
4. Spawn sub-agents via Task — one Task call per sub-question, all Task calls in the same assistant message. Each sub-agent receives:
   - The new sub-questions
   - The URL skip list from the existing sources JSON (avoid re-fetching)
   - The same domain profile as the original research
5. Append results as a new "## Extension: [topic]" section in the existing report
6. Update the sources JSON with new sources
7. Return to the follow-up prompt

## Option 3: Update findings

The user wants to refresh specific sections with more recent or additional sources.
Two modes are supported depending on whether the report is from the current or a
previous session.

### Within-session update

Re-search specific sections with tighter recency filters.

Workflow:
1. Ask the user which section(s) to update and any recency preference
   (e.g., "last 30 days only", "2025+ sources only")
2. Re-read the existing report and sources JSON
3. Spawn 1-2 sub-agents via Task. When spawning both, use one Task call per sub-agent and place both Task calls in the same assistant message. Each sub-agent receives:
   - Queries from the original sub-questions, modified with date filters
   - Instruction to find sources newer than those in the existing report
4. Merge new findings into the existing section (don't replace -- add)
5. Add a note: "Updated [date]: added [N] newer sources"
6. Update the sources JSON
7. Return to the follow-up prompt

### Cross-session update

User references an existing report file from a previous session.

Workflow:
1. Read the referenced report file and its sources JSON
2. Identify the original research date and key findings
3. Spawn sub-agents with queries targeting "what changed since [original date]"
4. Produce either:
   - An addendum section appended to the original report, OR
   - A new "update report" alongside the original
5. Update the sources JSON with new sources
6. Return to the follow-up prompt

## Option 4: Done

End the research session. No further action needed.

## Appended-section quality

Every `## Follow-up:`, `## Extension:`, and update section follows the writing rules in
`report-assembly.md` — prose, inline citations, no padding, readable over terse. Two rules are
specific to appended sections:

- **Add findings, not bulk.** A follow-up section covers what the new sub-agents actually found. Do
  not re-summarize the section it drills into, restate the executive summary, or recap the original
  research; the reader already has the report open. If a round returns little, the section is short
  and says what was not found.
- **Keep the counts honest.** The "Updated [date]: added [N] newer sources" note and any revised
  Methodology totals are counted from the updated sources JSON, not estimated from the round.

## Context management

- Always re-read the report file from disk for each follow-up round (don't rely on
  context memory)
- Follow-up sub-agents get their own context via Task -- keeps the orchestrator lean
- **Spawn every follow-up sub-agent with `model: "sonnet"`** (same worker tiering as
  STEP 3 — workers retrieve, the orchestrator keeps its session model)
- Follow-up sub-agents follow the same output contract as STEP 3: write the full evidence
  log to `./research-output/.interim-[topic-slug]/followup-[K].md` and return only a
  compact Source Index + Cluster Synthesis. Delete these files when the round is appended.
- Each follow-up round should be focused and narrow (1-2 sub-agents max)
- After 3+ follow-up rounds, suggest starting a new session if the topic has shifted
  significantly
