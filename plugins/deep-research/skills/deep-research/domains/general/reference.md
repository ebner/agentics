# General Research Reference

## Query Patterns

### Pattern 1: Factual and reference
```
"[topic] overview" site:wikipedia.org
"[topic]" site:britannica.com
"[topic] definition meaning"
"[topic] explained"
"[topic] history timeline"
```

### Pattern 2: Academic and institutional
```
"[topic]" site:*.edu
"[topic]" site:*.gov
"[topic] research study peer-reviewed"
"[topic] academic paper"
"[topic] Stanford Encyclopedia" (for philosophy)
"[topic] systematic review meta-analysis"
```

### Pattern 3: News and current events
```
"[topic] [year]" site:reuters.com
"[topic] [year]" site:apnews.com
"[topic] latest developments [year]"
"[topic] analysis [year]"
"[topic] explained context"
```

### Pattern 4: Fact-checking
```
"[claim]" site:snopes.com
"[claim]" site:politifact.com
"[claim]" site:fullfact.org
"[claim]" site:correctiv.org
"[claim] fact check"
"[claim] true or false"
```

### Pattern 5: Multiple perspectives
```
"[topic] arguments for against"
"[topic] debate pros cons"
"[topic] different perspectives"
"[topic] criticism critique"
"[topic] supporters opponents"
```

### Pattern 6: Expert sources
```
"[topic] expert analysis"
"[topic] [field] professor researcher"
"[topic] published author expert"
"[topic] professional opinion"
"[topic] interview [expert name]"
```

### Pattern 7: Cultural and arts topics
```
"[artwork/artist] analysis"
"[cultural topic] history significance"
"[art movement] characteristics works"
"[cultural practice] origin meaning"
"[topic]" site:metmuseum.org OR site:moma.org
```

---

## Preferred Source Tiers

### Tier 1 — Institutional and reference
| Source | URL | Specialty | Language |
|---|---|---|---|
| Wikipedia | wikipedia.org | General reference, citation links | Multi |
| Britannica | britannica.com | Encyclopedic reference | EN |
| Stanford Encyclopedia | plato.stanford.edu | Philosophy | EN |
| AP News | apnews.com | Wire service, factual reporting | EN |
| Reuters | reuters.com | Wire service, factual reporting | EN |
| AFP | afp.com | Wire service, factual reporting | FR/EN |
| UN | un.org | International data and reports | Multi |
| OECD | oecd.org | International economic/social data | EN |
| World Bank | worldbank.org | Development data | EN |

### Tier 2 — Quality journalism and analysis
| Source | URL | Specialty | Language |
|---|---|---|---|
| BBC | bbc.com | News, analysis, UK perspective | EN |
| NPR | npr.org | News, analysis, US perspective | EN |
| Guardian | theguardian.com | News, analysis, UK/int'l | EN |
| Die Zeit | zeit.de | News, analysis, German | DE |
| Dagens Nyheter | dn.se | News, analysis, Swedish | SV |
| SVT | svt.se | Swedish public broadcasting | SV |
| The Economist | economist.com | Analysis, global | EN |
| Der Spiegel | spiegel.de | News, analysis, German | DE |
| Le Monde | lemonde.fr | News, analysis, French | FR |

### Tier 3 — Fact-checking
| Source | URL | Specialty | Language |
|---|---|---|---|
| Snopes | snopes.com | Fact-checking, US focus | EN |
| PolitiFact | politifact.com | Political fact-checking | EN |
| Full Fact | fullfact.org | Fact-checking, UK | EN |
| Correctiv | correctiv.org | Fact-checking, Germany | DE |
| Faktiskt | faktiskt.se | Fact-checking, Sweden | SV |
| AFP Fact Check | factcheck.afp.com | Fact-checking, international | Multi |

### Tier 4 — Specialized reference
| Source | URL | Specialty | Language |
|---|---|---|---|
| Internet Archive | archive.org | Historical web content | EN |
| Google Scholar | scholar.google.com | Academic paper search | Multi |
| JSTOR | jstor.org | Academic journals | EN |
| Project Gutenberg | gutenberg.org | Public domain texts | EN |

---

## WebFetch Prompts by Source Type

**For Wikipedia articles:**
"What are the key facts presented in this article? What are the cited sources for
the main claims (look at references/footnotes)? Is there a 'Controversy' or
'Criticism' section? When was this article last updated? Are there any cleanup
or neutrality tags?"

**For news articles (AP, Reuters, BBC):**
"What are the key facts reported? Who are the named sources? What is the timeline
of events? Are there any caveats or uncertainties noted? What context is provided?
What is the publication date?"

**For academic papers:**
"What is the research question? What methodology was used? What are the key findings
and conclusions? What is the sample size? What are the stated limitations? Who are
the authors and their affiliations? Where was this published and when?"

**For government reports:**
"What are the key findings and recommendations? What data is presented? What is the
scope and methodology? When was this published? What agency or department produced
it? Are there dissenting views or caveats?"

**For opinion and analysis pieces:**
"What is the author's main argument? What evidence do they cite? What is the author's
background and potential biases? What counterarguments are acknowledged? Is the
reasoning logically sound?"

**For fact-checking articles:**
"What specific claim is being checked? What is the verdict (true, false, misleading,
unproven)? What evidence was used to reach this verdict? What are the primary
sources cited? What is the date of the fact-check?"

**For cultural and arts sources:**
"What is the subject of this page? What historical or cultural context is provided?
What are the key interpretive or analytical points? Are there references to other
related works or movements? Who is the author/institution?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Breaking news | Current (< 24 hours) | Evolves rapidly, verify continuously |
| Current events | Current (< 1 week) | Context changes |
| Political analysis | < 6 months | Policy landscapes shift |
| Statistical data | < 2 years | Government stats update periodically |
| Historical facts | Evergreen | But historiography evolves |
| Philosophy/theory | Evergreen | Foundational texts are permanent |
| Cultural events | Varies | Check specific event dates |
| Art/cultural analysis | < 10 years | Interpretations shift slowly |
| Fact-checks | < 2 years | Verify claim is still relevant |

---

## Local-Language Query Patterns

### German
```
"[Thema] Ueberblick"
"[Thema] Analyse"
"[Thema] Hintergrund"
"[Thema] Faktencheck" site:correctiv.org
"[Thema] Forschung Studie"
```

### Swedish
```
"[aemne] oeversikt"
"[aemne] analys"
"[aemne] bakgrund"
"[aemne] faktagranskning" site:faktiskt.se
"[aemne] forskning studie"
```

### French
```
"[sujet] analyse"
"[sujet] contexte"
"[sujet] verification" site:factcheck.afp.com
"[sujet] recherche etude"
```
