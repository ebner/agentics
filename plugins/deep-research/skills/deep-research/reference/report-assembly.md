# Report Assembly Reference

## Report structure template

```markdown
# [Research Title]

> **Mode**: [mode] | **Sources**: [count] | **Date**: [YYYY-MM-DD]
> **Domain**: [detected domain] | **Languages**: [search languages]
> **Research question**: [primary question]

[DOMAIN DISCLAIMER if HIGH-risk domain — medical, financial, or legal]

## Executive Summary
[Scales with report: ~10% of total length, max 1,500 words. Must be readable
as a standalone document — a reader who only reads this section should understand
the key findings, main conclusion, and primary recommendation. Include the
single most important number or data point from the research.]

## Table of Contents

## 1. [First major theme/finding]
**Key takeaway: [1-2 sentence bold summary of this section's main finding.]**

[Detailed analysis with inline citations numbered [1], [2], [3], continuing sequentially up to [N], matching the References list order]
[Include specific data points, numbers, comparisons]
[Write in prose (≥80%), not bullet lists]

## 2. [Second major theme/finding]
[repeat one `## N. [theme/finding]` section per major theme, using the same
sub-structure as section 1: bold key takeaway, prose analysis with inline
citations, specific data points]

## N. Synthesis & Cross-cutting Insights
[What emerges from looking across all findings together?]

## Misinformation Flags & Caveats
[For HIGH-risk domains: claims flagged during research with reasons and
contradicting authoritative sources. For all domains: notable misinformation
encountered and rejected.]

## Limitations & Caveats
- [What this research did NOT cover]
- [Where sources were thin or contradictory]
- [Potential biases in available sources]
- [Paywalled sources that limited access]

## Recommendations
[Numbered, prioritized, actionable. Each recommendation should include:]
1. **[Action]** (Priority: high/medium/low | Effort: low/medium/high)
   [Why this is recommended, based on which findings. Timeline if applicable.]

## Methodology
- Research mode: [mode]
- Domain profile: [domain]
- Search languages: [languages]
- Waves completed: [N] (terminated by: [saturation/wave-cap/time-cap])
- Total searches conducted: [N]
- Total pages fetched and analyzed: [N]
- Sub-agents deployed: [N]
- Sources by credibility: [N high, N medium, N low]
- Sources by access: [N full, N partial, N blocked]
- Unique domains: [N]

