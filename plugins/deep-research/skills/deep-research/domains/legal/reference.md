# Legal & Regulatory Research Reference

## Query Patterns

### Pattern 1: Statute and Regulation Targeting
```
"[topic] statute law [jurisdiction]"
"[topic] [jurisdiction] code section"
"[topic] regulation [agency] [jurisdiction]"
"[topic] act [year] [jurisdiction]"
"[US topic] USC title [number] section"
"[EU topic] directive regulation EU"
"[topic] site:eur-lex.europa.eu"
"[topic] site:govinfo.gov"
"[topic] site:legislation.gov.uk"
```

### Pattern 2: Case Law Targeting
```
"[topic] court decision ruling [jurisdiction]"
"[topic] Supreme Court [jurisdiction] [year range]"
"[topic] landmark case [jurisdiction]"
"[topic] [party name] v [party name]"
"[topic] court of appeals [circuit/jurisdiction]"
"[topic] case law precedent [jurisdiction]"
"[topic] site:supremecourt.gov"
"[topic] site:curia.europa.eu"                  (EU Court of Justice)
```

### Pattern 3: Regulatory Guidance Targeting
```
"[topic] regulatory guidance [agency]"
"[topic] enforcement guidance [agency]"
"[topic] advisory opinion [agency]"
"[topic] compliance guide [agency]"
"[topic] FAQ [regulatory body]"
"[topic] no-action letter SEC"
"GDPR guidance [topic] [DPA]"
"[topic] enforcement action [agency] [year]"
```

### Pattern 4: Compliance Queries
```
"[topic] compliance requirements [industry] [jurisdiction]"
"[topic] regulatory obligations [jurisdiction]"
"[topic] filing requirements [jurisdiction]"
"[topic] reporting obligations [jurisdiction]"
"[topic] penalty fine non-compliance [jurisdiction]"
"[topic] compliance checklist [industry]"
"[topic] best practices regulatory [jurisdiction]"
```

### Pattern 5: Intellectual Property
```
"[topic] patent law [jurisdiction]"
"[topic] copyright law [jurisdiction] [year]"
"[topic] trademark registration [jurisdiction]"
"[topic] fair use fair dealing [jurisdiction]"
"[topic] patent infringement case [jurisdiction]"
"[software/content] licensing [license type]"
"[topic] trade secret protection [jurisdiction]"
"[topic] IP enforcement [jurisdiction]"
```

### Pattern 6: Comparative and Cross-Border
```
"[topic] law comparison [jurisdiction A] [jurisdiction B]"
"[topic] international treaty convention"
"[topic] cross-border regulation"
"[topic] mutual recognition agreement"
"[topic] conflict of laws [jurisdictions]"
"[topic] harmonization EU member states"
```

## Preferred Source Tiers

### Tier 1 -- Primary law (always search first)
- US: GovInfo.gov, Congress.gov, state legislature official sites, supremecourt.gov
- EU: EUR-Lex (eur-lex.europa.eu), CURIA (curia.europa.eu)
- UK: legislation.gov.uk, judiciary.uk, BAILII (bailii.org)
- Germany: Gesetze-im-Internet.de, dejure.org, Bundesgesetzblatt (bgbl.de)
- Sweden: riksdagen.se, lagrummet.se, domstol.se
- International: treaties.un.org, WIPO Lex (wipo.int/wipolex)

### Tier 2 -- Regulatory and government
- US: SEC.gov, FTC.gov, EEOC.gov, EPA.gov, DOJ.gov, USPTO.gov, CFPB
- EU: European Commission (ec.europa.eu), EDPB (edpb.europa.eu), EUIPO
- UK: GOV.UK regulatory bodies, ICO (ico.org.uk)
- International: OECD, WTO, UNCITRAL

### Tier 3 -- Academic legal sources
- Law reviews: Harvard, Yale, Stanford, Columbia, Michigan, Georgetown
- Legal research platforms: SSRN legal studies, Google Scholar (case law)
- CRS Reports (crsreports.congress.gov)
- SCOTUSblog, Lawfare, Verfassungsblog

### Tier 4 -- Professional commentary
- Law firm client alerts from Am Law 100 / Magic Circle firms
- LexisNexis and Westlaw summaries (behind paywalls -- note if inaccessible)
- Bar association publications and guidance
- Practical Law (Thomson Reuters)
- Legal journalism: Law360, American Lawyer, LTO.de

### Tier 5 -- General legal reference (verify against higher tiers)
- Cornell LII (law.cornell.edu) -- good US code access
- Nolo.com (consumer legal info, US-focused)
- FindLaw (general overviews, verify specifics)
- Wikipedia legal articles (entry point only, always verify)

## WebFetch Prompts by Source Type

### For legislation / statute pages
```
"What is the exact title and section number of this law? What is its effective
date? What are the key provisions and definitions? Has it been amended since
enactment, and if so, what changed? What jurisdiction does it apply to? Are
there any sunset clauses or expiration dates? What penalties or enforcement
mechanisms does it establish? What exemptions or exceptions are provided?"
```

### For court decisions
```
"What is the full case citation (parties, court, date, reporter)? What were
the key facts? What legal issue(s) did the court address? What was the holding
(the court's decision on the legal question)? What was the reasoning? Were
there any concurring or dissenting opinions, and what did they argue? Has this
case been subsequently cited, overruled, or distinguished? What jurisdiction
and court level issued this decision?"
```

