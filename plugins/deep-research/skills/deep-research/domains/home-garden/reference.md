# Home & Garden — Search & Source Reference

## Query Patterns by Topic Type

### Code Compliance Queries
```
"[project type] building code [jurisdiction]"
"[project type] permit required [state/country]"
"IRC section [topic] residential [year]"
"NEC article [number] [topic] [year]"
"[project type] Bauordnung [Bundesland]"         → German building code
"[project type] BBR Boverket [year]"              → Swedish building code
"[project type] code requirements [climate zone]"
"[project type] inspection checklist"
```

### Material Comparison Queries
```
"[material A] vs [material B] [application] [year]"
"best [material type] for [application] [climate/region]"
"[material] durability lifespan [application]"
"[material] cost per [unit] [year] [region]"
"[material] pros cons [application]"
"[material] installation requirements"
"[material] R-value thermal performance"          → insulation
"[material] load bearing capacity"                → structural
```

### Gardening Zone-Specific Queries
```
"[plant name] growing zone [USDA zone number]"
"[plant name] hardiness zone [zone] care guide"
"what to plant [month] zone [number]"
"[vegetable/flower] planting calendar [region]"
"[plant] soil pH requirements sun exposure"
"companion planting [plant A] [plant B]"
"native plants [region/state/country]"
"[pest/disease] treatment [plant type] organic"
"[plant] winterization zone [number]"
```

### Cost Estimation Queries
```
"[project type] cost estimate [year] [region]"
"[project type] cost per square foot [year]"
"[project type] DIY vs contractor cost [year]"
"average cost [project type] [city/region] [year]"
"[project type] material list cost breakdown"
"HomeAdvisor [project type] cost"                 → cost aggregator
"[project type] Kosten [year] Deutschland"        → German cost data
```

### Step-by-Step Project Queries
```
"how to [project] step by step"
"[project type] DIY tutorial"
"[project type] installation guide"
"[project type] common mistakes to avoid"
"[project type] tools needed checklist"
"[project type] before and after process"
"[project type] building code compliant DIY"
```

### Seasonal and Maintenance Queries
```
"[season] home maintenance checklist [climate zone]"
"[month] garden tasks [zone/region]"
"[system type] maintenance schedule"
"when to [maintenance task] [region]"
"[season] planting guide [zone]"
"fall winterization checklist [climate]"
"spring garden preparation [zone]"
```

## Preferred Source Tiers

### Tier 1 — Always search and prefer
| Source Type | Examples | Use For |
|---|---|---|
| Building code databases | ICC Digital Codes, up.codes, eCodes | Code section lookups |
| Government housing agencies | HUD, DOE, local building depts | Permit requirements, energy codes |
| University extension services | Extension.org, state university extensions | Gardening, pest management, soil |
| Manufacturer technical docs | Product-specific installation manuals | Installation specs, compatibility |
| Safety standards bodies | UL, ASTM, CE databases | Product safety, testing standards |

### Tier 2 — Good secondary sources
| Source Type | Examples | Use For |
|---|---|---|
| Trade publications | Fine Homebuilding, JLC, Remodeling | Techniques, best practices |
| Expert-reviewed sites | This Old House, Bob Vila (expert content) | General how-to, overviews |
| Gardening authorities | RHS, AHS, Gardeners' World | Plant care, garden design |
| Contractor communities | ContractorTalk, professional forums | Real-world experience, gotchas |
| Product testing | Wirecutter (tools), Consumer Reports | Product recommendations |

### Tier 3 — Use with caution
| Source Type | Examples | Caveat |
|---|---|---|
| DIY communities | r/HomeImprovement, r/gardening | Verify against codes/standards |
| Video tutorials | YouTube channels with credentials | Check for code compliance |
| Cost aggregator sites | HomeAdvisor, Angi, Thumbtack | Ranges only, date-sensitive |
| Social media projects | Instagram, Pinterest builds | No methodology, survivorship bias |

## WebFetch Prompts by Source Type

**For building code pages:**
"What specific code requirements does this page describe for [topic]? Include section
numbers, dimensional requirements, material specifications, and any exceptions or
alternative compliance paths."

**For manufacturer installation guides:**
"What are the specific installation requirements, clearances, material compatibility
notes, and warranty conditions described on this page? Include any required tools
or accessories."

**For extension service / gardening pages:**
"What specific growing recommendations does this page provide? Include hardiness zones,
soil requirements, sun/shade needs, watering frequency, planting depth/spacing, and
seasonal timing. Note any pest or disease warnings."

**For cost estimation pages:**
"What specific cost figures does this page report? Include the date of the data, the
region or market it applies to, whether it covers materials only or materials plus labor,
and any cost breakdowns by component."

**For DIY tutorial pages:**
"What are the specific steps, tools required, materials list, and safety warnings
described in this project tutorial? Does it reference any building codes or permit
requirements? Note the author's stated qualifications."

**For product comparison pages:**
"What specific products are compared, what criteria are used, and what are the test
results or ratings for each? Include any price points with dates and any durability
or warranty comparisons."

**For contractor/trade forum posts:**
"What practical experience or advice does this post share? What specific problems or
solutions are described? Are there code references or professional credentials mentioned?
How many responses agree or disagree?"

## Temporal Sensitivity Rules

| Topic | Sensitivity | Guidance |
|---|---|---|
| Building codes | Update every 3 years (IRC/IBC cycle) | Note edition year; local adoption may lag |
| Material prices | Highly volatile (months) | Always note date; lumber/copper especially |
| Plant availability | Seasonal + annual cultivar changes | Note season and year |
| Energy codes | Update every 3-6 years | Note code version and jurisdiction |
| Tool models | Annual product cycles | Verify current availability |
| Labor costs | Annual variation by market | Note year and metro area |
| Pesticide regulations | Can change with regulatory action | Verify current legality in jurisdiction |
| Product recalls | Ongoing | Check CPSC (US), Rapex (EU) for safety issues |

## Local-Language Query Patterns

### German (DACH Region)
```
"[Projekt] Bauordnung [Bundesland]"
"[Projekt] Baugenehmigung erforderlich"
"[Projekt] nach DIN [Norm-Nummer]"
"[Projekt] EnEV GEG Anforderungen"
"[Projekt] Handwerker oder Eigenleistung"
"[Pflanze] Pflanzzeit [Region] Deutschland"
"[Pflanze] Standort Boden Pflege"
"[Projekt] Kosten pro Quadratmeter [Jahr]"
"Schornsteinfeger Pflicht [Bundesland]"
```

### Swedish
```
"[projekt] bygglov krävs"
"[projekt] Boverket BBR krav"
"[projekt] byggregler [år]"
"[växt] planteringstid [zon] Sverige"
"[växt] odlingszon [nummer]"
"[projekt] kostnad [år] Sverige"
"Elsäkerhetsverket [elarbete] regler"
"[projekt] ROT-avdrag"                            → tax deduction for home work
```
