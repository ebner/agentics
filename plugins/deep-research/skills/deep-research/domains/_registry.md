# Domain Registry

The orchestrator reads this file to determine which domain agent profile(s) to use
for a given research topic. Each entry maps a domain to its trigger signals, risk level,
and file paths.

## Routing Rules

1. Read the user's research topic and any clarification answers.
2. Evaluate each domain's trigger signals semantically (not regex) — consider the full
   context of the query, not just individual keywords.
3. Score each domain: count how many trigger signals are present or implied.
4. Select domains scoring >= 2 trigger matches, OR the single highest-scoring
   domain if only one scores >= 1.
5. If no domain scores >= 1, use `general`.
6. For cross-domain topics, tag each sub-question with its primary domain and spawn
   domain-appropriate agents.

**Disambiguation rules:**
- Technical terms in software context are NOT medical/legal triggers
  (e.g., "health check", "injection", "patch" in a Kubernetes context → tech, not health/legal)
- "Mortgage" in a home-buying context → home-garden (primary) + finance (secondary)
- Purchasing equipment FOR a sport → consumer (primary) + sports (secondary)
- Nutrition for health claims → health; nutrition for cooking → cooking
- Specific drug questions (mechanism, side effects, interactions, dosing, genetics) → medical-pharma
- General health conditions ("what is diabetes?", "is fasting healthy?") → health
- "Should I take metformin?" → medical-pharma (primary) + health (secondary)
- Child illness → health (not parenting-pets); pet illness → health (not parenting-pets)
- Tax implications → finance (primary) + legal (secondary)

## Domain Table

| Domain | Directory | Risk | Trigger Signals |
|---|---|---|---|
| Health & Medical | `domains/health/` | HIGH | health, medical, disease, treatment, symptoms, wellness, nutrition (health context), diet (health context), mental health, therapy, supplement, vaccine, surgery, condition, fitness (health context) |
| Medical & Pharma | `domains/medical-pharma/` | HIGH | drug, medication, pharmaceutical, pharmacology, side effects, adverse reaction, drug interaction, pharmacogenomics, CYP450, genotype, metabolizer, clinical trial, dosage, prescribing, contraindication, pharmacokinetics, drug safety, black box warning, FAERS, FDA label, SmPC |
| Finance & Investment | `domains/finance/` | HIGH | investment, stock, bond, ETF, fund, portfolio, dividend, market, trading, budget, savings, interest rate, mortgage (financial context), tax, retirement, pension, insurance (financial product), crypto, forex, ROI, financial planning |
| Legal & Regulatory | `domains/legal/` | HIGH | law, legal, regulation, compliance, contract, lawsuit, liability, patent, copyright, trademark, attorney, court, statute, rights, permit (legal context), zoning, GDPR, privacy law |
| Home & Garden | `domains/home-garden/` | MEDIUM | home improvement, renovation, build, construct, repair, plumbing, electrical (home context), garden, plant, soil, lawn, landscaping, fence, deck, patio, insulation, roofing, DIY, house maintenance, HVAC, painting |
| Sports & Fitness | `domains/sports/` | MEDIUM | sport, team, player, season, match, league, score, championship, training (sport context), athlete, coach, workout, exercise, gym, running, cycling, swimming, martial arts, draft, standings |
| Science & Education | `domains/science-education/` | MEDIUM | physics, chemistry, biology (non-medical), history, university, course, degree, certification, academic, research (scientific context), science, experiment, theory, education, learning, scholarship, admission |
| Parenting & Pets | `domains/parenting-pets/` | MEDIUM | parenting, child, baby, toddler, teenager, pet, dog, cat, veterinary, breed, puppy, kitten, childcare, school (K-12), pediatric (non-medical), pet care, animal behavior |
| Consumer & Product | `domains/consumer/` | LOW | buy, purchase, review (product context), product comparison, warranty, brand, price, best (product), rating, consumer reports, deal, which (product) should I, electronics, appliance, tool (purchase context) |
| Travel & Tourism | `domains/travel/` | LOW | travel, flight, hotel, destination, vacation, itinerary, visa, airline, booking, resort, cruise, backpacking, tourism, trip, sightseeing |
| Entertainment | `domains/entertainment/` | LOW | movie, film, TV, show, music, concert, streaming, album, theater, podcast, anime, series, festival, ticket (event), band, artist, venue, game (video/board) |
| Cooking & Food | `domains/cooking/` | LOW | recipe, cooking, ingredient, cuisine, restaurant, chef, baking, meal, food (culinary context), kitchen technique, spice, flavor, fermentation, barbecue, wine, cocktail |
| Technology | `domains/tech/` | LOW | software, programming, framework, API, database, cloud, server, deployment, benchmark, architecture (software), language (programming), library (code), open source, DevOps, algorithm, information architecture, data modeling |
| Career & Employment | `domains/career-employment/` | LOW | employment, salary, job, hiring, career, resume, interview, workplace, labor market, job market, remote work, freelance, promotion, profession, occupation, company reviews |
| General | `domains/general/` | LOW | (fallback — used when no other domain scores >= 1) |

## Language/Region Detection

After domain classification, detect language and region relevance:

1. **From topic context**: "German building codes" → German language, DACH region
2. **From user's question language**: Question in German → add German to search languages
3. **From domain + region**: Legal topics often need jurisdiction-specific local language
4. **Default**: English + auto-detected relevant language(s)

Output:
- `primary_language`: Language for the report (matches question language)
- `search_languages[]`: Languages to generate queries in
- `region_context`: Region for region-specific sources (building codes, legal, labor market)

## Cross-Domain Resolution

When multiple domains match:
1. Decompose sub-questions and TAG each with its primary domain.
2. Each sub-question uses ONE domain agent (best match), not multiple.
3. The orchestrator merges results across domains during triangulation (STEP 6).

Examples:
- "Should I buy a home gym?" → consumer + health + home-garden
- "Tax implications of stock options" → finance + legal
- "Best laptop for software engineering students" → consumer + tech + science-education
- "Best supplements for marathon training" → health + sports + consumer

## Adding a New Domain

1. Create `domains/<domain-name>/agent.md` with YAML frontmatter and domain-specific instructions
2. Create `domains/<domain-name>/reference.md` with credibility rules, preferred sources, query patterns
3. Add a row to the Domain Table above
4. Commit the new domain directory to the plugin repository