### For regulatory guidance documents
```
"Which agency issued this guidance and when? What specific law or regulation
does it interpret? What are the key interpretive positions or requirements?
Does the guidance have the force of law or is it non-binding? Are there any
safe harbors or compliance examples provided? What enforcement priorities does
it signal? Are there any pending updates or proposed revisions?"
```

### For legal commentary / law firm alerts
```
"What specific law, regulation, or case does this commentary analyze? What is
the author's key argument or interpretation? What primary sources does it cite?
Does the author identify any ambiguities or open questions in the law? What
practical implications does it identify? What is the author's and firm's
expertise in this area? Is there any disclaimer about the commentary not being
legal advice?"
```

### For compliance and regulatory filings
```
"What are the specific filing or reporting obligations described? What are the
deadlines and filing frequencies? What penalties apply for non-compliance or
late filing? What entities or persons are subject to these requirements? Are
there any exemptions or thresholds? What recent changes have been made to
these requirements? What jurisdiction and regulatory body administers this?"
```

### For IP / patent pages
```
"What is the patent/trademark/copyright registration number? Who is the
owner/assignee? What is the filing and issue date? What is the scope of
protection (claims for patents, classes for trademarks)? What is the current
status (active, expired, abandoned, challenged)? Are there any related
applications or continuations? What jurisdiction issued this right?"
```

## Temporal Sensitivity

| Content Type | Freshness Requirement | Notes |
|---|---|---|
| Statute text | Must verify current version | Check for amendments each legislative session |
| Regulations | Must verify current version | Agencies update frequently; check Federal Register / official gazettes |
| Court decisions | Any age, but check status | May be overruled, distinguished, or superseded |
| Regulatory guidance | Last 2-3 years preferred | Agencies revise interpretation over time |
| Proposed legislation | Current legislative session | Bills die at end of session |
| Tax law | Current tax year | Annual changes common |
| EU regulations | Check for amendments | Regulations directly applicable; directives need transposition |
| GDPR / data protection | Last 2 years | Enforcement interpretation still evolving |
| IP registrations | Verify current status | Rights can expire, lapse, or be challenged |
| Legal commentary | 1-3 years for analysis | Older commentary may cite superseded law |
| International treaties | Check ratification status | May not be in force in all signatory states |

Always verify the **current enforceability** of any legal provision. A statute
on the books may have been struck down by a court, preempted by federal law,
or effectively superseded by later legislation.

## Local-Language Query Patterns

### German (DACH Region)
```
"[Thema] Gesetz [Rechtsgebiet]"
"[Thema] site:gesetze-im-internet.de"
"[Thema] site:dejure.org"                     (case law and commentary)
"[Thema] Bundesgesetzblatt"
"[Thema] BGH Urteil"                          (Federal Court of Justice)
"[Thema] BVerfG Beschluss"                    (Federal Constitutional Court)
"[Thema] Verordnung [Bereich]"                (regulations)
"[Thema] DSGVO Datenschutz"                   (GDPR / data protection)
"[Thema] Arbeitsrecht [Aspekt]"               (labor law)
"[Thema] BGB Paragraph"                       (Civil Code)
"[Thema] HGB Handelsrecht"                    (Commercial Code)
"[Thema] site:bundesverfassungsgericht.de"
```

German legal source tiers:
- **Tier 1**: Gesetze-im-Internet.de, dejure.org, Bundesgesetzblatt, court websites
- **Tier 2**: Beck-online, juris (behind paywalls -- note if inaccessible), NJW
- **Tier 3**: LTO.de (Legal Tribune Online), Anwaltsblatt
- **Tier 4**: Haufe.de (practical guides, verify against primary sources)

Austrian additions:
```
"[Thema] site:ris.bka.gv.at"                  (Rechtsinformationssystem des Bundes)
"[Thema] OGH Entscheidung"                    (Supreme Court of Austria)
```

Swiss additions:
```
"[Thema] site:fedlex.admin.ch"                 (Swiss federal law)
"[Thema] BGE Bundesgericht"                    (Swiss Federal Supreme Court)
```

### Swedish
```
"[amne] lag forordning [omrade]"
"[amne] site:riksdagen.se"                     (parliament and legislation)
"[amne] site:lagrummet.se"                     (legal information portal)
"[amne] site:domstol.se"                       (Swedish courts)
"[amne] SFS [nummer]"                          (Svensk forfattningssamling)
"[amne] Hogsta domstolen"                      (Supreme Court)
"[amne] prop [session]"                        (government bill / proposition)
"[amne] SOU [year]"                            (government inquiry report)
"[amne] Datainspektionen IMY"                  (data protection authority)
```

Swedish legal source tiers:
- **Tier 1**: riksdagen.se, lagrummet.se, domstol.se
- **Tier 2**: Karnov (behind paywall), Zeteo, JP Infonet
- **Tier 3**: Svensk Juristtidning (SvJT), Ny Juridik
- **Tier 4**: Lawline.se (general overviews, verify against primary sources)

### EU Law (multilingual)
```
"[topic] site:eur-lex.europa.eu"
"[topic] CJEU judgment [case number]"
"[regulation/directive number] consolidated version"
"[topic] European Commission implementing regulation"
"[topic] EDPB guidelines [topic]"               (data protection)
"[topic] site:curia.europa.eu"
```

When researching EU law, check:
1. Is it a **regulation** (directly applicable in all member states)?
2. Is it a **directive** (requires national transposition -- check each relevant state)?
3. Has the CJEU interpreted it (check for preliminary rulings under Art. 267 TFEU)?
4. What is the transposition status in the relevant member state?