## References
[1] Title — URL (credibility: high/medium/low, access: full/partial)
[2] Title — URL (credibility: high/medium/low, access: full/partial)
[repeat one `[N] Title — URL (...)` line per cited source]
```

Every `[N]` in the Methodology block is a counted value, not an estimate: read the source, fetch,
domain, and credibility totals from the deduplicated URL registry and the interim evidence files;
read the wave count and termination reason from the saturation test that ended the run. If a number
cannot be derived from a recorded artifact, write `not tracked` rather than a plausible figure.

## Sources JSON structure

```json
{
  "meta": {
    "topic": "<topic string>",
    "mode": "<mode name>",
    "domain_detected": "<domain id>",
    "risk_level": "<LOW | MEDIUM | HIGH>",
    "search_languages": ["en", "de"],
    "date": "<YYYY-MM-DD>",
    "waves_completed": 3,
    "termination_reason": "saturation",
    "total_searches": 47,
    "total_fetches": 83,
    "total_sources_cited": 42,
    "unique_domains": 24,
    "misinformation_flags": 2,
    "paywalled_sources": 5
  },
  "sources": [
    {
      "id": 1,
      "url": "<full URL>",
      "title": "<page title>",
      "language": "en",
      "credibility": "high",
      "access": "full",
      "accessed": "<YYYY-MM-DD>",
      "key_claims": ["<short claim sentence>"]
    }
  ]
}
```

Replace each `<...>` placeholder with the actual value when writing the file;
repeat the `sources` object once per cited source, incrementing `id`.

---

## Progressive generation strategy

For long reports (deep/ultradeep), generate section by section to avoid
context window exhaustion.

### Section generation order

1. Main body sections (one per major theme) — write first
2. Cross-cutting insights
3. Misinformation Flags & Caveats (if HIGH-risk domain)
4. Limitations & Caveats
5. Recommendations
6. Methodology
7. References
8. Executive Summary (write LAST based on complete content, but position FIRST)
9. Table of Contents (auto-generate from headers)

### Per-section quality gates

Before writing each section, verify:
- [ ] At least 3 unique sources support the section's claims
- [ ] Specific data points are included (numbers, dates, versions)
- [ ] Both supporting and contradicting evidence is represented
- [ ] Section flows logically from the previous one

### Citation style

Use numeric inline citations: [1], [2], [3]

Map to the References section at the bottom:
```
[1] "Page Title" — https://example.com (credibility: high, access: full)
```

For claims supported by multiple sources: [1][3][7]

Sources in non-English languages: preserve the original title, note the language:
```
[15] "<original-language title>" — <source URL> (credibility: high, language: de)
```

### Writing quality rules

- **Prose first** — write in paragraphs, not bullet lists (≥ 80% prose)
- **Key takeaway per section** — every major body section opens with a 1-2 sentence **bold** key takeaway before the detailed prose. This lets readers scan the report quickly.
- **Lead with findings** — don't bury the insight under methodology
- **Quantify** — "3x faster" not "significantly faster"
- **Attribute** — "According to the official benchmarks [3]" not just "[3]"
- **Compare** — whenever possible, contextualize with alternatives
- **Acknowledge uncertainty** — "reportedly", "according to", "as of [date]"
- **Match language** — write in the same language the user asked the question in
- **Cross-references** — for reports with 8+ sections, cross-reference related sections (e.g., "See Section 3 for detailed risk analysis") to help readers navigate
- **No padding** — every section earns its place with researched content. Do not add a section that
  restates another, a summary of a summary, a "further considerations" section holding no findings,
  or process narration outside Methodology. If a planned section has fewer than 3 supporting sources
  (the per-section quality gate above), fold it into a related section or move the gap to Limitations
  — do not write it thin to hit a structure count.
- **Length comes from evidence** — the mode's word target is a budget for findings, not a quota to
  fill. A well-sourced topic fills it; a thin one produces a shorter report and a fuller Limitations
  section. Never stretch prose, restate a citation's content twice, or expand a caveat into a
  section to reach the range.
- **Readable over terse** — brevity comes from omitting detail that does not change what the reader
  does next, never from compressing prose into fragments, invented abbreviations, or arrow chains.
  Spell out the terms a reader who skipped the research would not know.

### Comparison table standards

When comparing alternatives (products, strategies, investments, technologies, etc.),
always produce a structured Markdown comparison table:

- **Define columns explicitly** — features, limitations (always include this), pricing,
  rating/score, source count. The "limitations" column is critical — readers need to see
  downsides, not just features.
- **Consistent rating format** — use a consistent scale (e.g., 1-10, or ✅/⚠️/❌)
- **Source count per claim** — note how many sources support each major claim in the table
- **Sorted by recommendation** — best option first, with clear indication of the basis

Example format:
```
| Criterion | Option A | Option B | Option C |
|---|---|---|---|
| [Feature 1] | ✅ Strong [1][3] | ⚠️ Partial [5] | ❌ Missing |
| [repeat one row per evaluated feature, with a status + citation per option] | | | |
| **Limitations** | [key limitation] | [key limitation] | [key limitation] |
| **Overall score** | 8.5/10 | 7.2/10 | 6.1/10 |
```

### Timeline and chronological formatting

When findings have a temporal dimension (regulatory changes, market evolution,
disease progression, technology roadmap, historical events), present them in
chronological format:

- Use a timeline table: `| Date | Event | Impact | Source |`
- Most recent events first (reverse chronological) unless the narrative requires
  forward chronological for comprehension
- Always include dates, not just relative time references

### Report length targets by mode

| Mode      | Target words | Sections |
|-----------|-------------|----------|
| quick     | 1,500-3,000 | 4-6      |
| standard  | 3,000-6,000 | 6-8      |
| deep      | 6,000-12,000| 8-12     |
| ultradeep | 12,000+     | 12-20    |

These are budgets for researched content, not quotas. Coming in under the range with a well-sourced
report and an honest Limitations section is correct; padding to reach the range is not. See the
"No padding" and "Length comes from evidence" rules above.

### Auto-continuation for ultradeep

If the report exceeds ~15,000 words, use file-based assembly:

1. Write sections 1-5 to the output file
2. Append sections 6-10
3. Continue until all sections are written
4. Generate executive summary based on complete content
5. Prepend executive summary + ToC

This avoids context window limits while maintaining coherence.

---

## Domain-specific report templates

When a domain agent profile is active, use the domain's report structure instead
of the generic structure. Domain-specific additions:

### HIGH-risk domains (health, finance, legal)

**Required additional sections:**
- Domain-appropriate disclaimer (immediately after metadata, before executive summary)
- Misinformation Flags & Caveats section (even if empty)
- Domain-specific validation (see STEP 8 in SKILL.md)

**Disclaimer templates:**

Medical:
```
> **DISCLAIMER**: This report summarizes published research and is NOT medical
> advice. Consult a qualified healthcare professional for medical decisions.
```

Financial:
```
> **DISCLAIMER**: This report is for informational purposes only and does NOT
> constitute financial advice. Past performance does not guarantee future results.
> Consult a qualified financial advisor for investment decisions.
```

Legal:
```
> **DISCLAIMER**: This report summarizes legal information and is NOT legal advice.
> Laws vary by jurisdiction and change over time. Consult a qualified attorney
> for legal decisions.
```

### Consumer/product domain

Use the specialized product report structure from `domains/consumer/agent.md`:
- Evaluation Criteria matrix (dimensions, weights, scoring) up front
- Top Recommendations (Best Overall / Best Value / Best for Use Case)
- Comparison Table, Independent Test Results, User Review Analysis
- Price & Value Analysis with TCO, Where to Buy, Warranty & Return Policies
- Longevity Assessment (repairability, software support, planned obsolescence)
- Review Integrity Assessment, Alternatives & Honorable Mentions

**Product comparison writing guidelines:**
- Always lead with the criteria used to evaluate, so the reader understands the basis
- Include a structured comparison table with all candidates scored on the same dimensions
- Distinguish between "best for most people" and "best for specific use case"
- Note if any top pick has known reliability issues or recalls

### Travel domain

When the research goal is vacation planning (detected from clarification answers),
use the full vacation plan structure from `domains/travel/agent.md`. The report should
be an actionable travel plan, not just a research summary.

**Required sections for vacation plans:**

1. **Quick Reference Card** — single-page summary with: destination, travel dates,
   flight info, hotel name/address, emergency numbers, currency, key phrases,
   weather forecast. This should be printable/screenshot-friendly.
2. **Entry Requirements & Safety** — visa, health, advisories
3. **Getting There & Around** — transport with specific recommendations
4. **Accommodation** — specific recommendations by budget tier with booking links
5. **Day-by-Day Itinerary** — the core of the vacation plan:
   - One section per day with morning/afternoon/evening activities
   - Include travel times between locations
   - Include meal suggestions (breakfast/lunch/dinner) with restaurant names,
     cuisine type, price level, and whether reservations are needed
   - Note what needs advance booking vs. walk-in
   - Include bad-weather alternatives where relevant
6. **Food & Dining Guide** — local cuisine overview, must-try dishes,
   restaurant recommendations (fine dining, local favorites, street food, markets),
   dietary accommodation options, food safety, tipping customs
7. **Budget Breakdown** — daily estimates by tier with category breakdown
8. **Booking Checklist** — timeline of what to book when (flights → hotel →
   specific activities → restaurant reservations), with links where available
9. **Practical Tips** — packing, connectivity, currency, language basics

**Itinerary writing guidelines:**
- Be specific: "Walk 15 min from hotel to Mercado de San Miguel" not "Visit a market"
- Include opening hours and prices where researched
- Balance structured activities with free time
- Account for jet lag on Day 1 (lighter schedule)
- Group geographically close activities together to minimize transit
- Note which activities are weather-dependent

### Entertainment domain

Use the entertainment report structure from `domains/entertainment/agent.md`:
- Overview, Key Facts (dates, venues, pricing), Critical Reception
- Ticket/Access Information, Seating & Section Guide
- Dining & Nearby Options, Group Planning logistics
- Practical Details (transport, parking, accessibility), Scam Alerts
- Alternatives & Related content, Sold-Out options

### Home & garden domain

Use the project report structure from `domains/home-garden/agent.md`:
- Project Overview, Permit & Code Requirements
- DIY vs Professional Assessment with clear recommendation
- Materials List with Costs (itemized, dated, regional)
- Tools Needed, Step-by-Step Approach, Timeline Estimate
- Common Mistakes to Avoid, Safety Warnings
- Contractor Selection Guidance, Budget Summary

**Project report writing guidelines:**
- Always check whether a permit is required before suggesting DIY
- Include safety warnings prominently, not buried in prose
- Cost estimates must include date and region qualifier
- Distinguish between code-required work and cosmetic/optional improvements

### Science & education domain

Use the research report structure from `domains/science-education/agent.md`:
- Background & Context, Literature Review (organized by evidence tier)
- Methodology Analysis, Key Findings Synthesis
- Consensus vs. Active Research, Open Questions & Research Frontiers
- Practical Implications, Pseudoscience & Misinformation Flags
- Educational Resources (textbooks, courses, primary papers)

**Scientific writing guidelines:**
- Organize evidence by quality tier (systematic reviews first)
- Clearly label preprints and distinguish from peer-reviewed work
- Flag predatory journals explicitly
- Note replication status of key findings

### Sports & fitness domain

Use the dual-track structure from `domains/sports/agent.md`:

**Training topics:** Program Overview, Evidence Base, Progression Plan,
Technique Guide, Safety & Injury Prevention, Equipment, Recovery Protocols,
Nutrition, Adaptation by Level, Sample Program

**Spectator topics:** Overview, Current Standings, Historical Context,
Statistical Analysis, Key Players, Predictions, Viewing Guide

### Career & employment domain

Use the career report structure from `domains/career-employment/agent.md`:
- Role Description, Market Overview, Compensation Analysis
- Demand Trends, Company Analysis, Skills & Requirements
- Career Path, Regional Context, Remote Work Landscape
- Interview Preparation, Networking & Professional Development
- Practical Recommendations

### Cooking domain

Use the culinary report structure from `domains/cooking/agent.md`:
- Overview, Recipe/Technique with step-by-step instructions
- Food Science, Ingredients, Equipment
- Food Safety, Allergen Information, Dietary Adaptations
- Troubleshooting & Common Mistakes, Scaling Guidance
- Storage & Make-Ahead Tips

### Parenting & pets domain

Use the dual-track structure from `domains/parenting-pets/agent.md`:

**Parenting topics:** Developmental Context, Evidence-Based Approaches,
Practical Guidance, Safety, Product Recommendations, When to Consult
a Professional, Support Resources

**Pet care topics:** Species & Breed Context, Evidence-Based Care,
Practical Guidance, Training & Behavior, Health & Nutrition, Safety,
When to See a Vet, Resources

### General domain (fallback)

Use the generic structure from `domains/general/agent.md`:
- Overview, Key Findings, Multiple Perspectives
- Evidence Assessment, Context & Background
- Limitations, Practical Implications

---

## Interim file management

During multi-wave research, interim files are created:

```
[output-dir]/.interim-[topic-slug]-wave-1.md
[output-dir]/.interim-[topic-slug]-wave-2.md
[one `.interim-[topic-slug]-wave-N.md` file per completed wave]
```

After the final report is written:
1. Delete ALL `.interim-*` files from the output directory
2. Keep only the final report `.md` and sources `.json`

---

## Source accessibility reporting

Track in the Methodology section:
- Total sources attempted to fetch
- Full access: [N] sources with complete content
- Partial access: [N] paywalled sources where abstract/summary was extracted
- Blocked: [N] sources that could not be accessed at all
- Failed: [N] sources that failed to load (timeout, error)

This transparency helps the user understand the research's coverage limitations.
