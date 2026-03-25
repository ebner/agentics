# Travel & Tourism Research Reference

## Query Patterns

### Pattern 1: Official advisories and entry requirements
```
"[country] travel advisory" site:travel.state.gov
"[country] travel advice" site:gov.uk/foreign-travel-advice
"[country] Reisehinweise" site:auswaertiges-amt.de
"[country] visa requirements [nationality]"
"[country] entry requirements [year]"
"[country] transit visa requirements"
```

### Pattern 2: Health and safety
```
"[country] travel vaccinations" site:cdc.gov
"[country] travel health" site:who.int
"[country] water safety drinking"
"[country] travel insurance requirements"
"[country] safety tips tourists [year]"
```

### Pattern 3: Transport and logistics
```
"[city A] to [city B] flights [year]"
"[city A] to [city B] train bus"
"[destination] airport transfer options"
"[destination] public transport guide"
"[destination] getting around"
site:seat61.com "[destination]"
site:rome2rio.com "[city A]" "[city B]"
```

### Pattern 4: Accommodation and costs
```
"[destination] hotels budget mid-range [year]"
"[destination] average hotel price"
"[destination] daily budget traveler [year]"
"[destination] cost of travel [year]"
"[destination] tourist tax accommodation"
```

### Pattern 5: Activities and experiences
```
"[destination] things to do [year]"
"[destination] top attractions"
"[destination] off the beaten path"
"[destination] local experiences"
"[destination] festivals events [month] [year]"
site:lonelyplanet.com "[destination]"
```

### Pattern 6: Food and dining
```
"[destination] best restaurants [year]"
"[destination] local food must try"
"[destination] street food guide"
"[destination] food market"
"[destination] traditional cuisine dishes"
"[destination] vegetarian vegan restaurants"
"[destination] food tour"
"[destination] restaurant reservations needed"
site:eater.com "[destination]"
site:thefork.com "[destination]"
```

### Pattern 7: Itinerary planning
```
"[destination] [N] day itinerary [year]"
"[destination] suggested itinerary"
"[destination] day trip from"
"[destination] walking tour route"
"[destination] must book in advance"
"[destination] opening hours attractions"
```

### Pattern 8: Seasonal and timing
```
"[destination] best time to visit"
"[destination] weather [month]"
"[destination] high season low season"
"[destination] rainy season avoid"
"[destination] peak tourist months"
```

---

## Preferred Source Tiers

### Tier 1 — Government and official
| Source | URL | Specialty | Language |
|---|---|---|---|
| US State Dept | travel.state.gov | Travel advisories, US | EN |
| UK FCDO | gov.uk/foreign-travel-advice | Travel advisories, UK | EN |
| Auswaertiges Amt | auswaertiges-amt.de | Travel advisories, DE | DE |
| Sweden UD | swedenabroad.se | Travel advisories, SE | SV/EN |
| CDC Traveler's Health | wwwnc.cdc.gov/travel | Health advisories | EN |
| WHO | who.int/travel-advice | Health advisories | EN |

### Tier 2 — Established travel publishers
| Source | URL | Specialty | Language |
|---|---|---|---|
| Lonely Planet | lonelyplanet.com | Destination guides | EN |
| Seat61 | seat61.com | Train/overland travel | EN |
| Rome2Rio | rome2rio.com | Route planning | EN |
| Google Flights | google.com/flights | Flight comparison | EN |
| Skyscanner | skyscanner.com | Flight comparison | EN |
| Eater | eater.com | City food guides | EN |
| The Infatuation | theinfatuation.com | Restaurant guides | EN |

### Tier 3 — Review and booking platforms
| Source | URL | Specialty | Language |
|---|---|---|---|
| TripAdvisor | tripadvisor.com | Reviews, forums | EN |
| Booking.com | booking.com | Accommodation | Multi |
| Google Maps | google.com/maps | Local reviews, restaurants | Multi |
| TheFork | thefork.com | Restaurant reservations | Multi |
| Yelp | yelp.com | Restaurant reviews | EN |

---

## WebFetch Prompts by Source Type

**For government travel advisories:**
"What is the current travel advisory level for this destination? When was it last
updated? What specific risks are mentioned? Are there any restricted areas? What
are the entry/exit requirements listed?"

**For visa/immigration pages:**
"What are the visa requirements for this destination? What types of visas are
available? What is the processing time? What documents are required? Is visa-on-arrival
or e-visa available? What is the cost?"

**For destination guides (Lonely Planet, guidebooks):**
"What are the recommended top experiences for this destination? What practical
information is provided (currency, language, tipping, safety)? What is the
suggested itinerary? What is the best time to visit?"

**For flight/transport comparison sites:**
"What are the available routes from origin to destination? What airlines serve this
route? What is the approximate price range? What is the typical journey time?
Are there direct flights or connections required?"

**For accommodation listings:**
"What is the price range for accommodation in this area? What are the average
review scores? What amenities are included? Is there a tourist tax? What is
the cancellation policy?"

**For health advisory pages:**
"What vaccinations are required or recommended for this destination? Are there
any current disease outbreaks? What health precautions are advised? Is
malaria prophylaxis recommended? What about altitude or heat-related risks?"

**For restaurant/food guides:**
"What are the top-rated restaurants in this area? What cuisine types are available?
What is the price range? Is a reservation required? What are the opening hours?
What are the must-try local dishes? Are there options for vegetarian/vegan/gluten-free
diets? What is the typical tipping custom?"

**For itinerary/activity pages:**
"What is the suggested day-by-day itinerary? What are the opening hours and ticket
prices for each attraction? How long does each activity typically take? What needs
to be booked in advance? What are the travel times between locations? Are there
weather-dependent activities with indoor alternatives?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Travel advisories | Current (< 1 month) | Can change overnight |
| Visa requirements | Current (< 3 months) | Rules change with policy |
| Flight prices | Indicative only | Volatile, state date observed |
| Hotel prices | Seasonal (< 3 months) | Vary by season, demand |
| Health requirements | Current (< 6 months) | New outbreaks change requirements |
| Destination guides | < 2 years | Infrastructure changes slowly |
| Event/festival dates | Current year | Verify annually |
| Transport schedules | Current (< 3 months) | Seasonal schedule changes |

---

## Local-Language Query Patterns

### Destination-language research (adapt to destination)
```
# General pattern — search in destination language for local info
"[destination in local language] evenemang [month]"     (Swedish example)
"[destination in local language] Veranstaltungen [Monat]" (German example)
"[destination in local language] festival [mois]"       (French example)

# Local transport (often cheaper/more accurate in local language)
"[city local name] kollektivtrafik"                     (Swedish)
"[city local name] oeffentlicher Nahverkehr"            (German)
"[city local name] transporte publico"                  (Spanish)

# Local restaurant/food recommendations
"[city local name] basta restauranger"                  (Swedish)
"[city local name] beste Restaurants"                   (German)
"[city local name] mejores restaurantes"                (Spanish)
```

### German (for DACH destinations or German travelers)
```
"[Reiseziel] Reisehinweise"
"[Reiseziel] Einreisebestimmungen"
"[Reiseziel] Sehenswuerdigkeiten"
"[Reiseziel] guenstige Fluege"
"[Reiseziel] Reisetipps [Jahr]"
```

### Swedish (for Nordic destinations or Swedish travelers)
```
"[resmaal] reseinformation UD"
"[resmaal] basta restid"
"[resmaal] sevaardheter"
"[resmaal] billiga flyg"
"[resmaal] resetips [aar]"
```
