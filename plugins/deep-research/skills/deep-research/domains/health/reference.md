# Health & Medical Research Reference

## Query Patterns

### Pattern 1: Evidence Hierarchy Targeting
Target the highest-quality evidence first, then work down.
```
"[condition/treatment] systematic review meta-analysis"
"[condition/treatment] Cochrane review"
"[condition/treatment] randomized controlled trial"
"[drug/supplement] clinical trial results"
"[condition] evidence-based guidelines"
```

### Pattern 2: Institutional Source Targeting
```
"[topic] site:pubmed.ncbi.nlm.nih.gov"
"[topic] site:who.int"
"[topic] site:cdc.gov"
"[topic] site:nih.gov"
"[topic] site:fda.gov"
"[topic] site:cochranelibrary.com"
"[drug] site:drugs.com"              (cross-reference, not primary)
"[topic] site:uptodate.com"
"[topic] clinical practice guideline [medical society]"
```

### Pattern 3: Safety and Risk Queries
```
"[drug/supplement] adverse effects side effects"
"[drug/supplement] contraindications warnings"
"[drug A] [drug B] interaction"
"[treatment] risk benefit analysis"
"[drug] FDA safety communication"
"[drug] black box warning"
"[supplement] toxicity overdose"
"[treatment] long-term safety data"
```

### Pattern 4: Consensus Verification
```
"[topic] scientific consensus evidence-based medicine"
"[topic] position statement [medical society]"
"[topic] clinical practice guideline recommendations"
"[topic] UpToDate summary"
"[claim] debunked myth misinformation"
"[topic] Cochrane evidence summary"
```

### Pattern 5: Epidemiological and Population Data
```
"[disease] prevalence incidence epidemiology"
"[disease] mortality morbidity statistics"
"[disease] risk factors cohort study"
"[condition] demographics affected populations"
"[disease] WHO global burden"
```

### Pattern 6: Drug and Supplement Specifics
```
"[drug] mechanism of action pharmacology"
"[drug] dosage administration route"
"[drug] FDA approval label"
"[drug] phase 3 trial results"
"[supplement] evidence efficacy dose"
"[supplement] examine.com"            (evidence-graded supplement data)
```

## Preferred Source Tiers

### Tier 1 -- Gold standard (always search first)
- Cochrane Library (cochranelibrary.com)
- PubMed / NCBI (pubmed.ncbi.nlm.nih.gov, ncbi.nlm.nih.gov)
- WHO publications (who.int)
- Clinical practice guidelines from major societies (AHA, NICE, SIGN, ACOG, AWMF)

### Tier 2 -- Authoritative institutional
- CDC (cdc.gov)
- NIH and institute-specific sites (cancer.gov, nimh.nih.gov)
- FDA (fda.gov) -- approvals, labels, safety communications
- EMA (ema.europa.eu)
- UpToDate (uptodate.com)

### Tier 3 -- Strong peer-reviewed
- NEJM (nejm.org)
- The Lancet (thelancet.com)
- JAMA Network (jamanetwork.com)
- BMJ (bmj.com)
- Annals of Internal Medicine, Nature Medicine, Cell

### Tier 4 -- Reputable secondary
- Mayo Clinic (mayoclinic.org)
- Cleveland Clinic (clevelandclinic.org)
- Johns Hopkins Medicine (hopkinsmedicine.org)
- STAT News (statnews.com)
- Examine.com (supplement evidence summaries)
- MedlinePlus (medlineplus.gov)

### Tier 5 -- Qualified tertiary (verify claims against higher tiers)
- Health journalism in major outlets (NYT Health, BBC Health, Guardian)
- WebMD, Healthline (only when citing studies -- follow the citation)
- Patient advocacy organizations (disease-specific foundations)

## WebFetch Prompts by Source Type

