# Cooking & Food Research Reference

## Query Patterns

### Pattern 1: Professional recipes and techniques
```
"[recipe name] recipe" site:seriouseats.com
"[technique] how to" site:americastestkitchen.com
"[recipe name] recipe" site:cooking.nytimes.com
"[recipe name] recipe" site:bbcgoodfood.com
"[baking topic]" site:kingarthurbaking.com
"[recipe name] tested recipe"
```

### Pattern 2: Food science
```
"[technique] food science why"
"[ingredient] Maillard reaction"
"[process] fermentation science"
"Harold McGee [topic]"
"Kenji Lopez-Alt [technique]"
"[topic] food chemistry"
```

### Pattern 3: Food safety
```
"[food item] safe internal temperature" site:fda.gov
"[food item] safe cooking temperature" site:usda.gov
"[preservation method] safety guidelines"
"[food item] storage time refrigerator"
"[canning topic] pressure canning safety"
"[food item] Lebensmittelsicherheit" site:bfr.bund.de
"[food item] livsmedelssaekerhet" site:livsmedelsverket.se
```

### Pattern 4: Cultural and traditional recipes
```
"[dish name] traditional recipe [origin country]"
"[dish name] authentic [cuisine]"
"[dish name] [origin language name]"
"[cuisine] regional variations"
"[dish name] history origin"
```

### Pattern 5: Ingredients and substitutions
```
"[ingredient] substitute in [recipe type]"
"[ingredient] what is how to use"
"[ingredient] seasonal availability"
"[ingredient] quality indicators how to choose"
"[ingredient A] vs [ingredient B] in baking"
```

### Pattern 6: Restaurant and dining
```
"[city] best restaurants [year]"
"[city] [cuisine type] restaurant recommendations"
"[restaurant name] review"
"[city] Michelin restaurants [year]"
"[city] food guide [year]"
```

---

## Preferred Source Tiers

### Tier 1 — Professional and institutional
| Source | URL | Specialty | Language |
|---|---|---|---|
| Serious Eats | seriouseats.com | Science-based recipes/techniques | EN |
| ATK / Cook's Illustrated | americastestkitchen.com | Systematic recipe testing | EN |
| NYT Cooking | cooking.nytimes.com | Tested recipes | EN |
| BBC Good Food | bbcgoodfood.com | Tested recipes, UK measures | EN |
| King Arthur Baking | kingarthurbaking.com | Baking science | EN |
| Epicurious | epicurious.com | Tested recipes | EN |
| Bon Appetit | bonappetit.com | Tested recipes | EN |
| FDA | fda.gov | US food safety | EN |
| EFSA | efsa.europa.eu | EU food safety | EN |
| BfR | bfr.bund.de | German food safety | DE |
| Livsmedelsverket | livsmedelsverket.se | Swedish food safety | SV |

### Tier 2 — Established food media
| Source | URL | Specialty | Language |
|---|---|---|---|
| Smitten Kitchen | smittenkitchen.com | Home cooking | EN |
| David Lebovitz | davidlebovitz.com | French pastry, Paris dining | EN |
| Just One Cookbook | justonecookbook.com | Japanese cuisine | EN |
| Chefkoch | chefkoch.de | German recipes, community | DE |
| ICA Recept | ica.se/recept | Swedish recipes | SV |
| Cookpad | cookpad.com | Community recipes, Japanese origin | Multi |
| Michelin Guide | guide.michelin.com | Restaurant reviews | Multi |
| Larousse Cuisine | larousse.fr/cuisine | French culinary reference | FR |

### Tier 3 — Community and reference
| Source | URL | Specialty | Language |
|---|---|---|---|
| Allrecipes | allrecipes.com | Community recipes | EN |
| Food52 | food52.com | Community + editorial | EN |
| The Kitchn | thekitchn.com | Technique guides | EN |
| Marmiton | marmiton.org | French community recipes | FR |

---

## WebFetch Prompts by Source Type

**For recipe pages (Serious Eats, NYT, BBC Good Food):**
"What are the exact ingredients with quantities and measurements? What is the
step-by-step method? What is the total time (prep + cook)? Are there any
notes on technique or common mistakes? What equipment is needed? What is the
yield/serving size?"

**For food science articles:**
"What is the scientific explanation for this cooking phenomenon? What chemical
reactions are involved? What specific temperatures, times, or ratios are
recommended based on the science? Are there references to primary research?"

**For food safety pages (FDA, EFSA, BfR):**
"What is the recommended safe internal temperature for this food? What are
the safe storage times and temperatures? What are the specific foodborne illness
risks? What populations are at higher risk? What handling precautions are
recommended?"

**For restaurant review/guide pages:**
"What is the rating or score? What cuisine type? What is the price range?
What dishes are highlighted as recommended? What are the hours and reservation
requirements? What is the address and how to get there?"

**For ingredient reference pages:**
"What is this ingredient? What does it taste like? What are common uses in
cooking? What are acceptable substitutes and how do they differ? How should
it be stored? Is it seasonal? Are there regional names or variations?"

**For cultural cuisine articles:**
"What is the cultural origin and significance of this dish? What are the
traditional ingredients and preparation method? How does it vary by region?
What is the historical context? Is there a traditional occasion for serving
this dish?"

---

## Temporal Sensitivity

| Data type | Freshness requirement | Notes |
|---|---|---|
| Food safety guidelines | Current (< 2 years) | Standards get updated |
| Recipes | Evergreen | Classic recipes do not expire |
| Restaurant reviews | < 1 year | Restaurants change frequently |
| Ingredient availability | Seasonal | Note growing/harvest seasons |
| Culinary trends | < 2 years | Trends shift |
| Cooking science | < 10 years | Foundational science is stable |
| Restaurant openings/closures | Current (< 3 months) | Verify still operating |

---

## Local-Language Query Patterns

### French (foundational cuisine)
```
"[plat] recette traditionnelle"
"[technique] methode classique"
"[ingredient] en cuisine francaise"
"[patisserie] recette"
```

### Italian
```
"[piatto] ricetta tradizionale"
"[piatto] ricetta originale [regione]"
"[ingrediente] come usare"
```

### Japanese
```
"[dish romanized] recipe traditional"
"[dish] tsukurikata"
"[ingredient] Japanese cooking"
```

### German
```
"[Gericht] Rezept original"
"[Gericht] traditionelles Rezept"
"[Zutat] Verwendung Kueche"
"[Backen] Rezept" site:chefkoch.de
```

### Swedish
```
"[raett] recept traditionellt"
"[raett] recept" site:ica.se
"[raett] ursprung tradition"
"[ingrediens] anvandning matlagning"
```
