# Consumer & Product Research Reference

## Query Patterns

### Pattern 1: Independent test results
```
"[product name] test" site:test.de
"[product name] review" site:consumerreports.org
"[product name] review" site:rtings.com
"[product name] review" site:which.co.uk
"[product category] Stiftung Warentest [year]"
"[product category] best [year]" site:nytimes.com/wirecutter
```

### Pattern 2: Comparison and alternatives
```
"[product A] vs [product B] [year]"
"[product category] comparison test [year]"
"best [product category] [year]" -"affiliate" -"buy now"
"[product name] alternative"
"[product name] vs [competitor] benchmark"
```

### Pattern 3: Long-term and reliability
```
"[product name] review after 6 months"
"[product name] one year later"
"[product name] long-term review"
"[product name] reliability problems"
"[product name] durability test"
"[brand name] reliability ratings"
```

### Pattern 4: Safety and recalls
```
"[product name] recall" site:cpsc.gov
"[product name] recall" site:ec.europa.eu
"[product name] safety alert"
"[product name] class action"
"[product name] defect"
```

### Pattern 5: Pricing and deals
```
"[product name] price history" site:camelcamelcamel.com
"[product name] Preisvergleich" site:idealo.de
"[product name] prisjakt"
"[product name] refurbished"
"[product name] open box deal"
```

### Pattern 6: Repairability and longevity
```
"[product name] teardown" site:ifixit.com
"[product name] repairability"
"[product name] replacement parts"
"[product name] battery replacement"
"[product name] software update support"
```

### Pattern 7: Fake review detection
```
"[product name] fake reviews"
"[product name] fakespot"
"[product name] reviewmeta"
"[brand name] astroturfing"
```

---

## Preferred Source Tiers

### Tier 1 — Always search these first
| Source | URL | Specialty | Language |
|---|---|---|---|
| Consumer Reports | consumerreports.org | All categories, US focus | EN |
| Stiftung Warentest | test.de | All categories, DACH focus | DE |
| Which? | which.co.uk | All categories, UK focus | EN |
| Wirecutter | nytimes.com/wirecutter | Curated picks, US focus | EN |
| RTINGS | rtings.com | TVs, monitors, headphones, soundbars | EN |
| iFixit | ifixit.com | Repairability teardowns | EN |
| CPSC | cpsc.gov | US product recalls | EN |

### Tier 2 — Cross-reference with Tier 1
| Source | URL | Specialty | Language |
|---|---|---|---|
| testberichte.de | testberichte.de | German review aggregator | DE |
| Pro Tool Reviews | protoolreviews.com | Power tools, hand tools | EN |
| Testfakta | testfakta.se | Swedish independent testing | SV |
| DxOMark | dxomark.com | Camera/sensor testing | EN |
| Tom's Hardware | tomshardware.com | PC components, peripherals | EN |
| The Verge | theverge.com | Consumer electronics | EN |
| Ars Technica | arstechnica.com | Technical deep dives | EN |

### Tier 3 — Pricing and market data
| Source | URL | Specialty | Language |
|---|---|---|---|
| CamelCamelCamel | camelcamelcamel.com | Amazon price history | EN |
| Idealo | idealo.de | EU price comparison | DE |
| Prisjakt | prisjakt.se | Nordic price comparison | SV |
| PriceRunner | pricerunner.com | EU/UK price comparison | EN |
| Geizhals | geizhals.de | DACH price comparison | DE |

---

## WebFetch Prompts by Source Type

**For independent testing organizations (Consumer Reports, Stiftung Warentest, RTINGS):**
"What is the overall score/rating for this product? What specific tests were conducted?
What were the measured performance numbers? What are the listed pros and cons? How does
it compare to alternatives tested in the same round?"

**For editorial review sites (Wirecutter, The Verge, Ars Technica):**
"What is the overall verdict and score? What specific aspects were tested and how?
What are the stated pros and cons? Is there an affiliate disclosure? How long was the
review period? Are there comparison recommendations?"

**For product specification pages:**
"What are the exact specifications: dimensions, weight, battery capacity, processor,
RAM, storage, display specs, connectivity, certifications? What is the warranty period?
What is the current price?"

**For iFixit teardowns:**
"What is the repairability score (out of 10)? What are the key repairability positives
and negatives? Are common failure components (battery, screen, ports) replaceable?
What tools are required? Are parts available for purchase?"

**For recall/safety pages:**
"What product models are affected? What is the hazard? What date range of manufacture
is covered? What is the remedy (repair, replace, refund)? How many units are affected?"

**For price comparison/history sites:**
"What is the current price? What is the historical low price? What is the average price
over the last 6 months? What retailers currently stock this product? Are there any
current deals or coupons?"

**For user review aggregation pages:**
"What is the average star rating? How many reviews total? What are the most common
praise themes? What are the most common complaint themes? Are there verified purchase
indicators? What is the rating distribution (1-5 stars)?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Product availability | Current (< 1 month) | Products get discontinued |
| Pricing | Current (< 1 week ideal) | Prices fluctuate daily |
| Reviews & ratings | < 6 months preferred | Recent firmware can change experience |
| Independent test results | < 2 years | Test methodology may change |
| Recall notices | All time | Safety data never expires |
| Repairability scores | < 3 years | Valid for product lifespan |
| Energy ratings | < 3 years | Regulations change scales |

---

## Local-Language Query Patterns

### German (DACH market)
```
"[Produktname] Test Stiftung Warentest"
"[Produktname] Testbericht"
"[Produktname] Erfahrungsbericht"
"[Produktname] Preisvergleich"
"[Produktkategorie] Testsieger [Jahr]"
"[Produktname] Bewertung"
"[Produktname] Rueckruf"
```

### Swedish (Nordic market)
```
"[produktnamn] test Testfakta"
"[produktnamn] recension"
"[produktkategori] bast i test [ar]"
"[produktnamn] prisjakt"
"[produktnamn] omdome"
```