### For research articles (PubMed, journal sites)
```
"What is the study design (RCT, cohort, meta-analysis, etc.)? What was the
sample size? What were the primary and secondary endpoints? What were the main
results with confidence intervals and p-values? What limitations do the authors
acknowledge? Who funded the study? Were there any conflicts of interest
disclosed? Has this study been retracted or corrected?"
```

### For clinical practice guidelines
```
"What are the specific recommendations? What is the strength of each
recommendation (strong, moderate, weak)? What level of evidence supports each?
Which patient populations do these guidelines apply to? Are there any
populations explicitly excluded? When were these guidelines last updated?
Which medical society published them?"
```

### For drug / supplement information pages
```
"What are the approved indications? What is the recommended dosage and
administration route? What are the contraindications? What are the most common
adverse effects and their incidence rates? What serious adverse effects or
warnings exist (including black box warnings)? What drug interactions are listed?
Is there guidance for special populations (pregnancy, renal impairment, elderly)?
What is the mechanism of action?"
```

### For health news articles
```
"Does this article cite specific studies? If so, what study or studies?
What did the study actually find vs what does the headline claim? What is the
study design and sample size? Does the article include expert commentary?
Does the article note any limitations? Is the headline consistent with the
study's actual conclusions? Are there any conflicts of interest mentioned?"
```

### For WHO / CDC fact sheets
```
"What are the key facts, statistics, and recommendations? What prevention
measures are recommended? What is the current epidemiological data? Are there
specific risk groups identified? What is the recommended treatment or response?
When was this fact sheet last updated?"
```

### For pre-prints (medRxiv, bioRxiv)
```
"What are the main findings and methodology? Has this pre-print been
peer-reviewed or published in a journal since posting? What limitations does
the study acknowledge? What is the sample size? NOTE: This is a pre-print
and has not undergone peer review."
```

## Temporal Sensitivity

| Content Type | Freshness Requirement | Notes |
|---|---|---|
| Clinical practice guidelines | Last 3 years | Older guidelines may be superseded |
| Drug safety information | Last 2 years | FDA/EMA may issue new warnings |
| Drug approvals / labels | Last 2 years | Label updates are common |
| Epidemiological data | Last 2-3 years | Incidence/prevalence changes |
| Foundational research | Any age | Landmark trials remain relevant |
| Systematic reviews | Prefer last 5 years | Older reviews miss newer trials |
| Supplement evidence | Last 3 years | Evidence base evolves |
| Emerging disease info | Last 6-12 months | Rapidly evolving knowledge |
| Vaccine schedules | Current year | Updated annually |

## Local-Language Query Patterns (DACH Region)

For German-speaking users or DACH-relevant health topics, supplement English
queries with German-language searches:

```
"[Erkrankung/Behandlung] Leitlinie AWMF"
"[Thema] site:rki.de"                       (Robert Koch Institut)
"[Arzneimittel] site:bfarm.de"              (Bundesinstitut fur Arzneimittel)
"[Medikament] Arznei-Telegramm"             (independent drug bulletin)
"[Thema] Deutsches Arzteblatt"
"[Thema] S3-Leitlinie"                      (highest guideline quality level)
"[Thema] Patienteninformation IQWIG"        (gesundheitsinformation.de)
"[Thema] site:gesundheitsinformation.de"
"[Impfung] STIKO Empfehlung"               (vaccination committee)
```

German medical source tiers:
- **Tier 1**: AWMF Leitlinien (S1/S2k/S2e/S3), RKI
- **Tier 2**: Arznei-Telegramm, BfArM, IQWiG, PEI
- **Tier 3**: Deutsches Arzteblatt, Charite, Uni-Kliniken
- **Tier 4**: Apotheken-Umschau (consumer, verify claims)

### Austrian Sources
```
"[Thema] site:sozialministerium.at"
"[Thema] site:ages.at"                      (AGES -- Austrian health agency)
```

### Swiss Sources
```
"[Thema] site:bag.admin.ch"                 (BAG -- Swiss federal health office)
"[Thema] site:swissmedic.ch"               (Swiss drug authority)
```
