# Medical & Pharmaceutical Search Strategy Reference

## Query Patterns

### Pattern 1: Regulatory Drug Information
```
"[drug generic name] prescribing information"
"[drug] FDA label site:dailymed.nlm.nih.gov"
"[drug] SmPC site:ema.europa.eu"
"[drug] FASS site:fass.se"
"[drug] black box warning"
"[drug] FDA approval review"
"[drug] EPAR European public assessment report"
```

### Pattern 2: Pharmacogenomics
```
"[drug] pharmacogenomics CPIC guideline"
"[drug] [gene] site:pharmgkb.org"
"[gene variant] clinical annotation PharmGKB"
"[drug] CYP2D6 OR CYP2C19 OR CYP3A4 metabolizer"
"[drug] pharmacogenomic biomarker FDA table"
"[drug] DPWG guideline dosing genotype"
"[gene] allele frequency gnomAD"
"[drug] [gene] poor metabolizer clinical consequence"
"[drug] companion diagnostic genetic test"
```

### Pattern 3: Clinical Trial Evidence
```
"[drug] [indication] clinical trial results phase III"
"[drug] site:clinicaltrials.gov"
"[drug] [indication] systematic review meta-analysis"
"[drug] randomized controlled trial [year]"
"[drug] vs [comparator] head-to-head trial"
"[drug] NNT NNH [indication]"
"[drug] [indication] Cochrane review"
"[drug] non-inferiority trial [comparator]"
```

### Pattern 4: Drug Safety & Pharmacovigilance
```
"[drug] adverse effects frequency"
"[drug] side effects post-market surveillance"
"[drug] FAERS safety signal"
"[drug] adverse event reporting EudraVigilance"
"[drug] withdrawn OR recalled [country]"
"[drug] drug interaction [other drug] clinical significance"
"[drug] contraindication"
"[drug] pregnancy risk category"
"[drug] hepatotoxicity OR nephrotoxicity"
"[drug] QT prolongation risk"
```

### Pattern 5: Drug Mechanism & Pharmacokinetics
```
"[drug] mechanism of action pharmacodynamics"
"[drug] pharmacokinetics half-life bioavailability"
"[drug] CYP metabolism pathway"
"[drug] drug class [class name] comparison"
"[drug] therapeutic index"
"[drug] dose-response relationship"
"[drug] renal dosing adjustment GFR"
"[drug] hepatic impairment Child-Pugh"
```

### Pattern 6: Comparative Effectiveness
```
"[drug] vs [alternative] comparative effectiveness"
"[drug class] comparison efficacy safety [year]"
"[indication] treatment guidelines first-line second-line"
"[drug] cost-effectiveness analysis QALY"
"[drug] therapeutic substitution [alternative]"
"[drug] formulary comparison [country/system]"
```

### Pattern 7: Genetic Variant Research
```
"[gene variant] functional impact"
"[gene] star allele nomenclature PharmVar"
"[gene variant] site:clinvar.ncbi.nlm.nih.gov"
"[gene] site:omim.org"
"[gene variant] population frequency [ethnicity]"
"[condition] genetic predisposition pharmacogenetic"
"[gene] loss of function variant drug response"
```

---

## Preferred Source Tiers

### Tier 1: Regulatory & Authoritative (always search first)
| Source | URL Pattern | Best For |
|---|---|---|
| DailyMed (FDA labels) | dailymed.nlm.nih.gov | Official US prescribing information |
| EMA (European) | ema.europa.eu | European SmPC, EPAR documents |
| FASS (Swedish) | fass.se | Swedish drug compendium (in Swedish) |
| Läkemedelsverket | lakemedelsverket.se | Swedish MPA decisions and safety info |
| PharmGKB | pharmgkb.org | Pharmacogenomic annotations, pathways |
| CPIC | cpicpgx.org | Genotype-based dosing guidelines |
| ClinicalTrials.gov | clinicaltrials.gov | Trial registration, design, results |
| FDA FAERS | fda.gov/drugs/fda-adverse-event-reporting-system | Post-market adverse events |
| ClinVar | clinvar.ncbi.nlm.nih.gov | Genetic variant clinical significance |

### Tier 2: Peer-Reviewed & Reference
| Source | Best For |
|---|---|
| PubMed / PMC | Peer-reviewed pharmacology literature |
| Cochrane Library | Systematic reviews of drug efficacy |
| DrugBank | Comprehensive drug data (pharmacokinetics, targets) |
| gnomAD | Population allele frequencies |
| OMIM | Gene-disease associations |
| UpToDate drug monographs | Clinical decision support |

