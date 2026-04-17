# Plan Preview Reference

## Purpose

Show the user what will be researched before starting, allowing them to modify the plan.

## Display format by mode

### Quick mode (inline display, NO AskUserQuestion)

Show a compact 2-3 line summary and proceed immediately:

```
Researching: [topic]
Sub-questions: [count] | Domain: [detected] | Mode: quick | Searches: ~10-15
Starting research.
```

Do NOT use AskUserQuestion — quick mode should not add interaction overhead.

### Standard mode (interactive via AskUserQuestion)

Show a compact plan and ask for approval:

```
Research plan for: [topic]
Domain: [detected domain] | Mode: standard | Languages: [search languages]

Sub-questions to investigate:
1. [sub-question 1] (domain: [tag])
2. [sub-question 2] (domain: [tag])
[repeat one numbered line per sub-question]

Planned: [N] sub-agents, ~20-30 searches, up to 3 waves

Proceed? (Press enter to start, or suggest changes)
```

### Deep mode (interactive via AskUserQuestion)

Show detailed plan with query counts per sub-question:

```
Research plan for: [topic]
Domain: [detected domain] | Mode: deep | Languages: [search languages]

Sub-questions to investigate:
1. [sub-question 1] (domain: [tag]) — [N] planned queries
2. [sub-question 2] (domain: [tag]) — [N] planned queries
[repeat one numbered line per sub-question]

Planned: [N] sub-agents, ~40-60 searches, up to 5 waves
Estimated duration: 15-30 minutes

Proceed? (Press enter to start, or suggest changes)
```

### Ultradeep mode (interactive via AskUserQuestion)

Same as deep mode but with additional detail:

- Show planned query samples per sub-question
- Note that ultradeep has no wave cap (saturation-driven)
- Show the estimated duration: 30-60 minutes

## Handling user modifications

When the user suggests changes to the plan:

- **Add sub-question**: Add to the list and tag with appropriate domain
- **Remove sub-question**: Remove and redistribute queries if needed
- **Change focus**: Adjust sub-question priorities and query allocation
- **Change mode**: Switch mode and adjust targets accordingly
- After modifications, show the updated plan and ask again

## Integration with STEP 2

The plan preview happens at the END of STEP 2, after all queries are planned.
The orchestrator should Read this file during STEP 2 to know the display format.
