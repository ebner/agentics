# Career & Employment Research Reference

## Query Patterns

### Pattern 1: Salary and compensation
```
"[job title] salary [year]" site:bls.gov
"[job title] compensation" site:levels.fyi
"[job title] salary [city/country] [year]"
"[job title] salary range median"
"[job title] total compensation equity bonus"
"[job title] Gehalt [Jahr]" site:kununu.com
"[job title] lon [aar]" site:scb.se
```

### Pattern 2: Job market and demand
```
"[job title] hiring trends [year]"
"[job title] job market outlook"
"[job title] demand growing declining"
"[industry] employment forecast [year]"
"[skill] in-demand jobs [year]"
"[job title] occupational outlook" site:bls.gov/ooh
```

### Pattern 3: Company research
```
"[company name] reviews" site:glassdoor.com
"[company name] Bewertungen" site:kununu.com
"[company name] culture work-life balance"
"[company name] interview process"
"[company name] career growth opportunities"
"[company name] layoffs hiring [year]"
```

### Pattern 4: Skills and career path
```
"[job title] required skills [year]"
"[job title] career path progression"
"[certification] worth it [job title]"
"transition from [role A] to [role B]"
"[job title] learning roadmap"
"[industry] skills gap [year]"
```

### Pattern 5: Remote work
```
"[job title] remote jobs"
"[company name] remote work policy"
"remote [job title] salary comparison"
"remote work trends [year]"
"best companies remote work [year]"
"[job title] remote" site:flexjobs.com
```

### Pattern 6: Regional labor market
```
"[job title] arbeitsmarkt [region]" site:arbeitsagentur.de
"[job title] arbetsmarknad [region]" site:arbetsformedlingen.se
"[region] labor market report [year]"
"[city] cost of living vs salary"
"[country] minimum wage [year]"
"[region] unemployment rate [year]"
```

---

## Preferred Source Tiers

### Tier 1 — Government and statistical
| Source | URL | Specialty | Language |
|---|---|---|---|
| BLS | bls.gov | US occupational data, wages | EN |
| BLS OOH | bls.gov/ooh | US career outlook | EN |
| Eurostat | ec.europa.eu/eurostat | EU labor statistics | EN |
| SCB | scb.se | Swedish labor statistics | SV |
| Destatis | destatis.de | German federal statistics | DE |
| ONS | ons.gov.uk | UK labor statistics | EN |
| ILO | ilo.org | Global labor data | EN |
| Arbetsformedlingen | arbetsformedlingen.se | Swedish employment service | SV |
| Bundesagentur fuer Arbeit | arbeitsagentur.de | German employment agency | DE |

### Tier 2 — Verified salary and review platforms
| Source | URL | Specialty | Language |
|---|---|---|---|
| Glassdoor | glassdoor.com | Salary, company reviews | EN |
| Levels.fyi | levels.fyi | Tech compensation | EN |
| Payscale | payscale.com | Salary survey data | EN |
| Kununu | kununu.com | DACH employer reviews | DE |
| LinkedIn Salary | linkedin.com/salary | Aggregated salary data | EN |
| Indeed Hiring Lab | hiringlab.org | Labor market research | EN |
| Blind | teamblind.com | Anonymous verified tech comp | EN |

### Tier 3 — Industry reports and career resources
| Source | URL | Specialty | Language |
|---|---|---|---|
| Robert Half Salary Guide | roberthalf.com | Recruiter salary survey | EN |
| Hays Salary Guide | hays.com | Recruiter salary survey | EN/DE |
| WEF Future of Jobs | weforum.org | Global employment trends | EN |
| FlexJobs | flexjobs.com | Remote work jobs | EN |
| Stack Overflow Survey | survey.stackoverflow.co | Developer salary/trends | EN |

---

## WebFetch Prompts by Source Type

**For government labor statistics (BLS, Eurostat, SCB):**
"What is the median salary for this occupation? What is the employment level and
projected growth rate? What are the salary percentiles (10th, 25th, 50th, 75th,
90th)? What is the sample size? What year is this data from? What are the top-paying
industries or regions for this occupation?"

**For salary platforms (Glassdoor, Levels.fyi, Payscale):**
"What is the reported salary range for this role? What is the median and mean?
How many salary reports are included? What is the breakdown by experience level?
What is total compensation vs base salary? What region does this data cover?"

**For company review pages (Glassdoor, Kununu):**
"What is the overall rating? How many reviews are there? What are the ratings for
compensation, work-life balance, management, culture, and career growth? What are
the most common pros and cons mentioned? What is the interview difficulty rating?
What is the CEO approval rating? Has the rating trended up or down recently?"

**For job posting aggregation:**
"What are the stated salary ranges in job postings for this role? What skills and
qualifications are most frequently required? What experience level is sought?
Is remote work offered? What benefits are mentioned? What is the posting volume
trend?"

**For industry reports and surveys:**
"What are the key findings about salary trends for this role/industry? What is the
projected job growth? What skills are identified as most in-demand? What is the
methodology and sample size of the survey? What year was the data collected?"

**For cost-of-living comparison:**
"What is the cost-of-living index for this city/region? How does it compare to the
national average? What are the specific costs for housing, food, transportation?
What salary would provide equivalent purchasing power in [comparison city]?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Salary data | < 1 year | Adjust for inflation if older |
| Unemployment rates | Current (< 3 months) | Monthly/quarterly updates |
| Hiring trends | < 6 months | Market shifts quickly |
| Company reviews | < 1 year | Culture changes, esp. post-M&A |
| Skills demand | < 1 year | Tech skills shift fast |
| Employment law | Current | Laws change with legislation |
| Cost of living | < 1 year | Housing costs volatile |
| Career outlook | < 2 years | BLS updates biennially |

---

## Local-Language Query Patterns

### German (DACH labor market)
```
"[Berufsbezeichnung] Gehalt Deutschland [Jahr]"
"[Berufsbezeichnung] Gehaltsvergleich"
"[Unternehmen] Arbeitgeberbewertung" site:kununu.com
"[Branche] Arbeitsmarkt [Jahr]"
"[Berufsbezeichnung] Stellenangebote"
"[Berufsbezeichnung] Berufsbild" site:arbeitsagentur.de
"Tarifvertrag [Branche] [Jahr]"
```

### Swedish (Nordic labor market)
```
"[yrke] lon Sverige [aar]"
"[yrke] lonestatistik" site:scb.se
"[foretag] omdome arbetsgivare"
"[bransch] arbetsmarknad [aar]"
"[yrke] lediga jobb"
"[yrke] yrkesbeskrivning" site:arbetsformedlingen.se
"kollektivavtal [bransch] [aar]"
```