### Tier 3: Secondary Reference
| Source | Best For | Caveat |
|---|---|---|
| drugs.com | Drug interactions, patient-facing info | Verify against regulatory labels |
| Medscape drug reference | Quick pharmacology reference | Not primary source |
| RxList | Drug overview | Consumer-oriented, verify claims |
| GoodRx | Pricing data (US) | Pricing only, not clinical |

---

## WebFetch Prompt Patterns

**For FDA drug labels (DailyMed):**
"What are the approved indications, black box warnings, contraindications,
dosage and administration, adverse reactions (by frequency), drug interactions,
use in specific populations (pregnancy, renal impairment, hepatic impairment),
and pharmacogenomic information in this prescribing label?"

**For EMA SmPC documents:**
"What are the therapeutic indications, posology, contraindications, special
warnings, interaction with other medicinal products, undesirable effects
(by system organ class and frequency), and pharmacogenomic information?"

**For PharmGKB gene-drug pages:**
"What is the evidence level for this gene-drug association? What are the
clinical annotations? What CPIC or DPWG guidelines exist? What are the
dosing recommendations by genotype/phenotype?"

**For ClinicalTrials.gov entries:**
"What is the trial phase, study design, primary and secondary endpoints,
enrollment size, sponsor, current status, and any posted results? Is there
a linked publication?"

**For clinical trial publications:**
"What were the primary endpoint results with effect size and 95% CI?
What was the sample size and statistical power? What were the main
adverse events? Was it superiority or non-inferiority? Who funded the trial?
Were there any conflicts of interest?"

**For FAERS/pharmacovigilance pages:**
"What adverse events have been reported? What are the reported frequencies?
Are there any safety signals or risk evaluations? Have any regulatory
actions been taken based on these reports?"

**For ClinVar variant pages:**
"What is the clinical significance of this variant? What conditions is it
associated with? What is the review status? What is the allele frequency?
Are there any pharmacogenomic annotations?"

**For CPIC guideline pages:**
"What gene-drug pair does this guideline cover? What are the dosing
recommendations for each metabolizer phenotype (ultra-rapid, normal,
intermediate, poor)? What is the strength of the recommendation?
What alternative drugs are suggested for affected phenotypes?"

---

## Temporal Sensitivity

| Data Type | Recency Requirement |
|---|---|
| Drug safety alerts, recalls, withdrawals | Current — check within last 6 months |
| FDA/EMA label updates | Current edition (labels are periodically updated) |
| CPIC guidelines | Current version (updated every 2-3 years) |
| Clinical trial results | Any age, but note publication date |
| Pharmacogenomic associations | Last 5 years preferred (field evolving rapidly) |
| Drug pricing | Last 6 months (prices change frequently) |
| Allele frequency data | Last 10 years acceptable (population genetics is stable) |
| Drug interaction data | Last 3 years preferred |

---

## Local-Language Query Patterns

### Swedish (Läkemedelsverket, FASS)
```
"[drug Swedish name] biverkningar FASS"
"[drug] Läkemedelsverket säkerhetsinformation"
"[drug] produktresumé SPC FASS"
"[drug] interaktioner janusinfo"
"farmakogenetik [gene] [drug] Sverige"
"[drug] graviditet amning FASS"
```

### German (BfArM, Rote Liste)
```
"[drug] Fachinformation BfArM"
"[drug] Nebenwirkungen Häufigkeit"
"[drug] Rote Liste Gebrauchsinformation"
"[drug] Wechselwirkungen"
"Pharmakogenetik [gene] [drug]"
"[drug] Schwangerschaft Stillzeit"
```

### EU-wide
```
"[drug] EPAR site:ema.europa.eu"
"[drug] referral procedure EMA"
"[drug] periodic safety update report PSUR"
"[drug] risk management plan EMA"
```

---

## Cross-Domain Boundaries

### When to defer to health-research-agent:
- General health condition questions ("what is diabetes?")
- Lifestyle interventions (diet, exercise, sleep)
- Preventive health measures
- General wellness and nutrition questions

### When to use THIS agent (medical-pharma):
- Specific drug questions (mechanism, side effects, interactions)
- Pharmacogenomic inquiries (genotype-drug response)
- Clinical trial evidence evaluation
- Drug comparison and therapeutic alternatives
- Adverse event investigation
- Dosing in special populations
- Drug safety surveillance data

### When to escalate to both agents (cross-domain):
- "Should I take metformin for my prediabetes?" → health agent for lifestyle context,
  medical-pharma for drug-specific evidence
- "What supplements interact with my medications?" → medical-pharma for interaction
  data, health agent for supplement evidence base
