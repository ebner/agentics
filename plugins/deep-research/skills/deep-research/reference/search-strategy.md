# Search Strategy Reference

## Query generation patterns

The quality of research depends heavily on query diversity. Use these patterns
to generate queries that surface different types of sources and perspectives.

### Pattern 1: Terminology variation
```
"[full name] [aspect]"
"[abbreviation] [aspect]"
"[alternative name] [aspect]"
```
Example: "Kubernetes horizontal pod autoscaling", "k8s HPA", "container autoscaling"

### Pattern 2: Comparison framing
```
"[X] vs [Y] [aspect]"
"[X] compared to [Y] [year]"
"[X] alternative to [Y]"
"migrate from [Y] to [X]"
```

### Pattern 3: Source-type targeting
```
"[topic] site:github.com"          → code & discussions
"[topic] blog engineering"         → engineering blogs
"[topic] benchmark results"        → performance data
"[topic] case study production"    → real-world usage
"[topic] RFC proposal"             → design decisions
"[topic] post-mortem"              → failure modes
"[topic] documentation guide"      → official docs
```

### Pattern 4: Temporal targeting
```
"[topic] [current year]"           → recent coverage
"[topic] latest release"           → newest version
"[topic] roadmap future"           → forward-looking
"[topic] changelog breaking"       → recent changes
```

### Pattern 5: Sentiment and experience
```
"[topic] issues problems"          → known issues
"[topic] review experience"        → user experiences
"[topic] why we chose"             → decision rationales
"[topic] why we left migrated"     → negative experiences
"[topic] lessons learned"          → practical wisdom
```

### Pattern 6: Quantitative data
```
"[topic] benchmarks performance"   → numbers
"[topic] pricing cost comparison"  → financial data
"[topic] adoption usage statistics"→ market data
"[topic] survey results developer" → survey data
```

## WebFetch prompt patterns

When fetching a page, the prompt should be specific to extract maximum value.

### Good prompts by source type

**For benchmark pages:**
"What specific benchmark numbers does this page report? Include test conditions,
hardware specs, and comparison baselines."

**For case studies:**
"What technology did they use, what problem did it solve, what scale did they
operate at, and what were the key results or metrics?"

**For documentation:**
"What are the key features, configuration options, and known limitations
described on this page?"

**For comparison articles:**
"What criteria does this article use to compare the options? What are the
specific strengths and weaknesses identified for each?"

**For GitHub repositories:**
"What is this project's purpose, how many stars/forks does it have, when was
it last updated, and what does the README say about its maturity?"

**For pricing pages:**
"What are the specific pricing tiers, what's included in each tier, and are
there usage-based costs? Include exact dollar amounts."

**For blog posts / opinions:**
"What is the author's main argument? What evidence do they cite? What is
their background/credibility on this topic?"

## Source credibility assessment

### HIGH credibility signals
- Domain: .gov, .edu, official company domains
- Authors: named individuals with verifiable credentials
- Citations: links to primary data, peer review
- Recency: updated within last 12 months
- Publisher: established technical publications (ACM, IEEE, official blogs)

### MEDIUM credibility signals
- Well-known community sites (Stack Overflow with high votes, HN with discussion)
- Established tech blogs (individual bloggers with reputation)
- Conference talks and slides
- Reputable news outlets covering tech

### LOW credibility signals
- No author attribution
- No dates
- Content farms / SEO-optimized aggregators
- Forums with unverified claims
- Marketing materials without data backing
