# Technology Research Reference

## Query Patterns

### Pattern 1: Official documentation and specs
```
"[technology] documentation" site:[official-domain]
"[technology] getting started guide"
"[technology] API reference"
"[technology] changelog release notes"
"[technology] RFC specification"
"[technology] architecture design doc"
```

### Pattern 2: Benchmarks and performance
```
"[technology] benchmark [year]"
"[technology A] vs [technology B] performance"
"[technology] benchmark results" site:techempower.com
"[technology] real-world performance production"
"[technology] latency throughput benchmark"
"[technology] load test results"
```

### Pattern 3: Engineering blogs and case studies
```
"[technology] engineering blog"
"[technology] case study production"
"why we chose [technology]"
"why we migrated from [technology A] to [technology B]"
"[technology] at scale"
"[technology] post-mortem"
"[technology] lessons learned production"
```

### Pattern 4: Community and adoption
```
"[technology]" site:github.com
"[technology] stars forks github"
"[technology] npm downloads" OR "[technology] pypi downloads"
"[technology] developer survey [year]"
"[technology] adoption statistics [year]"
"[technology] companies using production"
```

### Pattern 5: Comparison and alternatives
```
"[technology A] vs [technology B] [year]"
"[technology] alternatives comparison"
"[technology A] compared to [technology B] trade-offs"
"migrate from [technology A] to [technology B]"
"[technology] alternative to [technology B]"
```

### Pattern 6: Issues and limitations
```
"[technology] known issues limitations"
"[technology] problems production"
"[technology] scaling issues"
"[technology] security vulnerability CVE"
"[technology] breaking changes"
"[technology] deprecated"
```

### Pattern 7: Architecture and design patterns
```
"[pattern] architecture design"
"[pattern] vs [pattern] trade-offs"
"[technology] best practices [year]"
"[technology] anti-patterns avoid"
"[technology] design decisions rationale"
```

---

## Preferred Source Tiers

### Tier 1 — Primary technical sources
| Source | URL | Specialty | Language |
|---|---|---|---|
| GitHub | github.com | Source code, issues, discussions | EN |
| TechEmpower | techempower.com | Web framework benchmarks | EN |
| Phoronix | phoronix.com | Hardware/Linux benchmarks | EN |
| MLPerf | mlcommons.org | ML benchmarks | EN |
| ArXiv CS | arxiv.org/list/cs | CS research papers | EN |
| ACM Digital Library | dl.acm.org | CS proceedings | EN |
| IETF | ietf.org | Internet standards, RFCs | EN |
| W3C | w3.org | Web standards | EN |

### Tier 2 — Engineering blogs and journalism
| Source | URL | Specialty | Language |
|---|---|---|---|
| Netflix Tech Blog | netflixtechblog.com | Distributed systems, streaming | EN |
| Uber Engineering | eng.uber.com | Systems, ML, platform | EN |
| Stripe Engineering | stripe.com/blog/engineering | Payments, APIs, infrastructure | EN |
| Cloudflare Blog | blog.cloudflare.com | Networking, edge, performance | EN |
| InfoQ | infoq.com | Architecture, practices | EN |
| LWN.net | lwn.net | Linux, kernel, open source | EN |
| Ars Technica | arstechnica.com | Technical deep dives | EN |
| The Register | theregister.com | IT industry news | EN |

### Tier 3 — Community knowledge
| Source | URL | Specialty | Language |
|---|---|---|---|
| Stack Overflow | stackoverflow.com | Q&A (high-vote answers) | EN |
| Hacker News | news.ycombinator.com | Discussion, discovery | EN |
| Dev.to | dev.to | Community tutorials | EN |
| Reddit (technical subs) | reddit.com | Community discussion | EN |

### Tier 4 — Developer surveys and market data
| Source | URL | Specialty |
|---|---|---|
| Stack Overflow Survey | survey.stackoverflow.co | Developer trends |
| JetBrains Survey | jetbrains.com/lp/devecosystem | Language/tool adoption |
| State of JS | stateofjs.com | JavaScript ecosystem |
| TIOBE Index | tiobe.com/tiobe-index | Language popularity |
| ThoughtWorks Radar | thoughtworks.com/radar | Technology trends |

---

## WebFetch Prompts by Source Type

**For official documentation:**
"What are the key features, configuration options, and known limitations described
on this page? What version does this documentation apply to? Are there any
deprecation warnings or migration guides?"

**For engineering blog posts:**
"What technology stack is described? What problem were they solving? What scale
do they operate at? What were the results or metrics? What trade-offs did they
make? What would they do differently?"

**For GitHub repositories:**
"What is this project's purpose? How many stars, forks, and contributors does it
have? When was the last commit and last release? What does the README say about
maturity and production-readiness? What is the license? How many open issues
are there?"

**For benchmark pages:**
"What specific benchmark numbers does this page report? What is the test methodology?
What hardware and software versions were used? What comparison baselines are included?
Are the results reproducible?"

**For comparison articles:**
"What criteria does this article use to compare the technologies? What are the
specific strengths and weaknesses identified for each option? What use cases does
each option suit best? What are the trade-offs? Is there a recommendation?"

**For conference talks/proceedings:**
"What is the main thesis or finding? What evidence is presented? What system or
approach is described? What are the key metrics or results? What are the stated
limitations? Who are the authors and their affiliations?"

**For security advisories:**
"What is the vulnerability (CVE ID if available)? What versions are affected?
What is the severity rating (CVSS)? What is the fix or mitigation? Has it been
exploited in the wild?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Framework/library versions | Current (< 6 months) | APIs change with versions |
| Security vulnerabilities | Current (< 1 month) | Critical for production |
| Benchmark results | < 1 year | Hardware/software changes |
| Best practices | < 2 years (fast-moving), < 5 years (stable) | Depends on technology velocity |
| Architecture patterns | < 5 years | Patterns evolve slowly |
| CS fundamentals | Evergreen | Algorithms do not expire |
| Cloud service pricing | Current (< 3 months) | Prices change quarterly |
| Developer surveys | < 1 year | Annual surveys |
| GitHub activity | Current (< 3 months) | Maintenance status indicator |

---

## Local-Language Query Patterns

Technology research is primarily English-language, but local-language searches
can surface regional perspectives and communities.

### German
```
"[Technologie] Erfahrungsbericht"
"[Technologie] Vergleich [Jahr]"
"[Technologie] Einfuehrung Tutorial"
"[Technologie] Best Practices deutsch"
```

### Swedish
```
"[teknik] erfarenhet"
"[teknik] jaemfoerelse [aar]"
"[teknik] handledning"
```
