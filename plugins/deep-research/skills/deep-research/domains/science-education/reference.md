# Science & Education — Search & Source Reference

## Query Patterns by Topic Type

### Evidence Hierarchy Queries
```
"[topic] systematic review meta-analysis [year]"
"[topic] peer reviewed research [journal/year]"
"[topic] randomized controlled trial"
"[topic] scientific consensus [year]"
"[topic] review article [discipline] [year]"
"[topic] Cochrane review"                         → for health-adjacent science
"[topic] IPCC report"                             → for climate science
"[topic] NAS report National Academy"             → for U.S. science policy
```

### Institutional and Academic Targeting
```
"[topic] site:edu"
"[topic] site:ac.uk"
"[topic] site:nature.com"
"[topic] site:science.org"
"[topic] site:arxiv.org"
"[topic] site:scholar.google.com"
"[topic] [university name] research"
"[topic] MIT OpenCourseWare"
"[topic] lecture notes [university]"
"[topic] textbook chapter [level]"
```

### Education Platform and Course Verification
```
"[course/certification] accreditation recognized"
"[platform] [course] reviews student outcomes"
"[certification] industry recognition value [year]"
"[institution] accreditation status [accreditor]"
"[degree program] [university] ranking [year]"
"[certification] vs [certification] comparison"
"[platform] course quality [topic] [year]"
"best online courses [topic] [year] accredited"
"[institution] CHEA accreditation database"       → U.S. verification
"[institution] QAA review"                        → UK verification
```

### Historical Primary Source Queries
```
"[event/period] primary source documents"
"[event/period] original text translation"
"[historical figure] correspondence archives"
"[event] contemporary accounts [year range]"
"[topic] historiography scholarly debate"
"[event] site:archives.gov"                       → U.S. National Archives
"[event] site:europeana.eu"                       → European archives
"[topic] historical journal article [discipline]"
"[event/period] revisionist vs orthodox interpretation"
"[topic] [language] Quellensammlung"              → German: source collection
```

### Scientific Concept Queries
```
"[concept] explanation [level: introductory/advanced]"
"[concept] current understanding [year]"
"[theory] experimental evidence support"
"[phenomenon] mechanism explained"
"[concept A] vs [concept B] difference"
"[concept] open problems unsolved"
"[concept] recent discoveries breakthroughs [year]"
"[concept] applications real world"
"[concept] common misconceptions"
"[field] Nobel Prize [year] breakthrough"
```

### Predatory Journal / Source Verification Queries
```
"[journal name] impact factor legitimate"
"[journal name] predatory Beall's list"
"[journal name] peer review process"
"[publisher] DOAJ listed"                         → Directory of Open Access Journals
"[conference] legitimate academic"
"[institution] accreditation verification"
"Retraction Watch [author/paper/topic]"
"[paper title] retracted withdrawn"
```

## Preferred Source Tiers

### Tier 1 — Always search and prefer
| Source Type | Examples | Use For |
|---|---|---|
| Top-tier journals | Nature, Science, PNAS, PRL, Cell | Breakthrough findings, consensus |
| Academic databases | Google Scholar, PubMed, Web of Science | Literature searches, citations |
| University resources | MIT OCW, Stanford Online, edX/Coursera (accredited) | Learning resources, course content |
| Government science agencies | NSF, NASA, ESA, CERN, NOAA | Official data, research findings |
| National academies | NAS (US), Royal Society (UK), Leopoldina (DE) | Consensus statements, reports |

### Tier 2 — Good secondary sources
| Source Type | Examples | Use For |
|---|---|---|
| Science communication | Scientific American, Quanta, Nature News | Accessible explanations of research |
| Preprint servers | arXiv, bioRxiv, ChemRxiv, SSRN | Cutting-edge (with preprint caveat) |
| Science journalism | Ars Technica, BBC Science, New Scientist | Current events in science |
| Moderated Q&A | Physics/Math/Chem StackExchange | Concept explanations, derivations |
| Accreditation databases | CHEA, QAA, AQAS | Institutional verification |

### Tier 3 — Use with caution
| Source Type | Examples | Caveat |
|---|---|---|
| Wikipedia | English and other language editions | Orientation only; cite underlying sources |
| YouTube educators | 3Blue1Brown, Veritasium, PBS Space Time | Verify claims against papers |
| Pop-science books | Summaries by known authors | May oversimplify; check original research |
| Student forums | Reddit science subs, Quora | Verify with primary sources |
| News coverage of studies | General news outlets covering research | Often misinterprets; find the actual paper |

## WebFetch Prompts by Source Type

**For peer-reviewed journal articles (or abstracts):**
"What are the study's research question, methodology, sample size, key findings,
statistical significance, and stated limitations? Include the authors, journal name,
publication year, and DOI if available. Note if this is open access or paywalled."

**For preprint server pages:**
"What are the paper's claims, methodology, and key results? Note that this is a
preprint and has not been peer-reviewed. Check if a peer-reviewed version has been
published. Include the submission date and any version numbers."

**For university course or educational resource pages:**
"What topics does this resource cover, at what level (introductory/intermediate/advanced),
by which institution, and is it freely accessible? Note any prerequisites, certification
offered, and whether the institution is accredited."

**For science news / journalism pages:**
"What scientific finding is being reported? Does the article link to or cite the
original paper? What are the key claims, and does the journalist note any caveats
or limitations? Who are the researchers quoted?"

**For historical archive or primary source pages:**
"What primary source material is presented? What is the date, author, and original
context of the document? Is a translation provided, and if so, by whom? What
collection or archive does this belong to?"

**For certification or accreditation pages:**
"What certification or accreditation is described? What is the issuing body, what
are the requirements, what is the validity period, and is this recognized by
employers or other institutions? Note any costs and prerequisites."

**For science encyclopedia or reference pages:**
"What is the core explanation of the concept? What are the key equations, principles,
or mechanisms described? What level of detail is provided? Are there references to
primary literature?"

**For Google Scholar results pages:**
"What are the most cited papers on this topic? List the top results with their
titles, authors, publication years, citation counts, and journals. Note any
systematic reviews or meta-analyses in the results."

## Temporal Sensitivity Rules

| Topic | Sensitivity | Guidance |
|---|---|---|
| Established science (physics laws, evolution) | Stable (decades) | Textbooks and reviews are fine |
| Research frontiers (quantum computing, CRISPR) | Rapidly evolving (months) | Prefer 2024-2026 sources |
| Course offerings and pricing | Semester/annual cycles | Verify current availability |
| Accreditation status | Periodic reviews (5-10 years) | Check current status with accreditor |
| Historical scholarship | Slow evolution (years-decades) | Note historiographic era of interpretation |
| Preprint findings | Days to months before peer review | May be superseded or retracted |
| University rankings | Annual | Note ranking system and year |
| Certification requirements | Updated periodically | Verify with issuing body |
| Science policy and funding | Budget and administration dependent | Note political context |
| Retraction status | Can change at any time | Check Retraction Watch for flagged work |

## Cross-Discipline Awareness

Some science topics span multiple disciplines. When this occurs:

| Combined Topic | Primary Domain | Also Relevant |
|---|---|---|
| Bioethics | science-education | legal, health |
| Environmental science | science-education | legal (regulation), health (pollution) |
| Science of nutrition | health (primary) | science-education (biochemistry) |
| History of medicine | science-education (history) | health (context) |
| Engineering principles | science-education (physics) | tech (applied CS) |
| Animal biology | science-education | parenting-pets (care application) |
| Sports science | sports (application) | science-education (methodology) |
| Educational technology | science-education | tech (platforms) |
